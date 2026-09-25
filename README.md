# web-image-text-recognition-bot

This Telegram bot extracts text from an image located on a website and sends that text to the Telegram user.

- The Tesseract library (via the pytesseract module) is used for text recognition.
- The BeautifulSoup library is used to retrieve the image from the website.
- The aiogram 3 library is used for the bot.

## Setup
```bash
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-rus
uv sync
```

The `.env` file in the root directory stores tokens in the following format: 
```ini
API_TOKEN=
``` 

Working example https://t.me/novospass_bot    

## Todo
- ~~Add buttons to choose between viewing the original image and getting the text~~
- ~~Use aiohttp instead of requests~~
- ~~Add a "waiting for upload" message~~
- Add tests
- Add a check to see if the image has already been uploaded
- Switch to webhooks 
