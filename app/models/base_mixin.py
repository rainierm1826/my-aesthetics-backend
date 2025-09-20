from sqlalchemy import Column, Boolean
from sqlalchemy.ext.declarative import declared_attr

class SoftDeleteMixin:
    isDeleted = Column(Boolean, default=False)

    @declared_attr
    def __mapper_args__(cls):
        return {
            "eager_defaults": True
        }
