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

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.reply(string) # На команду start бот делает ответ на сообщение и высылает распознанный текст

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())