import os
import subprocess

GITIGNORE_CONTENT = """
# Sensitive files
api_keys.db
.env
*.hash

# Python artifacts
__pycache__/
*.py[cod]
*$py.class

# Virtual environments
venv/
ENV/

# IDE-specific files
.vscode/
.idea/
*.swp
*.swo
"""

def create_gitignore():
    with open(".gitignore", "w") as f:
        f.write(GITIGNORE_CONTENT.strip())
    print("✅ .gitignore file created with sensitive exclusions.")

def initialize_git():
    subprocess.run(["git", "init"])
    print("✅ Git repository initialized.")

def add_files():
    subprocess.run(["git", "add", "."])
    print("✅ Files added to staging (excluding .gitignore entries).")

def commit_changes():
    subprocess.run(["git", "commit", "-m", "Initial commit"])
    print("✅ Changes committed.")

def link_remote_repo():
    username = input("Enter your GitHub username: ")
    repo_name = input("Enter your new GitHub repository name: ")
    remote_url = f"https://github.com/{username}/{repo_name}.git"
    subprocess.run(["git", "remote", "add", "origin", remote_url])
    subprocess.run(["git", "branch", "-M", "main"])
    subprocess.run(["git", "push", "-u", "origin", "main"])
    print(f"🚀 Pushed to GitHub: {remote_url}")

def menu():
    while True:
        print("\n📦 Git Setup Menu")
        print("1. Create .gitignore")
        print("2. Initialize Git repository")
        print("3. Add files to staging")
        print("4. Commit changes")
        print("5. Link and push to GitHub")
        print("6. Exit")

        choice = input("Select an option (1–6): ")

        if choice == "1":
            create_gitignore()
        elif choice == "2":
            initialize_git()
        elif choice == "3":
            add_files()
        elif choice == "4":
            commit_changes()
        elif choice == "5":
            link_remote_repo()
        elif choice == "6":
            print("👋 Exiting setup.")
            break
        else:
            print("❌ Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    menu()
