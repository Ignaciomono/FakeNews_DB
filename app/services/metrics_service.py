from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from typing import List, Optional
from app.models.news import NewsAnalysis, DailyStats, AnalysisMetric
from app.schemas.news import SummaryMetrics, TimeseriesDataPoint, TimeseriesResponse
import logging

logger = logging.getLogger(__name__)

class MetricsService:
    """Servicio para generar métricas y estadísticas"""
    
    def __init__(self):
        pass
    
    async def get_summary_metrics(self, db: AsyncSession) -> SummaryMetrics:
        """Obtiene métricas resumidas de todos los análisis"""
        try:
            # Consulta para contar análisis por label
            result = await db.execute(
                select(
                    func.count(NewsAnalysis.id).label('total'),
                    func.count().filter(NewsAnalysis.label == 'FAKE').label('fake_count'),
                    func.count().filter(NewsAnalysis.label == 'REAL').label('real_count'),
                    func.count().filter(NewsAnalysis.label == 'UNCERTAIN').label('uncertain_count'),
                    func.avg(NewsAnalysis.score).label('avg_score'),
                    func.avg(NewsAnalysis.confidence).label('avg_confidence')
                )
            )
            
            stats = result.first()
            
            # Consulta para contar por tipo de fuente
            source_result = await db.execute(
                select(
                    func.count().filter(NewsAnalysis.source_type == 'text').label('text_count'),
                    func.count().filter(NewsAnalysis.source_type == 'url').label('url_count'),
                    func.count().filter(NewsAnalysis.source_type == 'file').label('file_count')
                ).select_from(NewsAnalysis)
            )
            
            source_stats = source_result.first()
            
            total = stats.total or 0
            fake_count = stats.fake_count or 0
            real_count = stats.real_count or 0
            uncertain_count = stats.uncertain_count or 0
            
            # Calcular porcentajes
            fake_percentage = (fake_count / total * 100) if total > 0 else 0
            real_percentage = (real_count / total * 100) if total > 0 else 0
            uncertain_percentage = (uncertain_count / total * 100) if total > 0 else 0
            
            return SummaryMetrics(
                total_analyses=total,
                fake_count=fake_count,
                real_count=real_count,
                uncertain_count=uncertain_count,
                fake_percentage=round(fake_percentage, 2),
                real_percentage=round(real_percentage, 2),
                uncertain_percentage=round(uncertain_percentage, 2),
                avg_score=round(stats.avg_score, 3) if stats.avg_score else None,
                avg_confidence=round(stats.avg_confidence, 3) if stats.avg_confidence else None,
                text_analyses=source_stats.text_count or 0,
                url_analyses=source_stats.url_count or 0,
                file_analyses=source_stats.file_count or 0
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo métricas resumen: {e}")
            # Retornar métricas vacías en caso de error
            return SummaryMetrics(
                total_analyses=0,
                fake_count=0,
                real_count=0,
                uncertain_count=0,
                fake_percentage=0,
                real_percentage=0,
                uncertain_percentage=0,
                avg_score=None,
                avg_confidence=None,
                text_analyses=0,
                url_analyses=0,
                file_analyses=0
            )
    
    async def get_timeseries_data(self, db: AsyncSession, days: int = 7) -> TimeseriesResponse:
        """Obtiene datos de series temporales para los últimos N días"""
        try:
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days)
            
            # Primero intentar obtener de DailyStats
            result = await db.execute(
                select(DailyStats)
                .where(
                    and_(
                        func.date(DailyStats.date) >= start_date,
                        func.date(DailyStats.date) <= end_date
                    )
                )
                .order_by(DailyStats.date)
            )
            
            daily_stats = result.scalars().all()
            
            # Si no hay stats pre-calculadas, calcular on-the-fly
            if not daily_stats:
                return await self._calculate_timeseries_on_demand(db, start_date, end_date, days)
            
            # Convertir stats a response
            data_points = []
            for stat in daily_stats:
                data_points.append(TimeseriesDataPoint(
                    date=stat.date.strftime('%Y-%m-%d'),
                    total_analyses=stat.total_analyses,
                    fake_count=stat.fake_count,
                    real_count=stat.real_count,
                    uncertain_count=stat.uncertain_count,
                    avg_score=round(stat.avg_score, 3) if stat.avg_score else None,
                    avg_confidence=round(stat.avg_confidence, 3) if stat.avg_confidence else None
                ))
            
            return TimeseriesResponse(
                data=data_points,
                period_days=days,
                total_points=len(data_points)
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo datos de serie temporal: {e}")
            return TimeseriesResponse(data=[], period_days=days, total_points=0)
    
    async def _calculate_timeseries_on_demand(
        self, 
        db: AsyncSession, 
        start_date: datetime, 
        end_date: datetime, 
        days: int
    ) -> TimeseriesResponse:
        """Calcula series temporales on-demand cuando no hay datos pre-calculados"""
        
        # Generar lista de fechas
        date_list = []
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date)
            current_date += timedelta(days=1)
        
        data_points = []
        
        for date in date_list:
            # Consultar análisis para esta fecha específica
            result = await db.execute(
                select(
                    func.count(NewsAnalysis.id).label('total'),
                    func.count().filter(NewsAnalysis.label == 'FAKE').label('fake_count'),
                    func.count().filter(NewsAnalysis.label == 'REAL').label('real_count'),
                    func.count().filter(NewsAnalysis.label == 'UNCERTAIN').label('uncertain_count'),
                    func.avg(NewsAnalysis.score).label('avg_score'),
                    func.avg(NewsAnalysis.confidence).label('avg_confidence')
                ).where(
                    func.date(NewsAnalysis.created_at) == date
                )
            )
            
            stats = result.first()
            
            data_points.append(TimeseriesDataPoint(
                date=date.strftime('%Y-%m-%d'),
                total_analyses=stats.total or 0,
                fake_count=stats.fake_count or 0,
                real_count=stats.real_count or 0,
                uncertain_count=stats.uncertain_count or 0,
                avg_score=round(stats.avg_score, 3) if stats.avg_score else None,
                avg_confidence=round(stats.avg_confidence, 3) if stats.avg_confidence else None
            ))
        
        return TimeseriesResponse(
            data=data_points,
            period_days=days,
            total_points=len(data_points)
        )
    
    async def update_daily_stats(self, db: AsyncSession, date: Optional[datetime] = None):
        """Actualiza o crea estadísticas diarias para una fecha específica"""
        if date is None:
            date = datetime.utcnow().date()
        
        try:
            # Calcular estadísticas para la fecha
            result = await db.execute(
                select(
                    func.count(NewsAnalysis.id).label('total'),
                    func.count().filter(NewsAnalysis.label == 'FAKE').label('fake_count'),
                    func.count().filter(NewsAnalysis.label == 'REAL').label('real_count'),
                    func.count().filter(NewsAnalysis.label == 'UNCERTAIN').label('uncertain_count'),
                    func.count().filter(NewsAnalysis.source_type == 'text').label('text_count'),
                    func.count().filter(NewsAnalysis.source_type == 'url').label('url_count'),
                    func.count().filter(NewsAnalysis.source_type == 'file').label('file_count'),
                    func.avg(NewsAnalysis.score).label('avg_score'),
                    func.avg(NewsAnalysis.confidence).label('avg_confidence'),
                    func.avg(NewsAnalysis.analysis_time_ms).label('avg_time')
                ).where(
                    func.date(NewsAnalysis.created_at) == date
                )
            )
            
            stats = result.first()
            
            # Buscar si ya existe una entrada para esta fecha
            existing = await db.execute(
                select(DailyStats).where(func.date(DailyStats.date) == date)
            )
            existing_stat = existing.scalar_one_or_none()
            
            if existing_stat:
                # Actualizar existente
                existing_stat.total_analyses = stats.total or 0
                existing_stat.fake_count = stats.fake_count or 0
                existing_stat.real_count = stats.real_count or 0
                existing_stat.uncertain_count = stats.uncertain_count or 0
                existing_stat.text_analyses = stats.text_count or 0
                existing_stat.url_analyses = stats.url_count or 0
                existing_stat.file_analyses = stats.file_count or 0
                existing_stat.avg_score = stats.avg_score
                existing_stat.avg_confidence = stats.avg_confidence
                existing_stat.avg_processing_time_ms = stats.avg_time
                existing_stat.updated_at = datetime.utcnow()
            else:
                # Crear nuevo
                new_stat = DailyStats(
                    date=datetime.combine(date, datetime.min.time()),
                    total_analyses=stats.total or 0,
                    fake_count=stats.fake_count or 0,
                    real_count=stats.real_count or 0,
                    uncertain_count=stats.uncertain_count or 0,
                    text_analyses=stats.text_count or 0,
                    url_analyses=stats.url_count or 0,
                    file_analyses=stats.file_count or 0,
                    avg_score=stats.avg_score,
                    avg_confidence=stats.avg_confidence,
                    avg_processing_time_ms=stats.avg_time
                )
                db.add(new_stat)
            
            await db.commit()
            logger.info(f"Estadísticas actualizadas para {date}")
            
        except Exception as e:
            logger.error(f"Error actualizando estadísticas diarias: {e}")
            await db.rollback()

# Instancia global del servicio
metrics_service = MetricsService()