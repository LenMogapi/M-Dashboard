from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Weblog(Base):
    __tablename__ = "weblogs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False)
    ip = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Float, nullable=False)
    user_agent = Column(String, nullable=False)

class SalesMetric(Base):
    __tablename__ = "sales_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False)  # Date and time of the sale
    product = Column(String, nullable=False)  # Name of the product sold
    salesperson = Column(String, nullable=False)  # Salesperson responsible for the sale
    revenue = Column(Float, nullable=False)  # Revenue generated from the sale
    profit = Column(Float, nullable=False)  # Profit earned from the sale
    country = Column(String, nullable=True)  # Country where the sale occurred

    