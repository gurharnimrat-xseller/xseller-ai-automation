from sqlmodel import create_engine
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./xseller.db')
engine = create_engine(DATABASE_URL, echo=True)
