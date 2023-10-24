from os import getenv

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

###
# dont forget to execute
# ```sql
# ALTER DATABASE test_db SET TIMEZONE TO 'Asia/Yekaterinburg'
# ```
###


engine = create_engine(getenv("DB_URL"))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
