# Despliegue de CineIA

## Instancias activas

- Frontend Vercel: `https://cineia-phi.vercel.app`
- Backend Render: `https://cineia-api-nm1g.onrender.com`
- Swagger: `https://cineia-api-nm1g.onrender.com/docs`
- Health: `https://cineia-api-nm1g.onrender.com/health`
- Repositorio: `https://github.com/JulioTzicap/cineia`

Estado validado el 7 de noviembre de 2026: frontend y backend públicos, CORS correcto y colección Postman 13/13.

## Backend en Render

1. Crear un **Web Service** conectado al repositorio.
2. Root Directory: `backend`.
3. Runtime: Docker o Python 3.12.
4. Build Command si se usa Python: `pip install -r requirements.txt`.
5. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
6. Configurar las variables de `backend/.env.example` con valores reales en el panel de Render.
7. Health Check Path: `/health`.
8. No copiar `.env` al repositorio.

Render gratuito puede apagar el servicio por inactividad y producir un arranque inicial lento. Revisar el plan antes de confirmar el despliegue para evitar cargos.

## Frontend en Vercel

1. Importar el mismo repositorio.
2. Root Directory: `frontend`.
3. Framework Preset: Vite.
4. Build Command: `npm run build`.
5. Output Directory: `dist`.
6. Variable `VITE_API_URL`: URL HTTPS pública de Render, sin `/` al final.
7. Actualizar `FRONTEND_ORIGIN` en Render con el dominio HTTPS de Vercel.

## CI/CD

Los workflows ejecutan pruebas/build en `main`. Los trabajos de despliegue dependen de esos trabajos y no se ejecutan si fallan.

Secretos opcionales de GitHub:

- `RENDER_DEPLOY_HOOK`
- `VERCEL_DEPLOY_HOOK`

Los hooks se crean desde los paneles de cada proveedor y nunca se incluyen en archivos o capturas.

## Validación pública

- `https://TU_API/health`
- `https://TU_API/docs`
- Login desde la URL de Vercel.
- RAG con fuentes.
- Endpoint BI con clave de lectura.
