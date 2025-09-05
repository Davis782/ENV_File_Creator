import os, sqlite3, getpass, hashlib
from datetime import datetime

DB_PATH = "api_keys.db"
ENV_PATH = ".env"
HASH_PATH = "master.hash"

# 20 popular APIs
DEFAULT_SERVICES = [
    "openai", "anthropic", "gemini", "ollama", "mistral", "cohere", "huggingface",
    "together", "fireworks", "groq", "lmstudio", "perplexity", "elevenlabs",
    "supabase", "langchain", "replicate", "serpapi", "pinecone", "weaviate", "vercel",
    "scrapeless", "gmail_oauth2"
]

# Dictionary mapping services to their API key documentation URLs
API_KEY_URLS = {
    "openai": "https://platform.openai.com/account/api-keys",
    "anthropic": "https://console.anthropic.com/settings/keys",
    "gemini": "https://ai.google.dev/gemini-api/docs/api-key",
    "ollama": "See option 5 in menu for Ollama token setup", # Ollama token setup is handled differently
    "mistral": "https://console.mistral.ai/api-keys/",
    "cohere": "https://dashboard.cohere.com/api-keys",
    "huggingface": "https://huggingface.co/settings/tokens",
    "together": "https://www.together.ai/", # Check their platform for API key location
    "fireworks": "https://app.fireworks.ai/api-keys",
    "groq": "https://console.groq.com/keys",
    "lmstudio": "https://lmstudio.ai/", # LM Studio runs locally, no external key needed
    "perplexity": "https://www.perplexity.ai/settings/api",
    "elevenlabs": "https://elevenlabs.io/speech-synthesis/api-reference",
    "supabase": "https://supabase.com/docs/guides/platform/api-keys",
    "langchain": "https://www.langchain.com/", # LangChain is a framework, not an API provider
    "replicate": "https://replicate.com/account/api-tokens",
    "serpapi": "https://serpapi.com/manage-api-key",
    "pinecone": "https://app.pinecone.io/", # Check their platform for API key location
    "weaviate": "https://weaviate.io/developers/weaviate/manage-data/security/api-keys",
    "vercel": "https://vercel.com/account/tokens",
    "scrapeless": "https://www.scrapeless.com/", # Placeholder, need to find actual URL
    "gmail_oauth2": "https://developers.google.com/gmail/api/auth/about-auth" # OAuth2, not a simple API key
}

def setup_password():
    """
    Sets up the master password for the application.
    If a password hash file already exists, it does nothing.
    Otherwise, it prompts the user to set a new password and stores its SHA256 hash.
    """
    if os.path.exists(HASH_PATH):
        return
    pw = getpass.getpass("🔐 Set master password: ")
    hashed = hashlib.sha256(pw.encode()).hexdigest()
    with open(HASH_PATH, "w") as f:
        f.write(hashed)
    print("✅ Password saved.")

def verify_password():
    """
    Verifies the master password entered by the user.
    Compares the SHA256 hash of the entered password with the stored hash.
    Exits the application if the password file does not exist or the password is incorrect.
    """
    if not os.path.exists(HASH_PATH):
        print("❌ No password set. Run setup again.")
        exit()
    pw = getpass.getpass("🔐 Enter master password: ")
    with open(HASH_PATH) as f:
        stored = f.read().strip()
    if hashlib.sha256(pw.encode()).hexdigest() != stored:
        print("❌ Incorrect password.")
        exit()
    print("✅ Access granted.")

def init_db():
    """
    Initializes the SQLite database for storing API keys.
    Creates the 'api_keys' table if it doesn't exist.
    Inserts default service entries into the table if they don't already exist.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service TEXT UNIQUE NOT NULL,
            key TEXT NOT NULL,
            model TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            timestamp INTEGER
        )
    """)
    conn.commit()

    # Check if 'timestamp' column exists and add it if not (for migration)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(api_keys)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'timestamp' not in columns:
        conn.execute("ALTER TABLE api_keys ADD COLUMN timestamp INTEGER")
        conn.commit()
        print("✅ Added 'timestamp' column to api_keys table.")
    # Check if 'model' column exists and add it if not (for migration)
    if 'model' not in columns:
        conn.execute("ALTER TABLE api_keys ADD COLUMN model TEXT")
        conn.commit()
        print("✅ Added 'model' column to api_keys table.")
    for service in DEFAULT_SERVICES:
        conn.execute("INSERT OR IGNORE INTO api_keys (service, key) VALUES (?, '')", (service,))
    conn.commit()
    conn.close()
    print("✅ Database initialized with default services.")

def list_keys():
    """
    Retrieves all API keys from the database.
    Returns a list of tuples, each containing the service name, API key, and formatted environment variable name.
    """
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT service, key, timestamp, model FROM api_keys").fetchall()
    conn.close()
    formatted_keys = []
    for service, key, timestamp, model in rows:
        env_key = f"{service.upper().replace('-', '_')}_API_KEY"
        
        status_info = ""
        if service == "ollama" and timestamp:
            current_time = datetime.now()
            last_updated = datetime.fromtimestamp(timestamp)
            days_since_update = (current_time - last_updated).days
            days_remaining = 90 - days_since_update

            if days_remaining <= 0:
                status_info = f" \033[31m[EXPIRED]\033[0m"
            elif days_remaining <= 5:
                status_info = f" \033[33m[Expires in {days_remaining} days]\033[0m"
            elif days_remaining <= 90:
                status_info = f" \033[38;5;208m[Valid for {days_remaining} days]\033[0m"
            else:
                status_info = f" \033[94m[Unknown status]\033[0m"
        elif service == "ollama" and not timestamp and key:
            status_color = "\033[94m"  # Blue
            status_text = "Token set (no expiration info)"
            status_info = f" {status_color}[{status_text}]\033[0m"

        model_info = f" ({model})" if model else ""
        formatted_keys.append((service, key, env_key, status_info + model_info))
    return formatted_keys

def update_key(service, key, timestamp=None, model=None):
    """
    Updates an API key for a given service in the database.
    Also updates the 'updated_at' timestamp for the entry.

    Args:
        service (str): The name of the service.
        key (str): The API key to set.
        timestamp (int, optional): Unix timestamp of when the key was last updated. Defaults to None.
        model (str, optional): The model associated with the key. Defaults to None.
    """
    conn = sqlite3.connect(DB_PATH)

    # Ensure timestamp is always set, defaulting to current time if not provided
    if timestamp is None:
        timestamp = int(datetime.now().timestamp())
    
    # Use INSERT OR REPLACE to handle both new entries and updates
    if model is not None:
        conn.execute("INSERT OR REPLACE INTO api_keys (service, key, timestamp, model) VALUES (?, ?, ?, ?)", (service, key, timestamp, model))
    else:
        conn.execute("INSERT OR REPLACE INTO api_keys (service, key, timestamp) VALUES (?, ?, ?)", (service, key, timestamp))

    conn.commit()
    conn.close()
    print(f"🔁 {service} updated.")

def export_env():
    """
    Exports all stored API keys to a .env file.
    Only exports keys that have a non-empty value.
    Formats the service names to uppercase with underscores for environment variable compatibility.
    """
    keys = list_keys()
    with open(ENV_PATH, "w") as f:
        for service, key, _, _ in keys: # Unpack only service and key, ignore env_key and status_info
            if key:
                env_key = f"{service.upper().replace('-', '_')}_API_KEY"
                f.write(f"{env_key}={key}\n")
    print(f"✅ .env file generated with {len([k for _, k, _, _ in keys if k])} keys.")

def handle_ollama_token():
    """
    Handles the generation, setting, and validation of the Ollama API token.
    """
    print("\n--- Ollama API Token Setup ---")
    print("1. Generate a new secure token (using openssl rand -hex 32)")
    print("2. Set existing token as environment variable")
    print("3. Start Ollama with authentication enabled")
    print("4. Back to main menu")

    while True:
        ollama_choice = input("Select: ")
        if ollama_choice == "1":
            print("Generating a new token...")
            # This command needs to be run in a shell where openssl is available
            # For simplicity, we'll just tell the user to run it manually for now.
            # In a real scenario, you might execute this via subprocess.
            print("Please run 'openssl rand -hex 32' in your terminal to generate a token.")
            print("Then copy the generated token.")
        elif ollama_choice == "2":
            token = input("Enter your Ollama API token: ")
            if token:
                model = input("Enter the Ollama model (e.g., llama2, mistral): ")
                update_key("ollama", token, timestamp=int(datetime.now().timestamp()), model=model)
                print("Ollama API token and model set.")
            else:
                print("Ollama API token not set.")
        elif ollama_choice == "3":
            if 'OLLAMA_API_TOKEN' in os.environ:
                print("Attempting to start Ollama with authentication...")
                print("Please run 'ollama serve --auth-token $env:OLLAMA_API_TOKEN' in a new PowerShell terminal.")
                print("This script cannot directly start a long-running process and manage its lifecycle.")
            else:
                print("OLLAMA_API_TOKEN not set. Please set it first (option 2).")
        elif ollama_choice == "4":
            break
        else:
            print("❌ Invalid choice.")

def menu():
    """
    Displays the main menu and handles user interactions.
    Provides options to list keys, update keys, export to .env, exit, and manage Ollama API token.
    """
    while True:
        print("\n🔧 DR-Silver Bullet Menu")
        print("1. List all keys")
        print("2. Update a key")
        print("3. Export to .env")
        print("4. Add a new key")
        print("5. Exit")
        print("6. Ollama API Token Setup")
        choice = input("Select: ")
        if choice == "1":
            keys_list = list_keys()
            for i, (s, k, ek, status_info) in enumerate(keys_list):
                url = API_KEY_URLS.get(s, "N/A")
                print(f"{i+1}. {ek}={k if k else 'YOUR_API_KEY_HERE'} ({s}): {'✅' if k else '❌'} | Get Key: {url}{status_info}")
        elif choice == "2":
            keys_list = list_keys()
            for i, (s, k, ek, status_info) in enumerate(keys_list):
                print(f"{i+1}. {s}{status_info}")
            try:
                service_index = int(input("Select service by number: ")) - 1
                if 0 <= service_index < len(keys_list):
                    s = keys_list[service_index][0]
                    # Special handling for Ollama
                    if s == "ollama":
                        handle_ollama_token()
                        continue
                else:
                    print("❌ Invalid service number.")
                    continue
            except ValueError:
                print("❌ Invalid input. Please enter a number.")
                continue
            k = input("API key: ").strip()
            model_name = input("Enter model name (optional, leave blank if not applicable): ").strip()
            if model_name:
                update_key(s, k, model=model_name)
            else:
                update_key(s, k)
            print(f"🔁 {s} updated.")
        elif choice == "3":
            export_env()
        elif choice == "4":
            service_name = input("Enter new service name: ").strip().lower()
            if not service_name:
                print("❌ Service name cannot be empty.")
                continue
            api_key = input("Enter API key: ").strip()
            model_name = input("Enter model name (optional, leave blank if not applicable): ").strip()
            update_key(service_name, api_key, model=model_name if model_name else None)
            print(f"✅ {service_name} added/updated.")
        elif choice == "5":
            break
        elif choice == "6":
            handle_ollama_token()
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    setup_password()
    verify_password()
    init_db()
    menu()
