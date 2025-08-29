import time
import requests


# wrapper to get URL from a vertex
def getURL(vertex: tuple[str, str]) -> str:
    if not isinstance(vertex, tuple) or len(vertex) != 6:
        raise ValueError(
            f"Vertex {vertex} is not properly formatted! Format should be a tuple of the form: (url, path)")
    return vertex[0]


# wrapper to get Path from a vertex
def getIP(vertex: tuple[str, str]) -> str:
    if not isinstance(vertex, tuple) or len(vertex) != 6:
        raise ValueError(
            f"Vertex {vertex} is not properly formatted! Format should be a tuple of the form: (url, path)")
    return vertex[1]


def getCharCount(vertex: tuple[str, str]) -> int:
    if not isinstance(vertex, tuple) or len(vertex) != 6:
        raise ValueError(f"Vertex {vertex} is not properly formatted!")
    return vertex[2]


def getWordCount(vertex: tuple[str, str]) -> int:
    if not isinstance(vertex, tuple) or len(vertex) != 6:
        raise ValueError(f"Vertex {vertex} is not properly formatted!")
    return vertex[3]


def getLinkFound(vertex: tuple[str, str]) -> bool:
    if not isinstance(vertex, tuple) or len(vertex) != 6:
        raise ValueError(f"Vertex {vertex} is not properly formatted!")
    return vertex[4]

def getStatusCode(vertex: tuple[str, str]) -> int:
    if not isinstance(vertex, tuple) or len(vertex) != 6:
        raise ValueError(f"Vertex {vertex} is not properly formatted!")
    return vertex[5]

def send_get_request(curr_dir, request_delay, page_count, page_limit, user_agent_string, cookies=None):
    if page_count >= page_limit:
        return None, None
    time.sleep(request_delay / 1000)
    try:
        req = requests.get(curr_dir, headers={'User-Agent': user_agent_string}, cookies=cookies)
        print("Currently at", curr_dir, req.status_code)
        return req.text, req.status_code
    except Exception as e:
        print(f"[ERROR] Connection error: {e}")
    return None, None


def send_post_request(curr_dir, request_delay, json_string, page_count, page_limit, user_agent_string, cookies=None):
    if page_count >= page_limit:
        return None
    time.sleep(request_delay / 1000)
    try:
        req = requests.post(curr_dir, headers={'User-Agent': user_agent_string}, data=json_string, cookies=cookies)
        return req.text, req.status_code
    except Exception as e:
        print(f"[ERROR] Connection error: {e}")
    return None


def send_put_request(curr_dir, request_delay, json_string, page_count, page_limit, user_agent_string, cookies=None):
    if page_count >= page_limit:
        return None
    time.sleep(request_delay / 1000)
    try:
        req = requests.put(curr_dir, headers={'User-Agent': user_agent_string}, data=json_string)
        return req.text, req.status_code
    except Exception as e:
        print(f"[ERROR] Connection error: {e}")
    return None

class CrawlerAlreadyRunningError(Exception):
    pass