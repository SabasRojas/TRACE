import random
import re
import uuid
from typing import Dict, Any
import json
import string

from bs4 import BeautifulSoup

from services.neo4j_service import create_or_update_and_link_fuzzer_results
from services.utils import send_get_request, send_post_request, send_put_request

# TODO: Create method to report back status.

class Fuzzer:
    config = dict()
    default_config =  {
            "TargetURL": "www.example.com",
            "HTTPMethod": "GET",
            "Cookies": [],
            "HideStatusCode": [],
            "ShowOnlyStatusCode": [],
            "FilterContentLength": 100,
            "PageLimit": 100,
            "WordList": ["username", "password", "search", "admin"]
        }
    def __init__(self, config=None, projectID = None,  stop_event = None, pause_event = None):
        self.progress = 0
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
                "HTTPMethod": config["HTTPMethod"],
                "Cookies": config["Cookies"],
                "HideStatusCode": config["HideStatusCode"],
                "ShowOnlyStatusCode": config["ShowOnlyStatusCode"],
                "FilterContentLength": int(config["FilterContentLength"]),
                "PageLimit": int(config["PageLimit"]),
                "WordList": config["WordList"]
            }
        except ValueError as e:
            raise ValueError(f"Invalid config values: {e}")
         #Store raw responses as {path:response}
        self.op_results: Dict[str, Any] = {}
        #Track visited URLs to prevent duplicate crawling
        self.visited_urls = set()
        #Track how many pages have been crawled
        self.page_count = int(0)
        self.projectID = projectID
        self.pause_event = pause_event
        self.stop_event = stop_event
        self.filtered_requests = 0
        self.found_urls = list()

    def start(self):
        if self.config['HTTPMethod'] == "GET":
            self.start_fuzzer_get()
        elif self.config['HTTPMethod'] == "POST":
            self.start_fuzzer_post()
        elif self.config['HTTPMethod'] == "PUT":
            self.start_fuzzer_put()
       

    def generate_fuzzing_params(self, max_length: int = 100) ->str:
        characters = string.ascii_letters + string.digits
        string_length = random.randint(0, max_length)
        return ''.join(random.choice(characters) for _ in range(string_length))



    def fuzz(self, word, mode, fuzzed_string=None, json_string=None):
        if self.stop_event.is_set():
            return
        self.pause_event.wait()
        curr_dir = self.config['TargetURL']+"/"+word+"/"+fuzzed_string
        # www.google.com/akjlsdhf www.google.com/search/alkdsjfh
        if mode == "GET":
            response, status_code = send_get_request(curr_dir, 0, self.page_count, self.config['PageLimit'], "", self.config['Cookies'])
        elif mode =="POST":
            response, status_code = send_post_request(curr_dir, 0, json_string, self.page_count, self.config['PageLimit'], "", self.config['Cookies'])
        elif mode == "PUT":
            response, status_code = send_put_request(curr_dir, 0, json_string, self.page_count, self.config['PageLimit'], "", self.config['Cookies'])
        else:
            raise TypeError("Invalid mode")
        filtered = False
        if str(status_code) in self.config['HideStatusCode']:
            filtered = True

        if self.config['ShowOnlyStatusCode'] and str(status_code) not in self.config['ShowOnlyStatusCode']:
            filtered = True
        if status_code == "200" and curr_dir not in self.found_urls:
            self.found_urls.append(curr_dir)
        soupText = BeautifulSoup(response, "html.parser")
        text = soupText.get_text()
        if mode == "GET":
            payload = curr_dir
        else:
            payload = word + ": " + fuzzed_string
        node = {
            "status": str(status_code),
            "char": str(len(re.sub(r"\s+", "", text))),
            "word_count": str(len(re.findall(r'\b\w+\b',text))),
            "payload": payload,
            "filtered": str(filtered)
        }
        self.op_results[curr_dir] = node
        self.visited_urls.add(curr_dir)
        self.update_fuzzer_data(fuzzer_data=self.op_results)
        self.page_count+=1
        if self.page_count >= self.config['PageLimit']:
            return

    def start_fuzzer_get(self):
        fuzzed_string = self.generate_fuzzing_params()
        self.fuzz("", "GET", fuzzed_string)
        while self.page_count < self.config['PageLimit']:
            for word in self.config['WordList']:
                if self.page_count >= self.config['PageLimit']:
                    return
                if self.stop_event.is_set():
                    return
                fuzzed_string = self.generate_fuzzing_params()
                self.fuzz(word, "GET" , fuzzed_string)

    def start_fuzzer_put(self):
        while self.page_count < self.config['PageLimit']:
            for word in self.config['WordList']:
                if self.page_count >= self.config['PageLimit']:
                    return
                if self.stop_event.is_set():
                    return
                fuzzed_string = self.generate_fuzzing_params()
                json_string = json.dumps({word: fuzzed_string})
                self.fuzz(word, "PUT", fuzzed_string, json_string)


    def start_fuzzer_post(self):
        while self.page_count < self.config['PageLimit']:
            for word in self.config['WordList']:
                if self.page_count >= self.config['PageLimit']:  # Double check to prevent overflow
                    return
                if self.stop_event.is_set():
                    return
                fuzzed_string = self.generate_fuzzing_params()
                json_string = json.dumps({word: fuzzed_string})
                self.fuzz(word, "POST", fuzzed_string, json_string)

    def get_data(self):
        return self.op_results
    
    def get_links(self):
        return self.visited_urls
            
    def reset(self):
        self.config = None
        self.config = self.default_config
        self.op_results = {} #reset operation results
        self.visited_urls = set() #reset curr list of visited urls
        self.page_count = 0 #reset pages count

    def update_fuzzer_data(self, fuzzer_data):
        # Update fuzzer data and links in real-time
        create_or_update_and_link_fuzzer_results(project_id=self.projectID, results_id=str(uuid.uuid4()),
                                                  fuzz=fuzzer_data, fuzz_links=self.found_urls)
        self.progress = round(self.page_count / self.config['PageLimit'] * 100)

    def getProgress(self):
        return self.progress