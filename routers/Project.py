from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from models.Project import Project
#from services.logger import Logger

from services.neo4j_service import (
    create_project_node,
    get_all_projects,
    get_project_node,
    update_project_lock,
    get_recently_accessed_projects,
    log_user_project_access,
    link_owner_to_project,
    user_is_project_owner,
    join_project,
    get_user_by_initials,
    get_joined_projects_for_user,
    remove_project_member,
    get_project_members
)
from typing import List, Tuple, Optional

router = APIRouter()
project_db: dict[str, Project] = {}

class AccessLogPayload(BaseModel):
    user_id: int

class LockToggleRequest(BaseModel):
    user_id: int
    initials: str
    lock: bool

@router.get("/")
def get_all_projects_route():
    return get_all_projects()

@router.post("/create")
def create_project(project: Project):
    #Logger.set_project(project.name)
    if project.id in project_db:
        raise HTTPException(status_code=400, detail="Project ID already exists.")

    project_db[project.id] = project
    create_project_node(project)
    link_owner_to_project(project.owner, project.id)

    return {"success": True, "message": f"Project '{project.name}' created."}

@router.get("/recent")
def get_recent_projects(user_id: int):
    try:
        return get_recently_accessed_projects(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recent projects: {str(e)}")

@router.get("/joined")
def get_joined_projects(user_id: int):
    try:
        return get_joined_projects_for_user(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}")
def get_project(project_id: str, requester_id: Optional[int] = Query(default=None)):
    try:
        proj = get_project_node(project_id)
        
        if proj["isLocked"]:
            raise HTTPException(status_code=403, detail="Project is locked.")
        #Logger.set_project(str(proj["name"]))
        return {"project": proj}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Project not found.")

@router.put("/{project_id}/lock-toggle")
def toggle_project_lock(project_id: str, payload: LockToggleRequest):
    if not user_is_project_owner(payload.initials, project_id):
        raise HTTPException(
            status_code=403,
            detail="Only the Lead Analyst (owner) with matching initials can lock/unlock this project."
        )
    update_project_lock(project_id, payload.lock)
    return {"message": f"Project {'locked' if payload.lock else 'unlocked'} successfully."}

@router.put("/{project_id}/name")
def update_project_name(project_id: str, new_name: str):
    proj = get_project_node(project_id)
    if proj["isLocked"]:
        raise HTTPException(status_code=403, detail="Project is locked.")
    project = project_db.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    result = project.set_project_name(new_name)
    return {"success": result}

@router.put("/{project_id}/owner")
def set_owner(project_id: str, initials: str, owner_id: str):
    project = project_db.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    project.set_owner(initials, owner_id)
    return {"success": True}

@router.post("/{project_id}/iplist")
def import_ip_list(project_id: str, ip_list: List[Tuple[str, int]]):
    project = project_db.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    project.import_ip_list(ip_list)
    return {"success": True, "message": "IP list updated."}

@router.get("/{project_id}/save")
def save_project(project_id: str):
    project = project_db.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return project.save_project()

@router.post("/{project_id}/access")
def log_project_access(project_id: str, payload: AccessLogPayload):
    try:
        log_user_project_access(payload.user_id, project_id)
        return {"message": f"User {payload.user_id} accessed project {project_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log access: {str(e)}")

@router.post("/{project_id}/join")
def api_join_project(
    project_id: str,
    user_initials: str = Query(..., description="Initials of the analyst joining"),
):
    proj = get_project_node(project_id)
    if proj["isLocked"]:
        raise HTTPException(status_code=403, detail="Project is locked.")
    user = get_user_by_initials(user_initials)
    if not user:
        raise HTTPException(404, f"User '{user_initials}' not found")
    join_project(project_id, user["id"])
    return {"message": f"User '{user_initials}' joined project '{project_id}'"}

@router.get("/{project_id}/members")
def get_members(project_id: str):
    proj = get_project_node(project_id)
    if proj["isLocked"]:
        raise HTTPException(status_code=403, detail="Project is locked.")
    try:
        return get_project_members(project_id)
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@router.post("/{project_id}/add_member")
def add_member(
    project_id: str,
    user_initials: str = Query(..., description="Initials of the analyst to add"),
    caller_initials: str = Query(..., description="Initials of the user making this call")
):
    proj = get_project_node(project_id)
    if proj["isLocked"]:
        raise HTTPException(status_code=403, detail="Project is locked.")
    if not user_is_project_owner(caller_initials, project_id):
        raise HTTPException(403, "Only the project owner can add members")
    user = get_user_by_initials(user_initials)
    if not user:
        raise HTTPException(404, f"User '{user_initials}' not found")
    join_project(project_id, user["id"])
    return {"message": f"Added {user_initials} to {project_id}"}

@router.delete("/{project_id}/remove_member")
def remove_member(
    project_id: str,
    user_initials: str = Query(..., description="Initials of analyst to remove")
):
    proj = get_project_node(project_id)
    if proj["isLocked"]:
        raise HTTPException(status_code=403, detail="Project is locked.")
    remove_project_member(project_id, user_initials)
    return {"message": f"Removed {user_initials} from {project_id}"}
