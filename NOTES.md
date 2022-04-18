# Notes

## Starting State of Development Machine
My development machine was set-up as follows when I began the exercise (April 16, 2022):

* WSL2 running Ubuntu 20.04
* Python versions managed by [pyenv](https://github.com/pyenv/pyenv):
    * 3.8 as a system installation
    * 3.10.0 as my daily working version.

## Poetry
The series uses [Poetry](https://python-poetry.org/) as its package manager. I was new to Poetry and encountered a few gotchas which required several hours of troubleshooting to resolve. I list a short description of the problem and eventual solution below. (Note: I installed Poetry v.1.1.13).

### Problems

1. **Poetry was locked to specific Python version**

    I made the mistake of first installing via pip. This had the effect of locking Poetry to the specific version of Python that pyenv had active at the time. Don't do this.

2. **Poetry virtual environment did not retain installation state between reactivations**

    Packages installed into the virtual environment were not retained once I exited and re-entered. Poetry would return errors like  _ModuleNotFoundError: No module named 'alembic`_ when I tried to run 3rd party packages that I previously installed. 

3. **Jinja2 update broke Starlette**

    The tutorial `pyproject.toml` called for `Jinja2 = "^3.0.1"`. As of mid-April 2022, however, this caused the following code to generate an error due to a [recent Jinja2 change](https://jinja.palletsprojects.com/en/3.1.x/changes/).

    ```python
    from fastapi.templating import Jinja2Templates

    BASE_PATH = Path(__file__).resolve().parent
    TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))
    ```
    Resulting error:
    ```bash
    File "/home/HOSTNAME/Education/PythonExperiments/FastAPI/./app/main.py", line 16, in <module>
        TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))
        File "/home/HOSTNAME/.cache/pypoetry/virtualenvs/app-D5imXWgp-py3.10/lib/python3.10/site-packages/starlette/templating.py", line 53, in __init__
        self.env = self.get_env(directory)
        File "/home/HOSTNAME/.cache/pypoetry/virtualenvs/app-D5imXWgp-py3.10/lib/python3.10/site-packages/starlette/templating.py", line 56, in get_env
        @jinja2.contextfunction
    AttributeError: module 'jinja2' has no attribute 'contextfunction'
    ```

    Troubleshooting Reference:

    * https://githubhot.com/repo/aio-libs/aiohttp-jinja2/issues/561


### Solutions

1. **Install system agnostic Poetry**

    Easily solved by simply [reading the documentation](https://python-poetry.org/docs/master/#installing-with-the-official-installer). `curl -sSL https://install.python-poetry.org | python3 -`

    There was still the risk of the wrong Python version being used if I changed my pyenv global variable. This was fixed by running `pyenv local 3.9.7`, which created a `.python-version` file in the root of the project to let Pyenv know that it should always use this version regardless of what version the global Python version was set to. 

    This solution seems very clean but also a little dangerous because I suspect I'll forget I used this technique in a few months (hence documented here).


2. **Fix virtual environment statefulness** 

    This problem was due to a missing system package (`python3.*-venv). My usage of Python3.10 made things more difficult due to:
        
    1. `python3.9-venv` being the most modern package available on the standard Ubuntu repositories.

    2. I did not want to add the [deadsnakes package repository}(https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa). This was for two reasons:

        1. I use 3rd party package repositories infrequently enough that I ALWAYS forget all the commands needed to manage them (and eventually start getting weird errors during `apt update` when things change).

        2. Given the growing prevalence of toolchain attacks, I'm trying to get into the habit of minimizing the addition of non-standard sources. **NOTE:** This is not to say that deadsnakes or its maintainer are bad, I just didn't want to the `python3.10-venv` badly enough to introduce these components to my system.

    Troubleshooting References:
    
    * https://github.com/python-poetry/poetry/issues/651
    * https://stackoverflow.com/questions/61351659/the-virtual-environment-found-seems-to-be-broken-python-poetry


3. **Fix Jinja2 Version**

    Set the `pyproject.tom` Jinja2 entry to: `Jinja2 = "3.0.*"`


### Command Cheatsheet
The following commands are useful to know:
```bash
> poetry init
> source $(poetry env info --path)/bin/activate    # Use over `poetry shell` apparently it's buggy.
> poetry env use $(pyenv which python)
> poetry install
> poetry update
> poetry run ./prescript.sh
> poetry deactivate
> poetry exit
```
        

## Alembic
Project uses Alembic to manage database updates. Although I'm of the opinion that using an ORM can complicate 
a project and it makes more sense to use standard SQL, I accepted ORM usage here because it was fundamental to the project's
database interaction and made migrations relatively easy due to the Alembic package.

There were a few gotchas and decisions that needed to be made here:

1. **Installing SQLite3**

    I originally tried downloading from the [offical site](https://www.sqlite.org/download.html) but it didn't want to work. Downloading from the official Ubuntu repo solved the problem: `sudo apt install sqlite3`.

2. **Duplicate models were acceptable in order to avoid additional 3rd party lock-in**

    SQLAlchemy required Python classes to be created to serve as database table models. A second set of nearly-identical Pydantic
    models also have to be generated for type-checking and API documentation. 
    
    At first I thought this was stupid and searched for a unified approach to minimize duplication. I found options like [ormar](https://collerek.github.io/ormar/) and [SQLModel](https://sqlmodel.tiangolo.com/) (another project by Tiangolo). While these looked appealing, I found several articles criticizing Tiangolo's slowness to provide updates to his stable of products (which seemed both unfair when one looked at the facts, but also seemed to have a kernel of truth). Given that I was already building a critical dependency on FastAPI, I didn't not want to introduce another critical dependency upon a potentially unstable SQLModel, nor did I want to have to figure out to introduce `ormar` to Christopher Samiullah's code. 

    I decided some repetition was acceptable to avoid dependency creep and potential integration issues. I may revist this decision later if I ever get to a point where I'm generating so many models that the duplication becomes a nightmare.

3. **Configuration**

    Various configuration was required to get this all working nicely:

    1. _alembic.ini_

        1. Set `file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s` to have date-traceability on migration steps.

        2. Set `sqlalchemy.url = sqlite:///example.db`

    2. _<ALEMBIC_FOLDER>/env.py_

        1. Replace `target_metadata = None` with:

        ```python
        # NOTE! The import statement here pulls a convenience file which aggregates the original Base and descendent children
        # (example of file in the indented comments). This is fine at small scale but likely should be replaced with a code
        # snipper which dynamically  detects class files via crawl (or maybe use an __all__ variable in the package __init__.py).
        # Example: https://docs.python.org/3/tutorial/modules.html#importing-from-a-package. 
        # I did not bother to implement since I wanted to focus on the example first, rather than prematurely optimize.
        from app.db import base         
            # from app.db.base_class import Base
            # from app.models.user import User
            # from app.models.recipe import Recipe
        target_metadata = base.Base.metadata   # VSCode Pylance will complain about `metadata` if you have type-checking activte but it works.
        ```

    3. **Creating revisions**

        Rather than git pull each new tutorial chapter, I would update the files based on the new content. This meant I had an existing database 
        and revisions to work with rather than a fresh environment to run a clean (and complete migration). 

        If you update SQLAlchemy models and want to create a new auto-generated migration, it appears that your database must exist and be fully migrated before you can run the `alembic revision --autogenerate -m "MESSAGE"` command. I generally followed this pattern:
        Delete DB -> `alembic upgrade head` -> `alembic revision --autogenerate -m "New revision"` -> `alembic upgrade head`.

    4. **Adding `nullable=False` column to pre-existing table**

        [Part 10](https://github.com/ChristopherGS/ultimate-fastapi-tutorial/tree/main/part-10-jwt-auth) introduces a new `hashed_password` column to the pre-existing User table in SQLite. Using the configuration supplied by the tutorial `hashed_password = Column(String, nullable=False)` results in the following error: _sqlite3.OperationalError: Cannot add a NOT NULL column with default value NULL_.

        Some internet sleuthing reveals this seems to Sqlite3-specific problem. Alot of posts got very deep into database weeds / custom code solutions and my eyes immediately glazed over. Found this solution in a thread related to [Miguel Grinberg's Flask-Migrate](https://github.com/miguelgrinberg/Flask-Migrate/issues/81) (ie. Flask implementation of Alembic). Suggested allowing the column to be nullable but set the default to an empty string: `hashed_password = Column(String, nullable=True, default="")`.

        This seems like a hack to me and likely requires a better answer long-term (particularly if one were going to use SQLite3 in a real production environment). I used the hack since it was good enough for my initial needs.


### Reference Video
I found it helpful to watch this [FastAPI #0027 Migrations using SQLAlchemy Alembic Youtube video](https://www.youtube.com/watch?v=gISf9AWAS7k) early into my work with Alembic to get a feel for how it works as a whole. The autogenerate feature
worked a tad bit differently, however, due to the Christopher Samiullah approach of using a [`as_declarative` decorator](https://docs.sqlalchemy.org/en/14/orm/mapping_api.html#sqlalchemy.orm.as_declarative) rather than the more traditional:
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SomeClass(Base):
    ...

...

engine = create_engine('sqlite://')
Base.metadata.create_all(bind=engine)
```

### Command Cheatsheet
The following commands are useful to know:
```bash
> alembic init <FOLDERNAME>                         # Creates folder objects and top-level alembic.ini
> alembic revision -m "Some message"                # Manually populate resulting revision
> alembic revision --autogenerate -m "Some message" # Let alembic generate migration based on delta to previous

# Remember that database keeps track of which version it is using via the `alembic_version` table!
> alembic upgrade head
> alembic upgrade +1
> alembic upgrade <VERSION_ID>
> alembic downgrade -1

# SQLite check table columns once migrated
> PRAGMA table_info(TABLE_NAME);
```


## Typing
Every time I try to get better at static typing, I immediately regret ever having chosen IT as my field of employment.

I know it's a good practice to have and can help catch many bugs early on, so I persist at trying to get better. The problem is that this system feels like it was bolted onto Python, and Pylance **ALWAYS** starts reporting tons of errors because it can't properly introspect some nested class/variable. Then I start googling and trying to read through discussion groups by people way smarter than me and my eyes spin as I try to follow the conversation.

And yet still I persist. This latest attempt was especially important due to how Samiullah chose to build a generic [CRUDBase class](https://github.com/ChristopherGS/ultimate-fastapi-tutorial/blob/main/part-07-database/app/crud/base.py). TypeVars were declared for SQLAlchemy and Pydantic models, and then mixed into a class inheriting from a Generic type. This took me a LONG time to figure out and I'm not convinced I understand it 100%. (Essentially, with this one class we can spawn any new instance type with requires DB CRUD capabilities so long as we feed the generic factor a few models). This part seems like overkill for such a small project but I can see how it would be fundamental to supporting a graceful scale-out without things becoming overwhelming from a model point of view.

### TypeVar (TO DO)
TypeVar can hold other types. Needed by Generic.
```python
from typing import TypeVar

T = TypeVar('T', int, float, str)

class BinaryTree(Generic[T]):
    def __init__(self, value: T):
        self.value = value

    def add(self, value: T) -> None:
        if value < self.value:
            ...

tree = BinaryTree(5)
tree.add(7)      # T will be treated as int
tree.add(0.5)    # T will be treated as float.
```

UPPER BOUNDS
Instead of changing our type variable declaration, use UPPER BOUND. 
Example: `ModelType = TypeVar("ModelType", bound=Base)` means `Any object that is either the upper bound itself (i.e. Base) or a subclass is OK`.
NOTE: `ANY` has weird behaviour.

Good references:
* [Kie Codes - "How to use python type hinting](https://www.youtube.com/watch?v=yScuF1UgGU0) - good coverage of TypeVar and Generics.
* 

## Dependency Injection

## React (TO DO)

NODEJS for React
# https://christophergs.com/tutorials/ultimate-fastapi-tutorial-pt-12-react-js-frontend/
# https://github.com/facebook/create-react-app
At project root # UPDATE: DIDNT DO. Figure out later (GH had more entries in packages.json, older versions): 
    > mkdir frontend && cd frontend
    > npx create-react-app recipe-app
    > mv recipe-app/* ./     (I don't want to copy all of his structure from git)
    > node --version    (make sure above 14)
    Add package delta from https://github.com/ChristopherGS/ultimate-fastapi-tutorial/blob/main/part-12-react-frontend/frontend/package.json)

UPDATE - I had enough problems, just copied the whole damn thing:
    > git clone git@github.com:ChristopherGS/ultimate-fastapi-tutorial.git
    > cp -r ultimate-fastapi-tutorial/part-12-react-frontend/frontend/ FastAPI/


NOTE:
* For the REACt app to work you have to set BACKEND_CORS_ORIGIN in the app/core/config.py and 
/app/main.py . YOu can see that FastAPI api is returning payload but browser is not allowing it.

# To let React app talk to FASTAPI backend on different origin, had to:
1. Update frontend/config.js
2. Update app/app/main.py
3. Update app/core/config.py

```python
# app/main.py
...
from fastapi import FastAPI, APIRouter, Request, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings

root_router = APIRouter()
app = FastAPI(title="Recipe API", openapi_url=f"{settings.API_V1_STR}/openapi.json")

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_origin_regex=settings.BACKEND_CORS_ORIGIN_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
...
```

```python
...
class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    JWT_SECRET: str = "TEST_SECRET_DO_NOT_USE_IN_PROD"
    ALGORITHM: str = "HS256"

    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8001",  # type: ignore
        "https://fastapi-recipe-app.herokuapp.com"
    ]
...
```

## OPENAPI and API invocation (To Do)
To access OpenAPI panel:

1. Run the FastAPI server via `poetry run ./run.sh`.

2. Point browser to `http://localhost:8001/docs`.

Example curl command (may no longer work since additional middleware was added to project):
```bash
curl -X 'POST' \
  'http://localhost:8001/recipe/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "label": "beef",
  "source": "Fast Foodz",
  "url": "http://example.com",
  "submitter_id": 5
}'
```

## FastAPI / Pydantic Coercion & Config (To Do)
While I can understand the reason for it framework does a few things I don't like, since I feel it obfuscates behaviour:

1. **Coercion of variable types**

    I define my Pydantic model with `count: int`, yet a client sends me a payload where `"count": "1"`. When the payload is processed by the API, it's automatically transformed into an int. Great, right? Maybe.

    Call me a pessimist, but unless we are in some sort of business environment where there is such a battle for clients that returning data validation errors to connecting system is a huge faux pas, I don't think it's good to silently fix mistakes. The clients will never know that messages they are sending are actually non-compliant and who know what sort of logic they themselves are building into this tooling on their end.

    To this end, my gut feelig is [Strict-type](https://pydantic-docs.helpmanual.io/usage/types/#strict-types) field definitions are probably a better choice despite the reisk of being called a nit-picker.

2. **Automatic detection of configuration variables.**

    I've seen a few videos/blogs now gushing about Pydantic's [settings management](https://pydantic-docs.helpmanual.io/usage/settings/) capabilities, but it just feels wrong to me. Maybe I don't understand it well enough yet to really appreciate what it does, but I don't see what's wrong with explicitly writing `some_var = os.environ.get["SOME_VAR"]`. This is simple, it's direct, and it's very easy for another person reading the code to follow. 

    I think the killer feature may be for testing, secrets files, and model inheritance. More investigation/implementaiton testing is required.


## Deployment Steps (To Do)
Deploy to Linode: https://christophergs.com/tutorials/ultimate-fastapi-tutorial-pt-6b-linode-deploy-gunicorn-uvicorn-nginx/

linode_install:
    sudo apt -y upgrade  
    sudo apt -y install python3-pip  # Install Python
    pip install poetry  # Install Poetry
    poetry install  # Install the app dependencies in our pyproject.toml file (recall we use this instead of a requirements.txt)
    sudo apt -y install nginx  # Install nginx
    sudo cp nginx/default.conf /etc/nginx/sites-available/fastapi_app  # Copy the nginx config
    # Disable the NGINX’s default configuration file by removing its symlink
    sudo unlink /etc/nginx/sites-enabled/default
    sudo ln -s /etc/nginx/sites-available/fastapi_app /etc/nginx/sites-enabled/

> poetry run gunicorn --bind=unix:///tmp/uvicorn.sock -w 2 --forwarded-allow-ips='*' -k uvicorn.workers.UvicornWorker app.main:app

But Gunicorn supports working as a process manager and allowing users to tell it which specific worker process class to use. Then Gunicorn would start one or more worker processes using that class. And Uvicorn has a Gunicorn-compatible worker class. Using that combination, Gunicorn would act as a process manager, listening on the port and the IP. And it would transmit the communication to the worker processes running the Uvicorn class. And then the Gunicorn-compatible Uvicorn worker class would be in charge of converting the data sent by Gunicorn to the ASGI standard for a FastAPI application to use it.

The other key thing we’ve done is configured nginx to act as a reverse proxy. If you look at the nginx/default.conf you’ll see:

    server {
        listen 80;
        client_max_body_size 4G;

        server_name example.com;

        location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        proxy_redirect off;
        proxy_buffering off;
        proxy_pass http://uvicorn;
        }

        location /static {
        # path for static files
        root /path/to/app/static;
        }
    }

    map $http_upgrade $connection_upgrade {
        default upgrade;
        '' close;
    }

    upstream uvicorn {
        server unix:/tmp/uvicorn.sock;
    }