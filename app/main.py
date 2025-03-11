import time

import psycopg2
from fastapi import FastAPI, HTTPException, Response, status
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True  # giving default value as True
    rating: int | None = None


while True:
    try:
        conn = psycopg2.connect(
            hostf="localhost",
            database="fastapi",
            user="postgres",
            cursor_factory=RealDictCursor,
        )
        cur = conn.cursor()
        print("connection was successful!")
        break
    except Exception as error:
        print("Connection failier")
        print(f"error: {error}")
        time.sleep(3)


@app.get("/")
async def root():
    return {"message": "welcome to my asi!"}


@app.get("/posts")
def get_posts():
    cur.execute(
        """
        SELECT * FROM posts
        """
    )
    posts = cur.fetchall()
    print(posts)
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    cur.execute(
        """
    INSERT INTO posts(title, content, published) VALUES(%s, %s, %s) RETURNING * """,
        (post.title, post.content, post.published),
    )
    new_post = cur.fetchone()
    conn.commit()

    return {"data": new_post}


@app.get("/posts/{id}")  # GET SPECIFIC POST WITH PATH PARAMETHER
def get_post(id: int):
    cur.execute(
        """
    SELECT * FROM posts where id=%s
    """,
        str(id),
    )
    post = cur.fetchone()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with this {id} does not exists",
        )
    return post


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cur.execute("""DELETE FROM posts WHERE id=%s RETURNING *""", (str(id)))
    post = cur.fetchone()
    conn.commit()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with this {id} does not exists",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cur.execute(
        """UPDATE posts SET title= %s, content=%s, published=%s WHERE id=%s RETURNING *""",
        (post.title, post.content, post.published, str(id)),
    )
    updated_post = cur.fetchone()
    conn.commit()

    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with this {id} does not exists",
        )

    return {"data": updated_post}
