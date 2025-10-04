from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import config

# Create the engine using the database URI from the config file
engine = create_engine(
    config.DATABASE_URI, 
    connect_args={"check_same_thread": False}
)

# Create a sessionmaker
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

def init_db():
    """
    Creates the database tables based on the models.
    This function is safe to run multiple times; it won't re-create existing tables.
    """
    Base.metadata.create_all(bind=engine)
