from typing import Literal

from pydantic import BaseModel, Field


class MeetingTicket(BaseModel):
    title: str = Field(
        description="Short, clear title suitable for an engineering ticket."
    )

    user_story: str = Field(
        description=(
            "User story written in the format: "
            "As a [user], I want [goal], so that [benefit]."
        )
    )

    description: str = Field(
        description="Detailed description of the requested functionality."
    )

    acceptance_criteria: list[str] = Field(
        default_factory=list,
        description=(
            "Acceptance criteria written using "
            "Given/When/Then style."
        )
    )

    priority: Literal["Low", "Medium", "High", "Critical"] = Field(
        description="Priority based only on evidence in the meeting notes."
    )

    edge_cases: list[str] = Field(
        default_factory=list,
        description="Potential edge cases explicitly mentioned or reasonably implied by the requirements."
    )

    dependencies: list[str] = Field(
        default_factory=list,
        description="Systems, features, teams, or prerequisites that the ticket depends on."
    )

    open_questions: list[str] = Field(
        default_factory=list,
        description="Important questions that must be clarified before implementation."
    )


class MeetingAnalysis(BaseModel):
    tickets: list[MeetingTicket] = Field(
        default_factory=list,
        description="Engineering tickets generated from the meeting notes."
    )