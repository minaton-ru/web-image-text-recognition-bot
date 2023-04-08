import io
import configparser
import asyncio
import aiohttp
import pytesseract
from PIL import Image
from aiogram import Bot, Dispatcher, types
from bs4 import BeautifulSoup

# Читаем файл, в котором хранится чувствительная информация - токен бота для API
config = configparser.ConfigParser()
config.read("config.ini")
TOKEN = config['Telegram']['API_TOKEN']

URL = 'http://новоспасский-монастырь.рф/raspisanie' # Адрес страницы, с которой будем забирать картинку
tesseract_config = r'--psm 6' # Настройка для распознавания текста с картинки

async def get_img_url(URL):
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as response:  # Забираем содержимое этой страницы
            html = await response.text() # Смотрим содержимое через HTML-парсер
            soup = BeautifulSoup(html, 'html.parser') # Смотрим содержимое через HTML-парсер
            my_img = soup.find("div", class_="leading-0").p.img.get('src') # Берем div, у которого нужный нам class, внутри этого div есть параграф, внутри которого нужный нам файл картинки, из которого мы забираем содержимое атрибута src
            img_url = "http://xn----7sbbf5agftchdbghyfcaiu3qxa.xn--p1ai" + my_img # Составляем адрес для картинки
            return img_url

async def text_recog_from_img(img_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(img_url) as response: # Загрузка нужной картинки, на которой текст
            data = await response.read()
            file = Image.open(io.BytesIO(data))
            string = pytesseract.image_to_string(file, lang='rus', config=tesseract_config) # Кладем сюда распознанный текст
            return string

bot = Bot(token=TOKEN) # Инициализация бота
dp = Dispatcher(bot)

@dp.message_handler(commands="start") # Бот по команде start показывает приветственный текст и две кнопки
async def command_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Текст", "Картинка"]
    keyboard.add(*buttons)
    await message.answer("Бот скачивает с сайта Новоспасского монастыря расписание богослужений и показывает его в виде текста или картинки. Распознавание текста с картинки может быть неточным. Связаться с разработчиком @minaton_ru.\n" "Официальный сайт Новоспасского монастыря - новоспасский-монастырь.рф.\n\n" "Выберите один из вариантов просмотра расписания: получить в виде текстового сообщения или загрузить в виде картинки.", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "Текст")
async def send_text(message: types.Message):
    info_message = await bot.send_message(message.from_user.id, "Загрузка, подождите........")
    img_url = await get_img_url(URL)
    string = await text_recog_from_img(img_url)
    await bot.delete_message(message.from_user.id, info_message.message_id)
    await message.answer(string) # Высылает распознанный текст

@dp.message_handler(lambda message: message.text == "Картинка")
async def send_img(message: types.Message):
    img_url = await get_img_url(URL)
    await bot.send_photo(message.chat.id, types.InputFile.from_url(img_url)) # Высылает картинку

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())