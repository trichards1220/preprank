from datetime import datetime
from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    tier: str  # premium_monthly, season_pass, annual


class CheckoutResponse(BaseModel):
    session_id: str
    url: str
    tier: str
    price: float
    name: str


class SubscriptionStatusOut(BaseModel):
    tier: str
    expires: datetime | None = None
    is_active: bool

    model_config = {"from_attributes": True}
