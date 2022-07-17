from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    line_notify_api = "https://notify-api.line.me/api/notify"
    line_token_path = "."
    sent_file_path = "./Sent"



@lru_cache()
def get_settings():
    return Settings()
