from fastapi import APIRouter

router = APIRouter(prefix="/health-check")


@router.get(
    path="",
    status_code=200
)
def health_check():
    return {"status": "ok"}
