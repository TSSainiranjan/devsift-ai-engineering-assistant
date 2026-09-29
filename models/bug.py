from typing import Literal

from pydantic import BaseModel, Field


class BugAnalysis(BaseModel):
    title: str = Field(
        description="Short, clear title describing the bug."
    )

    description: str = Field(
        description="Concise description of the reported problem."
    )

    severity: Literal["Low", "Medium", "High", "Critical"] = Field(
        description="Bug severity: Low, Medium, High, or Critical."
    )

    category: str = Field(
        description="Functional area affected by the bug."
    )

    environment: list[str] = Field(
        default_factory=list,
        description=(
            "Known environment details such as browser, OS, "
            "device, or application version."
        ),
    )

    reproduction_steps: list[str] = Field(
        default_factory=list,
        description=(
            "Steps that can be derived from the bug report "
            "to reproduce the issue."
        ),
    )

    expected_behavior: str = Field(
        description=(
            "What should happen according to the report "
            "or normal expected behavior."
        )
    )

    actual_behavior: str = Field(
        description="What actually happens according to the report."
    )

    missing_information: list[str] = Field(
        default_factory=list,
        description=(
            "Important information missing from the bug report."
        ),
    )

    acceptance_criteria: list[str] = Field(
        default_factory=list,
        description=(
            "Basic criteria that should be satisfied "
            "when the bug is fixed."
        ),
    )