from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password_hash: str

    class Config:
        orm_mode = True

class User(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


