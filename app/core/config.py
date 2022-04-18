from pydantic import AnyHttpUrl, BaseSettings, EmailStr, validator
from typing import List, Optional, Union


# Pydantic will try to determine the values of any fields not passed as keyworg arguments
# This is why we don't see code like:
#   `API_V1_STR: str = os.environ['API_V1_STR]`. I'm not sure I love the lack of explicitness.

class Settings(BaseSettings):  # 1
    API_V1_STR: str = "/api/v1"  # 2
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8001",  # type: ignore
    ]

    # Origins that match this regex OR are in the above list are allowed
    BACKEND_CORS_ORIGIN_REGEX: Optional[
        str
    ] = "https.*\.(netlify.app|herokuapp.com)"  # noqa: W605

    # Validator on the CORS value
    @validator("BACKEND_CORS_ORIGINS", pre=True)  # 3
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    SQLALCHEMY_DATABASE_URI: Optional[str] = "sqlite:///example.db"
    FIRST_SUPERUSER: EmailStr = "admin@recipeapi.com"
    FIRST_SUPERUSER_PW = "supersecret"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    JWT_SECRET: str = "TEST_SECRET_DO_NOT_USE_IN_PROD"
    ALGORITHM: str = "HS256"

    class Config:
        case_sensitive = True  # 4


# Instantiate for importation around the project.
settings = Settings()  # 5