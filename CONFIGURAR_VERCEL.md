# 🚀 CONFIGURACIÓN DE VERCEL - VARIABLES DE ENTORNO

## ✅ Variables que debes agregar en Vercel

### 1️⃣ Abre tu proyecto en Vercel:
https://vercel.com/ignaciomono/fakenewsignacio/settings/environment-variables

### 2️⃣ Agrega estas 2 variables (Click "Add New" para cada una):

---

**Variable 1: DATABASE_URL**
```
Name: DATABASE_URL

Value: postgresql://neondb_owner:npg_0thzVcyex6wo@ep-fancy-wildflower-ac8i5g4l-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require

Environment: ✅ Production  ✅ Preview  ✅ Development
```

---

**Variable 2: SECRET_KEY**
```
Name: SECRET_KEY

Value: b3a6e18ecc823b9bf6e93aaf6db93d1357433d51815e93dbb241e7049f0b2ef4

Environment: ✅ Production  ✅ Preview  ✅ Development
```

---

### 3️⃣ Inicializa las tablas en Neon:

Ejecuta este comando en PowerShell para crear las tablas en tu base de datos:

```powershell
$env:DATABASE_URL="postgresql://neondb_owner:npg_0thzVcyex6wo@ep-fancy-wildflower-ac8i5g4l-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require"
python init_db.py
```

---

### 4️⃣ Redeploy en Vercel:

1. Ve a: https://vercel.com/ignaciomono/fakenewsignacio
2. Click en "Deployments"
3. Click en los 3 puntos del último deployment
4. Click "Redeploy"
5. Espera 1-2 minutos

---

### 5️⃣ Verifica que funcione:

```powershell
python extract_vercel_config.py
```

Deberías ver ✅ en todos los endpoints.

---

## 📝 NOTAS:

- **NO** uses `channel_binding=require` en la URL para Vercel (puede causar problemas)
- La URL correcta ya está arriba sin ese parámetro
- Las tablas deben existir en Neon antes del redeploy
