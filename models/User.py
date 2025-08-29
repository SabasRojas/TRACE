# models/user_model.py

from pydantic import BaseModel

class UserInitRequest(BaseModel):
    initials: str
    role: str