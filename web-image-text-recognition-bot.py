import requests
import configparser
import asyncio
import pytesseract
from PIL import Image
from aiogram import Bot, Dispatcher, types
from bs4 import BeautifulSoup

# Читаем файл, в котором хранится чувствительная информация - токен бота для API
config = configparser.ConfigParser()
config.read("config.ini")
TOKEN = config['Telegram']['API_TOKEN']

URL = 'http://новоспасский-монастырь.рф/raspisanie' # Адрес страницы, с которой будем забирать картинку
contents = requests.get(URL).text # Забираем содержимое этой страницы
soup = BeautifulSoup(contents, 'html.parser') # Смотрим содержимое через HTML-парсер
my_img = soup.find("div", class_="leading-0").p.img.get('src') # Берем div, у которого нужный нам class, внутри этого div есть параграф, внутри которого нужный нам файл картинки, из которого мы забираем содержимое атрибута src
img_url = "http://xn----7sbbf5agftchdbghyfcaiu3qxa.xn--p1ai" + my_img # Составляем адрес для картинки

tesseract_config = r'--psm 6' # Настройка для распознавания текста с картинки 

# Загрузка изображения с текстом
with Image.open(requests.get(img_url, stream=True).raw) as image:
    string = pytesseract.image_to_string(image, lang='rus', config=tesseract_config) # Кладем сюда распознанный текст

bot = Bot(token=TOKEN) # Инициализация бота
dp = Dispatcher(bot)

@dp.message_handler(commands="start")
async def command_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Текст", "Картинка"]
    keyboard.add(*buttons)
    await message.answer("Бот скачивает с сайта Новоспасского монастыря расписание богослужений и показывает его в виде текста или картинки. Распознавание текста с картинки может быть неточным. Связаться с разработчиком @minaton_ru.\n" "Официальный сайт Новоспасского монастыря - новоспасский-монастырь.рф.\n\n" "Выберите один из вариантов просмотра расписания: получить в виде текстового сообщения или загрузить в виде картинки.", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "Текст")
async def send_text(message: types.Message):
    await message.answer(string) # Высылает распознанный текст

@dp.message_handler(lambda message: message.text == "Картинка")
async def send_text(message: types.Message):
    await bot.send_photo(message.chat.id, types.InputFile.from_url(img_url)) # Высылает картинку

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())