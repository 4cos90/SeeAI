import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import CORS_ORIGINS
from app.routers import leaderboard
from app.services.feishu import feishu_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up application...")
    asyncio.create_task(periodic_token_refresh())
    yield
    logger.info("Shutting down application...")


async def periodic_token_refresh():
    while True:
        try:
            await asyncio.sleep(3600)
            if feishu_service.token:
                logger.info("Proactively refreshing Feishu token...")
                await feishu_service.get_tenant_access_token(force_refresh=True)
        except asyncio.CancelledError:
            logger.info("Stopping token refresh task")
            break
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")


app = FastAPI(title="SeeAI Backend API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leaderboard.router)


@app.get("/")
async def root():
    return {"message": "SeeAI Backend API", "version": "1.0.0"}
