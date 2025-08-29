import random
import re
from collections import defaultdict
import numpy as np
from typing import Dict, List, Tuple, Set
import csv


csv.field_size_limit(10**6)
import os
import time
import requests
import unicodedata #added myself
from bs4 import BeautifulSoup
#Natural Language Processing routine that cleans CSV text 
def nlp_subroutine(csv_path: str, characters=True, numbers=True, symbols=True):
    stopwords = {
        "the", "this", "that", "these", "those",  
        "each", "every", "either", "neither",     
        "which", "what", "whose", "who", "whom"
    }
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    cleaned_rows = []
    with open(csv_path, "r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        if not fieldnames or not {"id", "content", "url"}.issubset(fieldnames):
            raise ValueError("CSV must contain columns: id, content, url")
        for row in reader:
            text = row["content"] if row["content"] else ""
            #Start of edit for separating hyphens
            text = unicodedata.normalize("NFKC", text)
            text = re.sub(r"(\w+)-(\w+)", r"\1, \2", text) # example: "miki-silva" becomes "miki, silva"
            words = re.findall(r"\w+", text, flags=re.IGNORECASE) # example: "Hello! I'm Miki" gives ["Hello", "I", "m", "Miki"]

            ascii_words = []
            for word in words:
                try:
                    word.encode('ascii')
                    ascii_words.append(word)
                except UnicodeEncodeError:
                    pass # Skip word if it contains non-ASCII characters
            words = ascii_words
            filtered_words = [
                word for word in words
                if word.lower() not in stopwords
                and (len(word) >= 4 or word.isupper())
                # NOTE removed since filters are only either for username or for password generators
                # and (  # filter whatever the users chooses as well
                #     (characters and word.isalpha())
                #     or (numbers and word.isdigit())
                #     or (symbols and not word.isalnum())
                # ) ^^^^This is no longer necessary^^^^
            ]
            # for word in filtered_words:
            #     print(word)
            # exit(0)
            cleaned_text = " ".join(filtered_words)
            row["content"] = cleaned_text
            cleaned_rows.append(row)
    #Overwrite original CSV with cleaned text
    with open(csv_path, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_rows)
    print(f"Cleaned CSV '{csv_path}' file has been generated.")

#Load URLs from a CSV file with columns 'id' and 'website'.
def load_urls_from_csv(csv_path: str) -> List[str]:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    try:
        urls = []
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            if not {'id', 'website'}.issubset(set(reader.fieldnames or [])):
                raise ValueError("CSV must contain columns: id, website")
            for row in reader:
                if row['website']:
                    urls.append(row['website'].strip())
        return urls
    except csv.Error as e:
        raise ValueError(f"Error reading CSV file: {e}")

#Web scraper functions and will pull something out of the URLs provided.
class WebScraper:
    # Initialize with list of URLs
    def __init__(self, urls):
        self.urls = urls

    # Scrape text content from web pages
    def scrape_pages(self):
        results = []
        for i, url in enumerate(self.urls, 1):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                # Extract text from p, h1, h2, h3, and span tags
                text = ' '.join([tag.get_text() for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'span'])])
                results.append((i, text, url))
                time.sleep(1)  # Be polite to servers
            except Exception as e:
                print(f"Error scraping {url}: {e}")
        return results

    # Generate CSV file with scraped data
    def generate_csv(self, filename):
        data = self.scrape_pages()
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['id', 'content', 'url'])  # Header
            csv_writer.writerows(data)
        print(f"CSV file '{filename}' has been generated.")
        
# Load web text from a CSV file
def load_web_text(csv_path: str) -> str:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            if not {'id', 'content', 'url'}.issubset(set(reader.fieldnames or [])):
                raise ValueError("CSV must contain columns: id, content, url")
            contents = []
            for row in reader:
                if row['content']:
                    contents.append(row['content'].lower())
        return " ".join(contents)
    except csv.Error as e:
        raise ValueError(f"Error reading CSV file: {e}")

# Load wordlist from a file
def load_wordlist(file_path: str) -> List[str]:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Wordlist file not found: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            words = [line.strip().lower() for line in file if line.strip()]
        return words
    except Exception as e:
        raise ValueError(f"Error reading wordlist file: {e}")
#TODO: mess with numbers here
# Class for managing the Markov Decision Process for generating credentials 
# #defaults are in another file
class CredentialMDP:
    def __init__(self, order: int = 2, gamma: float = 0.8): #modify gamma and maybe order to increase password length
        self.order = order
        self.gamma = gamma
        self.q_values: Dict[str, Dict[Tuple[str, str], float]] = defaultdict(lambda: defaultdict(float))
        self.state_transitions: Dict[str, Dict[str, Set[str]]] = defaultdict(lambda: defaultdict(set))
        self.used_usernames: Set[str] = set()
        self.epsilon = 0.8 #mess with this #this is what influences the greedy algorithm in choosing actions
        self.learning_rate = 0.15 #mess with this #this is how small a step is taken in each iteration, usually the smaller the better but this can lead to some rediculous runtimes
        self.initial_states: List[str] = []

    # Calculate the strength of a password
    def calculate_password_strength(self, password: str) -> float:
        score = 0.0
        if len(password) >= 12:
            score += 0.3 #weight for length
        if re.search(r'[A-Z]', password):
            score += 0.2 #weight for characters
        if re.search(r'[0-9]', password):
            score += 0.2 #weight for integers
        if re.search(r'[!@#$%^&*]', password):
            score += 0.2 #weight for special characters
        if len(set(password)) >= 8:
            score += 0.1
        return score

    # Calculate the quality of a username
    def calculate_username_quality(self, username: str) -> float:
        score = 0.0
        if len(username) >= 6:
            score += 0.3 #weight for password length
        if username not in self.used_usernames:
            score += 0.4 #weight for uniqueness
        if re.match(r'^[a-z]', username):
            score += 0.2 #weight for starting with lowercase
        if not re.search(r'\s', username):
            score += 0.1 #weight for no spaces
        if re.match(r'^\d', username):
            score -= 0.5  # Strong penalty for starting with a number
        return score

    # Get the reward for a state-action pair
    def get_reward(self, state: str, action: str, next_char: str) -> float:
        if 'username' in state:#before this we could also introduce a unique state for special symbols BUT I think it's messy/low priority
            current = state[9:] + next_char
            return self.calculate_username_quality(current) / len(current)
        else:
            current = state[9:] + next_char #we could implement a reward for special characters here
            return self.calculate_password_strength(current) / len(current)

    # Get possible actions for a state
    def get_possible_actions(self, state: str) -> List[str]:
        return list(self.state_transitions[state].keys())

    # Choose an action based on epsilon-greedy strategy
    def choose_action(self, state: str) -> Tuple[str, str]:
        possible_actions = self.get_possible_actions(state)
        if not possible_actions:
            return "", ""

        if random.random() < self.epsilon:
            action = random.choice(possible_actions)
            next_char = random.choice(list(self.state_transitions[state][action]))
        else:
            # Choose best action based on Q-values
            action_values = {}
            for act in possible_actions:
                if self.state_transitions[state][act]:
                    value = max([self.q_values[state][(act, nxt_ch)] for nxt_ch in self.state_transitions[state][act]])
                    action_values[act] = value

            if action_values:
                action = max(action_values.items(), key=lambda x: x[1])[0]
                next_char = random.choice(list(self.state_transitions[state][action]))
            else:
                action = random.choice(possible_actions)
                next_char = random.choice(list(self.state_transitions[state][action]))

        return action, next_char

    # Update Q-value based on the Bellman equation
    def update_q_value(self, state: str, action: str, next_char: str, next_state: str, reward: float):
        next_action_values = []
        for next_action in self.get_possible_actions(next_state):
            for next_next_char in self.state_transitions[next_state][next_action]:
                next_action_values.append(self.q_values[next_state][(next_action, next_next_char)])

        max_next_q = max(next_action_values, default=0)
        current_q = self.q_values[state][(action, next_char)]
        new_q = current_q + self.learning_rate * (reward + self.gamma * max_next_q - current_q)
        self.q_values[state][(action, next_char)] = new_q

# Class for generating credentials using Markov Decision Process
class CredentialGeneratorMDP:

    # constructor(self, csv_path, wordlist_path, user_settings, pw_settings)
    def __init__(self, csv_path: str, wordlist: list, config: dict):
        try:
            self.web_text = load_web_text(csv_path)
            self.wordlists = wordlist
            # passchars: bool
            # userchars: bool
            # passnums: bool
            # usernums: bool
            # passsyms: bool
            # usersyms: bool
            #
            # # set the length of the credentials to output
            # userlen: int
            # passle: int
            # credentialAmount: int
            # wordlist: list
            # pw settings:
            self.pw_chars = config['passchars']
            self.pw_nums = config['passnums']
            self.pw_symbols = config['passsyms']
            # username settings:
            self.user_chars = config['userchars']
            self.user_nums = config['usernums']
            self.user_symbols = config['usersyms']

            # self.wordlists = self.apply_filters(self.wordlists)  # NOTE removed this since now filters are separate for user and pw
            # For viewing purposes only
            # print(self.wordlists)
            # print(self.web_text)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error loading input files: {e}")
            self.web_text = csv_path
            self.wordlists = wordlist
        self.username_mdp = CredentialMDP(order=2)
        self.password_mdp = CredentialMDP(order=3)
        self.min_username_length = config['userlen']
        self.min_password_length = config['passle']
        self.progress = 0

    # Preprocess text data
    def preprocess_text(self, text: str) -> List[str]:
        words = re.findall(r'\w+', text.lower())
        return [word for word in words if len(word) >= 4]

    # Build state transitions for username and password generation
    def build_state_transitions(self):
        username_data = set(self.preprocess_text(self.web_text) + self.wordlists)
        username_data = set(self.apply_filters(list(username_data), alphabetical=self.user_chars, numerical=self.user_nums, special=self.user_symbols))
        password_data = set(word for word in username_data if len(word) >= 8)
        password_data = set(self.apply_filters(list(password_data), alphabetical=self.pw_chars, numerical=self.pw_nums, special=self.pw_symbols))

        for word in username_data:
            for i in range(len(word) - self.username_mdp.order):
                state = f"username_{word[i:i+self.username_mdp.order]}"
                action = word[i+self.username_mdp.order]
                next_char = word[i+self.username_mdp.order]
                self.username_mdp.state_transitions[state][action].add(next_char)
                if i == 0:
                    self.username_mdp.initial_states.append(state)

        for word in password_data:
            for i in range(len(word) - self.password_mdp.order):
                state = f"password_{word[i:i+self.password_mdp.order]}"
                action = word[i+self.password_mdp.order]
                next_char = word[i+self.password_mdp.order]
                self.password_mdp.state_transitions[state][action].add(next_char)
                if i == 0:
                    self.password_mdp.initial_states.append(state)

    def apply_filters(self, text_list: list, alphabetical: bool = True, numerical: bool = True, special: bool = True) -> list: # TODO maybe change here (As far as I can tell, we don't need this function at all)
        filtered_list = []
        for text in text_list:
            filtered_text = ""
            for char in text:
                include = True
                # TODO change here
                if not alphabetical and char.isalpha():
                    include = False
                if not numerical and char.isdigit():
                    include = False
                if not special and not char.isalnum():
                    include = False
                if include:
                    filtered_text += char
            filtered_list.append(filtered_text)
        return filtered_list


    # Generate a username and password pair
    def generate_credential(self) -> Tuple[str, str]:
        # Generate username
        if not self.username_mdp.initial_states:
            state = f"username_{random.choice(self.wordlists)[:2]}"
        else:
            state = random.choice(self.username_mdp.initial_states)

        username = state[9:]
        while len(username) < self.min_username_length:
            action, next_char = self.username_mdp.choose_action(state)
            if not action or not next_char:
                break
            username += next_char
            next_state = f"username_{username[-self.username_mdp.order:]}"
            reward = self.username_mdp.get_reward(state, action, next_char)
            self.username_mdp.update_q_value(state, action, next_char, next_state, reward)
            state = next_state

        if self.user_nums:
            username = f"{username}{random.randint(1, 999)}"
        self.username_mdp.used_usernames.add(username)

        # Generate password
        if not self.password_mdp.initial_states:
            state = f"password_{random.choice(self.wordlists)[:3]}"
        else:
            state = random.choice(self.password_mdp.initial_states)

        password = state[9:]
        while len(password) < self.min_password_length:
            action, next_char = self.password_mdp.choose_action(state)
            if not action or not next_char:
                break
            password += next_char
            next_state = f"password_{password[-self.password_mdp.order:]}"
            reward = self.password_mdp.get_reward(state, action, next_char)
            self.password_mdp.update_q_value(state, action, next_char, next_state, reward)
            state = next_state

        # if username or password does not meet min length requirement at this point, add random characters:

        # apply filters here
        alphabetic = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        numerical = '0123456789'
        special = "!@#$%^&*()_+-=[]}{|<>?/"

        character_types = []

        if self.user_chars:
            character_types.append(alphabetic)

        if self.user_nums:
            character_types.append(numerical)

        if self.user_symbols:
            character_types.append(special)

        if not character_types:
            raise ValueError(f"Invalid call to 'generate_credential()' (no filters were selected)")

        while len(username) < self.min_username_length:
            char_type = random.choice(character_types)
            char_selection = random.choice(char_type)
            username += char_selection
        
        character_types = []

        if self.pw_chars:
            character_types.append(alphabetic)

        if self.pw_nums:
            character_types.append(numerical)

        if self.pw_symbols:
            character_types.append(special)

        if not character_types:
            raise ValueError(f"Invalid call to 'generate_credential()' (no filters were selected)")

        while len(password) < self.min_password_length:
            char_type = random.choice(character_types)
            char_selection = random.choice(char_type)
            password += char_selection

        password = self.enhance_password(password)  # might increase password length, but this is okay
        return username, password

    # Enhance the generated password
    def enhance_password(self, password: str) -> str:
        enhanced = list(password)
        if self.pw_chars:
            letter_inserts = random.randint(1,4)
            letter_indices = [i for i, char in enumerate(enhanced) if char.isalpha()]
            num_of_cases = random.randint(1, min(3, len(letter_indices)))
            indices_sample = random.sample(letter_indices,num_of_cases)
            for i in indices_sample:
                if enhanced[i].islower():
                    enhanced[i] = enhanced[i].upper()
                else:
                    enhanced[i] = enhanced[i].lower()
            if letter_indices and not any(enhanced[i].isupper for i in letter_indices):
                randomindex = random.choice(letter_indices)
                enhanced[randomindex] = enhanced[randomindex].upper()
            for _ in range(letter_inserts):
                letter = random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
                insert_pos = random.randint(0,len(enhanced))
                enhanced.insert(insert_pos,letter)
        
        if self.pw_nums:
            insert_numbers = random.randint(1,4)
            for _ in range(insert_numbers):
                digit = str(random.randint(0,9))
                insert_pos = random.randint(0,len(enhanced))
                enhanced.insert(insert_pos,digit)
        if self.pw_symbols:
            special_chars = "!@#$%^&*()_+-=[]}{|<>?/"
            insert_specials = random.randint(1,4)
            for _ in range(insert_specials):
                char = random.choice(special_chars)
                insert_pos = random.randint(0,len(enhanced))
                enhanced.insert(insert_pos,char)
        
        return "".join(enhanced)

    # Generate multiple credentials
    def generate_credentials(self, count: int = 10) -> List[Tuple[str, str]]:
        self.build_state_transitions()
        credentials = []
        for i in range(count):
            username, password = self.generate_credential()
            credentials.append((username, password))
            self.progress = round(i / count) * 100
        self.progress = 100
        return credentials

# Main function to run the credential generation process
def main():
    # File paths
    site_list_csv_path = "site_list.csv"
    csv_path = "web_text.csv"
    wordlist_path = "wordlist.txt"

    # Load URLs from the CSV file
    urls = load_urls_from_csv(site_list_csv_path)

    scraper = WebScraper(urls)
    scraper.generate_csv(csv_path)

    # True or false for filters to apply to usernames or passwords per character, numbers, or symbols
    passchars = True
    userchars = True
    passnums = True
    usernums = True
    passsyms = True
    usersyms = False

    #set the length of the credentials to output
    userlen = 10
    passlen = 15

    #specify the amount of credentials to output
    credentialAmount = 5
    nlp_subroutine(csv_path)
    
    try:
        # filter parameters are passed here
        generator = CredentialGeneratorMDP(csv_path, wordlist_path, user_chars=userchars, user_nums=usernums, user_symbols=usersyms, user_len=userlen, pw_chars=passchars, pw_symbols=passsyms, pw_nums=passnums, pass_len=passlen)
        credentials = generator.generate_credentials(credentialAmount)#credentials generated here
        print("\nGenerated Credentials:")
        for username, password in credentials:
            print(f"Username: {username}, Password: {password}")
    except Exception as e:
        print(f"Error generating credentials: {e}")

if __name__ == "__main__":
    main()
