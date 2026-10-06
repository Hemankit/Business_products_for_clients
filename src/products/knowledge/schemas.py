from pydantic import BaseModel, Field


class KnowledgeDocument(BaseModel):
    document_id: str
    title: str

    content: str

    source: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class RetrievedChunk(BaseModel):
    document_id: str
    title: str

    content: str

    score: float

    metadata: dict[str, str] = Field(default_factory=dict)


class KnowledgeAnswer(BaseModel):
    answer: str

    sources: list[str] = Field(default_factory=list)