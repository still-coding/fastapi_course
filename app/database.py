from .config import settings

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


###
# dont forget to execute
# ```sql
# ALTER DATABASE test_db SET TIMEZONE TO 'Asia/Yekaterinburg'
# ```
###


engine = create_engine(settings.db_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
