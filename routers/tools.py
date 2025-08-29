from typing import Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from services.HTTPClient import HTTPClient, RequestManager, ProxyServer, HttpResponse 

router = APIRouter()

_http_done: set[str] = set()

# --- Pydantic model for the client request ---
class ClientRequest(BaseModel):
    url: str
    method: str = "GET"
    headers: dict = {}
    parameters: dict = {}
    payload: Any = None
    cookies: dict = {} 
    hide_status_codes: list[int] = []     
    show_only_status_codes: list[int] = []

@router.get("/{project_id}/http-requests/status")
def status(project_id: str):
    if project_id in _http_done:
        return {"progress": 100, "status": "Complete"}
    else:
        return {"progress":   0, "status": "No running"}

@router.get("/{project_id}/http-requests/exists")
def exists(project_id: str):
    # mirror the logic in your status endpoint
    if project_id in _http_done:
        return {"status": "Complete"}
    else:
        return {"status": "No Content"}

@router.post("/send")
async def send_client_request(client_request: ClientRequest,project_id: str = Query(..., description="Your project’s ID")):
    print("Endpoint /tools-dashboard/send received client_request:")
    print(client_request.dict())
    
    req_manager = RequestManager()
    proxy_server = ProxyServer()  
    client = HTTPClient(req_manager, proxy_server)
    
    # For GET requests, use the provided query parameters.
    if client_request.method.upper() == "GET":
        data = client_request.parameters
    else:
        data = client_request.payload


    client.send_request_with_cookies(
    url=client_request.url,
    data=data,
    req_type=client_request.method,
    headers=client_request.headers,
    cookies=client_request.cookies,
    hide_status_codes=client_request.hide_status_codes,
    show_only_status_codes=client_request.show_only_status_codes,
    )

    
    response = client.receive_response()

    if response is None:
        return {"message": "No response or filtered"}
    print("Endpoint /tools-dashboard/send sending final response:")
    print("  Status:", response.status_code)
    print("  Headers:", response.headers)
    print("  Body:", response.body)

    _http_done.add(project_id)
    
    return {
        "status": response.status_code,
        "headers": response.headers,
        "body": response.body
    }
