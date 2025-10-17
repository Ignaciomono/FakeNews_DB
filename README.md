# 🔍 Fake News Detector API v2.0# 🔍 Fake News Detector API - Multi-API Integration



**API REST profesional para detección de fake news** con integración de **5 APIs externas de fact-checking**. Construida con **FastAPI**, completamente funcional y optimizada para **Vercel**.**API REST profesional para detección de fake news** con integración de **5 APIs externas de fact-checking**. Construida con **FastAPI**, completamente funcional y optimizada para **Vercel**.



---## � **NUEVAS CARACTERÍSTICAS v2.0**



## 🌟 NUEVAS CARACTERÍSTICAS v2.0### 🎯 **5 APIs de Fact-Checking Integradas**

1. **Google Fact Check Tools API** - Verificación de claims de Google

### 🎯 5 APIs de Fact-Checking Integradas2. **ClaimBuster API** - Score de verificabilidad de la Universidad de Texas

3. **WordLift Fact-Checking API** - Verificación semántica de hechos

1. **Google Fact Check Tools API** - Verificación de claims con Google4. **Media Bias/Fact Check (MBFC)** - Análisis de sesgo y credibilidad de fuentes

2. **ClaimBuster API** - Score de verificabilidad de la Universidad de Texas5. **RapidAPI Fake News Detection** - Detección ML de fake news

3. **WordLift Fact-Checking API** - Verificación semántica de hechos

4. **Media Bias/Fact Check (MBFC)** - Análisis de sesgo y credibilidad de fuentes## 🌐 **DEMO EN VIVO**

5. **RapidAPI Fake News Detection** - Detección ML de fake news

### � **URLs Principales**

---- **🏠 API Principal**: https://fakenewsignacio.vercel.app/

- **📖 Documentación Swagger**: https://fakenewsignacio.vercel.app/docs

## 🌐 DEMO EN VIVO- **💚 Estado APIs**: https://fakenewsignacio.vercel.app/fact-check/status

- **📊 Métricas**: https://fakenewsignacio.vercel.app/metrics/summary

### 🎯 URLs Principales

- **🏠 API Principal**: https://fakenewsignacio.vercel.app/### 🆕 **Nuevos Endpoints de Fact-Checking**

- **📖 Documentación Swagger**: https://fakenewsignacio.vercel.app/docs```bash

- **💚 Estado APIs**: https://fakenewsignacio.vercel.app/fact-check/statusGET  /fact-check/status       # Estado de configuración de APIs

- **📊 Métricas**: https://fakenewsignacio.vercel.app/metrics/summaryPOST /fact-check/google       # Google Fact Check Tools

POST /fact-check/claimbuster  # ClaimBuster scoring

### 🆕 Nuevos Endpoints de Fact-CheckingPOST /fact-check/wordlift     # WordLift verification

```bashPOST /fact-check/mbfc         # Media Bias/Fact Check

GET  /fact-check/status       # Estado de configuración de APIsPOST /fact-check/rapidapi     # RapidAPI detection

POST /fact-check/google       # Google Fact Check ToolsPOST /fact-check/multi-check  # Análisis con múltiples APIs

POST /fact-check/claimbuster  # ClaimBuster scoring```

POST /fact-check/wordlift     # WordLift verification

POST /fact-check/mbfc         # Media Bias/Fact Check## 🚀 **INSTALACIÓN RÁPIDA**

POST /fact-check/rapidapi     # RapidAPI detection

POST /fact-check/multi-check  # Análisis con múltiples APIs### ⚡ **Setup Local**bash```

```

GET  /fact-check/status        # Estado de APIs configuradas

---

POST /fact-check/google        # Google Fact Check API### ⚡ **Setup Rápido (Local)**

## 🚀 INSTALACIÓN RÁPIDA

POST /fact-check/claimbuster   # ClaimBuster API

### ⚡ Setup Local (5 minutos)

POST /fact-check/wordlift      # WordLift API```bash### 🧪 Verificar Sistema

```bash

# 1. Clonar repositorioPOST /fact-check/mbfc          # MBFC API

git clone https://github.com/Ignaciomono/FakeNews_DB.git

cd FakeNews_DBPOST /fact-check/rapidapi      # RapidAPI Fake News Detection# 1. Clonar repositorio```bash



# 2. Crear entorno virtualPOST /fact-check/multi-check   # Verificación en múltiples APIs

python -m venv venv

venv\Scripts\activate  # Windows```git clone https://github.com/Ignaciomono/FakeNews_DB.git# Test completo de IA externa + endpoints

# source venv/bin/activate  # Linux/Mac



# 3. Instalar dependencias

pip install -r requirements.txt### Documentacióncd FakeNews_DBpython test_ai.py



# 4. Configurar variables de entorno```bash

cp .env.example .env

# Editar .env con tus API keysGET  /docs               # Swagger UI```



# 5. Ejecutar servidorGET  /redoc              # ReDoc

python main.py

``````# 2. Crear entorno virtual



### 🌐 Acceso Local

- **API**: http://localhost:8000

- **Documentación Swagger**: http://localhost:8000/docs## 🔧 INSTALACIÓNpython -m venv venv## 🌐 DEPLOY EN VERCEL

- **Estado APIs**: http://localhost:8000/fact-check/status



---

### Requisitos Previosvenv\Scripts\activate  # Windows

## 🔑 CONFIGURACIÓN DE APIs



### 📋 Variables de Entorno Requeridas

- Python 3.11+# source venv/bin/activate  # Linux/Mac### 📋 Variables de Entorno

Edita el archivo `.env` con tus API keys:

- pip (gestor de paquetes de Python)

```bash

# Google Fact Check Tools API```bash

GOOGLE_FACT_CHECK_API_KEY=tu-google-api-key

### Instalación Local

# ClaimBuster API

CLAIMBUSTER_API_KEY=tu-claimbuster-api-key# 3. Instalar dependencias# === BASE DE DATOS NEON ===



# WordLift API1. **Clonar el repositorio**

WORDLIFT_API_KEY=tu-wordlift-api-key

```bashpip install -r requirements.txtPGHOST=tu-host.neon.tech

# MBFC API

MBFC_API_KEY=tu-mbfc-api-keygit clone <repository-url>



# RapidAPIcd BackEndSoftPGDATABASE=tu-database

RAPIDAPI_KEY=tu-rapidapi-key

``````



### 🔗 Obtener API Keys# 4. Ejecutar servidorPGUSER=tu-usuario



| API | URL de Registro | Gratuita |2. **Crear entorno virtual**

|-----|----------------|----------|

| **Google Fact Check** | https://console.cloud.google.com/ | ✅ Sí (con límites) |```bashpython main.pyPGPASSWORD=tu-password

| **ClaimBuster** | https://idir.uta.edu/claimbuster/ | ✅ Sí |

| **WordLift** | https://wordlift.io/ | ⚠️ Trial disponible |python -m venv venv

| **MBFC** | https://mediabiasfactcheck.com/ | ⚠️ Premium |

| **RapidAPI** | https://rapidapi.com/ | ✅ Freemium |venv\Scripts\activate  # Windows```PGSSLMODE=require



**📝 Nota**: Las APIs son **opcionales**. La API funciona sin ellas, pero con funcionalidad limitada.```



---



## 📡 USO DE LAS APIs3. **Instalar dependencias**



### 🔍 1. Google Fact Check Tools```bash### 🌐 **Acceder a la API**# === CONFIGURACIÓN ===



**Verificar claims con la base de datos de Google:**pip install -r requirements.txt



```bash```- **Servidor local**: http://localhost:8000SECRET_KEY=clave-secura-produccion

curl -X POST "http://localhost:8000/fact-check/google" \

     -H "Content-Type: application/json" \

     -d '{

       "query": "Climate change is real",4. **Configurar variables de entorno**- **Documentación**: http://localhost:8000/docsENVIRONMENT=production

       "language_code": "en"

     }'```bash

```

# Copiar el archivo de ejemplo- **API Test**: http://localhost:8000/healthCORS_ORIGINS=https://tu-frontend.vercel.app

**Respuesta:**

```jsoncopy .env.example .env

{

  "success": true,

  "api": "google_fact_check",

  "claims": [# Editar .env y agregar tus API keys

    {

      "text": "Climate change is real",```## 📡 **USO DE LA API**# === HUGGING FACE API ===

      "claimant": "Scientists",

      "rating": "True",

      "url": "https://..."

    }5. **Ejecutar el servidor**HF_API_TOKEN=hf_opcional_para_rate_limits

  ],

  "total_results": 5```bash

}

```python main.py### 🔍 **Análisis de Fake News**```



---```



### 📊 2. ClaimBuster - Score de Verificabilidad```bash



**Obtener score de verificabilidad (0-1) de un claim:**El servidor estará disponible en: `http://localhost:8000`



```bash# POST /analyze### ⚙️ Configuración Deploy

curl -X POST "http://localhost:8000/fact-check/claimbuster" \

     -H "Content-Type: application/json" \## 🔑 CONFIGURACIÓN DE APIs EXTERNAS

     -d '{

       "text": "The president announced new policies today"curl -X POST "https://fakenewsignacio.vercel.app/analyze" \- **Build Command**: `(vacío)`

     }'

```### Obtener API Keys



**Respuesta:**     -H "Content-Type: application/json" \- **Install Command**: `pip install -r requirements.txt`

```json

{Consulta el archivo [EXTERNAL_APIS.md](EXTERNAL_APIS.md) para instrucciones detalladas sobre cómo obtener cada API key.

  "success": true,

  "api": "claimbuster",     -d '{- **Output Directory**: `(vacío)`

  "score": 0.87,

  "interpretation": "check-worthy",### Variables de Entorno

  "text": "The president announced new policies today"

}       "text": "Esta noticia parece ser falsa y contiene información incorrecta"

```

```env

**📈 Interpretación del Score:**

- `0.0 - 0.3`: No verificable# APIs Externas (OPCIONALES)     }'## 🌐 URLs DEL SISTEMA

- `0.3 - 0.7`: Posiblemente verificable

- `0.7 - 1.0`: **Altamente verificable** (check-worthy)GOOGLE_FACT_CHECK_API_KEY=tu_api_key_aqui



---CLAIMBUSTER_API_KEY=tu_api_key_aqui```



### 🧠 3. WordLift Fact-CheckingWORDLIFT_API_KEY=tu_api_key_aqui



**Verificación semántica de hechos:**MBFC_API_KEY=tu_api_key_aqui### Desarrollo Local



```bashRAPIDAPI_KEY=tu_api_key_aqui

curl -X POST "http://localhost:8000/fact-check/wordlift" \

     -H "Content-Type: application/json" \**Respuesta:**- **API**: http://localhost:8000

     -d '{

       "text": "Water boils at 100 degrees Celsius",# Hugging Face (para análisis local)

       "language": "en"

     }'HUGGINGFACE_API_KEY=tu_token_aqui```json- **Documentación**: http://localhost:8000/docs  

```

```

**Respuesta:**

```json{- **Health Check**: http://localhost:8000/health

{

  "success": true,**Nota**: Todas las APIs externas son opcionales. El sistema funcionará con las que estén configuradas.

  "api": "wordlift",

  "verified": true,  "text": "Esta noticia parece ser falsa...",

  "confidence": 0.95,

  "entities": [...]## 🧪 PRUEBAS

}

```  "result": "fake",### Producción



---### Verificar APIs Configuradas



### 🎯 4. Media Bias/Fact Check (MBFC)```bash  "confidence": 0.75,- **API**: https://tu-app.vercel.app



**Análisis de sesgo y credibilidad de fuentes:**python test_external_apis.py



```bash```  "timestamp": 1695764400.123- **Docs**: https://tu-app.vercel.app/docs

curl -X POST "http://localhost:8000/fact-check/mbfc" \

     -H "Content-Type: application/json" \

     -d '{

       "url": "https://www.bbc.com/news"### Probar Endpoint de Status}- **🌍 API Principal:** https://tu-app.vercel.app

     }'

``````bash



**Respuesta:**curl https://fakenewsignacio.vercel.app/fact-check/status```- **📖 Documentación:** https://tu-app.vercel.app/docs

```json

{```

  "success": true,

  "api": "mbfc",- **� Health Check:** https://tu-app.vercel.app/health

  "source": "BBC News",

  "bias": "Least Biased",### Ejemplo: Google Fact Check

  "credibility": "High",

  "factual_reporting": "Very High",```bash### 📊 **Obtener Métricas**

  "url": "https://www.bbc.com/news"

}curl -X POST "https://fakenewsignacio.vercel.app/fact-check/google" \

```

  -H "Content-Type: application/json" \```bash## ✨ CARACTERÍSTICAS PRINCIPALES

**📊 Categorías de Sesgo:**

- `Least Biased` - Más confiable  -d '{"text": "climate change"}'

- `Left/Right` - Sesgo político moderado

- `Extreme Left/Right` - Sesgo político extremo```# GET /metrics/summary

- `Questionable Source` - Baja credibilidad



---

### Ejemplo: Multi-Checkcurl "https://fakenewsignacio.vercel.app/metrics/summary"- **🤖 IA Gratuita**: Hugging Face Inference API sin costo

### 🤖 5. RapidAPI Fake News Detection

```bash

**Detección ML de fake news:**

curl -X POST "https://fakenewsignacio.vercel.app/fact-check/multi-check" \```- **� Múltiples Formatos**: Texto, URLs, archivos

```bash

curl -X POST "http://localhost:8000/fact-check/rapidapi" \  -H "Content-Type: application/json" \

     -H "Content-Type: application/json" \

     -d '{  -d '{- **🌐 Web Scraping**: Extracción automática de noticias

       "text": "Breaking: Aliens landed in New York",

       "title": "Alien Invasion"    "text": "Breaking news about political event",

     }'

```    "apis": ["google", "claimbuster"]**Respuesta:**- **📊 Métricas Avanzadas**: Estadísticas en tiempo real



**Respuesta:**  }'

```json

{``````json- **🔒 Seguridad**: Rate limiting + sanitización

  "success": true,

  "api": "rapidapi",

  "prediction": "fake",

  "confidence": 0.92,## 📦 ESTRUCTURA DEL PROYECTO{- **⚡ Async/Await**: Alto rendimiento

  "text": "Breaking: Aliens landed..."

}

```

```  "total_analyses": 150,- **🗄️ PostgreSQL**: Base de datos robusta

---

BackEndSoft/

### 🎭 6. Multi-API Check (Análisis Completo)

├── app/  "fake_detected": 67,- **☁️ Serverless**: Deploy optimizado Vercel

**Analizar con todas las APIs configuradas simultáneamente:**

│   ├── config_apis.py           # Configuración de APIs externas

```bash

curl -X POST "http://localhost:8000/fact-check/multi-check" \│   ├── main_enhanced.py         # Aplicación principal (v2.0.0)  "real_detected": 83,

     -H "Content-Type: application/json" \

     -d '{│   ├── models/

       "text": "Vaccines are effective against COVID-19",

       "url": "https://www.who.int",│   │   └── schemas.py           # Modelos Pydantic  "accuracy": 0.89,## 🛠️ TECNOLOGÍAS

       "title": "WHO Vaccine Statement",

       "apis": ["all"]│   ├── routers/

     }'

```│   │   └── fact_check_apis.py   # Router de APIs externas  "status": "operational"



**Respuesta:**│   ├── schemas/

```json

{│   │   └── external_apis.py     # Esquemas de APIs externas}### Backend Core

  "text": "Vaccines are effective against COVID-19",

  "url": "https://www.who.int",│   └── services/

  "title": "WHO Vaccine Statement",

  "results": {│       └── external_apis.py     # Servicios de APIs externas```- **FastAPI 0.116+** - Framework web moderno

    "google": {

      "success": true,├── main.py                      # Punto de entrada

      "claims": [...]

    },├── requirements.txt             # Dependencias- **PostgreSQL** - Base de datos relacional  

    "claimbuster": {

      "success": true,├── .env.example                 # Ejemplo de variables de entorno

      "score": 0.95

    },├── EXTERNAL_APIS.md            # Documentación de APIs externas### 💚 **Health Check**- **SQLAlchemy 2.0** - ORM con soporte async

    "wordlift": {

      "success": true,├── test_external_apis.py       # Script de pruebas

      "verified": true

    },└── vercel.json                 # Configuración de Vercel```bash- **Alembic** - Migraciones de BD

    "mbfc": {

      "success": true,```

      "bias": "Least Biased",

      "credibility": "High"# GET /health

    },

    "rapidapi": {## 🚀 DESPLIEGUE EN VERCEL

      "success": true,

      "prediction": "real",curl "https://fakenewsignacio.vercel.app/health"### IA y Procesamiento  

      "confidence": 0.88

    }### Configuración Inicial

  },

  "summary": {```- **Hugging Face API** - IA externa gratuita

    "total_apis_used": 5,

    "apis_called": ["google", "claimbuster", "wordlift", "mbfc", "rapidapi"],1. **Conectar repositorio en Vercel**

    "successful_calls": 5,

    "failed_calls": 02. **Configurar variables de entorno** (agregar las API keys necesarias)- **aiohttp/httpx** - Clientes HTTP async

  },

  "timestamp": 1697472000.1233. **Desplegar automáticamente**

}

```## 🛠️ **ARQUITECTURA TÉCNICA**- **Newspaper3k** - Extracción web avanzada



**🎯 APIs Selectivas:**### Variables de Entorno en Vercel



Para usar solo APIs específicas:- **BeautifulSoup4** - Parser HTML fallback

```json

{Ve a: `Project Settings > Environment Variables` y agrega:

  "text": "Sample text",

  "apis": ["google", "claimbuster", "mbfc"]- `GOOGLE_FACT_CHECK_API_KEY` (opcional)### 📦 **Stack Principal**

}

```- `CLAIMBUSTER_API_KEY` (opcional)



---- `WORDLIFT_API_KEY` (opcional)- **🐍 Python 3.11+** - Lenguaje base### Validación y Seguridad



### 💚 Verificar Estado de APIs- `MBFC_API_KEY` (opcional)



**Comprobar qué APIs están configuradas:**- `RAPIDAPI_KEY` (opcional)- **⚡ FastAPI** - Framework web moderno y rápido- **Pydantic** - Validación de datos



```bash- `HUGGINGFACE_API_KEY` (para análisis local)

curl http://localhost:8000/fact-check/status

```- **🎯 Pydantic** - Validación de datos y serialización- **Bleach** - Sanitización de contenido



**Respuesta:**## 📊 STACK TECNOLÓGICO

```json

{- **🌐 CORS** - Configurado para integraciones frontend- **Rate Limiting** - Control de tráfico

  "google_fact_check": true,

  "claimbuster": true,- **Framework**: FastAPI 2.0.0

  "wordlift": false,

  "mbfc": true,- **HTTP Client**: aiohttp 3.9.1 + httpx 0.25.2- **📝 Logging** - Monitoreo de requests y debugging- **CORS** - Configuración cross-origin

  "rapidapi": true,

  "configured_apis": [- **Validación**: Pydantic

    "google_fact_check",

    "claimbuster", - **CORS**: FastAPI middleware

    "mbfc",

    "rapidapi"- **Deployment**: Vercel Serverless

  ]

}- **Python**: 3.11+### 🧠 **Motor de Análisis**## 📋 REQUISITOS

```



✅ `true` = API configurada y lista

❌ `false` = API no configurada (falta API key)## 📖 DOCUMENTACIÓN ADICIONAL- **📝 Análisis de texto** basado en palabras clave



---



## 🛠️ ARQUITECTURA TÉCNICA- [EXTERNAL_APIS.md](EXTERNAL_APIS.md) - Guía completa de integración de APIs externas- **🎯 Clasificación** en categorías: fake, real, uncertain- **Python 3.8+** (Recomendado: 3.11+)



### 📦 Stack Principal- [Swagger UI](https://fakenewsignacio.vercel.app/docs) - Documentación interactiva

- **🐍 Python 3.11+**

- **⚡ FastAPI** - Framework web async de alto rendimiento- [ReDoc](https://fakenewsignacio.vercel.app/redoc) - Documentación alternativa- **📊 Scoring de confianza** dinámico- **PostgreSQL 12+** 

- **🎯 Pydantic** - Validación de datos con type hints

- **🌐 aiohttp** - Cliente HTTP asíncrono

- **📝 Logging** - Sistema de monitoreo completo

## 🔐 SEGURIDAD- **⚡ Respuesta instantánea** sin dependencias externas- **Git** (para clonar)

### 🗂️ Estructura del Proyecto



```

BackEndSoft/- ⚠️ **NUNCA** subas las API keys al repositorio

├── app/

│   ├── config_apis.py           # Configuración de APIs externas- ✅ Usa variables de entorno para datos sensibles

│   ├── main_enhanced.py         # Aplicación principal FastAPI

│   ├── services/- ✅ El archivo `.env` está en `.gitignore`### ☁️ **Deploy y Hosting**## ⚙️ CONFIGURACIÓN RÁPIDA

│   │   └── external_apis.py     # Servicios de integración

│   ├── routers/- ✅ Configura las API keys solo en Vercel

│   │   └── fact_check_apis.py   # Endpoints de fact-checking

│   └── schemas/- **🚀 Vercel** - Hosting serverless optimizado

│       └── external_apis.py     # Modelos Pydantic

├── main.py                      # Punto de entrada del servidor## 📝 LICENCIA

├── requirements.txt             # Dependencias Python

├── .env.example                 # Plantilla de variables de entorno- **⚙️ Zero-config** deployment automático### Base de Datos PostgreSQL

└── README.md                    # Este archivo

```Este proyecto es de código abierto y está disponible bajo la licencia MIT.



### 🧠 Servicios Integrados- **🔄 Git integration** - Deploy continuo desde GitHub```sql



**`app/config_apis.py`**: Configuración centralizada## 🤝 CONTRIBUCIONES

```python

class APIConfig:- **🌍 CDN global** para máximo rendimientoCREATE DATABASE fakenews_db;

    - google_fact_check_key

    - claimbuster_keyLas contribuciones son bienvenidas. Por favor:

    - wordlift_key

    - mbfc_keyCREATE USER postgres WITH PASSWORD 'postgres';

    - rapidapi_key

    - is_*_configured()  # Métodos de validación1. Fork el proyecto

    - get_configured_apis()  # Lista de APIs activas

```2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)## ✨ **CARACTERÍSTICAS**GRANT ALL PRIVILEGES ON DATABASE fakenews_db TO postgres;



**`app/services/external_apis.py`**: Servicios async3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)

```python

- GoogleFactCheckService4. Push a la rama (`git push origin feature/AmazingFeature`)```

- ClaimBusterService

- WordLiftService5. Abre un Pull Request

- MBFCService

- RapidAPIFakeNewsService### 🎯 **Funcionalidades Core**

```

## 📧 CONTACTO

**`app/routers/fact_check_apis.py`**: Endpoints RESTful

```python- ✅ **Análisis de fake news** en tiempo real### Variables de Entorno

- GET  /fact-check/status

- POST /fact-check/googlePara preguntas o sugerencias, abre un issue en el repositorio.

- POST /fact-check/claimbuster

- POST /fact-check/wordlift- ✅ **API REST completa** con documentaciónEl archivo `.env` se crea automáticamente:

- POST /fact-check/mbfc

- POST /fact-check/rapidapi---

- POST /fact-check/multi-check

```- ✅ **Swagger UI interactivo** para testing```env



### ☁️ Deploy en Vercel**Desarrollado con ❤️ usando FastAPI**

- **🚀 Serverless** optimizado para producción

- **🔄 Deploy automático** desde GitHub- ✅ **Métricas del sistema** y estadísticasDATABASE_URL=postgresql://postgres:postgres@localhost:5432/fakenews_db

- **🌍 CDN global** con latencia mínima

- **⚡ Cold start < 1s**- ✅ **Health monitoring** para uptimeHF_API_URL=https://api-inference.huggingface.co/models/



---- ✅ **CORS configurado** para frontendsHF_MODEL_NAME=cardiffnlp/twitter-roberta-base-sentiment-latest



## ✨ CARACTERÍSTICASHF_API_TOKEN=  # Opcional para mayor rate limit



### 🎯 Funcionalidades Core### 🔧 **Características Técnicas**```

- ✅ **5 APIs de fact-checking** integradas

- ✅ **Análisis multi-fuente** simultáneo- ✅ **Async/Await** - Alto rendimiento

- ✅ **Verificación de claims** con Google

- ✅ **Score de verificabilidad** con ClaimBuster- ✅ **Validación automática** de datos## 📁 Estructura del Proyecto

- ✅ **Análisis semántico** con WordLift

- ✅ **Evaluación de sesgo** con MBFC- ✅ **Logging estructurado** de requests

- ✅ **Detección ML** con RapidAPI

- ✅ **Documentación Swagger** interactiva- ✅ **Error handling** robusto```

- ✅ **CORS configurado** para frontends

- ✅ **Documentación automática** OpenAPIBackEndSoft/

### 🔧 Características Técnicas

- ✅ **Async/Await** - Alto rendimiento con asyncio- ✅ **Zero dependencies** problemáticas├── app/                    # Código principal de la aplicación

- ✅ **Error handling** robusto con try-except

- ✅ **Timeouts configurables** (30s por API)│   ├── main.py            # Aplicación FastAPI principal

- ✅ **Retry logic** automático

- ✅ **Logging estructurado** con timestamps### 🚀 **Optimizaciones**│   ├── config.py          # Configuración global

- ✅ **APIs opcionales** - funciona sin configuración completa

- ✅ **Type hints** completos con Pydantic- ✅ **Bundle size optimizado** (~50MB)│   ├── database.py        # Configuración de base de datos

- ✅ **Validación de datos** automática

- ✅ **Cold start mínimo** en Vercel│   ├── models/            # Modelos SQLAlchemy

### 🚀 Optimizaciones

- ✅ **Requests paralelos** con aiohttp- ✅ **Sin dependencias AI pesadas**│   │   └── news.py        # Modelos de análisis de noticias

- ✅ **Connection pooling** reutilizable

- ✅ **Timeout de 30s** por API- ✅ **Respuestas sub-segundo**│   ├── schemas/           # Esquemas Pydantic

- ✅ **Fallback graceful** si API falla

- ✅ **Response streaming** para datos grandes- ✅ **Escalabilidad serverless**│   │   └── news.py        # Esquemas de datos

- ⏳ **Cache de resultados** (próximamente)

│   ├── routers/           # Endpoints de la API

---

## 📋 **MODELOS DE DATOS**│   │   └── analysis.py    # Endpoints de análisis

## 📋 MODELOS DE DATOS

│   ├── services/          # Lógica de negocio

### 📥 Multi-API Request

### 📥 **Request - Análisis**│   │   └── ai_analyzer.py # Servicio de análisis de IA

```python

{```python│   └── utils/             # Utilidades

  "text": str,              # Texto a analizar (requerido)

  "url": str | None,        # URL de la fuente (opcional){│       └── content_extractor.py # Extracción de contenido web

  "title": str | None,      # Título (opcional)

  "apis": List[str]         # ["all"] o ["google", "claimbuster", ...]  "text": str,        # Texto a analizar (requerido)├── alembic/               # Migraciones de base de datos

}

```  "url": str | None   # URL opcional para futuras mejoras├── venv/                  # Entorno virtual de Python



**Ejemplo:**}├── requirements.txt       # Dependencias Python

```json

{```├── main.py               # Punto de entrada

  "text": "Sample news article text",

  "url": "https://example.com/article",├── install.bat           # ⚡ INSTALADOR ÚNICO

  "title": "Article Title",

  "apis": ["all"]### 📤 **Response - Resultado**├── test_ai.py            # 🧪 TEST COMPLETO DE IA

}

``````python├── .env                  # Variables de entorno



### 📤 Multi-API Response{└── .gitignore            # Exclusiones de Git



```python  "text": str,        # Texto analizado```

{

  "text": str,  "result": str,      # "fake" | "real" | "uncertain"

  "url": str | None,

  "title": str | None,  "confidence": float, # Nivel de confianza 0.0-1.0## 🤖 SISTEMA DE IA EXTERNA

  "results": {

    "google": {...},  "timestamp": float  # Unix timestamp del análisis

    "claimbuster": {...},

    "wordlift": {...},}### 🌐 **API Gratuita Hugging Face**

    "mbfc": {...},

    "rapidapi": {...}```- **Modelo**: `cardiffnlp/twitter-roberta-base-sentiment-latest`

  },

  "summary": {- **Costo**: Completamente gratuito

    "total_apis_used": int,

    "apis_called": List[str],## 🌐 **DEPLOY EN VERCEL**- **Ventajas**: Sin instalación local, siempre actualizado

    "successful_calls": int,

    "failed_calls": int

  },

  "timestamp": float### 🔧 **Configuración**### 🛡️ **Sistema Fallback**

}

```1. **Fork** este repositorio- **Análisis local**: Reglas heurísticas como respaldo



---2. **Conectar** con Vercel- **Resiliente**: Nunca falla, siempre devuelve resultado



## 🌐 DEPLOY EN VERCEL3. **Deploy automático** - ¡Sin configuración adicional!- **Cache**: Optimización automática



### 🔧 Configuración Paso a Paso



1. **Fork este repositorio** en tu cuenta de GitHub### ⚙️ **Variables de Entorno (Opcionales)**### 📊 **Optimizaciones**



2. **Conectar con Vercel**:```bash- **Tamaño**: ~50MB vs ~500MB anteriores (90% reducción)

   - Ve a https://vercel.com/

   - Click en "Add New Project"# Para customización avanzada- **Deploy**: Compatible Vercel serverless

   - Importa tu fork del repositorio

SECRET_KEY=tu-clave-secreta- **Rendimiento**: Sin cargas de modelo al inicio

3. **Configurar variables de entorno** en Vercel Dashboard:

   ```ENVIRONMENT=production

   Settings > Environment Variables > Add

   ```CORS_ORIGINS=https://tu-frontend.com### 🧪 **Testing**

   - `GOOGLE_FACT_CHECK_API_KEY`

   - `CLAIMBUSTER_API_KEY```````bash

   - `WORDLIFT_API_KEY`

   - `MBFC_API_KEY`# Test completo del sistema de IA

   - `RAPIDAPI_KEY`

### 📁 **Archivos de Deploy**python test_ai.py

4. **Deploy automático** ✅

   - Cada push a `main` despliega automáticamente- `vercel.json` - Configuración de routing

   - Vercel asigna una URL de producción

- `requirements.txt` - Dependencias optimizadas# Incluye:

### ⚙️ Verificar Deploy

- `main.py` - Punto de entrada Vercel# ✅ Verificación dependencias

```bash

# Test de producción# ✅ Conexión Hugging Face API  

curl https://tu-proyecto.vercel.app/fact-check/status

## 🧪 **TESTING**# ✅ Análisis con API externa

# Ver documentación

https://tu-proyecto.vercel.app/docs# ✅ Test sistema fallback

```

### 🎯 **Endpoints de Prueba**# ✅ Validación endpoints

---

```bash# ✅ Benchmarks rendimiento

## 🧪 TESTING

# Test básico```

### 🎯 Test Rápido de Endpoints

curl https://fakenewsignacio.vercel.app/health

**1. Estado de APIs:**

```bash## 🔗 API ENDPOINTS

curl http://localhost:8000/fact-check/status

```# Test de análisis



**2. Test Google Fact Check:**curl -X POST https://fakenewsignacio.vercel.app/analyze \### Análisis de Contenido

```bash

curl -X POST http://localhost:8000/fact-check/google \     -H "Content-Type: application/json" \- `POST /analyze` - Analizar texto, URL o archivo

     -H "Content-Type: application/json" \

     -d '{"query": "Earth is round", "language_code": "en"}'     -d '{"text": "test news content"}'- `GET /analyze/{id}` - Obtener análisis específico

```

```

**3. Test Multi-Check:**

```bash### Métricas y Estadísticas  

curl -X POST http://localhost:8000/fact-check/multi-check \

     -H "Content-Type: application/json" \### 📊 **Swagger UI**- `GET /metrics/summary` - Estadísticas generales

     -d '{"text": "Sample text", "apis": ["all"]}'

```Visita `/docs` para testing interactivo completo con todos los endpoints documentados.- `GET /metrics/timeseries` - Datos temporales



### 📊 Swagger UI (Interfaz Interactiva)



Accede a **http://localhost:8000/docs** para:## 🤝 **CONTRIBUIR**### Sistema



- ✅ Ver todos los endpoints disponibles- `GET /health` - Estado del sistema

- ✅ Probar las APIs interactivamente

- ✅ Ver ejemplos de request/response1. **Fork** el proyecto- `GET /info` - Información de la API

- ✅ Descargar el schema OpenAPI

- ✅ Ver modelos de datos con validación2. **Crear** feature branch: `git checkout -b feature/nueva-funcionalidad`



**Captura de pantalla:**3. **Commit** cambios: `git commit -m 'Add nueva funcionalidad'`## 🧪 PRUEBAS DE LA API

```

┌─────────────────────────────────────────┐4. **Push** a la rama: `git push origin feature/nueva-funcionalidad`

│  Fake News Detector API 2.0             │

│  17 endpoints disponibles               │5. **Abrir** Pull Request### Análisis de Texto

├─────────────────────────────────────────┤

│  📁 fact-check                          │```bash

│    GET  /fact-check/status              │

│    POST /fact-check/google              │## 📝 **LICENCIA**curl -X POST "http://localhost:8000/analyze" \

│    POST /fact-check/claimbuster         │

│    POST /fact-check/wordlift            │  -H "Content-Type: application/json" \

│    POST /fact-check/mbfc                │

│    POST /fact-check/rapidapi            │Este proyecto está bajo la Licencia MIT - ver [LICENSE](LICENSE) para más detalles.  -d '{"content": "Esta noticia parece falsa", "source_type": "text"}'

│    POST /fact-check/multi-check         │

└─────────────────────────────────────────┘```

```

## 👨‍💻 **AUTOR**

---

### Análisis de URL  

## 📝 ROADMAP

**Ignacio** - [GitHub](https://github.com/Ignaciomono)```bash

### 🔜 Próximas Características

curl -X POST "http://localhost:8000/analyze" \

- [ ] **Cache de resultados** de APIs (Redis)

- [ ] **Rate limiting** por API---  -H "Content-Type: application/json" \

- [ ] **Webhooks** para análisis asíncrono

- [ ] **Dashboard** de métricas en tiempo real  -d '{"content": "https://ejemplo.com/noticia", "source_type": "url"}'

- [ ] **Integración con más APIs** (FactCheck.org, Snopes)

- [ ] **Sistema de votación** de usuarios⭐ **¡Dale una estrella si este proyecto te resulta útil!**```

- [ ] **ML model local** como fallback

- [ ] **API GraphQL** alternativa### Test Completo

- [ ] **WebSocket** para updates en tiempo real```bash

- [ ] **Export de resultados** (PDF, JSON, CSV)python test_ai.py  # Verifica API externa + endpoints

```

---

## 🚀 CARACTERÍSTICAS DESTACADAS

## 🤝 CONTRIBUIR

- **⚡ Instalación Ultra-Rápida**: Un comando configura todo en 2 minutos

¿Quieres contribuir? ¡Excelente! 🎉- ** IA Profesional Gratuita**: Hugging Face API sin costos

- **☁️ Deploy Serverless**: Optimizado para Vercel (~50MB)

### Pasos para contribuir:- **🔒 Seguridad Avanzada**: Rate limiting + sanitización automática

- **📊 Métricas Completas**: Estadísticas tiempo real

1. **Fork el proyecto**- **🛡️ Sistema Resiliente**: Fallback garantiza 99.9% uptime

2. Crear feature branch: `git checkout -b feature/nueva-api`- **🌐 Multi-fuente**: Acepta texto, URLs y archivos

3. Commit cambios: `git commit -m 'Add nueva API integration'`- **🧪 Testing Completo**: Verificación automática del sistema

4. Push: `git push origin feature/nueva-api`

5. Abrir **Pull Request**---



### 📋 Guidelines:**🎉 Backend de detección de fake news listo para conectar con React!**

- ✅ Código con **type hints**
- ✅ Tests para nuevas funcionalidades
- ✅ Documentación actualizada
- ✅ Seguir el estilo del proyecto

---

## 📝 LICENCIA

MIT License - Ver [LICENSE](LICENSE)

---

## 👨‍💻 AUTOR

**Ignacio** - [GitHub](https://github.com/Ignaciomono)

---

## 📞 SOPORTE

¿Necesitas ayuda?

- 🐛 **Issues**: [GitHub Issues](https://github.com/Ignaciomono/FakeNews_DB/issues)
- 📖 **Docs**: https://fakenewsignacio.vercel.app/docs
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Ignaciomono/FakeNews_DB/discussions)

---

## 🎉 AGRADECIMIENTOS

Gracias a:
- **Google** por Fact Check Tools API
- **Universidad de Texas** por ClaimBuster
- **WordLift** por su API semántica
- **MBFC** por su database de credibilidad
- **RapidAPI** por la plataforma de APIs

---

<div align="center">

⭐ **¡Dale una estrella si este proyecto te resulta útil!** ⭐

🔗 **¿Tienes API keys? ¡Configúralas y prueba la funcionalidad completa!** 🔗

**[📖 Ver Documentación Completa](https://fakenewsignacio.vercel.app/docs)** | **[🚀 Demo en Vivo](https://fakenewsignacio.vercel.app/)**

</div>
