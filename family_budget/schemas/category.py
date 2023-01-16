from pydantic import BaseModel

from .base import SchemaBase


class Category(SchemaBase):
    name: str


class CategoryCreate(BaseModel):
    name: str
