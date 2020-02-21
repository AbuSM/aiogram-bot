"""
This is a echo bot.
It echoes any incoming text messages.
"""

import logging
from aiogram import Bot, Dispatcher, executor, types
from weather import Weather

API_TOKEN = '784847496:AAEMdIue3F7YIRl7GDcTX-Di--63we_0q4w'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi, I'm just a test bot")


@dp.message_handler(regexp='(^flag[s]?$|tj[k]?|tajik[is]?|tajikistan|vatan)')
async def flag(message: types.Message):
    with open('assets/images/tjk.jpg', 'rb') as photo:
        await message.reply_photo(photo, caption='We all live in Tajikistan')


@dp.message_handler(commands=['weather'])
async def send_weather(message: types.Message):
    weather = Weather.get_weather_by_city('Dushanbe')
    await message.reply(weather)

# @dp.message_handler()
# async def echo(message: types.Message):
#     # old style:
#     # await bot.send_message(message.chat.id, message.text)
#
#     await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)