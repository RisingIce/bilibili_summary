from fastapi.routing import APIRouter
from server.schame import BilibiliSummary,BilibiliSummaryResponse
from server.endpoints.bilibili_operate import BiliBiliTool
from sse_starlette.sse import EventSourceResponse
bt = BiliBiliTool()
api = APIRouter()

@api.post("/bilismmary",response_model=BilibiliSummaryResponse)
async def get_summary(req:BilibiliSummary):
    resp = await bt.get_video_summary(bv_id = req.bv_id,prompt=req.prompt,stream=req.stream)
    return EventSourceResponse(resp) if req.stream else BilibiliSummaryResponse(**resp)