# 🔌 Integración de APIs Externas de Fact-Checking

Esta aplicación integra 5 APIs externas de verificación de hechos para proporcionar análisis completo de fake news.

## 📋 APIs Integradas

### 1. 🔍 Google Fact Check Tools API
**Endpoint**: `/fact-check/google`

**Descripción**: API oficial de Google para verificación de claims. Busca en bases de datos de fact-checkers verificados.

**Configuración**:
```bash
GOOGLE_FACT_CHECK_API_KEY=tu-api-key-aqui
```

**Obtener API Key**:
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto
3. Habilita "Fact Check Tools API"
4. Crea credenciales (API Key)

**Ejemplo de uso**:
```bash
curl -X POST "http://localhost:8000/fact-check/google" \
  -H "Content-Type: application/json" \
  -d '{"query": "Climate change is a hoax", "language_code": "en"}'
```

---

### 2. 📊 ClaimBuster API
**Endpoint**: `/fact-check/claimbuster`

**Descripción**: Desarrollada por la Universidad de Texas Arlington. Analiza qué tan "verificable" es un claim (score 0-1).

**Configuración**:
```bash
CLAIMBUSTER_API_KEY=tu-api-key-aqui
```

**Obtener API Key**:
1. Ve a [ClaimBuster](https://idir.uta.edu/claimbuster/)
2. Regístrate para obtener acceso a la API
3. Solicita tu API key

**Ejemplo de uso**:
```bash
curl -X POST "http://localhost:8000/fact-check/claimbuster" \
  -H "Content-Type: application/json" \
  -d '{"text": "The president announced new policies yesterday"}'
```

---

### 3. 🧠 WordLift Fact-Checking API
**Endpoint**: `/fact-check/wordlift`

**Descripción**: Verificación semántica de hechos usando grafos de conocimiento y NLP.

**Configuración**:
```bash
WORDLIFT_API_KEY=tu-api-key-aqui
```

**Obtener API Key**:
1. Ve a [WordLift](https://wordlift.io/)
2. Crea una cuenta
3. Accede a la sección de API
4. Genera tu key

**Ejemplo de uso**:
```bash
curl -X POST "http://localhost:8000/fact-check/wordlift" \
  -H "Content-Type: application/json" \
  -d '{"text": "Article content to fact-check"}'
```

---

### 4. 📰 Media Bias / Fact Check (MBFC) API
**Endpoint**: `/fact-check/mbfc`

**Descripción**: Analiza el sesgo político y la credibilidad de fuentes de noticias.

**Configuración**:
```bash
MBFC_API_KEY=tu-api-key-aqui
```

**Obtener API Key**:
1. Visita [Media Bias/Fact Check](https://mediabiasfactcheck.com/)
2. Contacta para acceso API
3. Obtén tus credenciales

**Ejemplo de uso**:
```bash
curl -X POST "http://localhost:8000/fact-check/mbfc" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example-news-site.com"}'
```

---

### 5. 🤖 Fake News Detection (RapidAPI)
**Endpoint**: `/fact-check/rapidapi`

**Descripción**: Detector de fake news usando machine learning disponible en RapidAPI.

**Configuración**:
```bash
RAPIDAPI_KEY=tu-rapidapi-key-aqui
```

**Obtener API Key**:
1. Ve a [RapidAPI](https://rapidapi.com/)
2. Busca "Fake News Detection"
3. Suscríbete al plan que prefieras
4. Copia tu X-RapidAPI-Key

**Ejemplo de uso**:
```bash
curl -X POST "http://localhost:8000/fact-check/rapidapi" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "News article content here",
    "title": "Article title"
  }'
```

---

## 🔄 Multi-Check Endpoint

**Endpoint**: `/fact-check/multi-check`

Ejecuta verificación en múltiples APIs simultáneamente y agrega resultados.

**Ejemplo de uso**:
```bash
curl -X POST "http://localhost:8000/fact-check/multi-check" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Content to verify",
    "url": "https://source.com",
    "title": "Article title",
    "apis": ["all"]
  }'
```

**Parámetro `apis`**:
- `["all"]` - Usar todas las APIs configuradas
- `["google", "claimbuster"]` - Usar solo APIs específicas
- Opciones: `google`, `claimbuster`, `wordlift`, `mbfc`, `rapidapi`

---

## 📊 Status Endpoint

**Endpoint**: `/fact-check/status`

Verifica qué APIs están configuradas y disponibles.

```bash
curl "http://localhost:8000/fact-check/status"
```

**Respuesta**:
```json
{
  "google_fact_check": true,
  "claimbuster": false,
  "wordlift": true,
  "mbfc": false,
  "rapidapi": true,
  "configured_apis": ["google_fact_check", "wordlift", "rapidapi"]
}
```

---

## 🚀 Deploy en Vercel

Para usar las APIs en producción, configura las variables de entorno en Vercel:

1. Ve a tu proyecto en Vercel Dashboard
2. Settings → Environment Variables
3. Agrega cada API key:
   - `GOOGLE_FACT_CHECK_API_KEY`
   - `CLAIMBUSTER_API_KEY`
   - `WORDLIFT_API_KEY`
   - `MBFC_API_KEY`
   - `RAPIDAPI_KEY`

---

## 💡 Mejores Prácticas

1. **No todas las APIs son requeridas**: La aplicación funciona con las que configures
2. **Rate limits**: Cada API tiene sus propios límites de uso
3. **Costos**: Algunas APIs son gratuitas, otras tienen planes de pago
4. **Redundancia**: El multi-check endpoint permite comparar resultados
5. **Fallback**: Si una API falla, las demás continúan funcionando

---

## 🔐 Seguridad

- ✅ Nunca commitees las API keys al repositorio
- ✅ Usa variables de entorno
- ✅ El `.gitignore` ya está configurado para excluir `.env`
- ✅ Rota las keys periódicamente
- ✅ Monitorea el uso de cada API

---

## 📚 Documentación Interactiva

Visita `/docs` en tu servidor para ver la documentación completa de Swagger con ejemplos interactivos de todos los endpoints.