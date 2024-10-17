from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List


class UserSchema(BaseModel):
    email: EmailStr

    model_config = ConfigDict(extra="forbid", from_attributes=True)
