import os

from fastapi import APIRouter

router = APIRouter(prefix="/info")


@router.get(
    path="/version"
)
def show_version():
    return {"version_id": os.environ.get('COMMIT_ID', 'Unknown')}
