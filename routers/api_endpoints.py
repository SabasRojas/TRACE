import json
import threading
import socket

from fastapi import FastAPI, HTTPException, BackgroundTasks, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Literal

from starlette.responses import JSONResponse

from routers.Project import project_db
from services.HTTPClient import RequestManager, ProxyServer, HTTPClient
from services.logger import Logger
from services.Crawler import Crawler
from services.Fuzzer import Fuzzer
from services.BruteForce import BruteForce
from services.mdp3 import WebScraper, nlp_subroutine, CredentialGeneratorMDP
from services.neo4j_service import create_or_update_and_link_crawler_results, \
    get_fuzzer_results_by_project_id, get_crawler_results_by_project_id, ResultsNotFoundError, \
    get_crawler_links_by_project_id, get_brute_force_results_by_project_id, \
    create_or_update_and_link_brute_force_results, create_or_update_and_link_fuzzer_results, \
    get_credentials_by_project_id, create_or_update_and_link_credentials, get_fuzzer_links_by_project_id, \
    get_brute_force_links_by_project_id
import uuid

router = APIRouter()
logger = Logger()
fuzzer_data = Optional[list[str, str]]
fuzzer_links = [list[str]]
fuzzer: Fuzzer = None

bruteForce_data = Optional[list[str, str]]
bruteForce_links = [list[str]]
bruteForce: BruteForce = None
operation_done: bool = False
# Dictionary to keep track of running crawler tasks per project
active_crawlers = {}
complete_crawlers = {}
failed_crawlers = {}

active_bruteForce = {}
complete_bruteForce = {}
failed_bruteForce = {}

active_fuzzer = {}
complete_fuzzer = {}
failed_fuzzer = {}

active_generators = {}
complete_generators = {}
failed_generators = {}

class CrawlerConfig(BaseModel):
    TargetURL: str
    CrawlDepth: int
    PageNumberLimit: int
    UserAgent: str
    RequestDelay: float
    FilterRelative: bool

class CrawlerStatusResponse(BaseModel):
    status: Literal["Starting", "Running", "Complete", "Failed", "Not Found"] = Field(..., description="Current status of the crawler for the project.")
    progress: Optional[float] = Field(None, ge=0.0, le=1.0, description="Approximate crawler progress (0.0 to 1.0), if available.")
    detail: Optional[str] = Field(None, description="Additional detail, e.g., error message on failure.")


class FuzzerConfig(BaseModel):
    TargetURL: str
    HTTPMethod: str
    Cookies: list
    HideStatusCode: list
    ShowOnlyStatusCode: list
    FilterContentLength: int
    PageLimit: int
    WordList: list


class BruteForceConfig(BaseModel):
    TargetURL: str
    TopLevelDirectory: Optional[str]
    HideStatusCode: list[str]
    ShowOnlyStatusCode: list[str]
    FilterContentLength: int
    WordList: list[str]

class WebscraperConfig(BaseModel):
    passchars: bool
    userchars: bool
    passnums: bool
    usernums: bool
    passsyms: bool
    usersyms: bool

    # set the length of the credentials to output
    userlen: int
    passle: int
    credentialAmount: int
    wordlist: list

@router.post("/{projectID}/fuzzer")
async def set_up_fuzzer(config: FuzzerConfig, background_tasks: BackgroundTasks, projectID: str):
    if active_fuzzer.get(projectID):
        raise HTTPException(status_code=409, detail="fuzzer is already running for this project.")
    def run_fuzzer():
        try:
            failed_fuzzer.pop(projectID, None)
            complete_fuzzer.pop(projectID, None)
            end_log = logger.log_action("running fuzzer")  # start log
            stop_event = threading.Event()
            pause_event = threading.Event()
            pause_event.set()
            print("Received config: ", config)
            req_manager = RequestManager()
            proxy_server = ProxyServer()
            client = HTTPClient(request_manager=req_manager, proxy_server=proxy_server)
            if config:
                fuzzer = Fuzzer(config.model_dump(), projectID=projectID, stop_event=stop_event, pause_event=pause_event)
            else:
                fuzzer = Fuzzer()
            active_fuzzer[projectID] = {"fuzzer": fuzzer, "stop_event": stop_event, "pause_event": pause_event}
            fuzzer.start()
            fuzzer_data = fuzzer.get_data()
            create_or_update_and_link_fuzzer_results(projectID, str(uuid.uuid4()), fuzzer_data, fuzz_links=fuzzer.found_urls)
            complete_fuzzer[projectID] = True
            end_log()
        except Exception as e:
            failed_fuzzer[projectID] = True
            logger.log_action(f"fuzzer failed: {e}")
            raise HTTPException(status_code=499, detail=str(e))
        finally:
            active_fuzzer.pop(projectID, None)
    background_tasks.add_task(run_fuzzer)
    return {"message": " Fuzz started on the background successfully"}



@router.get("/{projectID}/fuzzer/data")
def get_fuzzer_data(projectID: str):
    try:
        fuzzer_results = get_fuzzer_results_by_project_id(project_id=projectID)
        return fuzzer_results
    except ResultsNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: Could not parse fuzzer data. {e.msg}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@router.get("/{projectID}/fuzzer/status")
def get_fuzzer_status(projectID: str):
    if projectID not in active_fuzzer:
        if projectID in complete_fuzzer:
            return {"status": "Complete", "progress": 100}
        elif projectID in failed_fuzzer:
            return {"status": "Failed", "progress": 0}
        else:
            return {"status": "No running", "progress": 0}
    else:
        fuzzer = active_fuzzer.get(projectID)["fuzzer"]
        if fuzzer.pause_event.is_set():
            return {"status": "Running", "progress": fuzzer.getProgress()}
        else:
            return {"status": "Paused", "progress": fuzzer.getProgress()}

@router.get("/{projectID}/fuzzer/exists")
def get_if_fuzzer_exists(projectID: str):
    try:
        fuzzer_results = get_fuzzer_results_by_project_id(project_id=projectID)
        if fuzzer_results:
            complete_fuzzer[projectID] = True
            return {"status": "Complete"}
        else:
            return {"status": "No Content"}
    except ResultsNotFoundError as e:
        return {"status": "No Content"}
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: Could not parse fuzzer data. {e.msg}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.post("/{projectID}/bruteForce")
async def set_up_bruteForce(config: BruteForceConfig, background_tasks: BackgroundTasks, projectID: str):
        if active_bruteForce.get(projectID):
         raise HTTPException(status_code=409, detail="Brute forcer is already running for this project.")

        def run_brute_force():
            try:
                failed_bruteForce.pop(projectID, None)
                complete_bruteForce.pop(projectID, None)
                end_log = logger.log_action("running brute force")
                stop_event = threading.Event()
                pause_event = threading.Event()
                pause_event.set()
                print("Received config: ", config.model_dump())
                if config:
                    bruteForce = BruteForce(config.model_dump(), projectID=projectID, stop_event=stop_event, pause_event=pause_event)
                else:
                    bruteForce = BruteForce()
                active_bruteForce[projectID] = {"bruteForce": bruteForce, "stop_event": stop_event, "pause_event": pause_event}
                bruteForce.start_brute_force()
                bruteForce_data = bruteForce.get_data()
                create_or_update_and_link_brute_force_results(projectID, str(uuid.uuid4()), bruteForce_data, bruteForce.found_urls)
                complete_bruteForce[projectID] = True
                end_log()
            except Exception as e:
                failed_bruteForce[projectID] = True
                logger.log_action(f"bruteForce failed: {e}")
                raise HTTPException(status_code=499, detail=str(e))
            finally:
                active_bruteForce.pop(projectID, None)

        background_tasks.add_task(run_brute_force)
        return {"message: " "Brute Force started in the background successfully"}



@router.get("/{projectID}/bruteForce/data")
def get_brute_force_data(projectID: str):
    try:
        brute_forcer_results = get_brute_force_results_by_project_id(project_id=projectID)
        return brute_forcer_results
    except ResultsNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: Could not parse brute forcer data. {e.msg}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.get("/{projectID}/bruteForce/status")
def get_bruteForce_status(projectID: str):
    if projectID not in active_bruteForce:
        if projectID in complete_bruteForce:
            return {"status": "Complete", "progress": 100}
        elif projectID in failed_bruteForce:
            return {"status": "Failed", "progress": 0}
        else:
            return {"status": "No running", "progress": 0}
    else:
        bruteForce = active_bruteForce.get(projectID)["bruteForce"]
        if bruteForce.pause_event.is_set():
            return {"status": "Running", "progress": bruteForce.getProgress()}
        else:
            return {"status": "Paused", "progress": bruteForce.getProgress()}


@router.get("/{projectID}/bruteForce/exists")
def get_if_bruteForce_exists(projectID: str):
    try:
        bruteForce_results = get_brute_force_results_by_project_id(project_id=projectID)
        if bruteForce_results:
            complete_bruteForce[projectID] = True
            return {"status": "Complete"}
        else:
            return {"status": "No Content"}
    except ResultsNotFoundError as e:
        return {"status": "No Content"}
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: Could not parse brute force data. {e.msg}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.post("/{projectID}/crawler")
async def set_up_crawler(config: CrawlerConfig, background_tasks: BackgroundTasks, projectID: str):

    if active_crawlers.get(projectID):
        raise HTTPException(status_code=409, detail="Crawler is already running for this project.")

    def run_crawler():
        try:
            failed_crawlers.pop(projectID, None)
            complete_crawlers.pop(projectID,None)
            end_log = logger.log_action("running Crawler")  # start log
            req_manager = RequestManager()
            proxy_server = ProxyServer()
            client = HTTPClient(request_manager=req_manager, proxy_server=proxy_server)
            stop_event = threading.Event()
            pause_event = threading.Event()
            pause_event.set()
            crawler = Crawler(config.model_dump(), http_client=client, projectID=projectID, stop_event=stop_event, pause_event=pause_event)
            active_crawlers[projectID] = {"crawler": crawler, "stop_event": stop_event, "pause_event": pause_event}
            crawler.start_crawl()
            if crawler.tree_creator.tree.root:
                crawler_data = crawler.tree_creator.get_tree_map(crawler.tree_creator.tree.root)
            else:
                crawler_data = None
            create_or_update_and_link_crawler_results(projectID, str(uuid.uuid4()), crawler_data, crawler.visited_urls)
            complete_crawlers[projectID] = True
            end_log()  # log end time
        except Exception as e:
            failed_crawlers[projectID] = True
            logger.log_action(f"Crawler failed: {e}")
        finally:
            # Always clear lock even if the crawl crashes
            active_crawlers.pop(projectID, None)

    background_tasks.add_task(run_crawler)

    return {"message": "Crawl started in the background"}


@router.get("/{projectID}/crawler/data")
def get_crawler_data(projectID: str):
    try:
        crawler_results = get_crawler_results_by_project_id(project_id=projectID)
        return crawler_results
    except ResultsNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: Could not parse crawler data. {e.msg}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@router.get("/{projectID}/crawler/status")
def get_crawler_status(projectID: str):
    if projectID not in active_crawlers:
        if projectID in complete_crawlers:
            return {"status": "Complete", "progress": 100}
        elif projectID in failed_crawlers:
            return {"status": "Failed", "progress": 0}
        else:
            return {"status": "No running", "progress": 0}
    else:
        crawler = active_crawlers.get(projectID)["crawler"]
        if crawler.pause_event.is_set():
            return {"status": "Running", "progress": crawler.getProgress()}
        else:
            return {"status": "Paused", "progress": crawler.getProgress()}

@router.get("/{projectID}/crawler/exists")
def get_if_crawler_exists(projectID: str):
    try:
        crawler_results = get_crawler_results_by_project_id(project_id=projectID)
        if crawler_results:
            complete_crawlers[projectID] = True
            return {"status": "Complete"}
        else:
            return {"status": "No Content"}
    except ResultsNotFoundError as e:
        return {"status": "No Content"}
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: Could not parse crawler data. {e.msg}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.post("/{projectID}/crawler/stop")
def stop_crawler(projectID: str):
    if projectID in active_crawlers:
        active_crawlers[projectID]["pause_event"].set()
        active_crawlers[projectID]["stop_event"].set()
        active_crawlers.pop(projectID, None)
        return {"status": "Stopped"}
    else:
        return {"status": "Not Running"}

@router.post("/{projectID}/crawler/pause")
def stop_crawler(projectID: str):
    if projectID in active_crawlers:
        active_crawlers[projectID]["pause_event"].clear()
        return {"status": "Paused"}
    else:
        return {"status": "Not Running"}

@router.post("/{projectID}/crawler/resume")
def stop_crawler(projectID: str):
    if projectID in active_crawlers:
        active_crawlers[projectID]["pause_event"].set()
        return {"status": "Running"}
    else:
        return {"status": "Not Running"}
    
@router.post("/{projectID}/bruteForce/stop")
def stop_bruteForce(projectID: str):
    if projectID in active_bruteForce:
        active_bruteForce[projectID]["pause_event"].set()
        active_bruteForce[projectID]["stop_event"].set()
        active_bruteForce.pop(projectID, None)
        return {"status": "Stopped"}
    else:
        return {"status": "Not Running"}

@router.post("/{projectID}/bruteForce/pause")
def pause_bruteForce(projectID: str):
    if projectID in active_bruteForce:
        active_bruteForce[projectID]["pause_event"].clear()
        return {"status": "Paused"}
    else:
        return {"status": "Not Running"}

@router.post("/{projectID}/bruteForce/resume")
def resume_bruteForce(projectID: str):
    if projectID in active_bruteForce:
        active_bruteForce[projectID]["pause_event"].set()
        return {"status": "Running"}
    else:
        return {"status": "Not Running"}

@router.post("/{projectID}/fuzzer/stop")
def stop_fuzzer(projectID: str):
    if projectID in active_fuzzer:
        active_fuzzer[projectID]["pause_event"].set()
        active_fuzzer[projectID]["stop_event"].set()
        active_fuzzer.pop(projectID, None)
        return {"status": "Stopped"}
    else:
        return {"status": "Not Running"}

@router.post("/{projectID}/fuzzer/pause")
def pause_fuzzer(projectID: str):
    if projectID in active_fuzzer:
        active_fuzzer[projectID]["pause_event"].clear()
        return {"status": "Paused"}
    else:
        return {"status": "Not Running"}

@router.post("/{projectID}/fuzzer/resume")
def resume_fuzzer(projectID: str):
    if projectID in active_fuzzer:
        active_fuzzer[projectID]["pause_event"].set()
        return {"status": "Running"}
    else:
        return {"status": "Not Running"}   


@router.post("/{projectID}/webscraper")
def get_webscraper_data(projectID: str, options: WebscraperConfig, background_tasks: BackgroundTasks):
    failed_generators.pop(projectID, None)
    complete_generators.pop(projectID, None)
    fuzzer_links = get_fuzzer_links_by_project_id(projectID)
    bruteForce_links = get_brute_force_links_by_project_id(projectID)
    crawler_links = get_crawler_links_by_project_id(project_id=projectID)
    all_links = list(set(fuzzer_links + bruteForce_links + crawler_links))
    if all_links is None:
        raise HTTPException(status_code=400, detail="No data available")
    if active_generators.get(projectID):
        raise HTTPException(status_code=409, detail="Generator is already running for this project.")
    active_generators[projectID] = True
    csv_path = "web_text.csv"
    wordlist_path = options.wordlist
    end_log = logger.log_action("generating wordlist of usernames and passwords")  # start log
    scraper = WebScraper(all_links)
    def run_generator():
        try:
            scraper.generate_csv(csv_path)
            nlp_subroutine(csv_path)
            generator = CredentialGeneratorMDP(csv_path, wordlist_path, options.model_dump())
            generator.progress = 40
            credentials = generator.generate_credentials(options.credentialAmount)
            create_or_update_and_link_credentials(project_id=projectID, results_id=str(uuid.uuid4()), credentials=credentials)
            end_log()
            print(credentials)
            complete_generators[projectID] = generator
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating credentials: {e}")
        finally:
            # Always clear lock even if the crawl crashes
            active_generators.pop(projectID, None)
    background_tasks.add_task(run_generator)
    return {"message": "Generator started in the background"}

@router.get("/{projectID}/aiGenerator/status")
def get_ai_generator_status(projectID: str):
    if projectID not in active_generators:
        if projectID in complete_generators:
            return {"status": "Complete", "progress": 100}
        elif projectID in failed_generators:
            return {"status": "Failed", "progress": 0}
        else:
            return {"status": "No running", "progress": 0}
    else:
        return {"status": "Running", "progress": 20}

@router.get("/{projectID}/aiGenerator/data")
def get_crawler_data(projectID: str):
    try:
        credentials = get_credentials_by_project_id(project_id=projectID)
        return credentials
    except ResultsNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: Could not parse credentials data. {e.msg}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.get("/status")
def check_connection():
    return {"status":"active"}

@router.get("/ip")
def get_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return {"ip": ip_address}


def set_fuzzer_data(data):
    global fuzzer_data
    fuzzer_data = data


def set_fuzzer_links(links):
    global fuzzer_links
    fuzzer_links = links


def set_bruteForce_data(data):
    global bruteForce_data
    bruteForce_data = data


def set_bruteForce_links(links):
    global bruteForce_links
    bruteForce_links = links