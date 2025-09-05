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
    """
    Adds all files in the current directory to the Git staging area,
    excluding those specified in .gitignore.
    """
    subprocess.run(["git", "add", "."])
    print("✅ Files added to staging (excluding .gitignore entries).")

def commit_changes():
    """
    Commits the staged changes to the Git repository.
    """
    commit_message = input("Enter commit message (e.g., 'Initial commit'): ")
    subprocess.run(["git", "commit", "-m", commit_message])
    print("✅ Changes committed.")

def create_readme():
    """
    Creates a basic README.md file in the current directory.
    """
    readme_content = "# ENV_File_Creator\n\nThis repository contains the ENV_File_Creator utility.\n"
    with open("README.md", "w") as f:
        f.write(readme_content)
    print("✅ README.md created.")

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
        print("5. Create README.md")
        print("6. Link and push to GitHub")
        print("7. Exit")

        choice = input("Select an option (1–7): ")

        if choice == "1":
            create_gitignore()
        elif choice == "2":
            initialize_git()
        elif choice == "3":
            add_files()
        elif choice == "4":
            commit_changes()
        elif choice == "5":
            create_readme()
        elif choice == "6":
            link_remote_repo()
        elif choice == "7":
            print("👋 Exiting setup.")
            break
        else:
            print("❌ Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    menu()
