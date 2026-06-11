import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
from datetime import datetime

from database.database import get_db, create_tables
from database.models import *
from models.neural_network import ProductivityBot, SmartScheduler
from utils.auth import create_access_token, verify_token, get_password_hash
from pydantic import BaseModel

# Inicialización
app = FastAPI(
    title="Ecosistema Luis API",
    description="API REST para Productividad con IA",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seguridad
security = HTTPBearer()
bot = ProductivityBot()
scheduler = SmartScheduler()

# Modelos Pydantic
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "media"
    context: Optional[str] = None
    due_date: Optional[datetime] = None
    urgency: Optional[float] = 0.5
    importance: Optional[float] = 0.5
    complexity: Optional[float] = 0.5
    energy_required: Optional[float] = 0.5
    recurring: Optional[bool] = False
    estimated_duration: Optional[int] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: str
    status: str
    context: Optional[str]
    due_date: Optional[datetime]
    ai_priority_score: Optional[dict]
    ai_recommendations: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True

class NoteCreate(BaseModel):
    title: str
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    is_favorite: Optional[bool] = False

class CalendarEventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    event_type: Optional[str] = "task"
    is_all_day: Optional[bool] = False

class InventoryItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    sku: Optional[str] = None
    quantity: Optional[int] = 0
    min_quantity: Optional[int] = 1
    price: Optional[float] = None
    cost: Optional[float] = None
    supplier: Optional[str] = None
    location: Optional[str] = None

class LearningItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    resource_type: Optional[str] = None
    url: Optional[str] = None
    priority: Optional[str] = "media"
    estimated_hours: Optional[float] = None
    tags: Optional[List[str]] = []

# Endpoints de Autenticación
@app.post("/auth/login")
async def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoints de Tasks
@app.get("/api/v1/tasks", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    context: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Verificar token
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    
    query = db.query(Task).filter(Task.owner_id == user.id)
    
    if context:
        query = query.filter(Task.context == context)
    if status:
        query = query.filter(Task.status == status)
        
    tasks = query.offset(skip).limit(limit).all()
    return tasks

@app.post("/api/v1/tasks", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    
    # Predecir prioridad con IA
    task_data = task.dict()
    ai_priority = bot.predict_priority(task_data)
    recommendations = bot.get_context_recommendations(task.context or "")
    
    db_task = Task(
        **task_data,
        owner_id=user.id,
        ai_priority_score=ai_priority,
        ai_recommendations={"recommendations": recommendations}
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    return db_task

@app.put("/api/v1/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: dict,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    # Actualizar campos
    for field, value in task_update.items():
        if hasattr(task, field):
            setattr(task, field, value)
    
    task.updated_at = datetime.utcnow()
    
    # Si se marca como completada
    if task_update.get("status") == "completada" and not task.completed_at:
        task.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(task)
    
    return task

@app.delete("/api/v1/tasks/{task_id}")
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    db.delete(task)
    db.commit()
    
    return {"message": "Tarea eliminada"}

# Endpoints de Notes
@app.get("/api/v1/notes")
async def get_notes(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    
    query = db.query(Note).filter(Note.owner_id == user.id)
    if category:
        query = query.filter(Note.category == category)
        
    notes = query.offset(skip).limit(limit).all()
    return notes

@app.post("/api/v1/notes")
async def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    
    db_note = Note(**note.dict(), owner_id=user.id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    return db_note

# Endpoints de Calendar Events
@app.get("/api/v1/calendar-events")
async def get_calendar_events(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    
    query = db.query(CalendarEvent).filter(CalendarEvent.owner_id == user.id)
    
    if start_date:
        query = query.filter(CalendarEvent.start_time >= start_date)
    if end_date:
        query = query.filter(CalendarEvent.start_time <= end_date)
        
    events = query.all()
    return events

@app.post("/api/v1/calendar-events")
async def create_calendar_event(
    event: CalendarEventCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    
    # Verificar conflictos
    event_data = event.dict()
    conflicts = scheduler.get_conflicts(event_data)
    
    db_event = CalendarEvent(**event_data, owner_id=user.id)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    return {
        **db_event.__dict__,
        "conflicts": conflicts
    }

# Endpoints de Inventory
@app.get("/api/v1/inventory")
async def get_inventory(
    category: Optional[str] = None,
    low_stock: bool = False,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    
    query = db.query(InventoryItem).filter(InventoryItem.owner_id == user.id)
    
    if category:
        query = query.filter(InventoryItem.category == category)
    if low_stock:
        query = query.filter(InventoryItem.quantity <= InventoryItem.min_quantity)
        
    items = query.all()
    return items

@app.post("/api/v1/inventory")
async def create_inventory_item(
    item: InventoryItemCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    
    db_item = InventoryItem(**item.dict(), owner_id=user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    return db_item

# Endpoints de Learning
@app.get("/api/v1/learning")
async def get_learning_items(
    status: Optional[str] = None,
    resource_type: Optional[str] = None,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    
    query = db.query(LearningItem).filter(LearningItem.owner_id == user.id)
    
    if status:
        query = query.filter(LearningItem.status == status)
    if resource_type:
        query = query.filter(LearningItem.resource_type == resource_type)
        
    items = query.all()
    return items

@app.post("/api/v1/learning")
async def create_learning_item(
    item: LearningItemCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    
    db_item = LearningItem(**item.dict(), owner_id=user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    return db_item

# Endpoint de AI Priority Logs
@app.get("/api/v1/ai-priority-logs")
async def get_ai_logs(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    
    logs = db.query(AIPriorityLog).filter(
        AIPriorityLog.user_id == user.id
    ).offset(skip).limit(limit).all()
    
    return logs

# Endpoint de Analytics
@app.get("/api/v1/analytics/productivity")
async def get_productivity_analytics(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    
    # Obtener tareas completadas
    completed_tasks = db.query(Task).filter(
        Task.owner_id == user.id,
        Task.status == "completada"
    ).all()
    
    # Análisis con IA
    task_history = [
        {
            "completed_at": t.completed_at,
            "priority": t.priority,
            "context": t.context,
            "completed": True
        } for t in completed_tasks
    ]
    
    productivity_pattern = bot.analyze_productivity_pattern(task_history)
    
    return {
        "total_completed": len(completed_tasks),
        "productivity_pattern": productivity_pattern,
        "completion_by_context": {},
        "completion_by_priority": {}
    }

# Inicialización
@app.on_event("startup")
async def startup_event():
    create_tables()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
