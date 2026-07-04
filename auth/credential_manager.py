import os


class CredentialManager:

    def get(self, key: str):
        """
        Get credential from environment.
        """

        value = os.getenv(key)

        if not value:
            raise Exception(
                f"{key} is missing"
            )

        return value


    def exists(self, key: str):
        """
        Check credential exists.
        """

        return bool(
            os.getenv(key)
        )