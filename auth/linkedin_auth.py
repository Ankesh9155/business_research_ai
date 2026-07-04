from auth.session_manager import SessionManager


class LinkedInAuth:

    def __init__(self):
        self.session = SessionManager()


    def save_session(self, cookies: list):
        self.session.save("linkedin", cookies)


    def load_session(self):
        return self.session.load("linkedin")


    def is_logged_in(self):
        return self.session.exists("linkedin")


    def logout(self):
        self.session.delete("linkedin")