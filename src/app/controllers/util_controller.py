from fastapi import HTTPException, UploadFile

from src.app.services.util_service import UtilService


class UtilController:
    def __init__(self, util_service: UtilService):
        self.util_service = util_service

    async def extract_excel(self, file: UploadFile):
        try:
            result = self.util_service.extract_excel(file)
            return result
        except Exception as e:
            raise HTTPException(500, detail=f"Error processing file: {e}")
