from sqlalchemy import func, String, create_engine, Integer, Date, Numeric
from sqlalchemy.orm import DeclarativeBase, mapped_column

from settings import SQLALCHEMY_DATABASE_URI

engine = create_engine(SQLALCHEMY_DATABASE_URI)


class Base(DeclarativeBase):
    pass


class Operation(Base):
    __tablename__ = "operation"
    id = mapped_column(Integer, primary_key=True)
    description = mapped_column(String)
    date = mapped_column(Date, server_default=func.now())
    value = mapped_column(Numeric(10, 2))
