import time
from datetime import datetime
from config import PROJECT_ROOT
from src.utils.file_handler import FileHandler

def get_most_recent_login():
    input_file_path = f"{PROJECT_ROOT}/data/users.json"

    users = FileHandler.load_json(input_file_path)

    most_recent_login = 0
    for user in users:
        if not user.get("last_login"):
            continue

        login = user["last_login"]
        if isinstance(login, dict):
            if not login.get("$date"):
                login = login["$numberLong"]
            else:
                login = login["$date"]
        if isinstance(login, str) and "Z" in login:
            dt = datetime.fromisoformat(login.replace('Z', '+00:00'))
            login = int(dt.timestamp())
        else:
            login = int(login)
        if login > most_recent_login:
            most_recent_login = login
    
    return login

print(get_most_recent_login())