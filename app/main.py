from fastapi import FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from typing import Optional

import psycopg
from psycopg import OperationalError
from psycopg.rows import dict_row

from icecream import ic
from tzlocal import get_localzone

app = FastAPI()



def create_connection(db_name, db_user, db_password, db_host, db_port):
    connection = None
    try:
        connection = psycopg.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            row_factory=dict_row,
        )
        print(f"Connection to PostgreSQL DB '{db_name}' successful")
    except OperationalError as e:
        print(f"The error '{e}' occurred")
    return connection


# def execute_read_query(connection, query):
#     cursor = connection.cursor()
#     result = None
#     try:
#         cursor.execute(query)
#         result = cursor.fetchall()
#         return result
#     except OperationalError as e:
#         print(f"The error '{e}' occurred")


def execute_query(connection, query, values=None):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query, values)
        if values:
            result = cursor.fetchall()
        connection.commit()
        print("Query executed successfully")
        return result
    except OperationalError as e:
        print(f"The error '{e}' occurred")



class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None



create_posts_table = """
CREATE TABLE IF NOT EXISTS posts
(
    id serial PRIMARY KEY
    , title varchar(255) NOT NULL
    , content text NOT NULL
    , published boolean NOT NULL DEFAULT True
    , created_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

# TODO: move credentials to dotenv
try:
    conn = create_connection('fastapi_course', 'ivan', '', '192.168.2.2', 5433)
    execute_query(conn, f"SET TIMEZONE to '{get_localzone().key}';")
    execute_query(conn, "DROP TABLE IF EXISTS posts;")
    execute_query(conn, create_posts_table)
    insert_posts = """
    INSERT INTO posts (title, content) VALUES (%(title)s, %(content)s) RETURNING id;
    """
    execute_query(conn, insert_posts, {"title": "title1", "content": "content1"})
    execute_query(conn, insert_posts, {"title": "title2", "content": "content2"})

except:
    print('DB error')




@app.get("/")
async def root():
    return {"message": "welcome"}


@app.get("/posts")
def get_posts():
    # TODO: remove dummy
    posts = execute_query(conn, "SELECT * FROM posts;", {"dummy": 0})
    ic(posts)
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    result = execute_query(conn, """INSERT INTO posts (title, content, published) VALUES
(%(title)s, %(content)s, %(published)s) RETURNING *;""", post.model_dump())
    ic(result)
    return {"data": result}


@app.get("/posts/latest")
def get_latest_post():
    return {"data": my_posts[-1]}


@app.get("/posts/{id}")
def get_post(id: int):
    post = execute_query(conn, "SELECT * FROM posts WHERE id = %(id)s;", {"id": id})
    ic(post)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found"
        )
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    post = execute_query(conn, "DELETE FROM posts WHERE id = %(id)s RETURNING *;", {"id": id})
    ic(post)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found"
        )
    return {"post_detail": post}


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    post_dict = post.model_dump()
    post_dict['id'] = id
    ic(post_dict)
    updated_post = execute_query(conn, """UPDATE posts SET title = %(title)s, content = %(content)s, published = %(published)s WHERE id = %(id)s RETURNING *;""", post_dict)
    ic(updated_post)
    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found"
        )
    return {"post_detail": updated_post}

    