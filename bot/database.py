import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def get_settings(guild_id: int):
    res = supabase.table("guild_settings").select("*").eq("guild_id", guild_id).execute()
    if not res.data:
        supabase.table("guild_settings").insert({"guild_id": guild_id}).execute()
        return {"guild_id": guild_id, "log_channel_id": None, "welcome_channel_id": None, "automod_active": False}
    return res.data[0]

def update_settings(guild_id: int, column: str, value):
    supabase.table("guild_settings").upsert({"guild_id": guild_id, column: value}).execute()
