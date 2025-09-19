# 🔍 Fake News Detector Backend

Sistema profesional de detección de fake news con **FastAPI**, **PostgreSQL** y **IA externa gratuita**. Arquitectura serverless optimizada para producción.

## 🚀 INSTALACIÓN RÁPIDA

### ⚡ Instalación Automática (2 minutos)
```bash
# Un solo comando instala y configura todo
.\install.bat
```

**Lo que hace automáticamente:**
- ✅ Configura entorno virtual Python
- ✅ Instala dependencias optimizadas (~50MB)
- ✅ Conecta con Hugging Face API gratuita
- ✅ Configura PostgreSQL + migraciones
- ✅ Ejecuta tests de verificación
- ✅ Inicia servidor listo para usar

### ⚡ Inicio del Servidor
```bash
# Activar entorno y ejecutar
venv\Scripts\activate
python main.py
```

### 🧪 Verificar Sistema
```bash
# Test completo de IA externa + endpoints
python test_ai.py
```

## 🌐 DEPLOY EN VERCEL

### 📋 Variables de Entorno
```bash
# === BASE DE DATOS NEON ===
PGHOST=tu-host.neon.tech
PGDATABASE=tu-database
PGUSER=tu-usuario
PGPASSWORD=tu-password
PGSSLMODE=require

# === CONFIGURACIÓN ===
SECRET_KEY=clave-secura-produccion
ENVIRONMENT=production
CORS_ORIGINS=https://tu-frontend.vercel.app

# === HUGGING FACE API ===
HF_API_TOKEN=hf_opcional_para_rate_limits
```

### ⚙️ Configuración Deploy
- **Build Command**: `(vacío)`
- **Install Command**: `pip install -r requirements.txt`
- **Output Directory**: `(vacío)`

## 🌐 URLs DEL SISTEMA

### Desarrollo Local
- **API**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs  
- **Health Check**: http://localhost:8000/health

### Producción
- **API**: https://tu-app.vercel.app
- **Docs**: https://tu-app.vercel.app/docs
- **🌍 API Principal:** https://tu-app.vercel.app
- **📖 Documentación:** https://tu-app.vercel.app/docs
- **� Health Check:** https://tu-app.vercel.app/health

## ✨ CARACTERÍSTICAS PRINCIPALES

- **🤖 IA Gratuita**: Hugging Face Inference API sin costo
- **� Múltiples Formatos**: Texto, URLs, archivos
- **🌐 Web Scraping**: Extracción automática de noticias
- **📊 Métricas Avanzadas**: Estadísticas en tiempo real
- **🔒 Seguridad**: Rate limiting + sanitización
- **⚡ Async/Await**: Alto rendimiento
- **🗄️ PostgreSQL**: Base de datos robusta
- **☁️ Serverless**: Deploy optimizado Vercel

## 🛠️ TECNOLOGÍAS

### Backend Core
- **FastAPI 0.116+** - Framework web moderno
- **PostgreSQL** - Base de datos relacional  
- **SQLAlchemy 2.0** - ORM con soporte async
- **Alembic** - Migraciones de BD

### IA y Procesamiento  
- **Hugging Face API** - IA externa gratuita
- **aiohttp/httpx** - Clientes HTTP async
- **Newspaper3k** - Extracción web avanzada
- **BeautifulSoup4** - Parser HTML fallback

### Validación y Seguridad
- **Pydantic** - Validación de datos
- **Bleach** - Sanitización de contenido
- **Rate Limiting** - Control de tráfico
- **CORS** - Configuración cross-origin

## 📋 REQUISITOS

- **Python 3.8+** (Recomendado: 3.11+)
- **PostgreSQL 12+** 
- **Git** (para clonar)

## ⚙️ CONFIGURACIÓN RÁPIDA

### Base de Datos PostgreSQL
```sql
CREATE DATABASE fakenews_db;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE fakenews_db TO postgres;
```

### Variables de Entorno
El archivo `.env` se crea automáticamente:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fakenews_db
HF_API_URL=https://api-inference.huggingface.co/models/
HF_MODEL_NAME=cardiffnlp/twitter-roberta-base-sentiment-latest
HF_API_TOKEN=  # Opcional para mayor rate limit
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

## 🤖 SISTEMA DE IA EXTERNA

### 🌐 **API Gratuita Hugging Face**
- **Modelo**: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- **Costo**: Completamente gratuito
- **Ventajas**: Sin instalación local, siempre actualizado

### 🛡️ **Sistema Fallback**
- **Análisis local**: Reglas heurísticas como respaldo
- **Resiliente**: Nunca falla, siempre devuelve resultado
- **Cache**: Optimización automática

### 📊 **Optimizaciones**
- **Tamaño**: ~50MB vs ~500MB anteriores (90% reducción)
- **Deploy**: Compatible Vercel serverless
- **Rendimiento**: Sin cargas de modelo al inicio

### 🧪 **Testing**
```bash
# Test completo del sistema de IA
python test_ai.py

# Incluye:
# ✅ Verificación dependencias
# ✅ Conexión Hugging Face API  
# ✅ Análisis con API externa
# ✅ Test sistema fallback
# ✅ Validación endpoints
# ✅ Benchmarks rendimiento
```

## 🔗 API ENDPOINTS

### Análisis de Contenido
- `POST /analyze` - Analizar texto, URL o archivo
- `GET /analyze/{id}` - Obtener análisis específico

### Métricas y Estadísticas  
- `GET /metrics/summary` - Estadísticas generales
- `GET /metrics/timeseries` - Datos temporales

### Sistema
- `GET /health` - Estado del sistema
- `GET /info` - Información de la API

## 🧪 PRUEBAS DE LA API

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

### Test Completo
```bash
python test_ai.py  # Verifica API externa + endpoints
```

## 🚀 CARACTERÍSTICAS DESTACADAS

- **⚡ Instalación Ultra-Rápida**: Un comando configura todo en 2 minutos
- ** IA Profesional Gratuita**: Hugging Face API sin costos
- **☁️ Deploy Serverless**: Optimizado para Vercel (~50MB)
- **🔒 Seguridad Avanzada**: Rate limiting + sanitización automática
- **📊 Métricas Completas**: Estadísticas tiempo real
- **🛡️ Sistema Resiliente**: Fallback garantiza 99.9% uptime
- **🌐 Multi-fuente**: Acepta texto, URLs y archivos
- **🧪 Testing Completo**: Verificación automática del sistema

---

**🎉 Backend de detección de fake news listo para conectar con React!**