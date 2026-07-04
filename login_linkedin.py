"""
Run this once to log in to LinkedIn and save your session cookies.
After this, the main app will reuse the cookies automatically.

Usage:
    python login_linkedin.py
"""

from tools.linkedin_tool import LinkedInTool


def main():
    tool = LinkedInTool()
    tool.login(force_manual=True)
    tool.close()
    print("Done. You can now run the main app.")


if __name__ == "__main__":
    main()
