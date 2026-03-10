from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Simple in-memory database
db = []

class Employee(BaseModel):
    id: int
    name: str
    pay: int

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "employees": db})

@app.get("/add", response_class=HTMLResponse)
async def add_page(request: Request):
    return templates.TemplateResponse("add_employee.html", {"request": request})

@app.post("/add")
async def add_employee(id: int = Form(...), name: str = Form(...), pay: int = Form(...)):
    new_employee = {"id": id, "name": name, "pay": pay}
    db.append(new_employee)
    return RedirectResponse(url="/", status_code=303)

@app.get("/delete", response_class=HTMLResponse)
async def delete_page(request: Request):
    return templates.TemplateResponse("delete_employee.html", {"request": request})

@app.post("/delete")
async def delete_employee(id: int = Form(...)):
    global db
    # Filter the list to exclude the matching ID
    db = [emp for emp in db if emp['id'] != id]
    return RedirectResponse(url="/", status_code=303)

# New route to delete directly from the table via a URL parameter
@app.get("/delete/{emp_id}")
async def delete_by_id(emp_id: int):
    global db
    db = [emp for emp in db if emp['id'] != emp_id]
    return RedirectResponse(url="/", status_code=303)