from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class GenerateSchema(BaseModel):
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    query: Optional[str] = None
    memory: Optional[List[dict]] = None
    category: Optional[str] = None
    radius: Optional[int] = None
    prompt: Optional[str] = None
    context: Optional[str] = None

    model_config = ConfigDict(extra="forbid", from_attributes=True)
