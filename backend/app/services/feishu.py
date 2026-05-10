import httpx
from typing import Optional
from app.config import FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_API_BASE, FEISHU_APP_TOKEN, FEISHU_TABLE_ID


class FeishuService:
    def __init__(self):
        self.app_id = FEISHU_APP_ID
        self.app_secret = FEISHU_APP_SECRET
        self.token: Optional[str] = None
        self.app_token = FEISHU_APP_TOKEN
        self.table_id = FEISHU_TABLE_ID

    async def get_tenant_access_token(self) -> str:
        url = f"{FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            if data.get("code") != 0:
                raise Exception(f"Failed to get token: {data.get('msg')}")
            self.token = data.get("tenant_access_token")
            return self.token

    async def get_leaderboard_data(self) -> dict:
        if not self.token:
            await self.get_tenant_access_token()

        url = f"{FEISHU_API_BASE}/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/records/search"
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        all_records = []
        page_token = None
        
        async with httpx.AsyncClient() as client:
            try:
                while True:
                    payload = {
                        "page_size": 500
                    }
                    if page_token:
                        payload["page_token"] = page_token
                    
                    response = await client.post(url, headers=headers, json=payload, timeout=30)
                    response.raise_for_status()
                    data = response.json()
                    
                    if data.get("code") != 0:
                        raise Exception(f"API error: {data.get('msg')}")
                    
                    items = data.get("data", {}).get("items", [])
                    all_records.extend(items)
                    
                    has_more = data.get("data", {}).get("has_more", False)
                    if not has_more:
                        break
                    
                    page_token = data.get("data", {}).get("page_token")
                    if not page_token:
                        break
                
                return {"records": all_records, "total": len(all_records)}
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    self.token = None
                    await self.get_tenant_access_token()
                    return await self.get_leaderboard_data()
                raise


feishu_service = FeishuService()
