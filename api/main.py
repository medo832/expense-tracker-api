from fastapi import FastAPI , HTTPException
from pydantic import BaseModel
import uuid
from datetime import datetime
import storage


class ExpenseIN(BaseModel):
    product_name: str
    quantity: float
    unit: str
    category: str
    price_paid: float
    currency_paid: str


class Expense(ExpenseIN):
    id: str
    created_at: str
    model_config = {"from_attributes": True}


app = FastAPI(title="Expense tracker API", version="0.1.0")
storage.init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/settings")
def get_settings():
    return {"base_currency": "EGP"}


@app.post("/expenses", status_code=201)
def create_expense(expense: ExpenseIN):
    expense = Expense(
        id=str(uuid.uuid4().hex[:8]),
        created_at=datetime.now().astimezone().isoformat(),
        **expense.model_dump()
    )
    storage.save_expense(expense.model_dump())
    return expense


@app.get("/expenses", response_model=list[Expense])
def get_expenses():
    return storage.get_all()


@app.delete("/expenses/{id}", status_code=204)
def delete_expense(id:str):
    if not storage.delete_expense(id):
        raise HTTPException(status_code=404, detail="Expense not found")