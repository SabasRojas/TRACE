import json
import socket
import uuid
from typing import Dict, Any, Optional, Callable
import re
import time
from urllib.parse import urljoin, urlparse, urlunparse
import requests
from bs4 import BeautifulSoup

from models.DirectoryTreeCreator import DirectoryTreeCreator
from services.neo4j_service import create_or_update_and_link_crawler_results

class Crawler:
	MAX_LINKS_PER_PAGE = 1000
	config = dict()
	default_config = {
		"TargetURL": "www.example.com",
		"CrawlDepth": 10,
		"PageNumberLimit": int(20),
		"UserAgent": "",
		"RequestDelay": 1000,
		"FilterRelative": True
	}

	def __init__(self, config=None, http_client=None, projectID = None,  stop_event = None, pause_event = None):
		self.progress = 0
		if config is None:
			self.reset()
			return
		elif len(config) == 0:
			self.reset()
			return
		for key in self.default_config.keys():
			if key not in config:
				print(key + " is not configured")
				raise KeyError("Invalid config dictionary")
		try:
			self.config = {
				"TargetURL": config["TargetURL"],
				"CrawlDepth": int(config["CrawlDepth"]),
				"PageNumberLimit": int(config["PageNumberLimit"]),
				"UserAgent": config["UserAgent"],
				"RequestDelay": float(config["RequestDelay"]),
				"FilterRelative": config["FilterRelative"]
			}
		except ValueError as e:
			raise ValueError(f"Invalid config values: {e}")

		# Store raw responses as {path:response}
		self.op_results: Dict[str, Any] = {}
		# Track visited URLs to prevent duplicate crawling
		self.visited_urls = list()
		# Track how many pages have been crawled
		self.page_count = int(0)
		# Tree creator instance to handle the tree structure
		self.tree_creator = DirectoryTreeCreator()
		self.curr_depth = 0
		self.client = http_client
		self.projectID = projectID
		self.pause_event = pause_event
		self.stop_event = stop_event
		self.filter_relative = self.config['FilterRelative']
		print(self.filter_relative)
		if self.client is None:
			raise ValueError("HTTPClient instance required")


	def start_crawl(self):
		self.tree_creator.reset()
		curr_dir = self.config["TargetURL"]
		self.client.send_request(curr_dir,None, "GET", {'User-Agent': self.config['UserAgent']})
		response = self.client.receive_response()
		response_status = response.status_code
		links = self.get_valid_links(response.body, curr_dir)
		if len(links) == 0:
			return
		soupText = BeautifulSoup(response.body, "html.parser")
		text = soupText.get_text()
		try:
			ip_address = socket.gethostbyname(urlparse(curr_dir).hostname)
		except socket.gaierror:
			ip_address = "N/A"  # Handle cases where IP lookup fails
		parent_node = {
			"url": curr_dir,
			"ip": ip_address,
			"children": [],
			"char_count": len(re.sub(r"\s+", "", text)),
			"word_count": len(re.findall(r'\b\w+\b', text)),
			"links_found": len(links),
			"status_code": response_status
		}
		self.visited_urls.append(curr_dir)
		self.page_count = 1
		self.process_response(response.body, parent_node, curr_dir, depth_count=0)

	def process_response(self, response, parent_node, curr_dir, depth_count=0):
		if self.stop_event.is_set():
			return
		self.pause_event.wait()
		print(f"Depth: {depth_count}, URL: {curr_dir}")

		if depth_count >= self.config['CrawlDepth']:
			return
		if self.page_count >= self.config['PageNumberLimit']:
			return

		links = self.get_valid_links(response, curr_dir)
		for link in links:
			if self.stop_event.is_set():
				return
			if self.page_count >= self.config['PageNumberLimit']:
				print(f"Stopping: Page limit reached in loop for {curr_dir}")
				return
			print("current link", link)
			if link in self.visited_urls:
				print(f"Skipping: {link}")
				continue
			if link is None:
				return
			response, response_status = self.send_request(link)
			if not response:
				continue
			soupText = BeautifulSoup(response, "html.parser")
			text = soupText.get_text()
			try:
				ip_address = socket.gethostbyname(urlparse(link).hostname)
			except socket.gaierror:
				ip_address = "N/A"  # Handle cases where IP lookup fails
			node = {
				"url": link,
				"ip": ip_address,
				"children": [],
				"char_count": len(re.sub(r"\s+", "", text)),
				"word_count": len(re.findall(r'\b\w+\b', text)),
				"links_found": len(links),
				"status_code": response_status
			}
			if parent_node is not None:
				if node not in parent_node["children"]:
					parent_node["children"].append(node)
					parent = (
					parent_node["url"], parent_node["ip"], parent_node['char_count'], parent_node['word_count'],
					parent_node['links_found'], parent_node['status_code'])
					child = (node["url"], node["ip"], node['char_count'], node['word_count'],
							 node['links_found'], node['status_code'])

					if child not in self.tree_creator.tree.dir_tree.get(parent, []):
						self.tree_creator.add_edge(parent, child)

			self.process_response(response, node, link, depth_count + 1)

	def send_request(self, curr_dir):
		if self.page_count >= self.config['PageNumberLimit']:
			return None, None
		time.sleep(self.config['RequestDelay'] / 1000)
		try:
			self.client.send_request(curr_dir, None, "GET", {'User-Agent': self.config['UserAgent']})
			req = self.client.receive_response()
			if req.status_code == 200:
				print(f"Currently crawling: {curr_dir}")
				self.op_results[curr_dir] = req.body
				self.visited_urls.append(curr_dir)
				self.page_count += 1
				if self.tree_creator.tree.root is not None:
					self.update_crawler_data(self.tree_creator.get_tree_map(self.tree_creator.tree.root))
				return req.body, req.status_code
			else:
				print(f"[ERROR] Failed to access {curr_dir}: {req.status_code}")
		except Exception as e:
			print(f"[ERROR] Connection error: {e}")
		return None,None

	def get_valid_links(self, response: str, curr_dir):
		soup = BeautifulSoup(response, 'html.parser')
		links = [a.get('href') for a in soup.find_all('a', href=True)]
		links = links[:self.MAX_LINKS_PER_PAGE]
		if self.filter_relative:
			links = [link for link in links if not link.startswith("#")]
		valid_links = []
		for link in links:
			parsed = urlparse(link)
			if parsed.scheme in ["http", "https"]:
				valid_links.append(link)
			elif parsed.scheme == "":
				valid_links.append(urljoin(curr_dir, link))
		return valid_links

	def normalize_url(self, url):
		try:
			parts = urlparse(url)
			# Lowercase scheme and netloc, remove fragment, ensure path starts with /
			path = parts.path if parts.path else '/'
			# Remove trailing slash from path if it's not the root
			if len(path) > 1 and path.endswith('/'):
				path = path[:-1]
			# Reconstruct, ignoring params, query, fragment for visited check
			# You might want to keep query/params depending on crawl needs
			normalized = urlunparse((
				parts.scheme.lower(),
				parts.netloc.lower(),
				path,
				'',  # params - remove?
				'',  # query - remove?
				''  # fragment - always remove
			))
			return normalized
		except Exception:  # Handle potential parsing errors
			return url  # Return original if parsing fails

	def update_crawler_data(self, crawler_data):
		# Update crawler data and links in real-time
		create_or_update_and_link_crawler_results(project_id=self.projectID, results_id=str(uuid.uuid4()),crawl=crawler_data, crawler_links=self.visited_urls)
		self.progress = round(self.page_count / self.config['PageNumberLimit'] * 100)
		print(f"Updated crawler data:")

	def getConfig(self):
		if self.config is None:
			self.reset()
			raise ValueError("Config cannot be None, resetting to default")
		elif len(self.config) == 0:
			self.reset()
			raise ValueError("Config cannot be an empty list, resetting to default")
		elif self.config is not None:
			return self.config

	def setConfig(self, config):
		if config is None:
			self.reset()
			raise ValueError("Config cannot be None, resetting to default")
		elif len(config) == 0:
			self.reset()
			raise ValueError("Config cannot be an empty list, resetting to default")
		elif config is not None:
			self.config = config

	def reset(self):
		self.config = None
		self.config = self.default_config
		self.op_results = {}  # reset operation results
		self.visited_urls = set()  # reset curr list of visited urls
		self.page_count = 0  # reset pages count
		self.tree_creator = DirectoryTreeCreator()  # reset tree

	def getCrawlResults(self) -> list[str]:
		# Return a list of URLs that have been crawled
		# Sample usage (urls = crawler.getCrawlResults())
		return list(self.op_results.keys())

	def getTree(self):
		return self.visited_urls

	def getDefaultConfig(self):
		return self.default_config

	def getProgress(self):
		return self.progress

