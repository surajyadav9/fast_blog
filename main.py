from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.exceptions import (
    HTTPException as StarletteHTTPException,  # fastapi uses starlette for exceptions under the hood
)

import models
from database import Base, engine, get_db
from schemas import (
    PostCreate,
    PostResponse,
    PostUpdate,
    UserCreate,
    UserResponse,
    UserUpdate,
)

# Create database tables from SQLAlchemy models if they do not already exist.
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

templates = Jinja2Templates(directory="templates")


# ====================
#     CLIENT
# ====================


# Return all posts to user
@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).order_by(models.Post.date_posted.desc()))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "Home"},  # context
    )


# Return single post to user using path parameter
@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(
    request: Request, post_id: int, db: Annotated[Session, Depends(get_db)]
):  # if post_id is not int; then flask returns default JSON validation error: 422
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return templates.TemplateResponse(
        request, "post.html", {"post": post, "title": post.title}
    )


# Get all posts by a user
@app.get("/users/{user_id}/posts", include_in_schema=False)
def user_posts(request: Request, user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"user": user, "posts": user.posts, "title": f"{user.username}'s Posts"},
    )


# ====================
#     API
# ====================


# =========================USERS API==========================


# Create a user
@app.post(
    "/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.username == user.username),
    )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    result = db.execute(
        select(models.User).where(models.User.email == user.email),
    )
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    new_user = models.User(
        username=user.username,
        email=user.email,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# Get user by id
@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.id == user_id),
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user  # Return model.User instance directly, FastAPI will handle serialization to UserResponse


# Update user by id
@app.put("/api/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int, user: UserUpdate, db: Annotated[Session, Depends(get_db)]
):
    result = db.execute(
        select(models.User).where(models.User.id == user_id),
    )
    existing_user = result.scalars().first()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.username is not None and user.username != existing_user.username:
        # Check if the new username already exists
        result = db.execute(
            select(models.User).where(models.User.username == user.username),
        )
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

    if user.email is not None and user.email != existing_user.email:
        # Check if the new email already exists
        result = db.execute(
            select(models.User).where(models.User.email == user.email),
        )
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    # Update fields only if they are provided (not None)
    if user.username is not None:
        existing_user.username = user.username
    if user.email is not None:
        existing_user.email = user.email
    if user.image_file is not None:
        existing_user.image_file = user.image_file

    db.commit()
    db.refresh(existing_user)
    return existing_user  # Return model.User instance directly, FastAPI will handle serialization to UserResponse


# Delete user by id
@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.id == user_id),
    )
    existing_user = result.scalars().first()
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    db.delete(existing_user)
    db.commit()


# =========================POSTS API==========================
# Return all posts
@app.get("/api/posts", response_model=list[PostResponse])
def get_posts(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).order_by(models.Post.date_posted.desc()))
    posts = result.scalars().all()
    return posts


# Return single post using path parameter
@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int, db: Annotated[Session, Depends(get_db)]
):  # if post_id is not int; then flask returns default JSON validation error: 422
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    return post


# Get all posts by a user
@app.get("/api/users/{user_id}/posts", response_model=list[PostResponse])
def get_user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.id == user_id),
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user.posts


# Create a post
@app.post("/api/posts", response_model=PostResponse)
def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.id == post.user_id),
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )
    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


# Update a post full
@app.put("/api/posts/{post_id}", response_model=PostResponse)
def update_post_full(
    post_id: int, post: PostCreate, db: Annotated[Session, Depends(get_db)]
):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    existing_post = result.scalars().first()
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # check if user_id is valid
    result = db.execute(
        select(models.User).where(models.User.id == post.user_id),
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )

    existing_post.title = post.title
    existing_post.content = post.content
    existing_post.user_id = post.user_id

    db.commit()
    db.refresh(existing_post)
    return existing_post


# Update a post partial
@app.patch("/api/posts/{post_id}", response_model=PostResponse)
def update_post_partial(
    post_id: int, post: PostUpdate, db: Annotated[Session, Depends(get_db)]
):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    existing_post = result.scalars().first()
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    update_data = post.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(existing_post, key, value)

    db.commit()
    db.refresh(existing_post)
    return existing_post


# ==========================================================
#     GENERAL CLIENT SIDE HTTP EXCEPTION EXPLICITLY
# i.e. instead of returning JSON return error template
# ==========================================================


@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):

    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    # if /api call then, return JSON
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={
                "detail": message
            },  # same as fastapi default HTTPException JSON body but can be anything
        )

    # if USER call then, return error template
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


# ==========================================================
#     VALIDATION ERROR
# i.e. parsing errors
# ==========================================================


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):

    # if /api call
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()},
        )

    # USER call
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )
