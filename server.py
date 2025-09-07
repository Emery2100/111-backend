from unicodedata import category
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

#get user by id
@app.get("/api/users/<user_id>")
def get_user(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404

    user_data = {"id": user.id, "username": user.username}
    return jsonify(user_data), 200

#update a user
@app.put("/api/users/<user_id>")
def update_user(user_id):
    data = request.get_json()
    new_username = data.get("username")
    new_password = data.get("password")

    user = session.query(User).filter_by(id=user_id).first()

    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if new_username:
        user.username = new_username
    if new_password:
        user.password = new_password

    session.commit()
    return jsonify({"message": "User updated successfully"}), 200

#delete a user
@app.delete("/api/users/<user_id>")
def delete_user(user_id):
    user = session.query(User).filter_by(id=user_id).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    session.delete(user)
    session.commit()
    return jsonify({"message": "User deleted successfully"}), 200

# Expense routes
@app.post("/api/expenses")
def create_expense():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    amount = data.get("amount")
    category = data.get("category")
    user_id = data.get("user_id")

#validate category
    allowed_categories = ["Food", "Education", "Entertainment"] # set, not allowed duplicates

    if category not in allowed_categories:
        return jsonify({"error": "Invalid category"}), 400
    
    new_expense = Expense(
        title=title,
        description=description,
        amount=amount,
        category=category,
        user_id=user_id
    )
    session.add(new_expense) #Add to session
    session.commit() #Commit to DB

    return jsonify({"message": "Expense created successfully"}), 201

@app.get("/api/expenses/<expense_id>")
def get_expense(expense_id):
    expense = session.query(Expense).filter_by(id=expense_id).first()
    if not expense:
        return jsonify({"error": "Expense not found"}), 404

    expense_data = {
        "id": expense.id,
        "title": expense.title,
        "description": expense.description,
        "amount": expense.amount,
        "date": expense.date.isoformat(),
        "category": expense.category,
        "user_id": expense.user_id
    }

    return jsonify(expense_data), 200

@app.put("/api/expenses/<expense_id>")
def update_expense(expense_id):
    data = request.get_json()
    expense = session.query(Expense).filter_by(id=expense_id).first()

    if not expense:
        return jsonify({"error": "Expense not found"}), 404

    title = data.get("title")
    description = data.get("description")
    amount = data.get("amount")
    category = data.get("category")

    if title:
        expense.title = title
    if description:
        expense.description = description
    if amount:
        expense.amount = amount
    if category:
        allowed_categories = ["Food", "Education", "Entertainment"]
        if category not in allowed_categories:
            return jsonify({"error": "Invalid category"}), 400
        expense.category = category

    session.commit()
    return jsonify({"message": "Expense updated successfully"}), 200

@app.delete("/api/expenses/<expense_id>")
def delete_expense(expense_id):
    expense = session.query(Expense).filter_by(id=expense_id).first()

    if not expense:
        return jsonify({"error": "Expense not found"}), 404

    session.delete(expense)
    session.commit()
    return jsonify({"message": "Expense deleted successfully"}), 200

# Ensures the server runs only when this script is executed directly
if __name__ == "__main__":
    app.run(debug=True)



