# CineIA

MVP de Programación Comercial: catálogo de películas y videojuegos con FastAPI, React, PostgreSQL/Neon y servicios de IA controlados por rol y cuota.

## Aplicación publicada

- Frontend: https://cineia-phi.vercel.app
- Backend: https://cineia-api-nm1g.onrender.com
- Swagger: https://cineia-api-nm1g.onrender.com/docs
- Health check: https://cineia-api-nm1g.onrender.com/health

## Puesta en marcha local

1. Instala Python 3.12+, Node.js 22+ y PostgreSQL (o crea Neon).
2. En Neon, abre **SQL Editor**, pega y ejecuta `database/schema.sql`; después ejecuta `database/seed.sql`.
3. Copia `backend/.env.example` como `backend/.env` y define valores propios. No compartas ese archivo.
4. En una terminal: `cd backend; python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt`.
5. Define temporalmente una contraseña de administrador: `$env:ADMIN_PASSWORD='UnaClaveLargaPropia'; python scripts/create_admin.py`.
6. Inicia API: `uvicorn app.main:app --reload --port 8000`. Swagger: `http://localhost:8000/docs`.
7. En otra terminal: `cd frontend; Copy-Item .env.example .env; npm install; npm run dev`.

## Instancias y publicación

- **Neon:** proyecto PostgreSQL gratuito; ejecuta los dos SQL y copia solo la URL de conexión a `DATABASE_URL` local/variables de hosting.
- **Groq:** crea una API key gratuita y configúrala como `GROQ_API_KEY`. El MVP deja la integración real aislada para activarla sin exponer la llave.
- **TMDB:** crea token gratuito para enriquecer el recomendador; guárdalo como `TMDB_ACCESS_TOKEN`.
- **Render:** crea Web Service desde `backend`, comando `uvicorn app.main:app --host 0.0.0.0 --port $PORT`; configura todas las variables del `.env.example`.
- **Vercel:** importa el repositorio, Root Directory `frontend`, define `VITE_API_URL` con URL HTTPS de Render.
- **GitHub:** sube el repositorio; Actions ejecuta pruebas/build al hacer push o pull request a `main`. Configura secretos solo para despliegue, nunca en YAML.
- **Power BI:** usa la consulta segura de `powerbi/CineIA_Consumo.pq`; la URL pública ya está configurada y la clave se mantiene fuera de Git.

## Verificación

`cd backend; pytest -q` y `cd frontend; npm run build`.

También puedes usar desde la raíz:

```powershell
.\verify.ps1
```

Para iniciar cada capa en terminales separadas:

```powershell
.\start-backend.ps1
.\start-frontend.ps1
```

**Captura del hito inicial:** Neon SQL Editor mostrando `schema.sql` ejecutado y el explorador con las tablas `app_users`, `catalog_items`, `usage_logs` y `ai_services`.
