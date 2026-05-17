from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException # fastapi uses starlette for exceptions under the hood

from schemas import PostCreate, PostResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

posts: list[dict] = [
    {
        "id": 1,
        "author": "Suraj Yadav",
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "author": "Master Corey",
        "title": "Python is Great for Web Development",
        "content": "Python is a great language for web development, and FastAPI makes it even better.",
        "date_posted": "April 21, 2025",
    }
]

#====================
#     USERS
#====================

@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request):
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "Home"} # context 
    )

# Return single post to user 
@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(request: Request, post_id: int): # if post_id is not int; then flask returns default JSON validation error: 422
    for post in posts: 
        if post.get("id") == post_id:
            title = post["title"]
            return templates.TemplateResponse(
                request,
                "post.html",
                {"post": post, "title": title}
            ) 
    
    # Return client error: JSON
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")



#====================
#     API
#====================

# Return all posts
@app.get("/api/posts", response_model=list[PostResponse])
def get_posts():
    return posts

# Return single post using path parameter
@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int): # if post_id is not int; then flask returns default JSON validation error: 422
    for post in posts: 
        if post.get("id") == post_id:
            return post 
    
    # Return client error: JSON
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


# Create a post 
@app.post("/api/posts", response_model=PostResponse)
def create_post(post: PostCreate):
    # new id 
    new_id = max(p['id'] for p in posts) + 1

    new_post = {
        'id': new_id,
        'author': post.author,
        'title': post.title,
        'content': post.content,
        'date_posted': 'April 23, 2025'
    }

    posts.append(new_post)
    return new_post 


#==========================================================
#     GENERAL CLIENT SIDE HTTP EXCEPTION EXPLICITLY 
# i.e. instead of returning JSON return error template 
#==========================================================

@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    
    message = exception.detail if exception.detail else "An error occurred. Please check your request and try again."
    

    # if /api call then, return JSON 
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message} # same as fastapi default HTTPException JSON body but can be anything 
        )
    
    # if USER call then, return error template 
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message
        },
        status_code=exception.status_code
    )


#==========================================================
#     VALIDATION ERROR 
# i.e. parsing errors  
#==========================================================

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):

    # if /api call
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()}
        )
    
    # USER call
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again."
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
    )