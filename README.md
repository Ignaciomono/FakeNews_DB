# Fake News Detector API v2.0

API REST profesional para detección de fake news con IA, 5 APIs de fact-checking y autenticación JWT. Construida con FastAPI y optimizada para Vercel + Neon PostgreSQL.

## Demo en Vivo

- **API Principal**: https://fakenewsignacio.vercel.app
- **Documentación Swagger**: https://fakenewsignacio.vercel.app/docs
- **Health Check**: https://fakenewsignacio.vercel.app/health
- **Estado de APIs**: https://fakenewsignacio.vercel.app/fact-check/status

## Características Principales

- Análisis de fake news con IA usando Hugging Face
- 5 APIs externas de fact-checking integradas
- Sistema completo de autenticación JWT
- Base de datos PostgreSQL en Neon con migraciones Alembic
- Sistema de métricas y estadísticas en tiempo real
- Documentación interactiva con Swagger UI
- Procesamiento asíncrono con aiohttp
- Soporte para múltiples formatos: texto, URLs y archivos
- CORS configurado para integración con frontend

## APIs de Fact-Checking Integradas

### 1. Google Fact Check Tools API
Verificación de claims usando la base de datos de fact-checking de Google.

### 2. ClaimBuster API
Score de verificabilidad (0-1) desarrollado por la Universidad de Texas.

### 3. WordLift Fact-Checking API
Verificación semántica de hechos con análisis de entidades.

### 4. Media Bias/Fact Check (MBFC)
Análisis de sesgo político y credibilidad de fuentes periodísticas.

### 5. RapidAPI Fake News Detection
Detección de fake news basada en machine learning.

## Endpoints de la API

### Health Checks
- `GET /health/` - Estado general del sistema
- `GET /health/database` - Verificar conexión a PostgreSQL
- `GET /health/ai-model` - Estado del modelo de IA
- `GET /health/web-extractor` - Estado del extractor web

### Autenticación
- `POST /auth/register` - Registrar nuevo usuario
  - Body: `{"email": "user@example.com", "password": "password123"}`
- `POST /auth/login` - Iniciar sesión y obtener JWT token
  - Form: `username=user@example.com&password=password123`

### Análisis de Contenido
- `POST /analyze/` - Analizar contenido de fake news
  - Soporta: texto directo, URLs, archivos
  - Body: `{"text": "contenido", "source_type": "text"}`
- `GET /analyze/{id}` - Obtener resultado de análisis por ID

### Fact-Checking APIs
- `GET /fact-check/status` - Ver qué APIs están configuradas
- `POST /fact-check/google` - Verificar con Google Fact Check
- `POST /fact-check/claimbuster` - Obtener score de ClaimBuster
- `POST /fact-check/wordlift` - Verificación semántica con WordLift
- `POST /fact-check/mbfc` - Análisis de sesgo con MBFC
- `POST /fact-check/rapidapi` - Detección ML con RapidAPI
- `POST /fact-check/multi-check` - Verificar con múltiples APIs simultáneamente

### Métricas y Estadísticas
- `GET /metrics/summary` - Estadísticas generales del sistema
- `GET /metrics/timeseries` - Datos de series temporales
- `POST /metrics/refresh-daily` - Actualizar métricas diarias

## Instalación Local

### Requisitos Previos
- Python 3.11 o superior
- PostgreSQL 12+ (o cuenta en Neon)
- Git

### Pasos de Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/Ignaciomono/FakeNews_DB.git
cd FakeNews_DB

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 6. Ejecutar migraciones de base de datos
alembic upgrade head

# 7. Iniciar el servidor
python main.py
```

El servidor estará disponible en: http://localhost:8000

## Configuración de Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
# Base de Datos (Requerido)
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require

# Seguridad (Requerido)
SECRET_KEY=tu-clave-secreta-de-al-menos-32-caracteres

# Configuración General
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# APIs de Fact-Checking (Opcionales)
GOOGLE_FACT_CHECK_API_KEY=tu-google-api-key
CLAIMBUSTER_API_KEY=tu-claimbuster-api-key
RAPIDAPI_KEY=tu-rapidapi-key
WORDLIFT_API_KEY=tu-wordlift-api-key
MBFC_API_KEY=tu-mbfc-api-key

# Hugging Face (Opcional)
HF_API_TOKEN=tu-huggingface-token
```

## Deploy en Vercel

### Configuración Paso a Paso

1. **Conectar Repositorio**
   - Ve a https://vercel.com/new
   - Importa tu repositorio de GitHub
   - Selecciona el proyecto FakeNews_DB

2. **Configurar Variables de Entorno**
   - Ve a Settings > Environment Variables
   - Agrega todas las variables del archivo `.env`
   - Variables requeridas: `DATABASE_URL`, `SECRET_KEY`, `ENVIRONMENT=production`

3. **Configurar Build**
   - Build Command: (dejar vacío)
   - Output Directory: (dejar vacío)
   - Install Command: `pip install -r requirements.txt`

4. **Deploy**
   - Click en "Deploy"
   - Vercel automáticamente detecta Python y configura el entorno
   - Cada push a `main` desplegará automáticamente

### Inicializar Base de Datos en Neon

Opción 1 - Desde terminal local:
```bash
export DATABASE_URL="tu-url-de-neon"
alembic upgrade head
```

Opción 2 - SQL directo en Neon Dashboard:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE news_analyses (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    source_type VARCHAR(20) NOT NULL,
    source_url VARCHAR(500),
    score FLOAT NOT NULL,
    label VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    model_version VARCHAR(100) NOT NULL,
    content_length INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE daily_stats (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP WITH TIME ZONE NOT NULL UNIQUE,
    total_analyses INTEGER DEFAULT 0,
    fake_count INTEGER DEFAULT 0,
    real_count INTEGER DEFAULT 0,
    avg_confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Ejemplos de Uso

### 1. Analizar Texto

```bash
curl -X POST "https://fakenewsignacio.vercel.app/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Breaking news: Scientists discover cure for all diseases",
    "source_type": "text"
  }'
```

### 2. Analizar URL

```bash
curl -X POST "https://fakenewsignacio.vercel.app/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "https://ejemplo.com/noticia",
    "source_type": "url"
  }'
```

### 3. Registrar Usuario

```bash
curl -X POST "https://fakenewsignacio.vercel.app/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "password": "password123"
  }'
```

### 4. Login y Obtener Token

```bash
curl -X POST "https://fakenewsignacio.vercel.app/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=usuario@example.com&password=password123"
```

### 5. Verificación Multi-API

```bash
curl -X POST "https://fakenewsignacio.vercel.app/fact-check/multi-check" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Climate change is real and supported by scientists",
    "apis": ["google", "claimbuster", "rapidapi"]
  }'
```

### 6. Ver Estado de APIs

```bash
curl "https://fakenewsignacio.vercel.app/fact-check/status"
```

## Obtener API Keys

| API | URL de Registro | Costo | Límites Gratuitos |
|-----|----------------|-------|-------------------|
| Google Fact Check | https://console.cloud.google.com/ | Gratis | 10,000 req/día |
| ClaimBuster | https://idir.uta.edu/claimbuster/ | Gratis | 1,000 req/día |
| RapidAPI | https://rapidapi.com/ | Freemium | 500 req/mes |
| WordLift | https://wordlift.io/ | Trial 14 días | Luego $59/mes |
| MBFC | N/A | No oficial | Web scraping |

### Guía Rápida: Google Fact Check API

1. Ve a Google Cloud Console
2. Crea un nuevo proyecto
3. Habilita "Fact Check Tools API"
4. Ve a Credenciales > Crear Credencial > API Key
5. Copia la key y agrégala a tu `.env`

### Guía Rápida: RapidAPI

1. Crea cuenta en RapidAPI.com
2. Busca "Fake News Detection"
3. Suscríbete al plan gratuito
4. Copia tu "X-RapidAPI-Key"
5. Agrégala como `RAPIDAPI_KEY` en tu `.env`

## Estructura del Proyecto

```
BackEndSoft/
├── main.py                          # Aplicación FastAPI principal
├── requirements.txt                 # Dependencias Python
├── vercel.json                      # Configuración de Vercel
├── alembic.ini                      # Configuración de Alembic
├── init_db.py                       # Script de inicialización de BD
├── .env.example                     # Plantilla de variables
├── alembic/
│   └── versions/                    # Migraciones de base de datos
└── app/
    ├── config.py                    # Configuración general
    ├── config_apis.py               # Configuración de APIs externas
    ├── database.py                  # Conexión a PostgreSQL
    ├── models/
    │   ├── news.py                  # Modelo de análisis
    │   └── user.py                  # Modelo de usuarios
    ├── routers/
    │   ├── analysis.py              # Endpoints de análisis
    │   ├── auth.py                  # Endpoints de autenticación
    │   ├── fact_check_apis.py       # Endpoints de fact-checking
    │   ├── health.py                # Health checks
    │   └── metrics.py               # Métricas y estadísticas
    ├── schemas/
    │   ├── analysis.py              # Schemas de análisis
    │   ├── external_apis.py         # Schemas de APIs externas
    │   └── user.py                  # Schemas de usuarios
    ├── services/
    │   ├── ai_analyzer.py           # Servicio de análisis con IA
    │   └── external_apis.py         # Integración con APIs externas
    └── utils/
        └── auth.py                  # Utilidades de autenticación
```

## Stack Tecnológico

- **Framework Web**: FastAPI 0.116.0
- **Base de Datos**: PostgreSQL (Neon)
- **ORM**: SQLAlchemy 2.0.36 con soporte async
- **Migraciones**: Alembic 1.13.1
- **Autenticación**: JWT con python-jose 3.3.0 y passlib 1.7.4
- **IA**: Hugging Face Inference API
- **HTTP Client**: aiohttp 3.9.1 para requests asíncronos
- **Validación**: Pydantic 2.10.0 con email-validator
- **Deployment**: Vercel Serverless
- **CORS**: FastAPI middleware

## Troubleshooting

### Error: "relation does not exist"
Este error indica que las tablas no existen en la base de datos.

**Solución:**
```bash
alembic upgrade head
```

### Error: "no pg_hba.conf entry for host"
Problema de conexión SSL con PostgreSQL.

**Solución:**
```bash
DATABASE_URL=postgresql://user:pass@host.neon.tech/db?sslmode=require
```

### Error: "SECRET_KEY not configured"
Falta la clave secreta para JWT.

**Solución:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Copia el resultado y agrégalo como `SECRET_KEY` en tu `.env`

### Error: "Module not found"
Faltan dependencias.

**Solución:**
```bash
pip install -r requirements.txt
```

### APIs no responden
Verifica que las API keys estén configuradas correctamente.

**Solución:**
```bash
curl http://localhost:8000/fact-check/status
```

## Testing

### Test Local Completo

```bash
# Health check
curl http://localhost:8000/health

# Ver documentación
open http://localhost:8000/docs

# Estado de APIs
curl http://localhost:8000/fact-check/status

# Test de análisis
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "test content", "source_type": "text"}'
```

## Licencia

MIT License - Ver archivo LICENSE para más detalles.

## Autor

**Ignacio** - [GitHub](https://github.com/Ignaciomono)

## Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m 'Agregar nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

## Soporte

- **Issues**: [GitHub Issues](https://github.com/Ignaciomono/FakeNews_DB/issues)
- **Documentación**: https://fakenewsignacio.vercel.app/docs
- **Email**: Contactar a través de GitHub

## Roadmap

- [ ] Implementar cache con Redis
- [ ] Agregar más APIs de fact-checking
- [ ] Sistema de webhooks para notificaciones
- [ ] Dashboard de métricas en tiempo real
- [ ] API GraphQL
- [ ] Soporte para más idiomas
- [ ] Exportar resultados en PDF/CSV
