# 🔍 Fake News Detector Backend

Backend completo para detección de fake news construido con **FastAPI** y **PostgreSQL**. Sistema listo para producción con análisis de IA integrado.

## 🚀 INSTALACIÓN LOCAL

### ⚡ Una Sola Instalación - Todo Incluido
```bash
# Ejecutar instalador completo que configura todo automáticamente
.\install.bat
```

Este comando único:
- ✅ Verifica Python y PostgreSQL
- ✅ Crea entorno virtual
- ✅ Instala todas las dependencias
- ✅ Configura la base de datos
- ✅ Ejecuta migraciones
- ✅ Inicia el servidor
- ✅ Ejecuta pruebas de verificación

### 🧪 Probar el Sistema de IA
```bash
# Ejecutar test completo del sistema de IA
python test_ai.py
```

### ⚡ Inicio Rápido (Si ya está instalado)
```bash
# Activar entorno y ejecutar servidor
venv\Scripts\activate
python main.py
```

## 🌐 DEPLOY EN VERCEL

### 📋 Variables de Entorno Requeridas
En el dashboard de Vercel, configura estas variables:

```bash
PGHOST=tu-host-postgresql
PGDATABASE=tu-database
PGUSER=tu-usuario
PGPASSWORD=tu-password
PGSSLMODE=require

SECRET_KEY=tu-clave-secreta-super-segura-para-produccion
ENVIRONMENT=production
MAX_FILE_SIZE_MB=10
CORS_ORIGINS=https://tu-frontend.vercel.app
```

### ⚙️ Build and Output Settings
```bash
Build Command: (dejar vacío)
Output Directory: (dejar vacío)
Install Command: pip install -r requirements-vercel.txt
```

### 🔗 URLs Post-Deploy
- **API Base**: `https://tu-app.vercel.app`
- **Documentación**: `https://tu-app.vercel.app/docs`
- **Health Check**: `https://tu-app.vercel.app/health`

## 🌐 URLs del Sistema

### Local (Desarrollo)
- **🌍 API Principal:** http://localhost:8000
- **📖 Documentación Interactiva:** http://localhost:8000/docs
- **📋 Documentación Redoc:** http://localhost:8000/redoc
- **💚 Estado de Salud:** http://localhost:8000/health
- **📊 Información del Sistema:** http://localhost:8000/info

### Producción (Vercel)
- **🌍 API Principal:** https://tu-app.vercel.app
- **📖 Documentación:** https://tu-app.vercel.app/docs
- **� Health Check:** https://tu-app.vercel.app/health

## ✨ Características

- **🤖 Análisis de IA:** Detección automática de fake news con modelos de Hugging Face
- **📝 Múltiples Formatos:** Acepta texto directo, URLs de noticias, y archivos
- **🌐 Extracción Web:** Extrae contenido automáticamente de URLs de noticias
- **📊 Métricas Avanzadas:** Estadísticas completas y análisis de tendencias
- **🔒 Seguridad:** Rate limiting, validación de contenido, y sanitización
- **⚡ Async/Await:** Operaciones asíncronas para mejor rendimiento
- **🗄️ PostgreSQL:** Base de datos robusta con migraciones automáticas
- **🔄 CORS:** Configurado para integración con React
- **☁️ Deploy:** Optimizado para Vercel con fallbacks automáticos

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
├── requirements.txt       # Dependencias Python
├── main.py               # Punto de entrada
├── install.bat           # ⚡ INSTALADOR ÚNICO
├── test_ai.py            # 🧪 TEST COMPLETO DE IA
├── .env                  # Variables de entorno
└── .gitignore            # Exclusiones de Git
```

## 🤖 Sistema de IA Integrado

El backend incluye análisis real de IA con:
- **Modelo Principal:** `martin-ha/toxic-comment-model` de Hugging Face
- **Extracción Web:** `newspaper3k` para URLs de noticias
- **Sistema Fallback:** Análisis mock para desarrollo/pruebas
- **Cache Inteligente:** Optimización automática de rendimiento

### Probar Sistema de IA
```bash
# Ejecutar test completo
python test_ai.py

# El test incluye:
# ✅ Verificación de dependencias
# ✅ Carga de modelos de IA
# ✅ Análisis de texto real
# ✅ Test de APIs endpoints
# ✅ Benchmarks de rendimiento
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

## 🧪 Probar la API

### Análisis de Texto Directo
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"content": "Esta noticia parece falsa", "source_type": "text"}'
```

### Análisis de URL de Noticia
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"content": "https://ejemplo.com/noticia", "source_type": "url"}'
```

### Test Completo del Sistema
```bash
# Ejecutar todas las pruebas de IA y API
python test_ai.py
```

## 🚀 Características Destacadas

- **✅ Instalación Simplificada:** Un solo comando `install.bat` configura todo
- **🧪 Testing Integrado:** `test_ai.py` verifica todo el sistema de IA
- **🤖 IA Real:** Modelos de Hugging Face con análisis profesional
- **⚡ Rendimiento:** Sistema asíncrono optimizado para producción
- **🔒 Seguridad:** Rate limiting, validación y sanitización integrada
- **📊 Métricas:** Estadísticas completas y monitoreo del sistema
- **☁️ Deploy Fácil:** Optimizado para Vercel con configuración automática

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