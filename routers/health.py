from fastapi import APIRouter


router = APIRouter(
    prefix="/health",
    tags=["health"],
    responses={404: {"description": "Not found"}}
)

@router.get("/", status_code=200)
async def health_check():
    return {"status": "healthy"}