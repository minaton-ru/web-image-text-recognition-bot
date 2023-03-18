# web-image-text-recognition-bot
Телеграм-бот распознает текст с картинки, которая находится на сайте, высылает этот текст пользователю телеграма.  

Для распознавания текста с картинки используется библиотека Tesseract через модуль pytesseract.  
Для получения картинки с сайта используется библиотека BeautifulSoup.  
В файле config.ini хранится токен для телеграм-бота.  

Todo:  
- Добавить кнопки для выбора - посмотреть исходную картинку или получить текст  
- Добавить проверку на то, что эту картинку уже смотрели (кеширование)  