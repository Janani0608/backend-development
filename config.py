import os
import pytz
from dotenv import load_dotenv

#Load the environment variables
load_dotenv()

#timezone for Germany
GERMANY_TZ = pytz.timezone("Europe/Berlin")

#Database url
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

