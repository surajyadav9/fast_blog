# Summary of Python FastAPI Tutorial (Part 1)

This tutorial introduces FastAPI, a fast and modern Python web framework, and sets up a project that will eventually include a JSON REST API and an HTML frontend [1, 2]. 

## Important Setup Commands

The tutorial uses UV, a fast Python package manager, though traditional `pip` can also be used [3].

### 1. Creating the Project Folder
To initialize a new project and navigate into it using UV, run the following commands [3]:
`uv init fastapi_blog`
`cd fastapi_blog`

If you are not using UV, you can simply create a new directory and navigate into it manually [3].

### 2. Installing FastAPI
It is recommended to install FastAPI with the "standard" extras, which bundles the FastAPI framework, the Uvicorn ASGI server, and the FastAPI CLI [4]. 
- **Using UV:** `uv add "fastapi[standard]"` [4]
- **Using pip:** `pip install "fastapi[standard]"` [4]

### 3. Running the Development Environment
To start the server in development mode, which automatically reloads whenever you make changes to your code, use the following commands [5, 6]:
- **Using UV:** `uv run fastapi dev main.py` [5]
- **Using pip:** `fastapi dev main.py` [5]

For production environments, you should use `fastapi run` instead, as it is optimized for performance rather than debugging [6].

## Key Concepts Covered

* **Basic Routing:** You can define application routes using decorators like `@app.get("/")`, and FastAPI will automatically convert the returned Python dictionaries into JSON data [5, 7, 8].
* **Automatic Documentation:** FastAPI automatically generates interactive API documentation via a Swagger UI at the `/docs` route and a more modern interface at `/redoc` [9, 10]. This lets you execute test requests directly in your browser or copy `curl` commands for terminal testing [9, 10].
* **HTML Responses:** You can return HTML strings instead of JSON by importing `HTMLResponse` from `fastapi.responses` and adding `response_class=HTMLResponse` to your route decorator [11].
* **Stacking Decorators:** You can map multiple URL paths to the exact same function by stacking multiple decorators (such as `@app.get("/")` and `@app.get("/post")`) on top of the function [12, 13].
* **Hiding Routes from Documentation:** To keep your API documentation clean, you can hide HTML routes meant for human browsing by adding `include_in_schema=False` to the route's decorator [13, 14].


<br><br>
# Comprehensive Guide to FastAPI (Part 2): HTML Frontend & Jinja2 Templates

This guide explains how to use Jinja2 templates in FastAPI to serve complete HTML pages to users, while keeping your JSON API endpoints intact for programmatic access,. If you installed FastAPI using the "standard" extras (`fastapi[standard]`), Jinja2 is already included automatically.

## 1. Setting up Jinja2 Templates

To begin, you need to create a directory named `templates` inside your project folder. Next, update your `main.py` file to configure FastAPI to find and use these templates. You must import `Request` (which is required by Jinja2) and `Jinja2Templates`.

```python
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Configure the templates directory
templates = Jinja2Templates(directory="templates")
```
This creates a template object that tells FastAPI to look inside your `templates` directory for your HTML files.

## 2. Rendering a Template Response and Passing Data

To serve an HTML template instead of raw strings or JSON data, your route function must be updated. First, the function must accept a `request` parameter of type `Request`. You then return a `TemplateResponse` specifying the request, the name of the template, and a context dictionary containing the dynamic data you want to display on the HTML page,.

```python
# Dummy data for demonstration
posts = [
    {"title": "First Post", "content": "This is the first post"},
    {"title": "Second Post", "content": "This is the second post"}
]

@app.get("/", include_in_schema=False, name="home")
@app.get("/post", include_in_schema=False, name="post")
def home(request: Request):
    # Pass 'request', the template name, and context variables
    return templates.TemplateResponse(
        request=request, 
        name="home.html", 
        context={"posts": posts, "title": "Home"}
    )
```
By keeping `include_in_schema=False` on the decorator, these HTML-rendering routes remain hidden from your automatic API documentation (like `/docs`), ensuring a clean separation between your human-facing web pages and your programmatic JSON API endpoints,.

## 3. Jinja2 Templating Syntax

Inside your HTML templates, you can use Jinja2 syntax to dynamically render the data passed via the context dictionary.

*   **Variables:** Use double curly braces `{{ }}` to display variables. Jinja2 allows you to use dot notation (e.g., `post.title`) to access dictionary keys cleanly.
*   **For Loops:** Use `{% for item in list %}` and `{% endfor %}` to iterate over lists of data, like displaying multiple blog posts.
*   **Conditionals:** Use `{% if %}`, `{% else %}`, and `{% endif %}` to conditionally render blocks, such as setting a default page title if none was passed in,.

```html
<!-- Example of a conditional block -->
<title>
    {% if title %}
        FastAPI Blog - {{ title }}
    {% else %}
        FastAPI Blog
    {% endif %}
</title>

<!-- Example of a loop and variables -->
{% for post in posts %}
    <h2>{{ post.title }}</h2>
    <p>{{ post.content }}</p>
{% endfor %}
```

## 4. Template Inheritance

Template inheritance prevents you from duplicating boilerplate HTML structure (like headers, navigation bars, CSS links, and footers) across every page. You can create a parent template, typically called `layout.html`, which defines the common structure and specifies placeholder blocks.

**Parent Template (`templates/layout.html`):**
```html
<!DOCTYPE html>
<html>
<head>
    <title>FastAPI Blog</title>
</head>
<body>
    <nav>
        <!-- Navigation bar content here -->
    </nav>
    
    <main>
        <!-- Define a block that child templates will override -->
        {% block content %}{% endblock content %}
    </main>
</body>
</html>
```

Child templates then extend this layout and only provide the specific content needed for their respective pages.

**Child Template (`templates/home.html`):**
```html
<!-- Extend the parent layout -->
{% extends "layout.html" %}

<!-- Fill in the defined block -->
{% block content %}
    {% for post in posts %}
        <article>
            <h2>{{ post.title }}</h2>
            <p>{{ post.content }}</p>
        </article>
    {% endfor %}
{% endblock content %}
```

## 5. Serving Static Files (CSS, JS, Images)

To add CSS styling (like Bootstrap), JavaScript, icons, and images, you must configure FastAPI to serve static files,. Create a directory named `static` in your project root. Then, mount this directory to your application in `main.py` using the `StaticFiles` module,.

```python
from fastapi.staticfiles import StaticFiles

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")
```
The URL path `"/static"` makes any file placed in the `static` directory accessible in the browser under that path (e.g., `"/static/css/main.css"`).

## 6. Using `url_for` for Dynamic Routing

Instead of hardcoding URLs for navigation links or static file paths, you should use the `url_for` function directly inside your templates,. This best practice ensures that if your route paths or static mount paths ever change in the future, the templates will automatically update.

**For Static Files:** Use `url_for`, pass the mount name (`'static'`), and specify the relative path to the file,.
```html
<!-- dynamically linking a CSS stylesheet -->
<link rel="stylesheet" href="{{ url_for('static', path='css/main.css') }}">

<!-- dynamically linking an image -->
<img src="{{ url_for('static', path='profile_pics/default.jpg') }}">
```

**For Route Navigation:** Pass the name of the Python route function to `url_for`.
```html
<a href="{{ url_for('home') }}">Home Page</a>
```

*Important Note on Stacked Decorators:* If you map multiple decorators to the exact same function (e.g., `@app.get("/")` and `@app.get("/post")` on the `home` function), `url_for` might default to the wrong route name. To fix this, provide an explicit `name` argument to each decorator (e.g., `@app.get("/", name="home")` and `@app.get("/post", name="post")`). This guarantees that `url_for` routes users to the precise URL intended.


<br><br>
# Comprehensive Guide to FastAPI (Part 3): Path Parameters, Validation, and Error Handling

This guide explains how to use path parameters in FastAPI to access specific resources, how to leverage automatic data validation, and how to properly handle HTTP exceptions so that your JSON API and HTML frontend display appropriate error messages.

## 1. Understanding Path Parameters

Path parameters allow you to capture variables directly from the URL path. For example, instead of returning a list of all posts, you can fetch a single post by putting its ID in the URL, such as `/api/post/1`.

To define a path parameter, wrap the variable name in curly braces `{}` within the route decorator, and then pass it as an argument to the route function.

```python
# Assuming 'posts' is a list of dictionary data

@app.get("/api/post/{post_id}")
def get_post(post_id: int):
    # Loop through posts to find the matching ID
    for post in posts:
        if post.get("id") == post_id:
            return post
```

## 2. Automatic Type Validation

Notice the `post_id: int` type hint in the function signature. This type hint is incredibly important because FastAPI uses it to automatically validate the input. 

If a user navigates to a valid integer path like `/api/post/1`, it processes successfully. However, if they try to pass a string like `/api/post/hello`, FastAPI will automatically intercept the request and return a 422 (Unprocessable Entity) validation error detailing exactly what went wrong, without you having to write any validation logic. This automatic validation is also instantly reflected in the interactive API documentation.

## 3. Raising HTTP Exceptions (404 Not Found)

If a user searches for a post that doesn't exist (e.g., `/api/post/99`), you shouldn't just return a normal dictionary with an error message. Returning a dictionary results in a `200 OK` status code, which misleadingly tells the client application that the request was a success. Instead, you should return a `404 Not Found` status code.

To do this, import `HTTPException` and `status` from FastAPI, and raise an exception if the post isn't found.

```python
from fastapi import FastAPI, HTTPException, status

@app.get("/api/post/{post_id}")
def get_post(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    
    # If the loop finishes without returning, the post wasn't found
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="Post not found"
    )
```

## 4. Creating a Single Post Page (HTML Route)

Just like the API, you can create a specific page route that returns an HTML template for a single post. To do this, you use a similar path parameter but return a `TemplateResponse`.

```python
from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

@app.get("/post/{post_id}", include_in_schema=False, name="post_page")
def post_page(request: Request, post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            # Return the post template with dynamic data
            return templates.TemplateResponse(
                request=request, 
                name="post.html", 
                context={"post": post, "title": post.get("title")[:50]}
            )
            
    # Raise a 404 if the post doesn't exist
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="Post not found"
    )
```

## 5. Dynamic Links with Path Parameters in Templates

To make the posts on your homepage clickable, you can update your Jinja2 templates using `url_for`. When using `url_for` to link to a route that requires path parameters, you can pass those parameters directly as keyword arguments.

Inside your `home.html` template:

```html
<!-- Generating a link to the 'post_page' route, passing the dynamic post.id -->
<a href="{{ url_for('post_page', post_id=post.id) }}">
    {{ post.title }}
</a>
```

## 6. Advanced Exception Handling (JSON vs HTML Errors)

If you raise an `HTTPException` or trigger a validation error on an HTML page route, FastAPI defaults to returning a raw JSON error in the browser. To provide a better user experience, you can create custom exception handlers that return JSON for `/api` routes and beautifully styled HTML error pages for standard web routes.

To accomplish this, you must catch `StarletteHTTPException` (which handles all 404s, even for non-existent routes) and `RequestValidationError` (which handles type hint validation errors).

```python
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# 1. Handle standard HTTP Exceptions (like 404s)
@app.exception_handler(StarletteHTTPException)
def http_exception_handler(request: Request, exc: StarletteHTTPException):
    message = exc.detail if exc.detail else "An error occurred."
    
    # If the URL starts with /api, return JSON
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exc.status_code, 
            content={"detail": message}
        )
    
    # Otherwise, return an HTML template for frontend users
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={"status_code": exc.status_code, "message": message, "title": exc.status_code},
        status_code=exc.status_code
    )

# 2. Handle Validation Errors (like passing a string instead of an int)
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Validation errors are always 422 Unprocessable Entity
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status_code, 
            content={"detail": exc.errors()}
        )
        
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={"status_code": status_code, "message": "The request was invalid.", "title": status_code},
        status_code=status_code
    )
```
By doing this, your API endpoints under `/api` strictly return machine-readable JSON errors, while human users navigating your web pages will see a friendly `error.html` page when something goes wrong.


## Note: Why Use Starlette for 404 Exception Handling in FastAPI?

**FastAPI is built directly on top of Starlette**, which means Starlette handles much of the underlying routing and request processing. 

Here is why you need to catch Starlette exceptions to handle 404 errors properly:

* **Starlette Triggers Default 404s:** When a user navigates to a completely non-existent route on your website (for example, a random URL like `/does-not-exist`), it is actually Starlette that automatically raises the `404 Not Found` error, not FastAPI.
* **The Limitation of FastAPI's Exceptions:** If you were to only catch FastAPI's `HTTPException` in your custom exception handler, you would successfully catch the manual errors you specifically raised in your code (such as searching for a post ID that doesn't exist). However, you would completely miss the default "page not found" errors generated by Starlette for invalid URLs.
* **The Complete Solution:** By importing and catching the **`StarletteHTTPException`**, you ensure that your custom exception handler covers **both cases**: the manual HTTP exceptions you write in your FastAPI routes, as well as the overarching "page not found" errors triggered by Starlette.


<br><br>
# Comprehensive Guide to FastAPI (Part 4): Pydantic Schemas - Request and Response Validation

This guide explains how to use Pydantic schemas in FastAPI to validate your API requests and responses. Pydantic is a data validation library that comes built into FastAPI, utilizing Python type hints to enforce validation at runtime and generate detailed error messages. 

## 1. Setting up Pydantic Schemas (`schemas.py`)

To keep a clean separation of concerns, it is best practice to define your schemas in a separate file from your main application. Schemas define what data the API accepts from clients and what data it returns, which is different from database models that define how data is stored.

Create a `schemas.py` file and define your Pydantic models by inheriting from `BaseModel`. You can use `Field` to add validation constraints (like minimum and maximum length) and `ConfigDict` to configure model behavior.

```python
from pydantic import BaseModel, ConfigDict, Field

# 1. Base Schema: Contains fields shared across both creating and returning posts
class PostBase(BaseModel):
    # Field constraints make these required, since there are no default values
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=50)

# 2. Create Schema: Defines what we expect from the client when creating a post
class PostCreate(PostBase):
    pass # Currently identical to PostBase, but provides flexibility for future changes

# 3. Response Schema: Defines what we return to the client
class PostResponse(PostBase):
    # Allows Pydantic to read data using dot notation (objects) instead of just dictionaries, essential for future database integration
    model_config = ConfigDict(from_attributes=True) 
    
    # Server-generated fields that the client does not provide when creating a post
    id: int
    date_posted: str 
```
By not assigning default values to the fields in `PostBase`, Pydantic automatically makes them required fields. The `from_attributes=True` configuration allows Pydantic to read data attributes via dot notation (e.g., `post.title`), which will be necessary when transitioning from in-memory dictionaries to a real database later.

## 2. Updating GET Endpoints with Response Models

Back in your `main.py` file, you can now update your existing route decorators to include a `response_model`. This acts as a safeguard that filters out any unintended extra data and ensures that the returned data exactly matches the schema. 

```python
from fastapi import FastAPI
from schemas import PostCreate, PostResponse

app = FastAPI()

# Specify that this endpoint returns a list of PostResponse objects
@app.get("/api/post", response_model=list[PostResponse])
def get_posts():
    return posts

# Specify that this endpoint returns a single PostResponse object
@app.get("/api/post/{post_id}", response_model=PostResponse)
def get_post(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    # ... handle 404 error
```

## 3. Creating a POST Endpoint for New Posts

To create new resources, you use the `@app.post` decorator. When you pass your `PostCreate` schema as an argument to the function, FastAPI automatically parses the incoming JSON body, validates it against your constraints, and handles errors.

```python
from fastapi import status

# Use HTTP 201 Created status code as a RESTful best practice for new resources
@app.post("/api/post", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate):
    # Manually generate an ID (temporary logic until a database is used)
    new_id = len(posts) + 1 if posts else 1
    
    # Create a dictionary using the automatically validated 'post' data
    new_post = {
        "id": new_id,
        "title": post.title,
        "content": post.content,
        "author": post.author,
        "date_posted": "2026-05-10" # Hard-coded date for now
    }
    
    # Append the new post to the in-memory list
    posts.append(new_post)
    return new_post
```

## 4. Automatic Validation and Documentation

One of the largest benefits of Pydantic is how it enhances both safety and documentation automatically:
*   **Automatic 422 Errors:** If a client tries to create a post missing a required field (like `author`) or violates a length constraint (like submitting a blank string for `title`), FastAPI immediately intercepts the request and returns a `422 Unprocessable Entity` error detailing exactly which field failed and why.
*   **Interactive Swagger Docs:** The `/docs` API documentation automatically updates to show developers exactly what JSON structure is expected in the request body, exactly what the response will look like, and all the minimum/maximum length constraints defined in the Pydantic models.

## 5. The Need for a Database

While the API and templates now work cleanly together and share the same data, the application currently stores posts in a Python list in memory. This means any new posts created via the POST endpoint will disappear as soon as the development server restarts. Because of this, transitioning the app to use a real database with persistent storage (like SQLAlchemy) is the necessary next step.



<br><br>
# Comprehensive Guide to FastAPI (Part 5): Adding a SQLite Database with SQLAlchemy

Up until now, the application stored data in a standard Python list, which resets every time the server restarts. This tutorial transitions the app to a real database so data persists.

## 1. The Architecture: Why Three Separate Layers?

When adding a database, the application is divided into three distinct layers:
1.  **Database Models (SQLAlchemy):** Define how data is stored in the actual database tables.
2.  **Pydantic Schemas:** Define the structure of the JSON data your API receives and returns.
3.  **API Routes (FastAPI):** The endpoints that handle the web requests.

**Why not use one single model for both?** 
While libraries like SQLModel combine these layers, keeping them separate is the industry standard. It gives you precise control over what a user is allowed to send or see. For example, a user provides a password when creating an account (Pydantic Schema), but you don't return that password in the API response, even though it lives in the database (SQLAlchemy Model). The flow works like this: ```Pydantic validates incoming requests -> SQLAlchemy stores/retrieves data -> Pydantic formats the final outgoing response```.

## 2. Database Configuration (`database.py`)

To interact with the database, the tutorial uses **SQLAlchemy** (a popular Python Object-Relational Mapper or ORM) and **SQLite** (a lightweight database built directly into Python). 

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# 1. The Connection String
SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"

# 2. The Engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. The Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. The Base Class
class Base(DeclarativeBase):
    pass

# 5. Dependency Injection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Tricky Logic Explained:**
*   `check_same_thread=False`: SQLite normally only allows one thread to communicate with it at a time. FastAPI processes requests using multiple threads concurrently, so we must explicitly disable this SQLite restriction to prevent errors.
*   `get_db()` and `yield`: This is a dependency function. Using `yield` turns it into a context manager. It hands a database session to a route, and the `finally` block ensures the session is safely closed and cleaned up after the route finishes responding, even if an error crashes the app.

## 3. Creating SQLAlchemy Models (`models.py`)

Models represent your database tables. We are adding a `User` model and updating the `Post` model to establish a relationship.

```python
from __future__ import annotations
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    
    # Establish a One-to-Many relationship with Post
    posts: Mapped[list[Post]] = relationship(back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    
    # Foreign Key linking this post to a specific user
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    
    # Establish the Many-to-One relationship back to the User
    author: Mapped[User] = relationship(back_populates="posts")
```

**Why Relationships?** By defining `ForeignKey` and `relationship`, SQLAlchemy will automatically handle SQL "JOIN" operations under the hood. If you fetch a post, you can instantly access the author's information by calling `post.author.username`. Setting `index=True` on the `user_id` acts like a textbook index, drastically speeding up queries when you search for all posts by a specific user.

## 4. Updating Pydantic Schemas (`schemas.py`)

Because our database now returns complex SQLAlchemy objects instead of simple Python dictionaries, our schemas need an update.

```python
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    
    # Critical: Tells Pydantic to read from ORM objects, not just dictionaries
    model_config = ConfigDict(from_attributes=True)

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    
    # Nesting the UserResponse schema inside the Post schema!
    author: UserResponse 
    
    model_config = ConfigDict(from_attributes=True)
```

**The Magic of Nested Schemas:** Notice how `PostResponse` has an `author` field set to the `UserResponse` schema. When you fetch a post from the database, FastAPI automatically grabs the related user object via SQLAlchemy, validates it against the `UserResponse` schema, and embeds it as nested JSON inside your post response.

## 5. Using the Database in Routes (`main.py`)

To use the database inside an API endpoint, we inject the `get_db` dependency we created earlier.

```python
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
import models, schemas
from database import engine, get_db

app = FastAPI()

# Tell SQLAlchemy to automatically create the database tables file 
models.Base.metadata.create_all(bind=engine)

@app.post("/api/users", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Create the SQLAlchemy model instance
    new_user = models.User(username=user.username, email=user.email)
    
    # 2. Stage the new user to be added
    db.add(new_user)
    
    # 3. Commit the transaction to the database
    db.commit()
    
    # 4. Refresh the object to grab the auto-generated ID from the database
    db.refresh(new_user)
    
    return new_user
```
The `db: Session = Depends(get_db)` parameter automatically provides a clean database session for every single request.

## 6. Updating Templates

Since `date_posted` is now a real `datetime` object instead of a basic string, we need to format it in the HTML templates so it is human-readable. Furthermore, we can use dot-notation to access the related user's information.

```html
<!-- Accessing the nested author relationship via dot notation -->
<a href="{{ url_for('user_post', user_id=post.author.id) }}">
    {{ post.author.username }}
</a>

<!-- Formatting the datetime object using Python's strftime -->
<small>{{ post.date_posted.strftime('%B %d, %Y') }}</small>
```
The API continues to return the raw, standardized ISO format data (ideal for computers), while the template formats it nicely using `strftime` (ideal for human reading).
```

Does this setup make sense, or would you like to review how to use this database to update or delete posts (the PUT and DELETE operations) next?