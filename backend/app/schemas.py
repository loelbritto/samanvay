from datetime import date
from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class LoginInput(StrictInput):
    username: str = Field(min_length=3, max_length=120)
    password: str = Field(min_length=1, max_length=200)


class FactsInput(StrictInput):
    incident_reference: str = Field(default='',max_length=100)
    incident_date: date | None = None
    receipt_reference: str = Field(default='',max_length=100)
    amount: str = Field(default='',max_length=80)
    remedy: str = Field(default='',max_length=300)


class CaseInput(StrictInput):
    institution_id: str = Field(min_length=1, max_length=50)
    original_institution_text: str = Field(min_length=2, max_length=500)
    received_date: date
    subject: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10, max_length=20000)
    category: str = Field(min_length=1, max_length=80)
    next_action: str = Field(min_length=3, max_length=500)
    expected_disposal_date: date | None = None
    complainant_token: str = Field(min_length=6, max_length=80)
    synthetic: bool = True
    facts: FactsInput = Field(default_factory=FactsInput)

    @field_validator("complainant_token")
    @classmethod
    def demo_token(cls, value):
        if not value.startswith("DEMO-"):
            raise ValueError("Use a fictional DEMO- complainant token.")
        return value


class AssignmentInput(StrictInput):
    owner_id: str
    expected_version: int = Field(ge=1)
    reason: str = Field(min_length=5, max_length=500)
