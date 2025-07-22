from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password_hash: str

    class Config:
        from_attributes = True

class User(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str
