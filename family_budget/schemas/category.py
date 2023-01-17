from pydantic import BaseModel

from .base import SchemaBase


class Category(SchemaBase):
    id: int
    name: str


class CategoryCreate(BaseModel):
    name: str
