"""
This is a echo bot.
It echoes any incoming text messages.
"""

import logging
import sys
import hashlib
import re

from typing import List
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from aiogram.types import InlineQuery, \
    InputTextMessageContent, InlineQueryResultArticle, Update, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from lib.weather import Weather
from aiogram.utils.markdown import hbold, hitalic

API_TOKEN = '784847496:AAEMdIue3F7YIRl7GDcTX-Di--63we_0q4w'
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
I18N_DOMAIN = 'bot'

BASE_DIR = sys.path[0]
LOCALES_DIR = BASE_DIR + '/locales'

i18n = I18nMiddleware(I18N_DOMAIN, LOCALES_DIR)
dp.middleware.setup(i18n)

_ = i18n.gettext

dictionary = [
    "mobile",
    "hello",
    "city",
    "message",
    "word",
    "people",
    "person"
]


class Form(StatesGroup):
    city = State()
    search = State()
    lang = State()


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message, *args):
    """
    This handler will be called when user sends `/start` command
    """
    await message.answer(_("Hi, I'm just a test bot, nice to meet you {}!\nType /help for more commands".format(message.chat.full_name)))


@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    text = [
        hbold(_("Here you can read the list of my commands:")),
        _("{command} - Start bot").format(command="/start"),
        _("{command} - Get this message").format(command="/help"),
        _("{command} - Get weather of city").format(command="/weather"),
        _("{command} - Search a word in local dictionary").format(command="/search"),
        _("{command} - My language").format(command="/lang"),
        _("{command} - Change language").format(command="/setlang"),
        "",
    ]
    await message.answer("\n".join(text))


@dp.message_handler(commands='lang')
async def cmd_lang(message: types.Message, locale):
    # For setting custom lang you have to modify i18n middleware
    await message.reply(_('Your current language: {}').format(hitalic(locale)))


@dp.message_handler(commands='setlang')
async def set_lang(message: types.Message):
    await Form.lang.set()
    await message.answer('Type locale to switch (Ex: tg - for tajik, ru - russian, en - english)!')


@dp.message_handler(state=Form.lang)
async def process_lang(message: types.Message, state: FSMContext, *args):
    async with state.proxy() as data:
        print('args: ', args)
        lang = message.text
        if re.match('(en|tg|ru)', lang):
            data['lang'] = lang
            await message.answer(_("Language switched to {}".format(hbold(lang))))
            await state.finish()
        else:
            await message.answer(_("This type of locale doesn't support!\nPlease type one of: en, ru, tg"))


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


# @dp.message_handler(state=Form.name)
# async def process_name(message: types.Message, state: FSMContext):
#     """
#     Process user name
#     """
#     async with state.proxy() as data:
#         data['name'] = message.text
#
#     await message.answer("Nice to meet you, {}!".format(data['name']))
#     await state.finish()


@dp.message_handler(regexp='(^flag[s]?$|tj[k]?|tajik[is]?|tajikistan|vatan)')
async def flag(message: types.Message):
    with open('assets/images/tjk.jpg', 'rb') as photo:
        await message.answer_photo(photo, caption=_('We all live in Tajikistan'))


@dp.message_handler(commands=['weather'])
async def send_weather(message: types.Message):
    await Form.city.set()
    await message.answer(_('Please type a city name!'))


@dp.message_handler(state=Form.city)
async def process_weather(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['city'] = message.text

    weather = Weather.get_weather_by_city(message.text)
    text = _('Nothing found(')

    if weather:
        temp = weather.get('temp')
        temp_min = weather.get('temp_min', '-')
        temp_max = str(weather.get('temp_max', '-'))
        pressure = str(weather.get('pressure', '-')) + 'hPa'
        humidity = str(weather.get('humidity', '-')) + '%'
        feels_like = str(weather.get('feels_like', '-'))
        text = [
            _("Temperature: {}").format(temp),
            _("Minimum temp: {}").format(temp_min),
            _("Maximum temp: {}").format(temp_max),
            _("Feels like: {}").format(feels_like),
            _("Pressure: {}").format(pressure),
            _("Humidity: {}").format(humidity)
        ]
    await message.answer("\n".join(text))
    await state.finish()


@dp.message_handler(commands=['logs'])
async def send_logs(message: types.Message):
    await message.answer('Logs: ')


@dp.message_handler(commands=['search'])
async def send_search(message: types.Message):
    await Form.search.set()
    await message.answer(_('Type a word you want to search!'))


@dp.message_handler(state=Form.search)
async def process_search(message: types.Message, state: FSMContext):
    text = message.text
    founded = []
    for _str in dictionary:
        if _str.find(text) > -1:
            founded.append(_str)
    if len(founded):
        await message.answer(_("I've found {} in dictionary!").format(hbold(', '.join(founded))))
    else:
        await message.answer(_("Nothing found("))
    await state.finish()


@dp.message_handler(regexp='')
async def _reply(message: types.Message):
    updates: List[Update] = await bot.get_updates()
    for m in updates:
        print('Message: ', m.message.text)
    await message.reply(_("I don't know this message"))


@dp.message_handler()
async def check_language(message: types.Message):
    locale = message.from_user.locale
    print('User locale: ', locale)


@dp.inline_handler()
async def inline_echo(inline_query: InlineQuery):
    # id affects both preview and content,
    # so it has to be unique for each result
    # (Unique identifier for this result, 1-64 Bytes)
    # you can set your unique id's
    # but for example i'll generate it based on text because I know, that
    # only text will be passed in this example
    text = inline_query.query or 'echo'
    input_content = InputTextMessageContent(text)
    result_id: str = hashlib.md5(text.encode()).hexdigest()
    item = InlineQueryResultArticle(
        id=result_id,
        title=f'Result {text!r}',
        input_message_content=input_content,
    )
    # don't forget to set cache_time=1 for testing (default is 300s or 5m)
    await bot.answer_inline_query(inline_query.id, results=[item], cache_time=1)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
