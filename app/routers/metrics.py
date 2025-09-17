from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.schemas.news import SummaryMetrics, TimeseriesResponse
from app.services.metrics_service import metrics_service

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/summary", response_model=SummaryMetrics)
async def get_summary_metrics(db: AsyncSession = Depends(get_db)):
    """
    Obtiene métricas resumidas de todos los análisis realizados.
    
    Incluye:
    - Total de análisis
    - Conteo por categoría (fake, real, uncertain)
    - Porcentajes por categoría
    - Promedios de score y confianza
    - Distribución por tipo de fuente
    """
    return await metrics_service.get_summary_metrics(db)

@router.get("/timeseries", response_model=TimeseriesResponse)
async def get_timeseries_metrics(
    days: int = Query(default=7, ge=1, le=365, description="Número de días hacia atrás"),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene datos de series temporales para análisis de tendencias.
    
    Parámetros:
    - days: Número de días hacia atrás a incluir (1-365)
    
    Retorna datos diarios incluyendo:
    - Conteos por categoría
    - Promedios de score y confianza
    - Total de análisis por día
    """
    return await metrics_service.get_timeseries_data(db, days)

@router.post("/refresh-daily")
async def refresh_daily_stats(
    date: Optional[str] = Query(None, description="Fecha en formato YYYY-MM-DD (opcional)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualiza las estadísticas diarias para una fecha específica.
    
    Si no se proporciona fecha, actualiza las estadísticas de hoy.
    Útil para recalcular estadísticas o corregir datos.
    """
    from datetime import datetime
    
    target_date = None
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail="Formato de fecha inválido. Use YYYY-MM-DD"
            )
    
    await metrics_service.update_daily_stats(db, target_date)
    
    return {
        "message": "Estadísticas diarias actualizadas exitosamente",
        "date": target_date.strftime("%Y-%m-%d") if target_date else "today"
    }