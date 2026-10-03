# Telegram bot with text recognition from web image

The Telegram bot recognizes text from an image located on a website and sends that text to the Telegram user.

## Technology Stack
- aiogram 3
- Tesseract OCR (via the pytesseract package) for text recognition from image
- BeautifulSoup 4 to retrieve images from the website

## Project Structure
- `handlers/` - routers with handlers
- `keyboards/` - keyboards
- `utils/` - helpers, utils, logger
- `config.py` - environment variables and other settings
- `constants.py` - all constant variables for project
- `exceptions.py` - custom exception classes
- `main.py` - entry point for bot initialization

## Project Setup and Management
- Install tesseract: `apt install tesseract-ocr` and `apt install tesseract-ocr-rus`.
- Dependency management: `uv` and `pyproject.toml`
- Run the bot with `uv run main.py`.
- Create branch from `master` according to the project's branch naming convention with the command `git checkout master && git pull && git checkout -b <type>-<short-description>`.
- Stage changes for review. Don't commit or push without being asked.

## Testing
- Tests - only `pytest`, functions. No `unittest.TestCase`.
- Mocks - only Fake classes. No `MagicMock`, `patch`, `unittest.mock`.

## Code Style
- Write clear, short code without unnecessary complexity.
- If logic repeats - extract it into helper functions.
- Follow PEP 8 for formatting (99 characters per line, snake_case for functions/variables, PascalCase for classes, UPPER_SNAKE for constants).
- Use descriptive, unambiguous names for variables. Use descriptive names that start with a verb for functions.
- Type annotations - required everywhere, including `-> None`.
- Write Google-style docstrings for every public function and method.
- Do not add unused imports.
- All exception raises must be logged.
- Add logger.info at the main places, add logger.debug at the critical places with payload in logs with `%` formatting. Create a module-level logger with `__name__`.
- Apply KISS, DRY and SOLID principles to the code.

## Definition of done (quality gates)
Declare a task done only after docstrings are updated, README.md is updated, and all of these pass green:
  - `uv run ruff format .`
  - `uv run ruff check --fix .`
  - `uv run pytest` passes, with a test added for every new code

## Constraints
- Never edit: lock files, `.env`.
- Never commit `.env` files.
- Ask before adding dependencies.
- Before starting work, create a new git branch from `master` according to the project's branch naming convention.
- If a mismatch causes you to think for too long, ask the user this question and suggest possible next steps.
- Do not look at the `__pycache__` folder unless the user has explicitly asked you to do so.
- Do not look at git branches other than `master` unless the user has explicitly asked you to do so.

## Git branch naming convention
Branches should be named according to the type of task.

Git branch name format: `<type>-<short-description>`, where:
- `type` - task type: `feat`, `fix`, `test`, `refactor`, `docs`, `ci`, `chore`, `style`, according to the Conventional Commits
- `short-description` - a short description in the style of `kebab-case`

## Commit tag rules
Each commit must be marked with a tag in square brackets at the beginning of the message:
- `[agent]` - the diff from the agent was accepted without significant edits
- `[assisted]` - the agent did the bulk of the work, but the developer rewrote a significant portion (logic, structure, >20% of lines)
- `[manual]` - the code was written manually without the agent's assistance
