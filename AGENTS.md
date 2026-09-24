# Telegram bot with text recognition from web image

The Telegram bot recognizes text from an image located on a website and sends that text to the Telegram user.

## Technology Stack
- aiogram 3
- Tesseract OCR (via the pytesseract package) for text recognition from image
- BeautifulSoup 4 to retrieve images from the website

## Project Structure
`handlers/` - routers
`keyboards/` - keyboards
`utils/` - helpers for parsing and image recognition
`main.py` - entry point for bot initialization

## Project Setup and Management
- Install tesseract: `apt install tesseract-ocr` and `apt install tesseract-ocr-rus`.
- Dependency management: `uv` and `pyproject.toml`
- Run the app with `uv run fastapi dev main.py`.
- Create branch from `main` according to the project's branch naming convention.
- Stage changes for review. Don't commit to `main` or push without being asked.

## Testing
- Tests - only `pytest`, functions. No `unittest.TestCase`.
- Mocks - only Fake classes. No `MagicMock`, `patch`, `unittest.mock`.

## Code Style
- Use modern Python 3.13 syntax:
  - `X | None` instead of `Optional[X]`
  - `list[str]` instead of `List[str]`
- Write clear, short code without unnecessary complexity.
- If logic repeats - extract it into helper functions.
- Follow PEP 8 for formatting (99 characters per line, snake_case for functions/variables, PascalCase for classes, UPPER_SNAKE for constants).
- Type annotations - required everywhere, including `-> None`.
- Write Google-style docstrings for every public function and method.
- Do not add unused imports.
- `print()` - do not use for debugging. 
- Add logger.info at the main places, add logger.debug at the critical places with payload in logs with `%` formatting.

## Definition of done
Declare a task done only after docstrings are updated and all of these pass:
  - `uv run ruff format .`
  - `uv run ruff check --fix .`
  - `uv run pytest` passes, with a test added for every new code

## Constraints
- Never edit: lock files, `.env`.
- Never commit `.env` files.
- Ask before adding dependencies.
- Before starting work, create a git branch.
- If a mismatch causes you to think for too long, ask the user this question and suggest possible next steps.
- Do not look at the __pycache__ folder unless the user has explicitly asked you to do so.

## Git branch naming convention
Branches should be named according to the type of task.  
Git branch name format:  
`<type>-<short-description>`
Where:
- `type` - task type: `feature`, `fix`, `tests`, `refactor`
- `short-description` - a short description in the style of `kebab-case`
