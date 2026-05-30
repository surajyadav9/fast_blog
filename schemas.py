from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ====================
#     USERS
# ====================
class UserBase(BaseModel):
    """Mandatory user fields either for request or response"""

    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(min_length=1, max_length=120)


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_file: str | None
    image_path: str


# ====================
#     POSTS
# ====================
class PostBase(BaseModel):
    """Mandatory Fields"""

    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)


class PostCreate(PostBase):
    user_id: int  # TEMPORARY


class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date_posted: datetime
    author: UserResponse
