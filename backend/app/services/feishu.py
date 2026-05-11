import httpx
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from app.config import (
    FEISHU_APP_ID,
    FEISHU_APP_SECRET,
    FEISHU_API_BASE,
    FEISHU_APP_TOKEN,
    FEISHU_TABLE_ID,
)

logger = logging.getLogger(__name__)


class FeishuService:
    def __init__(self):
        self.app_id = FEISHU_APP_ID
        self.app_secret = FEISHU_APP_SECRET
        self.token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self.app_token = FEISHU_APP_TOKEN
        self.table_id = FEISHU_TABLE_ID
        self._is_refreshing = False
        
        logger.info(f"FeishuService initialized. app_token: {self.app_token}, app_id: {self.app_id[:8] if self.app_id else 'empty'}...")

    def _get_async_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            verify=True,
            timeout=30.0,
        )

    async def get_tenant_access_token(self, force_refresh: bool = False) -> str:
        if not force_refresh and self.token and self.token_expires_at:
            if datetime.now() < self.token_expires_at - timedelta(minutes=5):
                logger.debug("Token still valid, no refresh needed")
                return self.token
        
        url = f"{FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
        payload = {"app_id": self.app_id, "app_secret": self.app_secret}
        
        logger.info(f"Requesting tenant_access_token from: {url}")
        
        async with self._get_async_client() as client:
            response = await client.post(url, json=payload)
            logger.info(f"Token request status: {response.status_code}")
            
            try:
                data = response.json()
                logger.info(f"Token response: {data}")
            except Exception:
                logger.error(f"Token response text: {response.text}")
                raise
            
            if response.status_code != 200 or data.get("code") != 0:
                error_msg = f"Failed to get token. Status: {response.status_code}, Code: {data.get('code')}, Msg: {data.get('msg')}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
            self.token = data.get("tenant_access_token")
            expire_in = data.get("expire", 7200)
            self.token_expires_at = datetime.now() + timedelta(seconds=expire_in)
            logger.info(f"Successfully obtained tenant_access_token, expires in {expire_in}s")
            return self.token
    
    def _is_token_expired(self) -> bool:
        if not self.token or not self.token_expires_at:
            return True
        return datetime.now() >= self.token_expires_at - timedelta(minutes=5)
    
    def _is_token_invalid_error(self, data: dict) -> bool:
        if data.get("code") == 99991663:
            return True
        if data.get("code") == 99991400:
            return True
        if "Invalid access token" in str(data.get("msg", "")):
            return True
        return False

    async def get_table_records(self, table_id: str, retry_on_401: bool = True) -> List[dict]:
        if not self.token or self._is_token_expired():
            await self.get_tenant_access_token()

        url = f"{FEISHU_API_BASE}/bitable/v1/apps/{self.app_token}/tables/{table_id}/records/search"
        logger.info(f"Fetching records from table: {table_id}, URL: {url}")

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        all_records = []
        page_token = None

        async with self._get_async_client() as client:
            while True:
                payload = {"page_size": 500}
                if page_token:
                    payload["page_token"] = page_token

                try:
                    response = await client.post(
                        url, headers=headers, json=payload, timeout=30
                    )
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 401 and retry_on_401:
                        self.token = None
                        self.token_expires_at = None
                        logger.warning("Token expired, refreshing...")
                        await self.get_tenant_access_token()
                        return await self.get_table_records(table_id, retry_on_401=False)
                    raise

                logger.info(f"Records response status: {response.status_code}")
                try:
                    data = response.json()
                    logger.debug(f"Records response data: {data}")
                except Exception:
                    logger.error(f"Records response text: {response.text}")
                    raise

                if data.get("code") != 0:
                    if self._is_token_invalid_error(data) and retry_on_401:
                        self.token = None
                        self.token_expires_at = None
                        logger.warning(f"Token invalid (code {data.get('code')}), refreshing...")
                        await self.get_tenant_access_token()
                        return await self.get_table_records(table_id, retry_on_401=False)
                    
                    error_msg = f"API error fetching records. Code: {data.get('code')}, Msg: {data.get('msg')}"
                    logger.error(error_msg)
                    raise Exception(error_msg)

                items = data.get("data", {}).get("items", [])
                all_records.extend(items)

                has_more = data.get("data", {}).get("has_more", False)
                if not has_more:
                    break

                page_token = data.get("data", {}).get("page_token")
                if not page_token:
                    break

        logger.info(f"Total records fetched from table {table_id}: {len(all_records)}")
        return all_records

    async def get_all_tables(self, retry_on_401: bool = True) -> List[dict]:
        if not self.token or self._is_token_expired():
            await self.get_tenant_access_token()

        url = f"{FEISHU_API_BASE}/bitable/v1/apps/{self.app_token}/tables"
        logger.info(f"Fetching all tables from URL: {url}")

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        async with self._get_async_client() as client:
            try:
                response = await client.get(url, headers=headers, timeout=30)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401 and retry_on_401:
                    self.token = None
                    self.token_expires_at = None
                    logger.warning("Token expired, refreshing...")
                    await self.get_tenant_access_token()
                    return await self.get_all_tables(retry_on_401=False)
                raise
            
            logger.info(f"Get tables response status: {response.status_code}")
            
            try:
                data = response.json()
                logger.info(f"Get tables response: {data}")
            except Exception:
                logger.error(f"Get tables response text: {response.text}")
                raise

            if data.get("code") != 0:
                if self._is_token_invalid_error(data) and retry_on_401:
                    self.token = None
                    self.token_expires_at = None
                    logger.warning(f"Token invalid (code {data.get('code')}), refreshing...")
                    await self.get_tenant_access_token()
                    return await self.get_all_tables(retry_on_401=False)
                
                error_msg = f"API error fetching tables. Code: {data.get('code')}, Msg: {data.get('msg')}"
                logger.error(error_msg)
                raise Exception(error_msg)

            tables = data.get("data", {}).get("items", [])
            logger.info(f"Total tables found: {len(tables)}")
            return tables

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
                    task_start = fields.get("开始日期", "")

                    task_year = ""
                    if task_start:

                        # 处理时间戳（毫秒级）
                        if isinstance(task_start, (int, float)):
                            timestamp_sec = task_start / 1000
                            date_obj = datetime.fromtimestamp(timestamp_sec)
                            task_year = str(date_obj.year)

                        # 处理字符串格式日期
                        elif isinstance(task_start, str) and len(task_start) >= 4:
                            task_year = task_start[:4]
                        # 处理日期对象
                        elif hasattr(task_start, "year"):
                            task_year = str(task_start.year)

                    if isinstance(executors, list) and len(executors) > 0:
                        for executor in executors:
                            executor_name = (
                                executor.get("name", "未知")
                                if isinstance(executor, dict)
                                else str(executor)
                            )

                            all_records.append(
                                {
                                    "executor": executor_name,
                                    "month": task_month,
                                    "year": task_year,
                                    "score": (
                                        task_score if task_score is not None else 0
                                    ),
                                }
                            )
                    elif executors:
                        executor_name = (
                            executors.get("name", "未知")
                            if isinstance(executors, dict)
                            else str(executors)
                        )
                        all_records.append(
                            {
                                "executor": executor_name,
                                "month": task_month,
                                "year": task_year,
                                "score": task_score if task_score is not None else 0,
                            }
                        )

            month_stats = {}
            for record in all_records:
                executor = record["executor"]
                month = record["month"]
                year = record.get("year", "")
                score = record["score"] or 0

                if not month:
                    continue

                key = (executor, month)
                if key not in month_stats:
                    month_stats[key] = {
                        "executor": executor,
                        "month": month,
                        "year": year,
                        "total_score": 0,
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
