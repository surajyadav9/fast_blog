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