from pydantic import BaseModel


class SchoolOut(BaseModel):
    id: int
    name: str
    city: str | None = None
    parish: str | None = None
    classification: str | None = None
    division: str | None = None
    select_status: str | None = None
    enrollment: int | None = None

    model_config = {"from_attributes": True}
