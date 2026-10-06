from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TransformationCache(Base):
    __tablename__ = "transformation_cache"
    
    input: Mapped[str] = mapped_column(String, primary_key=True)
    output: Mapped[str] = mapped_column(String)


class PayloadCache(Base):
    __tablename__ = "payload_cache"

    hash: Mapped[str] = mapped_column(String, primary_key=True)
    output: Mapped[str] = mapped_column(String)
