from pydantic import BaseModel as PydanticBaseModel


class SchemaBase(PydanticBaseModel):
    id: int

    class Config:
        orm_mode = True
