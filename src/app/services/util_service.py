from typing import Any, Dict

from fastapi import UploadFile

from src.domain.services.excel_file_service import IExcelFileService


class UtilService:
    def __init__(self, excel_file_service: IExcelFileService) -> None:
        self.excel_file_service = excel_file_service

    async def extract_excel(self, file: UploadFile) -> Dict[str, Any]:
        return await self.excel_file_service.extract_file(file)
