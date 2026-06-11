from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    tasks = relationship("Task", back_populates="owner")
    notes = relationship("Note", back_populates="owner")
    calendar_events = relationship("CalendarEvent", back_populates="owner")
    inventory_items = relationship("InventoryItem", back_populates="owner")
    learning_items = relationship("LearningItem", back_populates="owner")
    ai_logs = relationship("AIPriorityLog", back_populates="user")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    priority = Column(String, default="media")  # baja, media, alta
    status = Column(String, default="pendiente")  # pendiente, en_progreso, completada
    context = Column(String)  # Local Xicopack, Casa/Estudio, etc.
    due_date = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Campos para IA
    urgency = Column(Float, default=0.5)
    importance = Column(Float, default=0.5)
    complexity = Column(Float, default=0.5)
    energy_required = Column(Float, default=0.5)
    recurring = Column(Boolean, default=False)
    estimated_duration = Column(Integer)  # minutos
    
    # IA predictions
    ai_priority_score = Column(JSON)
    ai_recommendations = Column(JSON)
    
    # Relaciones
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="tasks")

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text)
    category = Column(String)  # dialogos, ideas, proyectos, etc.
    tags = Column(JSON)  # lista de tags
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="notes")

class CalendarEvent(Base):
    __tablename__ = "calendar_events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String)
    event_type = Column(String)  # task, meeting, personal, musical
    is_all_day = Column(Boolean, default=False)
    calendar_source = Column(String)  # local, google, outlook
    external_id = Column(String)  # ID del calendario externo
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="calendar_events")

class InventoryItem(Base):
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)  # productos, materiales, equipos
    sku = Column(String, unique=True)
    quantity = Column(Integer, default=0)
    min_quantity = Column(Integer, default=1)
    price = Column(Float)
    cost = Column(Float)
    supplier = Column(String)
    location = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="inventory_items")

class LearningItem(Base):
    __tablename__ = "learning"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    resource_type = Column(String)  # curso, libro, video, articulo
    url = Column(String)
    progress = Column(Float, default=0.0)  # 0-100
    status = Column(String, default="no_iniciado")  # no_iniciado, en_progreso, completado
    priority = Column(String, default="media")
    estimated_hours = Column(Float)
    tags = Column(JSON)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relaciones
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="learning_items")

class AIPriorityLog(Base):
    __tablename__ = "ai_priority_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    action = Column(String)  # prediction, recommendation, analysis
    input_data = Column(JSON)
    output_data = Column(JSON)
    confidence_score = Column(Float)
    model_version = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="ai_logs")

class ShopifyIntegration(Base):
    __tablename__ = "shopify_integration"
    
    id = Column(Integer, primary_key=True, index=True)
    store_url = Column(String)
    api_key = Column(String)
    password = Column(String)
    webhook_secret = Column(String)
    is_active = Column(Boolean, default=False)
    last_sync = Column(DateTime)
    sync_status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    owner_id = Column(Integer, ForeignKey("users.id"))

class MusicProject(Base):
    __tablename__ = "music_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    project_type = Column(String)  # album, single, ep, collaboration
    status = Column(String, default="idea")  # idea, writing, recording, mixing, mastered, released
    target_date = Column(DateTime)
    collaborators = Column(JSON)  # lista de colaboradores
    instruments = Column(JSON)  # instrumentos involucrados
    genre = Column(String)
    bpm = Column(Integer)
    key = Column(String)
    file_path = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    owner_id = Column(Integer, ForeignKey("users.id"))
