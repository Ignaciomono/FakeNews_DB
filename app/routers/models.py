"""
Router para gestión de modelos de IA
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict
from pydantic import BaseModel

from app.utils.model_manager import model_manager, FakeNewsModel
from app.services.ai_analyzer import ai_analyzer
from app.config import settings

router = APIRouter(prefix="/models", tags=["models"])


class ModelChangeRequest(BaseModel):
    model_name: str


class CurrentModelResponse(BaseModel):
    current_model: str
    model_info: Dict


class ModelsListResponse(BaseModel):
    total_models: int
    current_model: str
    available_models: List[Dict]


@router.get("/", response_model=ModelsListResponse)
async def list_models():
    """
    Lista todos los modelos de fake news disponibles con su información.
    """
    models_list = model_manager.list_all_models()
    
    return ModelsListResponse(
        total_models=len(models_list),
        current_model=settings.HF_MODEL_NAME,
        available_models=models_list
    )


@router.get("/current", response_model=CurrentModelResponse)
async def get_current_model():
    """
    Obtiene el modelo actualmente en uso.
    """
    current = settings.HF_MODEL_NAME
    info = model_manager.get_model_info(current)
    
    return CurrentModelResponse(
        current_model=current,
        model_info=info
    )


@router.get("/spanish")
async def get_spanish_models():
    """
    Lista solo los modelos especializados en español.
    """
    spanish_models = model_manager.get_spanish_models()
    return {
        "total": len(spanish_models),
        "models": [
            {
                "model_id": model_id,
                **model_manager.get_model_info(model_id)
            }
            for model_id in spanish_models
        ]
    }


@router.get("/english")
async def get_english_models():
    """
    Lista solo los modelos especializados en inglés.
    """
    english_models = model_manager.get_english_models()
    return {
        "total": len(english_models),
        "models": [
            {
                "model_id": model_id,
                **model_manager.get_model_info(model_id)
            }
            for model_id in english_models
        ]
    }


@router.post("/change")
async def change_model(request: ModelChangeRequest):
    """
    Cambia el modelo de IA actual (requiere reinicio en producción).
    
    En desarrollo, esto cambiará el modelo inmediatamente.
    En producción (Vercel), necesitarás actualizar la variable de entorno HF_MODEL_NAME.
    """
    # Validar que el modelo existe
    all_models = [model.value for model in FakeNewsModel]
    
    if request.model_name not in all_models:
        raise HTTPException(
            status_code=400,
            detail=f"Modelo no válido. Modelos disponibles: {all_models}"
        )
    
    # Actualizar el modelo (solo en runtime, no persiste)
    settings.HF_MODEL_NAME = request.model_name
    ai_analyzer.model_name = request.model_name
    ai_analyzer.api_url = f"{settings.HF_API_URL}{request.model_name}"
    
    model_info = model_manager.get_model_info(request.model_name)
    
    return {
        "success": True,
        "message": "Modelo cambiado exitosamente (solo en esta sesión)",
        "new_model": request.model_name,
        "model_info": model_info,
        "note": "En producción, actualiza la variable de entorno HF_MODEL_NAME para persistir el cambio"
    }


@router.get("/info/{model_name:path}")
async def get_model_info(model_name: str):
    """
    Obtiene información detallada de un modelo específico.
    """
    info = model_manager.get_model_info(model_name)
    
    return {
        "model_id": model_name,
        **info
    }
