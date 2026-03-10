from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_all, Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# --- DATABASE SETUP ---
DATABASE_URL = "sqlite:///./payroll.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the Employee table
class EmployeeDB(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    pay = Column(Integer)

# Create the database file and table
Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ROUTES ---

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    employees = db.query(EmployeeDB).all()
    return templates.TemplateResponse("index.html", {"request": request, "employees": employees})

@app.get("/add", response_class=HTMLResponse)
async def add_page(request: Request):
    return templates.TemplateResponse("add_employee.html", {"request": request})

@app.post("/add")
async def add_employee(id: int = Form(...), name: str = Form(...), pay: int = Form(...), db: Session = Depends(get_db)):
    new_emp = EmployeeDB(id=id, name=name, pay=pay)
    db.add(new_emp)
    db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.get("/delete/{emp_id}")
async def delete_employee(emp_id: int, db: Session = Depends(get_db)):
    emp = db.query(EmployeeDB).filter(EmployeeDB.id == emp_id).first()
    if emp:
        db.delete(emp)
        db.commit()
    return RedirectResponse(url="/", status_code=303)