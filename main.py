import os
from fastapi import FastAPI
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from routers import analysts, lead_analysts, role_manager, webtree, request_manager, api_endpoints, tools
from routers import Project, ProjectManager, User, DbEnumerator, sql_injection
from services.neo4j_driver import create_database_if_not_exists, get_driver
import logging
import uvicorn
from contextlib import asynccontextmanager

from routers.tools import status, exists

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup...")
    try:
        database_name = "neo4j"
        logger.info(f"Ensuring database '{database_name}' exists...")
        create_database_if_not_exists(database_name)
        logger.info(f"Database '{database_name}' is ready.")
    except Exception as e:
        logger.error(f"Error during startup: {e}")


    yield
    logger.info("Application shutdown...")
    try:
        driver = get_driver(no_init_error=True)
        if driver:
            driver.close()
            logger.info("Database connection closed.")
        else:
            logger.info("No active database driver to close.")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

app = FastAPI(lifespan=lifespan)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# create a mini–router for just the HTTP-Tester bits
root_http = APIRouter()

app.add_api_route(
    "/{project_id}/http-requests/status",
    status,
    methods=["GET"]
)


app.add_api_route(
    "/{project_id}/http-requests/exists",
    exists,
    methods=["GET"]
)
app.include_router(analysts.router, prefix="/analysts", tags=["analysts"])
app.include_router(lead_analysts.router, prefix="/lead_analysts", tags=["lead_analysts"])
app.include_router(role_manager.router, prefix="/role_manager", tags=["role_manager"])
app.include_router(webtree.router, prefix="/webtree", tags=["webtree"])
app.include_router(request_manager.router, prefix="/request_manager", tags=["request_manager"])
app.include_router(tools.router, prefix="/tools")
app.include_router(Project.router, prefix="/project", tags=["project"])
app.include_router(ProjectManager.router)
app.include_router(User.router)
app.include_router(root_http)
app.include_router(DbEnumerator.router)
app.include_router(api_endpoints.router)
app.include_router(sql_injection.router, prefix="/tools/sql-injection", tags=["sql_injection"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
