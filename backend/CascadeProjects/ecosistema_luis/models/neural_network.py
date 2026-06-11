import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

class TaskPrioritizer(nn.Module):
    """Red neuronal para priorizar tareas basado en contexto"""
    
    def __init__(self, input_size: int = 10, hidden_size: int = 64, output_size: int = 3):
        super(TaskPrioritizer, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size // 2, output_size),
            nn.Softmax(dim=1)
        )
        
    def forward(self, x):
        return self.network(x)

class ProductivityBot:
    """Bot principal con capacidades de IA"""
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = TaskPrioritizer().to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.CrossEntropyLoss()
        
        # Contextos predefinidos
        self.contexts = {
            "Local Xicopack": {"priority": 1, "tasks": ["limpieza", "atencion", "cotizaciones"]},
            "Casa / Estudio": {"priority": 2, "tasks": ["optimizacion", "inventario", "musica"]},
            "Evento Musical": {"priority": 3, "tasks": ["ensayo", "promocion", "logistica"]}
        }
        
    def extract_features(self, task_data: Dict[str, Any]) -> np.ndarray:
        """Extraer características de una tarea para la red neuronal"""
        features = []
        
        # Características temporales
        due_date = task_data.get('due_date')
        if due_date:
            days_until = (due_date - datetime.now()).days
            features.extend([
                min(days_until / 30, 1.0),  # Normalizado a 0-1
                task_data.get('urgency', 0.5),
                task_data.get('importance', 0.5)
            ])
        else:
            features.extend([0.5, 0.5, 0.5])
            
        # Características de contexto
        context = task_data.get('context', '')
        context_features = [
            1.0 if "Xicopack" in context else 0.0,
            1.0 if "Casa" in context else 0.0,
            1.0 if "Musica" in context else 0.0
        ]
        features.extend(context_features)
        
        # Características de tarea
        features.extend([
            len(task_data.get('description', '')) / 100,  # Longitud normalizada
            task_data.get('complexity', 0.5),
            1.0 if task_data.get('recurring', False) else 0.0,
            task_data.get('energy_required', 0.5)
        ])
        
        return np.array(features, dtype=np.float32)
    
    def predict_priority(self, task_data: Dict[str, Any]) -> Dict[str, float]:
        """Predecir prioridad de una tarea"""
        self.model.eval()
        with torch.no_grad():
            features = self.extract_features(task_data)
            features_tensor = torch.FloatTensor([features]).to(self.device)
            
            priorities = self.model(features_tensor)
            priorities_list = priorities.cpu().numpy()[0]
            
            return {
                "baja": float(priorities_list[0]),
                "media": float(priorities_list[1]),
                "alta": float(priorities_list[2])
            }
    
    def get_context_recommendations(self, context: str) -> List[str]:
        """Obtener recomendaciones basadas en contexto actual"""
        if context in self.contexts:
            return self.contexts[context]["tasks"]
        return ["sin_recomendaciones"]
    
    def analyze_productivity_pattern(self, tasks_history: List[Dict]) -> Dict[str, Any]:
        """Analizar patrones de productividad"""
        if not tasks_history:
            return {"pattern": "insufficient_data"}
            
        # Análisis simple de patrones
        completed_by_hour = {}
        for task in tasks_history:
            if task.get('completed_at'):
                hour = task['completed_at'].hour
                completed_by_hour[hour] = completed_by_hour.get(hour, 0) + 1
                
        best_hour = max(completed_by_hour.items(), key=lambda x: x[1])[0] if completed_by_hour else 10
        
        return {
            "best_productivity_hour": best_hour,
            "total_completed": len(tasks_history),
            "completion_rate": sum(1 for t in tasks_history if t.get('completed')) / len(tasks_history),
            "pattern": "analyzed"
        }

class SmartScheduler:
    """Planificador inteligente con integración de calendarios"""
    
    def __init__(self):
        self.events = []
        
    def add_calendar_event(self, title: str, start_time: datetime, end_time: datetime, 
                          event_type: str = "task"):
        """Agregar evento al calendario"""
        event = {
            "title": title,
            "start": start_time,
            "end": end_time,
            "type": event_type,
            "created_at": datetime.now()
        }
        self.events.append(event)
        return event
    
    def get_conflicts(self, new_event: Dict) -> List[Dict]:
        """Detectar conflictos de horario"""
        conflicts = []
        new_start = new_event["start"]
        new_end = new_event["end"]
        
        for event in self.events:
            if (new_start < event["end"] and new_end > event["start"]):
                conflicts.append(event)
                
        return conflicts
    
    def suggest_optimal_time(self, duration_minutes: int, preferred_hours: List[int] = None) -> datetime:
        """Sugerir tiempo óptimo para nueva tarea"""
        from datetime import timedelta
        
        if preferred_hours is None:
            preferred_hours = [9, 10, 11, 14, 15, 16]
            
        now = datetime.now()
        duration = timedelta(minutes=duration_minutes)
        
        for day_offset in range(7):  # Buscar en los próximos 7 días
            test_date = now + timedelta(days=day_offset)
            for hour in preferred_hours:
                test_start = test_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                test_end = test_start + duration
                
                test_event = {"start": test_start, "end": test_end}
                if not self.get_conflicts(test_event):
                    return test_start
                    
        # Si no encuentra hora ideal, return la primera disponible
        return now + timedelta(hours=1)
