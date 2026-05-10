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
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
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
async def validation_exception_handler(request: Request, exc: RequestValidationError):
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
```