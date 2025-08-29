from neo4j import GraphDatabase
from pydantic import BaseModel
from typing import List, Tuple, Optional, Dict
from datetime import date
import json

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"  # Change this to your actual password

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

class Project(BaseModel):
    id: str
    name: str
    owner: str
    isLocked: bool = False
    files: List[str] = []
    IPList: List[Tuple[str, int]] = []

class ProjectManager(BaseModel):
    name: str
    owner: str
    IPList: List[Tuple[str, int]]
    dateRange: Optional[Tuple[date, date]] = None
    locked: bool = False

class BruteForceResults(BaseModel):
    id: str
    bruteForceResults: Dict[str, Dict[str, str]]

class CrawlerResults(BaseModel):
    id: str
    crawlerResults: list

class FuzzerResults(BaseModel):
    id: str
    fuzzerResults: Dict[str, Dict[str, str]]

class Credentials(BaseModel):
    id: str
    credentials: list

# def get_results_by_project_id(project_id: str) -> results:
#     with driver.session() as session:
#         result = session.run("""
#             MATCH (p:Project {id: $project_id})-[:HAS_RESULTS]->(r:Results)
#             RETURN r.crawlerResults AS crawlerResults, r.bruteForceResults AS bruteForceResults, r.fuzzerResults AS fuzzerResults
#         """, project_id=project_id)
#         record = result.single()
#         if not record:
#             raise Exception("No results found for the given project ID")
#         return results(
#             crawlerResults=record["crawlerResults"],
#             bruteForceResults=record["bruteForceResults"],
#             fuzzerResults=record["fuzzerResults"]
#         )

# TODO: Modify neo4j methods for fuzzer and bruteforcer to match the crawler.


def get_fuzzer_results_by_project_id(project_id: str) -> FuzzerResults:
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Project {id: $project_id})-[:HAS_RESULTS]->(r:Results)
            WHERE r.fuzzerResults IS NOT NULL
            RETURN r.fuzzerResults AS fuzzerResults
            ORDER BY r.timestamp DESC
            LIMIT 1
        """, project_id=project_id)

        record = result.single()
        if not record or not record["fuzzerResults"]:
            raise Exception("No fuzzer results found for the given project ID")

        return FuzzerResults(
            id=project_id,
            fuzzerResults=json.loads(record["fuzzerResults"])
        )


def get_brute_force_results_by_project_id(project_id: str) -> BruteForceResults:
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Project {id: $project_id})-[:HAS_RESULTS]->(r:Results)
            WHERE r.bruteForceResults IS NOT NULL
            RETURN r.bruteForceResults AS bruteForceResults
            ORDER BY r.timestamp DESC
            LIMIT 1
        """, project_id=project_id)

        record = result.single()
        if not record or not record["bruteForceResults"]:
            raise Exception("No brute force results found for the given project ID")

        return BruteForceResults(
            id=project_id,
            bruteForceResults=json.loads(record["bruteForceResults"])
        )


class ResultsNotFoundError(Exception):
    pass


def get_crawler_results_by_project_id(project_id: str) -> CrawlerResults:
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Project {id: $project_id})-[:HAS_RESULTS]->(r:Results)
            WHERE r.crawlerResults IS NOT NULL
            RETURN r.crawlerResults AS crawlerResults
            ORDER BY r.timestamp DESC
            LIMIT 1
        """, project_id=project_id)

        record = result.single()
        if not record or not record["crawlerResults"]:
            raise ResultsNotFoundError(f"No crawler results found for project ID: {project_id}")

        try:
            # Parse the JSON string before returning
            parsed_results = json.loads(record["crawlerResults"])
            return parsed_results
        except json.JSONDecodeError as e:
            # Handle cases where the stored string is not valid JSON
            print(f"Error decoding JSON for project {project_id}: {e}")  # Log the error
            raise json.JSONDecodeError(f"Failed to parse stored crawler results for project {project_id}.", e.doc,
                                       e.pos) from e

def get_credentials_by_project_id(project_id: str) -> Credentials:
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Project {id: $project_id})-[:HAS_RESULTS]->(r:Results)
            WHERE r.credentials IS NOT NULL
            RETURN r.credentials AS credentials
            ORDER BY r.timestamp DESC
            LIMIT 1
        """, project_id=project_id)

        record = result.single()
        if not record or not record["credentials"]:
            raise ResultsNotFoundError(f"No credentials results found for project ID: {project_id}")

        try:
            # Parse the JSON string before returning
            parsed_results = json.loads(record["credentials"])
            return parsed_results
        except json.JSONDecodeError as e:
            # Handle cases where the stored string is not valid JSON
            print(f"Error decoding JSON for project {project_id}: {e}")  # Log the error
            raise json.JSONDecodeError(f"Failed to parse stored credentials for project {project_id}.", e.doc,
                                       e.pos) from e


def get_crawler_links_by_project_id(project_id: str) -> CrawlerResults:
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Project {id: $project_id})-[:HAS_RESULTS]->(r:Results)
            WHERE r.crawlerLinks IS NOT NULL
            RETURN r.crawlerLinks AS crawlerLinks
            ORDER BY r.timestamp DESC
            LIMIT 1
        """, project_id=project_id)

        record = result.single()
        if not record or not record["crawlerLinks"]:
            raise ResultsNotFoundError(f"No crawler links found for project ID: {project_id}")

        try:
            # Parse the JSON string before returning
            parsed_results = json.loads(record["crawlerLinks"])
            return parsed_results
        except json.JSONDecodeError as e:
            # Handle cases where the stored string is not valid JSON
            print(f"Error decoding JSON for project {project_id}: {e}")  # Log the error
            raise json.JSONDecodeError(f"Failed to parse stored crawler links for project {project_id}.", e.doc,
                                       e.pos) from e

def get_brute_force_links_by_project_id(project_id: str):
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Project {id: $project_id})-[:HAS_RESULTS]->(r:Results)
            WHERE r.bruteForceLinks IS NOT NULL
            RETURN r.bruteForceLinks AS bruteForceLinks
            ORDER BY r.timestamp DESC
            LIMIT 1
        """, project_id=project_id)

        record = result.single()
        if not record or not record["bruteForceLinks"]:
            raise ResultsNotFoundError(f"No crawler links found for project ID: {project_id}")

        try:
            # Parse the JSON string before returning
            parsed_results = json.loads(record["bruteForceLinks"])
            return parsed_results
        except json.JSONDecodeError as e:
            # Handle cases where the stored string is not valid JSON
            print(f"Error decoding JSON for project {project_id}: {e}")  # Log the error
            raise json.JSONDecodeError(f"Failed to parse stored bruteforcer links for project {project_id}.", e.doc,
                                       e.pos) from e

def get_fuzzer_links_by_project_id(project_id: str):
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Project {id: $project_id})-[:HAS_RESULTS]->(r:Results)
            WHERE r.fuzzerLinks IS NOT NULL
            RETURN r.fuzzerLinks AS fuzzerLinks
            ORDER BY r.timestamp DESC
            LIMIT 1
        """, project_id=project_id)

        record = result.single()
        if not record or not record["fuzzerLinks"]:
            raise ResultsNotFoundError(f"No crawler links found for project ID: {project_id}")

        try:
            # Parse the JSON string before returning
            parsed_results = json.loads(record["fuzzerLinks"])
            return parsed_results
        except json.JSONDecodeError as e:
            # Handle cases where the stored string is not valid JSON
            print(f"Error decoding JSON for project {project_id}: {e}")  # Log the error
            raise json.JSONDecodeError(f"Failed to parse stored fuzzer links for project {project_id}.", e.doc,
                                       e.pos) from e

import json
def create_or_update_and_link_fuzzer_results(project_id: str, results_id: str, fuzz: list, fuzz_links: list):
    with driver.session() as session:
        session.run("""
               MATCH (p:Project {id: $project_id})
               MERGE (p)-[r:HAS_RESULTS]->(res:Results)
               ON CREATE SET
                   res.id = $results_id,
                   res.fuzzerResults = $fuzzerResults,
                   res.fuzzerLinks = $fuzzerLinks,
                   res.timestamp = datetime()
               ON MATCH SET
                   res.fuzzerResults = $fuzzerResults,
                   res.fuzzerLinks = $fuzzerLinks,
                   res.timestamp = datetime()
               RETURN res
           """, project_id=project_id,
                    results_id=results_id,
                    fuzzerResults=json.dumps(fuzz), fuzzerLinks=json.dumps(fuzz_links))

def create_or_update_and_link_brute_force_results(project_id: str, results_id: str, brute: list, bruteForce_links:list):
    with driver.session() as session:
        session.run("""
               MATCH (p:Project {id: $project_id})
               MERGE (p)-[r:HAS_RESULTS]->(res:Results)
               ON CREATE SET
                   res.id = $results_id,
                   res.bruteForceResults = $brute,
                   res.bruteForceLinks = $bruteForce_links,
                   res.timestamp = datetime()
               ON MATCH SET
                   res.bruteForceResults = $brute,
                   res.bruteForceLinks = $bruteForce_links,
                   res.timestamp = datetime()
               RETURN res
           """, project_id=project_id,
                    results_id=results_id,
                    brute=json.dumps(brute), bruteForce_links=json.dumps(bruteForce_links) )

def create_or_update_and_link_crawler_results(project_id: str, results_id: str, crawl: list, crawler_links: list):
    with driver.session() as session:
        session.run("""
            MATCH (p:Project {id: $project_id})
            MERGE (p)-[r:HAS_RESULTS]->(res:Results)
            ON CREATE SET
                res.id = $results_id,
                res.crawlerResults = $crawl,
                res.crawlerLinks = $crawler_links,
                res.timestamp = datetime()
            ON MATCH SET
                res.crawlerResults = $crawl,
                res.crawlerLinks = $crawler_links,
                res.timestamp = datetime()
            RETURN res
        """, project_id=project_id,
             results_id=results_id,
             crawl=json.dumps(crawl),
                    crawler_links=json.dumps(crawler_links),)

def create_or_update_and_link_credentials(project_id: str, results_id: str, credentials:list):
    with driver.session() as session:
        session.run("""
            MATCH (p:Project {id: $project_id})
            MERGE (p)-[r:HAS_RESULTS]->(res:Results)
            ON CREATE SET
                res.id = $results_id,
                res.credentials = $credentials,
                res.timestamp = datetime()
            ON MATCH SET
                res.credentials = $credentials,
                res.timestamp = datetime()
            RETURN res
        """, project_id=project_id,
             results_id=results_id,
             credentials=json.dumps(credentials))

    
def get_all_projects():
    with driver.session() as session:
        result = session.run("MATCH (p:Project) RETURN p")
        projects = []
        for record in result:
            node = record["p"]
            iplist_raw = node.get("IPList", "[]")
            try:
                iplist = json.loads(iplist_raw) if isinstance(iplist_raw, str) else iplist_raw
            except Exception:
                iplist = []
            projects.append({
                "id": node["id"],
                "name": node["name"],
                "owner": node["owner"],
                "isLocked": node.get("isLocked", False),
                "files": node.get("files", []),
                "IPList": iplist
            })
        return projects

def get_user_by_initials(initials: str):
    with driver.session() as session:
        result = session.run("MATCH (u:User {name: $name}) RETURN u", name=initials)
        record = result.single()
        if record:
            user_node = record["u"]
            return {
                "id": user_node["id"],
                "name": user_node["name"],
                "role": user_node.get("role", "analyst")
            }
        return None  # clearly return None if not found


def create_user_node(initials: str, role: str) -> int:
    with driver.session() as session:
        result = session.run("MATCH (u:User) RETURN COALESCE(MAX(u.id), 0) + 1 AS newId")
        new_id = result.single()["newId"]

        session.run(
            "CREATE (u:User {id: $id, name: $name, role: $role})",
            id=new_id, name=initials, role=role
        )
        return new_id


def verify_user(user_id: int, name: str):
    with driver.session() as session:
        result = session.run("MATCH (u:User {id: $id, name: $name}) RETURN u", id=user_id, name=name)
        return result.single() is not None

def create_project_node(project: Project):
    with driver.session() as session:
        # Convert IPList from tuples to lists, then JSON stringify
        json_iplist = json.dumps([list(item) for item in project.IPList])
        
        session.run("""
            MERGE (p:Project {id: $id})
            SET p.name = $name,
                p.owner = $owner,
                p.isLocked = $isLocked,
                p.files = $files,
                p.IPList = $iplist
        """, 
        id=project.id,
        name=project.name,
        owner=project.owner,
        isLocked=project.isLocked,
        files=project.files,
        iplist=json_iplist)

def create_project_manager_node(pm: ProjectManager):
    with driver.session() as session:
        session.run("""
            MERGE (pm:ProjectManager {name: $name})
            SET pm.owner = $owner,
                pm.IPList = $IPList,
                pm.dateRange = $dateRange,
                pm.locked = $locked
        """, name=pm.name,
             owner=pm.owner,
             IPList=json.dumps(pm.IPList),
             dateRange=str(pm.dateRange),
             locked=pm.locked)

def link_owner_to_project(initials: str, project_id: str):
    with driver.session() as session:
        session.run("""
            MATCH (u:User {name: $initials}), (p:Project {id: $project_id})
            MERGE (u)-[:OWNS]->(p)
        """, initials=initials, project_id=project_id)

def get_project_node(project_id: str):
    with driver.session() as session:
        result = session.run("MATCH (p:Project {id: $id}) RETURN p", id=project_id)
        record = result.single()
        if not record:
            raise Exception("Project not found")
        node = record["p"]
        iplist_raw = node.get("IPList", "[]")
        try:
            iplist = json.loads(iplist_raw) if isinstance(iplist_raw, str) else iplist_raw
        except Exception:
            iplist = []
        return {
            "id": node["id"],
            "name": node["name"],
            "owner": node["owner"],
            "isLocked": node.get("isLocked", False),
            "files": node.get("files", []),
            "IPList": iplist
        }

def get_project_owner_node(project_id: str):
    with driver.session() as session:
        result = session.run("""
            MATCH (u:User)-[:OWNS]->(p:Project {id: $project_id})
            RETURN u
        """, project_id=project_id)
        record = result.single()
        if not record:
            raise Exception("Owner not found")
        node = record["u"]
        return {"id": node["id"], "name": node["name"]}

def update_project_owner(project_id: str, new_owner: str):
    with driver.session() as session:
        session.run("MATCH (p:Project {id: $id}) SET p.owner = $new_owner", id=project_id, new_owner=new_owner)

def update_project_id(old_id: str, new_id: str):
    with driver.session() as session:
        session.run("MATCH (p:Project {id: $old_id}) SET p.id = $new_id", old_id=old_id, new_id=new_id)

def update_project_lock(project_id: str, lock: bool):
    with driver.session() as session:
        session.run("""
            MATCH (p:Project {id: $id})
            SET p.isLocked = $lock
        """, id=project_id, lock=lock)

def link_user_access_to_project(user_id: int, project_id: str):
    with driver.session() as session:
        session.run("""
            MERGE (u:User {id: $user_id})
            MERGE (p:Project {id: $project_id})
            MERGE (u)-[:ACCESSED]->(p)
        """, user_id=user_id, project_id=project_id)

def get_all_users():
    with driver.session() as session:
        result = session.run("MATCH (u:User) RETURN u")
        return [
            {
                "id": record["u"]["id"],
                "name": record["u"]["name"]
            }
            for record in result
        ]
    
def delete_project_node(project_id: str):
    with driver.session() as session:
        session.run("MATCH (p:Project {id: $id}) DETACH DELETE p", id=project_id)

def delete_project_and_results(project_id: str):
    with driver.session() as session:
        session.run("""
            MATCH (p:Project {id: $id})<-[:BELONGS_TO]-(r:Results)
            DETACH DELETE p, r
        """, id=project_id)

def user_owns_project(user_id: int, project_id: str) -> bool:
    with driver.session() as session:
        result = session.run("""
            MATCH (u:User {id: $user_id})-[:OWNS]->(p:Project {id: $project_id})
            RETURN COUNT(p) > 0 AS owns
        """, user_id=user_id, project_id=project_id)
        record = result.single()
        return record and record["owns"]

def get_recently_accessed_projects(user_id: int):
    with driver.session() as session:
        result = session.run("""
            MATCH (u:User {id: $user_id})-[:ACCESSED]->(p:Project)
            RETURN p.id AS id, p.name AS name
            ORDER BY p.name
            LIMIT 5
        """, user_id=user_id)
        return [{"id": record["id"], "name": record["name"]} for record in result]
    
def log_user_project_access(user_id: int, project_id: str):
    with driver.session() as session:
        session.run("""
            MATCH (u:User {id: $user_id}), (p:Project {id: $project_id})
            MERGE (u)-[:ACCESSED]->(p)
        """, user_id=user_id, project_id=project_id)


def user_is_project_owner(initials: str, project_id: str) -> bool:
    with driver.session() as session:
        result = session.run("""
            MATCH (u:User {name: $initials})-[:OWNS]->(p:Project {id: $project_id})
            RETURN COUNT(p) > 0 AS isOwner
        """, initials=initials, project_id=project_id)
        record = result.single()
        return record and record["isOwner"]

def join_project(project_id: str, user_id: int):
    """
    Creates a relationship between an existing User and Project:
      (u:User {id:user_id})-[:ON_PROJECT]->(p:Project {id:project_id})
    """
    with driver.session() as session:
        session.run(
            """
            MATCH (u:User {id: $user_id}), (p:Project {id: $project_id})
            MERGE (u)-[:ON_PROJECT]->(p)
            """,
            user_id=user_id,
            project_id=project_id,
        )

def get_joined_projects_for_user(user_id: int) -> List[dict]:
    """
    Returns all projects that the given user has joined
    (i.e. (u:User)-[:ON_PROJECT]->(p:Project)).
    """
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $user_id})-[:ON_PROJECT]->(p:Project)
            RETURN p.id AS id, p.name AS name
            """,
            user_id=user_id
        )
        return [{"id": record["id"], "name": record["name"]} for record in result]


def get_project_members(project_id: str) -> List[dict]:
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User)-[:ON_PROJECT]->(p:Project {id:$project_id})
            RETURN u.id AS id, u.name AS name, u.role AS role
            """,
            project_id=project_id
        )
        return [{
            "id": r["id"],
            "name": r["name"],
            "role": r["role"]
        } for r in result]

def remove_project_member(project_id: str, user_initials: str):
    with driver.session() as session:
        session.run(
            """
            MATCH (u:User {name:$initials})-[r:ON_PROJECT]->(p:Project {id:$project_id})
            DELETE r
            """,
            initials=user_initials,
            project_id=project_id
        )
def get_or_create_user(initials: str, role: str):
    with driver.session() as session:
        # Check if user already exists
        result = session.run(
            "MATCH (u:User {name: $initials}) RETURN u",
            initials=initials
        )
        record = result.single()

        if record:
            user = record["u"]
            return {
                "id": user["id"],
                "name": user["name"],
                "role": user["role"]
            }

        # Generate new user ID
        result = session.run("MATCH (u:User) RETURN MAX(u.id) AS maxId")
        max_id = result.single()["maxId"] or 0
        new_id = max_id + 1

        # Create user
        session.run(
            "CREATE (u:User {id: $id, name: $name, role: $role})",
            id=new_id, name=initials, role=role
        )
        return {
            "id": new_id,
            "name": initials,
            "role": role
        }