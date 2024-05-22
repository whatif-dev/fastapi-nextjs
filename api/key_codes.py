import os

os.chdir(os.path.dirname(os.path.dirname(__file__)))
load_dotenv('.env')

some_key = os.getenv("API_KEY")