from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UploadStatusResponse(BaseModel):
    uploaded_files: Optional[bool]
    uploaded_time: Optional[datetime]

    class Config:
        from_attributes = True
