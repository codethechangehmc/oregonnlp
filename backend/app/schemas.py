from pydantic import BaseModel


class TopicResult(BaseModel):
    topic_id: int
    label: str
    description: str
    category: str
    count: int
    percentage: float
    keywords: list[str]
    sample_responses: list[str]


class Assignment(BaseModel):
    id: int
    text: str
    topic_id: int
    topic_label: str
    probability: float


class Summary(BaseModel):
    total_responses: int
    num_topics: int


class AnalysisResponse(BaseModel):
    analysis_id: str
    summary: Summary
    topics: list[TopicResult]
    assignments: list[Assignment]


class LibraryItem(BaseModel):
    id: str
    filename: str
    title: str | None
    created_at: str
    total_responses: int
    num_topics: int


class SaveRequest(BaseModel):
    title: str | None = None
