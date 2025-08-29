import random
from datetime import datetime
from functools import wraps

class Logger:
    _instance = None
    _analyst_initials = None
    _project_name = None
    def __init__(self, analyst_initials="test", filename="Trace_analayst_Log.txt"):
        self.filename = filename
        self.analyst_initials = analyst_initials

    def __new__(cls, analyst_initials=None, project_name=None):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls)
            if analyst_initials:
                cls._analyst_initials = analyst_initials
            if project_name:
                cls._project_name = project_name
            # Random number appended to ensure uniqueness of the log file
            random_number = random.randint(1000, 9999)
            cls._instance.filename = f"TRACE_{cls._analyst_initials}_{cls._project_name}_LOG_{random_number}.txt"
        return cls._instance

    @classmethod
    def set_initials(cls, analyst_initials):
        if cls._analyst_initials is None:
            cls._analyst_initials = analyst_initials
            
        else:
            raise ValueError("Analyst initials can only be set once.")
    
    @classmethod
    def set_project(cls, project_name):
        if cls._project_name is None:
            cls._project_name = project_name
        elif cls._project_name != project_name:
            raise ValueError("Project name can only be set once.")
    

    def log_action(self, action_desc):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n{self._analyst_initials} | {action_desc} | START: {timestamp}"

        with open(self.filename, mode='a') as file:
            file.write(entry)

        def end():
            end_time = datetime.now()
            entry = f" | END   | {end_time}"
            with open(self.filename, mode='a') as file:
                file.write(entry)

        print(entry.strip())
        return end


def auto_logger():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            actiondesc = f"{func.__name__.replace('_', ' ').capitalize()}"
            # Use the globally set initials and project name
            log_filename = f"TRACE_{Logger._analyst_initials}_{Logger._project_name}_LOG.txt"
            entry = f"{timestamp} | {Logger._analyst_initials} | {actiondesc}\n"
            with open(log_filename, 'a') as file:
                file.write(entry)
            print(entry.strip())
            return func(*args, **kwargs)
        return wrapper
    return decorator
