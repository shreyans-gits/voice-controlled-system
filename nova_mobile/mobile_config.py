# import os
# from dotenv import load_dotenv

# current_dir = os.path.dirname(os.path.abspath(__file__))
# env_path = os.path.join(current_dir, ".env")

# load_dotenv(dotenv_path=env_path)

# # APP-MOBILE
# LAPTOP_TAILSCALE_IP = os.getenv("laptop_tailscape_id")

# if not LAPTOP_TAILSCALE_IP:
#     print("[Mobile Config Warning] 'laptop_tailscape_id' not found in .env! Falling back to localhost.")
#     LAPTOP_TAILSCALE_IP = "127.0.0.1"

# API_URL = f"http://{LAPTOP_TAILSCALE_IP}:8000/api/query"

LAPTOP_TAILSCALE_IP = "100.71.247.61"
API_URL = f"http://{LAPTOP_TAILSCALE_IP}:8000/api/query"