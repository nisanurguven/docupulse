from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: Optional[str] = None
    created_at: datetime = Field(default_factory=get_utc_now)
    documents: List["Document"] = Relationship(back_populates="user")

class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    filename: str
    file_path: str
    file_hash: str
    file_size_bytes: int
    total_chunks: int = 0
    created_at: datetime = Field(default_factory=get_utc_now)
    user: Optional[User] = Relationship(back_populates="documents")