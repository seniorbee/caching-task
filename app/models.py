from typing import Self

from pydantic import BaseModel, Field, model_validator


class PayloadRequest(BaseModel):
    list_1: list[str] = Field(min_length=1, max_length=1000)
    list_2: list[str] = Field(min_length=1, max_length=1000)

    @model_validator(mode="after")
    def lists_must_have_same_length(self) -> Self:
        # Interleaving pairs items by position, so a length mismatch has no valid output.
        if len(self.list_1) != len(self.list_2):
            raise ValueError("list_1 and list_2 must have the same length")
        return self


class PayloadResponse(BaseModel):
    id: int


class PayloadOutput(BaseModel):
    output: str