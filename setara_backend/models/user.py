from sqlalchemy import (
    Column,
    String,
    DateTime,
    Enum,
    ForeignKey,
    Boolean,
    Text,
)
import enum
import uuid
from .meta import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class UserStatusEnum(enum.Enum):
    deleted = 'deleted'
    active = 'active'
    inactive = 'inactive'


class TblUser(Base):
    __tablename__ = 'tblUser'
    user_id = Column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    user_phone = Column(
        String(17),
        unique=True,
        nullable=True
    )
    user_username = Column(
        Text,
        unique=True,
        nullable=True
    )
    user_email = Column(
        Text,
        nullable=True
    )
    user_name = Column(
        Text,
        nullable=True
    )
    user_password = Column(
        Text,
        nullable=True
    )
    user_is_verified = Column(
        Boolean,
        default=False,
        nullable=False
    )
    user_is_login = Column(
        Boolean,
        default=False,
        nullable=False
    )
    user_role = Column(
        Text,
        nullable=False
    )
    user_created_at = Column(
        DateTime,
        default=func.now()
    )
    user_updated_at = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now()
    )
    user_approved_at = Column(
        DateTime,
        nullable=True
    )
    user_reject_message = Column(
        Text,
        nullable=True
    )
    user_status = Column(
        Enum(UserStatusEnum),
        nullable=False
    )

    # Foreign Keys
    user_created_by = Column(
        String(255),
        ForeignKey('tblUser.user_id', ondelete='CASCADE'),
        nullable=True
    )
    user_approved_by = Column(
        String(255),
        ForeignKey('tblUser.user_id', ondelete='CASCADE'),
        nullable=True
    )

    # Relationships
    creator = relationship(
        'TblUser',
        remote_side=[user_id],
        foreign_keys=[user_created_by],
        uselist=False
    )
    approver = relationship(
        'TblUser',
        remote_side=[user_id],
        foreign_keys=[user_approved_by],
        uselist=False
    )
