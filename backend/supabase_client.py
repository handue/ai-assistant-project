import os
from pathlib import Path
from dotenv import load_dotenv

from supabase import Client, create_client

load_dotenv(Path(__file__).with_name(".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
    raise RuntimeError("Set SUPABASE_URL and SUPABASE_SECRET_KEY in backend/.env.")


supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY,
)
