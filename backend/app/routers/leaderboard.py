from fastapi import APIRouter, HTTPException
from app.services.feishu import feishu_service

router = APIRouter(prefix="/api", tags=["leaderboard"])


@router.get("/health")
async def health_check():
    return {"status": "ok"}


@router.get("/leaderboard")
async def get_leaderboard():
    try:
        data = await feishu_service.get_leaderboard_data()
        return {"code": 0, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
