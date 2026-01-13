import os
from datetime import datetime, date as DateType
from typing import List, Optional
from sqlmodel import Field, Session, SQLModel, create_engine, select, col
from fastmcp import FastMCP
from schema import Expense

mcp = FastMCP("Expense Tracker")

DB_URL = "postgresql+psycopg2://postgres:Sheam000@localhost:5432/expenses"
engine = create_engine(DB_URL)

def init_db():
    SQLModel.metadata.create_all(engine)


@mcp.tool
def add_expense(reason: str, amount: float, date_str: Optional[str] = None) -> str:
    """Add a new expense. Date format: YYYY-MM-DD (defaults to today)"""
    init_db()
    expense_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.now().date()
    
    with Session(engine) as session:
        new_expense = Expense(reason=reason, amount=amount, date=expense_date)
        session.add(new_expense)
        session.commit()
        session.refresh(new_expense)
        return f"Saved: {new_expense.reason} (${new_expense.amount}) on {new_expense.date} (ID: {new_expense.id})"

@mcp.tool
def list_expenses(min_price: Optional[float] = None, date_filter: Optional[str] = None) -> List[dict]:
    """List all expenses with optional filtering by price or date."""
    init_db()
    with Session(engine) as session:
        statement = select(Expense)
        if min_price:
            statement = statement.where(Expense.amount >= min_price)
        if date_filter:
            target_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
            statement = statement.where(Expense.date == target_date)
            
        results = session.exec(statement).all()
        return [item.model_dump() for item in results]

@mcp.tool
def get_expense(expense_id: int) -> str:
    """Fetch details of a specific expense by ID."""
    init_db()
    with Session(engine) as session:
        expense = session.get(Expense, expense_id)
        return str(expense.model_dump()) if expense else "Expense not found."

@mcp.tool
def update_expense(expense_id: int, reason: Optional[str] = None, amount: Optional[float] = None) -> str:
    """Update an existing expense record."""
    init_db()
    with Session(engine) as session:
        db_expense = session.get(Expense, expense_id)
        if not db_expense:
            return "Expense not found."
        
        if reason: db_expense.reason = reason
        if amount: db_expense.amount = amount
        
        session.add(db_expense)
        session.commit()
        session.refresh(db_expense)
        return f"Successfully updated expense {expense_id}."

@mcp.tool
def delete_expense(expense_id: int) -> str:
    """Delete an expense record."""
    init_db()
    with Session(engine) as session:
        expense = session.get(Expense, expense_id)
        if not expense:
            return "Expense not found."
        session.delete(expense)
        session.commit()
        return f"Expense {expense_id} deleted."

if __name__ == "__main__":
    mcp.run()