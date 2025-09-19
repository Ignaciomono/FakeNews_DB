# 🚀 Deploy en Vercel - Fake News Detector Backend

## 📋 Preparación para Deploy

### 1. **Variables de Entorno en Vercel**
En el dashboard de Vercel, configura estas variables:

```bash
# Base de datos (usar servicio como Neon, PlanetScale, o Railway)
DATABASE_URL=postgresql://user:password@host:port/database

# Seguridad
SECRET_KEY=tu-clave-secreta-super-segura-para-produccion

# CORS (actualizar con tu dominio de frontend)
CORS_ORIGINS=https://tu-frontend.vercel.app,http://localhost:3000

# Configuración
ENVIRONMENT=production
MAX_FILE_SIZE_MB=10
```

### 2. **Base de Datos Recomendada**
Para Vercel, usa un servicio de PostgreSQL en la nube:

- **Neon** (Recomendado): https://neon.tech
- **PlanetScale**: https://planetscale.com
- **Railway**: https://railway.app
- **Supabase**: https://supabase.com

### 3. **Deploy Automático**
```bash
# 1. Conectar repositorio GitHub con Vercel
# 2. Vercel detectará automáticamente el vercel.json
# 3. Configurar variables de entorno
# 4. Deploy automático en cada push
```

## ⚙️ Configuración de vercel.json

El archivo `vercel.json` incluye:
- ✅ Configuración para FastAPI
- ✅ Rutas optimizadas
- ✅ Headers CORS
- ✅ Timeout de 60 segundos
- ✅ Redirect automático a /docs
- ✅ Requirements optimizado para Vercel

## 🔗 URLs Post-Deploy

Una vez deployado, tu API estará disponible en:
- **API Base**: `https://tu-app.vercel.app`
- **Documentación**: `https://tu-app.vercel.app/docs`
- **Health Check**: `https://tu-app.vercel.app/health`

## 🧪 Testing del Deploy

```bash
# Test básico
curl https://tu-app.vercel.app/health

# Test de análisis
curl -X POST "https://tu-app.vercel.app/analyze" \
  -H "Content-Type: application/json" \
  -d '{"content": "Esta es una noticia de prueba", "source_type": "text"}'
```

## 🚨 Consideraciones Importantes

### Limitaciones de Vercel
- **Timeout**: Máximo 60 segundos por request
- **Memory**: Limitada para modelos de IA grandes
- **Cold Start**: Primer request puede ser lento

### Optimizaciones Incluidas
- Requirements ligeros (`requirements-vercel.txt`)
- Versión CPU de PyTorch
- Modelos de IA optimizados
- Cache inteligente

### Fallbacks
- Sistema mock si los modelos de IA fallan
- Graceful degradation
- Error handling robusto

## 🔧 Solución de Problemas

### Error: "Function timeout"
- Los modelos de IA pueden ser pesados
- El sistema incluye fallback automático
- Considera usar modelos más ligeros

### Error: "Memory limit exceeded"
- Usa `requirements-vercel.txt` (más ligero)
- Los modelos se cargan bajo demanda
- Cache automático para optimización

### Error de Base de Datos
- Verifica `DATABASE_URL` en variables de entorno
- Asegúrate que la DB esté accesible públicamente
- Ejecuta migraciones en la DB externa

## 🎯 Próximos Pasos

1. **Conectar con Frontend React**
2. **Configurar dominio personalizado**
3. **Monitoring y analytics**
4. **Cache Redis opcional**
5. **CDN para archivos estáticos**

---

¡Tu backend de Fake News está listo para producción en Vercel! 🎉