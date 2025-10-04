import os

# Define the base directory of the project
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Define the path for the database file inside the 'data' folder
DATABASE_PATH = os.path.join(BASE_DIR, 'data', 'sentiment_ai.db')

# Define the SQLAlchemy database URI
DATABASE_URI = f"sqlite:///{DATABASE_PATH}"
