from sqlmodel import SQLModel, Field
from datetime import datetime, date as DateType
from typing import Optional

class Expense(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    reason: str
    amount: float
    date: DateType = Field(default_factory=lambda: datetime.now().date())