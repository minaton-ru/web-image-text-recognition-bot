import io
import configparser
import asyncio
import aiohttp
import pytesseract
from PIL import Image
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from bs4 import BeautifulSoup

# Reading the file that stores sensitive information - the bot token for the API
config = configparser.ConfigParser()
config.read("config.ini")
TOKEN = config['Telegram']['API_TOKEN']

URL = 'http://новоспасский-монастырь.рф/raspisanie/'  # The web page URL from which we will retrieve the image
tesseract_config = r'--psm 6'  # Configuration for text recognition


async def get_img_url(URL):
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as response:
            html = await response.text()  # Get page body
            soup = BeautifulSoup(html, 'html.parser')  # Parse html
            # We select the div with the required class; inside this div is a paragraph, which
            # contains the target image tag, from which we extract the content of the src attribute.
            img_url = soup.find("div", class_="single").img.get('src')
            return img_url


async def text_recog_from_img(img_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(img_url) as response:
            data = await response.read()
            file = Image.open(io.BytesIO(data))
            string = pytesseract.image_to_string(file, lang='rus', config=tesseract_config)
            return string

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))  # On start command bot show welcome message and two buttons
async def command_start(message: Message):
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Текст"), KeyboardButton(text="Картинка")]], resize_keyboard=True)
    await message.answer("Бот скачивает с сайта Новоспасского монастыря расписание богослужений и показывает его в виде текста или картинки. Распознавание текста с картинки может быть неточным. Связаться с разработчиком @minaton_ru.\n" "Официальный сайт Новоспасского монастыря - новоспасский-монастырь.рф.\n\n" "Выберите один из вариантов просмотра расписания: получить в виде текстового сообщения или загрузить в виде картинки.", reply_markup=keyboard)

@dp.message(F.text == "Текст")
async def send_text(message: Message):
    info_message = await bot.send_message(message.from_user.id, "Загрузка, подождите........")
    img_url = await get_img_url(URL)
    string = await text_recog_from_img(img_url)
    await bot.delete_message(message.from_user.id, info_message.message_id)
    await message.answer(string)
    print("DONE")

@dp.message(F.text == "Картинка")
async def send_img(message: Message):
    img_url = await get_img_url(URL)
    await bot.send_photo(message.chat.id, img_url)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
