# web-image-text-recognition-bot
Телеграм-бот распознает текст с картинки, которая находится на сайте, высылает этот текст пользователю телеграма.  

Для распознавания текста с картинки используется библиотека Tesseract через модуль pytesseract.  
Для получения картинки с сайта используется библиотека BeautifulSoup.
Для бота используется библиотека aiogram 2.    
В файле config.ini хранится токен для телеграм-бота.  

Посмотреть как работает можно на примере бота https://t.me/novospass_bot    

Todo:  
- ~~Добавить кнопки для выбора - посмотреть исходную картинку или получить текст~~  
- ~~Использовать aiohttp вместо requests~~  
- добавить прогрессбар   
- Добавить проверку на то, что эту картинку уже загружали (кеширование)  
- Перейти на webhook  
