from flask import Flask, jsonify, request
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
    user = relationship("User", back_populates="expenses")  # Expense.user.name


#Create tables
Base.metadata.create_all(engine)

#Health check route 
@app.get("/api/health")
def health_check():
    return jsonify({"status": "OK"}), 200

# User routes
@app.post("/api/register")
def register_user():
    data = request.get_json()
    username = data.get("username") #extract username
    password = data.get("password") #extract password

    #Validation
    existing_user = session.query(User).filter_by(username=username).first()
    if existing_user is not None:
        return jsonify({"error": "Username already exists"}), 400

    print(data)
    print(username)
    print(password)

    new_user = User(username = username, password = password) # Create user instance
    session.add(new_user) # Add to session
    session.commit() # Commit to DB

    return jsonify({"message": "User registered successfully"}), 201

# Login
@app.post("/api/login")
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400
    
    user = session.query(User).filter_by(username=username, password=password).first()

    if user and user.password == password:
        return jsonify({"Succuss": "Login successful"}), 200
    
    return jsonify({"error": "Invalid username or password"}), 401
# Ensures the server runs only when this script is executed directly
if __name__ == "__main__":
    app.run(debug=True)
