# web-image-text-recognition-bot


## Overview
This Telegram bot extracts text from an image located on a website and sends that text to the Telegram user.

- The Tesseract library (via the pytesseract module) is used for text recognition. `TextRecognizer` accepts an optional OCR engine (`TesseractOCR` by default), so it can be replaced, e.g. with a fake in tests.
- The BeautifulSoup library is used to retrieve the image from the website.
- The aiogram 3 library is used for the bot.

## Quickstart
1. Create `.env` from `.env.example` with settings as needed.
2. Install Tesseract OCR:
```bash
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-rus
```
3. Run `uv sync`.
3. Start the bot `uv run main.py`.

## Tests
Run tests with `uv run pytest`. Run only integration tests with `uv run pytest -m integration`, or skip them with `uv run pytest -m "not integration"`.

- `tests/unit/` - unit tests for `utils/` (HTTP download, scraping, text recognition) and `handlers/` (start command, menu buttons).
- `tests/integration/` - integration tests of the bot and dispatcher: updates go through the real routers, scraper and recognizer. A local aiohttp web server serves the fixture HTML page and image from `tests/integration/fixtures/`, a fake DNS resolver points the site domain to it, and a fake Telegram session stores the bot API requests in memory.
- `tests/fakes.py` - in-memory fakes of the aiohttp session, the DNS resolver, the OCR engine, the Telegram session, bot and message, the image scraper and the text recognizer, so tests need neither network, Tesseract nor Telegram.

## Configuration
The `.env` file in the root directory stores tokens in the following format:
```ini
API_TOKEN=
```

Other settings and interface texts are in `constants.py`.

## Live demo
Working example https://t.me/novospass_bot

## Todo
- ~~Add buttons to choose between viewing the original image and getting the text~~
- ~~Use aiohttp instead of requests~~
- ~~Add a "waiting for upload" message~~
- Add tests
- Add a check to see if the image has already been uploaded
- Switch to webhooks
