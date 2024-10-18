from pydantic import BaseModel, ConfigDict


class AuthSchema(BaseModel):
    api_key: str

    model_config = ConfigDict(extra="forbid", from_attributes=True)
