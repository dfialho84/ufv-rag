from pydantic import BaseModel, Field


class QuestionsList(BaseModel):
    """Represents a list of questions"""

    questions: list[str] = Field(description="The list of questions")
