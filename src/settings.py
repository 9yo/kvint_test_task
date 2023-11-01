import os

from dotenv import load_dotenv

# Specify the path to your .env file if it's not in the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, '../deployment/.env')
load_dotenv(dotenv_path)

# Now you can access the variables using os.getenv()
RABBIT_HOST = os.getenv('RABBIT_HOST')
REPORT_QUEUE = os.getenv('REPORT_QUEUE')
ONE_PHONE_RECORDS_COUNT = int(os.getenv('ONE_PHONE_RECORDS_COUNT'))
PHONE_DATA_STORAGE_PATH = os.getenv('PHONE_DATA_STORAGE_PATH')
