from fastapi import APIRouter, Depends, File, UploadFile

from src.app.controllers.util_controller import UtilController
from src.app.dependencies.util import get_util_controller


router = APIRouter()


@router.post("/excel/extract")
async def extract_excel(file: UploadFile = File(...), controller: UtilController = Depends(get_util_controller)):
    return await controller.extract_excel(file)
