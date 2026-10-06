from sqlmodel import Field, SQLModel


class TransformationCache(SQLModel, table=True):
    input: str = Field(primary_key=True)
    output: str


class PayloadCache(SQLModel, table=True):
    hash: str = Field(primary_key=True)
    output: str