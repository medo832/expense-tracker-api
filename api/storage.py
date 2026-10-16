from sqlalchemy import create_engine, String, Float, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


DATABASE_URL = "sqlite:///./expenses.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)




class Base(DeclarativeBase):
    pass


class ExpenseRow(Base):
    __tablename__ = "expenses"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    product_name: Mapped[str] = mapped_column(String)
    quantity: Mapped[float] = mapped_column(Float)
    unit: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String)
    price_paid: Mapped[float] = mapped_column(Float)
    currency_paid: Mapped[str] = mapped_column(String)
    created_at: Mapped[str] = mapped_column(String)


def init_db():
    Base.metadata.create_all(engine)

def save_expense(expense_dict):
    with SessionLocal() as session:
        row = ExpenseRow(**expense_dict)
        session.add(row)
        session.commit()
# For 
def get_all():
    with SessionLocal() as session:
        return session.scalars(select(ExpenseRow)).all()

# For the DELETE endpoint, we need a function to delete an expense by id
def delete_expense(id):
    with SessionLocal() as session:
        row = session.get(ExpenseRow, id)
        if row is None:
            return False
        session.delete(row)
        session.commit()
        return True

if __name__ == "__main__":
    init_db()
    print("database ready ->", DATABASE_URL)
