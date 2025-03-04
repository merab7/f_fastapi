from fastapi import FastAPI
from pydantic import BaseModel
from random import randrange
from fastapi import status, Response, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic.networks import import_email_validator
import time

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True  # giving default value as True
    rating: int | None = None


while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
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


my_posts = [
    {"title": "title of post 1", "content": "content of post 1", "id": 1},
    {"title": "title of post 2", "content": "content of post 2", "id": 2},
]


@app.get("/")
async def root():
    return {"message": "welcome to my asi!"}


@app.get("/posts")
def get_posts():
    return {"data": my_posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):

    post_dict = post.model_dump()
    post_dict["id"] = randrange(0, 10000000)
    my_posts.append(post_dict)

    return {"data": post_dict}


@app.get("/posts/{id}")  # GET SPECIFIC POST WITH PATH PARAMETHER
def get_posts(id: int, response=Response):

    for post in my_posts:
        if post["id"] == id:
            return {"Retrieved Post": f"Here is your post{post}"}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"post with id{id} does not exists",
    )


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    for p in my_posts:
        if p["id"] == id:
            my_posts.remove(my_posts[id - 1])
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:

            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT,
                detail=f"Post with this {id} does not exists",
            )


@app.put("/posts/{id}")
def update_post(id: int, post: Post):

    print(post.model_dump())
    for p in my_posts:

        if p["id"] == id:

            post_dict = post.model_dump()
            my_posts[id - 1] = post_dict

            return (
                f"Post with id {id} was successfuly updated {post.model_dump()}"
            )

        return f"Post with this id {id} does not exists "
