from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime, JSON, func, Integer
from sqlmodel import Field, Relationship, SQLModel

try:
    from werkzeug.security import check_password_hash, generate_password_hash
except ImportError:
    # Fallback minimal implementations if werkzeug isn't available
    import hashlib

    def generate_password_hash(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def check_password_hash(pwhash: str, password: str) -> bool:
        return pwhash == hashlib.sha256(password.encode("utf-8")).hexdigest()


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password_hash: str
    role: str = Field(default="admin", index=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    def set_password(self, password: str) -> None:
        """Set password hash from plain text password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if provided password matches the hash."""
        return check_password_hash(self.password_hash, password)


class Post(SQLModel, table=True):
    __tablename__ = "posts"

    id: Optional[int] = Field(default=None, primary_key=True)
    kind: str = Field(index=True)  # text or video
    title: str
    body: str
    source_url: Optional[str] = None
    content_hash: Optional[str] = Field(default=None, index=True)
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    platforms: Optional[List[str]] = Field(
        default=None, sa_column=Column(JSON))
    # draft, approved, published
    status: str = Field(default="draft", index=True)
    scheduled_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    published_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        ),
    )
    deleted_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )

    # Relationships (commented out for now due to SQLModel version compatibility)
    # assets: List["Asset"] = Relationship(back_populates="post")
    # publish_logs: List["PublishLog"] = Relationship(back_populates="post")
    # learning_logs: List["LearningLog"] = Relationship(back_populates="post")


class Asset(SQLModel, table=True):
    __tablename__ = "assets"

    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="posts.id", index=True)
    type: str = Field(index=True)  # video or image
    path: str
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    # post: Optional["Post"] = Relationship(back_populates="assets")


class PublishLog(SQLModel, table=True):
    __tablename__ = "publish_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="posts.id", index=True)
    provider: str = Field(index=True)  # publer, buffer, native
    platform: str = Field(index=True)  # youtube, tiktok, linkedin, x
    # success, failed, pending_retry
    status: str = Field(default="pending_retry", index=True)
    external_id: Optional[str] = Field(default=None, index=True)
    external_url: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = Field(default=0, sa_column=Column(Integer))
    next_retry_at: Optional[datetime] = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    # post: Optional["Post"] = Relationship(back_populates="publish_logs")


class LearningLog(SQLModel, table=True):
    __tablename__ = "learning_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="posts.id", index=True)
    topic: str = Field(index=True)
    hook_type: Optional[str] = Field(default=None, index=True)
    metric_snapshot: Optional[dict] = Field(
        default=None, sa_column=Column(JSON))
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )

    # post: Optional["Post"] = Relationship(back_populates="learning_logs")
