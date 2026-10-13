from pydantic import BaseModel
from typing import List

class AgentResponse(BaseModel):
    title:str
    body:str
    label:List[str]
    type:str
