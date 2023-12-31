from fastapi import FastAPI
from icecream import install as ic_install
from sqlalchemy.orm import Session

from . import models
from .database import engine
from .routers.auth import router as auth_router
from .routers.post import router as post_router
from .routers.user import router as user_router
from .routers.vote import router as vote_router
from .utils import hash_password

from fastapi.middleware.cors import CORSMiddleware


DEBUG = True
ic_install()

app = FastAPI()

# TODO: set up origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

routers = (post_router, user_router, auth_router, vote_router)
for router in routers:
    app.include_router(router)


if DEBUG:
    ic.enable()

    @app.on_event("startup")
    def startup_event():
        models.Base.metadata.drop_all(bind=engine)
        models.Base.metadata.create_all(bind=engine)
        with Session(engine) as session:
            users = [
                models.User(
                    email="user1@example.com", password=hash_password("password1")
                ),
                models.User(
                    email="user2@example.com", password=hash_password("password2")
                ),
            ]
            for u in users:
                session.add(u)
            session.commit()
            posts = [
                models.Post(
                    title="title 1",
                    content="content 1",
                    published=True,
                    author_id=users[0].id,
                ),
                models.Post(
                    title="title 2", content="content 2", author_id=users[1].id
                ),
                models.Post(
                    title="some title 3", content="content 3", author_id=users[1].id
                ),
            ]
            for p in posts:
                session.add(p)
            session.commit()
        del posts, users

else:
    ic.disable()


@app.get("/")
async def root():
    return {"message": "welcome :D"}
