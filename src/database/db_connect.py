from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONNECTION = f"postgresql://{os.getenv('DB_USER')}:{os.environ.get('DB_PSSWD')}@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}"

engine = create_engine(DB_CONNECTION, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        print(f"Error during database operation: {str(e)}")
        raise
    finally:
        if db:
            db.close()
