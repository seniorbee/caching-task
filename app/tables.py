from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TransformationCache(Base):
    """Persistent cache of individual transformations.

    The input string is the primary key because each input has one cached
    deterministic transformation.
    """
    __tablename__ = "transformation_cache"

    input: Mapped[str] = mapped_column(String, primary_key=True)
    output: Mapped[str] = mapped_column(String, nullable=False)


class PayloadCache(Base):
    """Persistent cache of complete generated payloads.

    The SHA-256 hash of the input lists is the primary key and therefore also
    serves as the public payload identifier.
    """
    __tablename__ = "payload_cache"

    hash: Mapped[str] = mapped_column(String, primary_key=True)
    output: Mapped[str] = mapped_column(String, nullable=False)
