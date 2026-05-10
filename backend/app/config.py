import os
from dotenv import load_dotenv

load_dotenv()

FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
FEISHU_APP_TOKEN = os.getenv("FEISHU_APP_TOKEN", "")
FEISHU_TABLE_ID = os.getenv("FEISHU_TABLE_ID", "")
FEISHU_API_BASE = "https://open.feishu.cn/open-apis"

CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:80",
]
