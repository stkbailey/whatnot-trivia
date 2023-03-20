import pydantic
import datetime
import uuid


class Quiz(pydantic.BaseModel):
    question: str
    answer: str
    quiz_id: str = uuid.uuid4().hex
    started_at: datetime.datetime = None
    ended_at: datetime.datetime = None


class Answer(pydantic.BaseModel):
    quiz_id: str
    username: str
    created_at: datetime.datetime
    value: str
    is_correct: bool = None
