from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


###
# dont forget to execute
# ```sql
# ALTER DATABASE test_db SET TIMEZONE TO 'Asia/Yekaterinburg'
# ```
###


# TODO: move credentials to dotenv
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg://ivan:@192.168.2.2:5433/fastapi_course"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
