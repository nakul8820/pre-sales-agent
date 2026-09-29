from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_audits():
    """Placeholder endpoint for listing audits."""
    return {"message": "Audits endpoint ready", "items": []}
