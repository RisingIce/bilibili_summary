from pydantic import BaseModel
from typing import Optional

class BilibiliSummary(BaseModel):
    bv_id: str
    prompt: Optional[str] = None
    stream : bool = False

class BilibiliSummaryResponse(BaseModel):
    avid: int
    bvid: str
    cid: int
    title: str
    url: str
    answer: str  
