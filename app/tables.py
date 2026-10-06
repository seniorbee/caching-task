from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TransformationCache(Base):
    input: Mapped[str] = mapped_column(String, primary_key=True)
    output: Mapped[str] = mapped_column(String)


class PayloadCache(Base):
    hash: Mapped[str] = mapped_column(String, primary_key=True)
    output: Mapped[str] = mapped_column(String)
