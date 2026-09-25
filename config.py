import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ["API_TOKEN"]  # Raise KeyError if env variable not found
