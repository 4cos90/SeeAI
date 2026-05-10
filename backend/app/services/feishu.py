import httpx
from typing import Optional, Dict, List
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

    async def get_table_records(self, table_id: str) -> List[dict]:
        if not self.token:
            await self.get_tenant_access_token()

        url = f"{FEISHU_API_BASE}/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/search"
        
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
                
                return all_records
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    self.token = None
                    await self.get_tenant_access_token()
                    return await self.get_table_records(table_id)
                raise

    async def get_all_tables(self) -> List[dict]:
        if not self.token:
            await self.get_tenant_access_token()

        url = f"{FEISHU_API_BASE}/bitable/v1/apps/{self.app_token}/tables"
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") != 0:
                raise Exception(f"API error: {data.get('msg')}")
            
            return data.get("data", {}).get("items", [])

    async def get_leaderboard_data(self) -> dict:
        all_records = []
        
        try:
            tables = await self.get_all_tables()
            
            for table in tables:
                table_id = table.get("table_id")
                table_name = table.get("name", "")
                records = await self.get_table_records(table_id)
                
                for record in records:
                    fields = record.get("fields", {})
                    executors = fields.get("任务执行人", [])
                    task_month = fields.get("任务月份", "")
                    task_score = fields.get("任务积分", 0)
                    
                    if isinstance(executors, list) and len(executors) > 0:
                        for executor in executors:
                            executor_name = executor.get("name", "未知") if isinstance(executor, dict) else str(executor)
                            
                            all_records.append({
                                "executor": executor_name,
                                "month": task_month,
                                "score": task_score if task_score is not None else 0
                            })
                    elif executors:
                        executor_name = executors.get("name", "未知") if isinstance(executors, dict) else str(executors)
                        all_records.append({
                            "executor": executor_name,
                            "month": task_month,
                            "score": task_score if task_score is not None else 0
                        })
            
            month_stats = {}
            for record in all_records:
                executor = record["executor"]
                month = record["month"]
                score = record["score"] or 0
                
                if not month:
                    continue
                    
                key = (executor, month)
                if key not in month_stats:
                    month_stats[key] = {
                        "executor": executor,
                        "month": month,
                        "total_score": 0
                    }
                month_stats[key]["total_score"] += score
            
            result = []
            for key, stats in month_stats.items():
                result.append(stats)
            
            result.sort(key=lambda x: (-x["total_score"], x["executor"]))
            
            return {"records": result, "total": len(result)}
        except Exception as e:
            raise


feishu_service = FeishuService()
