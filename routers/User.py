from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models.User import UserInitRequest

from services.logger import Logger
from services.neo4j_service import get_all_users, create_user_node, get_user_by_initials, get_or_create_user

router = APIRouter()

class UserInitRequest(BaseModel):
    initials: str
    role: str

@router.get("/users")
def fetch_users():
    return get_all_users()

@router.post("/user/identify")
def identify_or_create_user(data: UserInitRequest):
    existing = get_user_by_initials(data.initials)
    if existing:
        return existing

    user_id = create_user_node(initials=data.initials, role=data.role)
    Logger.set_initials(str(data.initials))
    return {"id": user_id, "name": data.initials, "role": data.role}
