from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

SCHEMA = "family_budget"
metadata_ = MetaData(schema=SCHEMA)
Base = declarative_base(metadata=metadata_)
