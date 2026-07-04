import os
import json


class SessionManager:

    def __init__(self):
        self.session_dir = "auth/sessions"
        os.makedirs(self.session_dir, exist_ok=True)


    def save(self, platform: str, data: dict):
        """
        Save session data.
        """
        path = os.path.join(
            self.session_dir,
            f"{platform}.json"
        )

        with open(path, "w") as file:
            json.dump(data, file, indent=4)


    def load(self, platform: str):
        """
        Load session data.
        """
        path = os.path.join(
            self.session_dir,
            f"{platform}.json"
        )

        if not os.path.exists(path):
            return None

        with open(path, "r") as file:
            return json.load(file)


    def delete(self, platform: str):
        """
        Delete a session.
        """
        path = os.path.join(
            self.session_dir,
            f"{platform}.json"
        )

        if os.path.exists(path):
            os.remove(path)


    def exists(self, platform: str) -> bool:
        """
        Check session exists.
        """

        path = os.path.join(
            self.session_dir,
            f"{platform}.json"
        )

        return os.path.exists(path)