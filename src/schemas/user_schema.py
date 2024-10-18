from pydantic import BaseModel, ConfigDict, EmailStr


class UserSchema(BaseModel):
    email: EmailStr

    model_config = ConfigDict(extra="forbid", from_attributes=True)
