import re
import uuid
from typing import Dict, Any

from bs4 import BeautifulSoup
from services.neo4j_service import create_or_update_and_link_brute_force_results
from services.utils import send_get_request

class BruteForce:
    config = dict()
    default_config =  {
            "TargetURL": "www.example.com",
            "TopLevelDirectory": "www.example.com",
            "HideStatusCode": [],
            "ShowOnlyStatusCode": [],
            "FilterContentLength": 1000,
            "WordList": ["username", "password", "search", "admin"],
        }
#     TargetURL: "https://www.wikipedia.org/", TopLevelDirectory: "https://www.wikipedia.org",…}
# FilterContentLength
# : 
# 0
# HideStatusCode
# : 
# [""]
# ShowOnlyStatusCode
# : 
# [""]
# TargetURL
# : 
# "https://www.wikipedia.org/"
# TopLevelDirectory
# : 
# "https://www.wikipedia.org/"
# WordList
# : 
# ["alex", "carlos", "jose"]

    # TODO: Add logic to send status to endpoint
    # TODO: Connect tree creator logic to bruteforcer
    def __init__(self, config=None, projectID = None,  stop_event = None, pause_event = None):
        if config is None:
            self.reset()
            return
        elif len(config) == 0:
            self.reset()
            return
        for key in self.default_config.keys():
            if key not in config:
                print(key)
                raise KeyError("Invalid config dictionary")
        try:
            self.config = {
                "TargetURL": config["TargetURL"],
                "TopLevelDirectory": config["TopLevelDirectory"],
                "HideStatusCode": config["HideStatusCode"],
                "ShowOnlyStatusCode": config["ShowOnlyStatusCode"],
                "FilterContentLength": int(config["FilterContentLength"]),
                "WordList": config["WordList"]
            }
        except ValueError as e:
            raise ValueError(f"Invalid config values: {e}")
         #Store raw responses as {path:response}
        self.op_results: Dict[str, Any] = {}
        #Track visited URLs to prevent duplicate crawling
        self.visited_urls = set()
        self.found_urls = list()
        #Track how many pages have been brute forced
        self.page_count = int(0)
        self.projectID = projectID
        self.pause_event = pause_event
        self.stop_event = stop_event
        self.progress = 0
        self.filtered_requests = 0


    def reset(self):
        self.config = None
        self.config = self.default_config
        self.op_results = {} #reset operation results
        self.visited_urls = set() #reset curr list of visited urls
        self.page_count = 0 #reset pages count

    def get_data(self):
        return self.op_results
    
    def get_links(self):
        return self.visited_urls
    
    def bruteForcer(self, word):
        if self.stop_event.is_set():
            return
        self.pause_event.wait()
        target_url = self.config['TargetURL']
        if self.config['TopLevelDirectory']:
            top_dir = self.config['TopLevelDirectory'].strip('/')
            curr_dir = f"{target_url}/{top_dir}/{word}"
        else:
            curr_dir = f"{target_url}/{word}"

        response, status_code = send_get_request(curr_dir, 0, self.page_count, len(self.config['WordList']), "", "")
        filtered = False
        if str(status_code) in self.config['HideStatusCode']:
            self.filtered_requests += 1
            filtered = True

        if self.config['ShowOnlyStatusCode'] and str(status_code) not in self.config['ShowOnlyStatusCode']:
            self.filtered_requests += 1
            filtered = True
        #the 1 in the line above is page limit, this will just get ignored because the page limit for this should be the ammount of words in the wordlist 
        if response is None or status_code is None:
            print(f"[ERROR] Failed to connect to {curr_dir}")
            return
        if status_code == "200" and curr_dir not in self.found_urls:
            self.found_urls.append(curr_dir)
        soupText = BeautifulSoup(response, "html.parser")
        text = soupText.get_text()
        node = {
            "status": str(status_code),
            "char": str(len(re.sub(r"\s+", "", text))),
            "word_count": str(len(re.findall(r'\b\w+\b', text))),
            "payload": word,
            "filtered_requests": str(self.filtered_requests),
            "filtered": str(filtered)
        }
        self.op_results[curr_dir] = node
        self.visited_urls.add(curr_dir)
        self.page_count+=1
        self.update_bruteForce_data(bruteForce_data=self.op_results)
        

    def start_brute_force(self):
        for word in self.config['WordList']:
            self.bruteForcer(word)

    def update_bruteForce_data(self, bruteForce_data):
        # Update crawler data and links in real-time

        create_or_update_and_link_brute_force_results(project_id=self.projectID, results_id=str(uuid.uuid4()),
                                                 brute=bruteForce_data, bruteForce_links = self.found_urls)
        self.progress = round((self.page_count / len(self.config['WordList']) * 100))
        print(self.page_count / len(self.config['WordList']) * 100)
    def getProgress(self):
        return self.progress