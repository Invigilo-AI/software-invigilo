from email.policy import default
from typing import TYPE_CHECKING
from enum import Enum

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils import ScalarListType

from app.db.base_class import Base

if TYPE_CHECKING:
    from .company import Company  # noqa: F401


class UserPermissions(str, Enum):
    ADMIN = 'admin'
    INSPECTOR = 'inspector'
    BRIDGE = 'bridge'

    def __str__(self):
        return str(self.value)


class User(Base):
    full_name = Column(String)
    email = Column(String, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    permissions = Column(ScalarListType(), nullable=True, default=[UserPermissions.INSPECTOR])
    company_id = Column(Integer, ForeignKey("company.id"), nullable=True)
    company = relationship("Company", backref="users")
