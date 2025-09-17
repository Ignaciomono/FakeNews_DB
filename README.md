# 🔍 Fake News Detector Backend

Backend completo para detección de fake news construido con **FastAPI** y **PostgreSQL**. Sistema listo para producción con análisis de IA integrado.

## 🚀 INICIO RÁPIDO

### Opción 1: Instalación Automática (Recomendado)
```bash
# Ejecutar instalador completo
.\install_step_by_step.bat
```

### Opción 2: Inicio Directo (Si ya está instalado)
```bash
# Iniciar servidor
.\start.bat
```

### Opción 3: Manual
```bash
# 1. Activar entorno virtual
venv\Scripts\activate

# 2. Crear tablas en PostgreSQL
alembic upgrade head

# 3. Iniciar servidor
python main.py
```

## 🌐 URLs del Sistema

Una vez ejecutándose:
- **🌍 API Principal:** http://localhost:8000
- **📖 Documentación Interactiva:** http://localhost:8000/docs
- **📋 Documentación Redoc:** http://localhost:8000/redoc
- **💚 Estado de Salud:** http://localhost:8000/health
- **📊 Información del Sistema:** http://localhost:8000/info

## ✨ Características

- **🤖 Análisis de IA:** Detección automática de fake news con modelos de Hugging Face
- **📝 Múltiples Formatos:** Acepta texto directo, URLs de noticias, y archivos
- **🌐 Extracción Web:** Extrae contenido automáticamente de URLs de noticias
- **📊 Métricas Avanzadas:** Estadísticas completas y análisis de tendencias
- **🔒 Seguridad:** Rate limiting, validación de contenido, y sanitización
- **⚡ Async/Await:** Operaciones asíncronas para mejor rendimiento
- **🗄️ PostgreSQL:** Base de datos robusta con migraciones automáticas
- **🔄 CORS:** Configurado para integración con React

## 🛠️ Tecnologías

### Backend
- **FastAPI 0.116+** - Framework web moderno y rápido
- **PostgreSQL 17** - Base de datos relacional
- **SQLAlchemy 2.0** - ORM avanzado con soporte async
- **Alembic** - Migraciones de base de datos
- **Uvicorn** - Servidor ASGI de alta performance

### IA y Procesamiento
- **Hugging Face Transformers** - Modelos de análisis de texto
- **Newspaper3k** - Extracción de contenido web
- **BeautifulSoup4** - Parser HTML alternativo
- **Bleach** - Sanitización de contenido

### Desarrollo
- **Pydantic** - Validación de datos
- **Asyncpg** - Driver PostgreSQL asíncrono
- **Python-multipart** - Soporte para uploads
- **Python-dotenv** - Gestión de variables de entorno

## 📋 Prerequisitos

- **Python 3.8+** (Recomendado: 3.11+)
- **PostgreSQL 12+** (Recomendado: 17+)
- **Git** (para clonar el repositorio)

## ⚙️ Configuración

### Base de Datos PostgreSQL
```sql
-- Crear base de datos
CREATE DATABASE fakenews_db;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE fakenews_db TO postgres;
```

### Variables de Entorno
El archivo `.env` se crea automáticamente con:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fakenews_db
ENVIRONMENT=development
SECRET_KEY=mi-super-clave-secreta-123456789
MAX_FILE_SIZE_MB=10
CORS_ORIGINS=http://localhost:3000
```

## 📁 Estructura del Proyecto

```
BackEndSoft/
├── app/                    # Código principal de la aplicación
│   ├── main.py            # Aplicación FastAPI principal
│   ├── config.py          # Configuración global
│   ├── database.py        # Configuración de base de datos
│   ├── models/            # Modelos SQLAlchemy
│   │   └── news.py        # Modelos de análisis de noticias
│   ├── schemas/           # Esquemas Pydantic
│   │   └── news.py        # Esquemas de datos
│   ├── routers/           # Endpoints de la API
│   │   └── analysis.py    # Endpoints de análisis
│   ├── services/          # Lógica de negocio
│   │   └── ai_analyzer.py # Servicio de análisis de IA
│   └── utils/             # Utilidades
│       └── content_extractor.py # Extracción de contenido web
├── alembic/               # Migraciones de base de datos
├── venv/                  # Entorno virtual de Python
├── requirements.txt       # Dependencias completas
├── requirements_basic.txt # Dependencias mínimas
├── main.py               # Punto de entrada
├── .env                  # Variables de entorno
├── start.bat             # Script de inicio rápido
├── install_step_by_step.bat # Instalador automático
└── test_api.bat          # Script de pruebas
```

## 🔗 API Endpoints

### Análisis de Noticias
- `POST /analyze` - Analizar texto, URL o archivo
- `GET /analyze/{analysis_id}` - Obtener análisis específico
- `GET /analyze/` - Listar todos los análisis

### Métricas y Estadísticas
- `GET /metrics` - Estadísticas generales del sistema
- `GET /metrics/daily` - Métricas diarias
- `GET /metrics/models` - Información de modelos

### Sistema
- `GET /health` - Estado de salud del sistema
- `GET /info` - Información de la API

## 🧪 Probar la API

### Análisis de Texto
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"content": "Esta noticia parece falsa", "source_type": "text"}'
```

### Análisis de URL
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"content": "https://ejemplo.com/noticia", "source_type": "url"}'
```

### Script de Pruebas Automáticas
```bash
.\test_api.bat
```

## 🚀 Despliegue

### Desarrollo
```bash
.\start.bat
```

### Producción
```bash
# Instalar dependencias completas
pip install -r requirements.txt

# Configurar variables de entorno
export DATABASE_URL="postgresql://user:password@host:port/database"
export ENVIRONMENT="production"

# Aplicar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🔧 Desarrollo

### Instalar Dependencias de Desarrollo
```bash
pip install -r requirements.txt
```

### Crear Nueva Migración
```bash
alembic revision --autogenerate -m "Descripción del cambio"
alembic upgrade head
```

### Ejecutar Pruebas
```bash
# Pruebas rápidas
.\test_api.bat

# Verificar salud del sistema
curl http://localhost:8000/health
```

## 🐛 Solución de Problemas

### Error de Conexión a PostgreSQL
1. Verificar que PostgreSQL esté ejecutándose
2. Revisar credenciales en `.env`
3. Confirmar que la base de datos `fakenews_db` existe

### Error de Modelo de IA
- El sistema usa un modelo MOCK por defecto para pruebas
- Para IA real: `pip install transformers torch newspaper3k`

### Puerto ya en uso
```bash
# Encontrar proceso en puerto 8000
netstat -ano | findstr :8000
# Terminar proceso si es necesario
taskkill /PID <process_id> /F
```

## 📝 Notas

- **Modo MOCK:** Por defecto, el sistema usa un modelo simulado para pruebas rápidas
- **CORS:** Configurado para React en `http://localhost:3000`
- **Rate Limiting:** 100 solicitudes por minuto por IP
- **Archivos:** Máximo 10MB por archivo
- **Logs:** Se guardan en consola con nivel INFO

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

**🎉 ¡Tu backend de detección de fake news está listo para conectar con React!**