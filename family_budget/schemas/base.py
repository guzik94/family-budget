from pydantic import BaseModel as PydanticBaseModel


class SchemaBase(PydanticBaseModel):
    class Config:
        orm_mode = True
