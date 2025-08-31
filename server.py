from flask import Flask
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Date,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import date 

# Create Flask app instance
app = Flask(__name__)

#database setup
engine = create_engine("sqlite:///budget_manager.db") # Way to connect to database
Base = declarative_base() # Base to define models, all models inherit from this
Session = sessionmaker(bind=engine) # Session factory, prepares sessions
session = Session() # Create a session to interact with the database (add,commit,...)

# Define models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(30), nullable=False)
    expenses = relationship("Expense", back_populates="user") #user.expenses, List all 

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(200))
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False, default=date.today)
    category = Column(Enum("Food", "Education", "Entertainment"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))       # Foreign key to users table
    user = relationship("User", back_populates="expense")  # Expense.user.name


#Create tables
Base.metadata.create_all(engine)

# Ensures the server runs only when this script is executed directly
if __name__ == "__main__":
    app.run(debug=True)
