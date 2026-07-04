from auth.credential_manager import CredentialManager


class ApolloAuth:

    def __init__(self):
        self.credential = CredentialManager()


    def get_api_key(self):

        return self.credential.get(
            "APOLLO_API_KEY"
        )


    def is_authenticated(self):

        return self.credential.exists(
            "APOLLO_API_KEY"
        )