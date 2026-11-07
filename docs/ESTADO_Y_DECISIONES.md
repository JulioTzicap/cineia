# Estado y decisiones — CineIA

### 2026-11-06 — Base del MVP

- Estado anterior: sin repositorio ni backend/frontend.
- Cambios realizados: se creó el esqueleto ejecutable de base de datos, FastAPI, React, pruebas, CI, Postman y guías de despliegue.
- Archivos modificados: raíz del repositorio CineIA.
- Pruebas ejecutadas: `npm run build` del frontend y `pytest -q` del backend, ambos correctos.
- Resultado: proyecto preparado, aún sin instancias externas configuradas.
- Captura solicitada/tomada: Neon SQL Editor y tablas después de ejecutar el esquema.
- Requisitos cubiertos: R01, R02 y R29 en implementación; pendientes de evidencia/prueba.
- Problemas pendientes: configurar Neon; posteriormente Groq, TMDB y hosting.
- Próximo paso: ejecutar `database/schema.sql` y `database/seed.sql` en Neon.

### 2026-11-06 — Entorno local de Python

- Cambios realizados: Python 3.12.10 instalado para el usuario actual y entorno virtual creado en `backend/.venv`.
- Dependencias: instaladas desde `backend/requirements.txt`.
- Pruebas ejecutadas: `1 passed`; importación de la API confirmó `CineIA API 1.0.0`.
- Próximo paso: configurar `DATABASE_URL` después de ejecutar el esquema en Neon.

### 2026-11-06 — Conexión Neon validada

- Base y rama: `neondb` en `production`.
- Rol: `neondb_owner` mediante conexión agrupada.
- Resultado: conexión TLS correcta y 8 tablas detectadas en el esquema `public`.
- Seguridad: credenciales almacenadas únicamente en `backend/.env`, excluido por `.gitignore`.
- Próximo paso: crear el usuario administrador inicial desde el backend.

### ADR-006: MVP con proveedores desacoplados

- Estado: aceptada.
- Decisión: la API funciona con catálogo y controles locales; Groq/TMDB se habilitan con variables de entorno.
- Motivo: permite pruebas y demostración sin secretos en el repositorio.

### 2026-11-06 — Panel administrativo e IA real

- Groq: clave validada sin exponerla; modelo activo `openai/gpt-oss-20b`.
- Catálogo: 10 títulos reproducibles y sin duplicados.
- RAG: recuperación PostgreSQL, memoria, fuentes, Groq y tokens reales verificados.
- Agente recomendador: preferencias, candidatos del catálogo, Wikipedia, comparación y fuentes.
- Agente de novedades: Google News RSS, resumen con Groq, fechas y enlaces.
- Administración web: usuarios, catálogo, activación de servicios, historial y consumo.
- Verificación: backend compilado, `pytest` correcto y frontend compilado con Vite.
- Evidencias pendientes: capturas del panel, RAG, recomendador, novedades, historial y consumo.
- Próximo paso: ampliar pruebas automatizadas y completar edición del catálogo/filtros del reporte.

### 2026-11-06 — Corrección del catálogo y reporte filtrable

- Incidente: la consulta del catálogo fallaba con HTTP 500 cuando el filtro opcional era nulo.
- Corrección: parámetros opcionales tipados explícitamente para PostgreSQL.
- Catálogo web: edición y desactivación incorporadas.
- Reporte administrativo: filtros por fechas, servicio y usuario; tarjeta de tokens totales.
- Pruebas: 5 pruebas automatizadas correctas y compilación Vite correcta.
- Verificación HTTP: catálogo, usuarios, servicios y consumo respondieron 200.
- Próximo paso: completar edición detallada de usuarios, ampliar pruebas de integración y finalizar Postman.

### 2026-11-06 — Colección Postman

- Colección completada con autenticación, catálogo, tres servicios IA, historial, consumo y BI.
- Login guarda el JWT automáticamente en la variable `token`.
- Entorno de ejemplo conserva contraseña y clave BI vacías para evitar secretos en Git.
- Próximo paso: importar, ejecutar y capturar una solicitud autenticada.

### 2026-11-06 — Seguridad, usuarios, Power BI y CI/CD

- Sesiones: cada solicitud revalida usuario activo y rol actual en Neon.
- Usuarios: edición de nombre, rol, límite y contraseña; activación/desactivación desde la web.
- Protección: un administrador no puede desactivarse ni quitarse su propio rol.
- Power BI: consulta M, tipos, medidas DAX y guía de coincidencia con la web.
- CI/CD: deploy hooks condicionados a tests/build correctos en `main`.
- Pruebas: 11 correctas, incluyendo saldo, bloqueo por cuota y usuario inactivo; frontend Vite compilado.
- Verificación HTTP: auth/me, catálogo, usuarios, servicios y reporte respondieron 200.
- Próximo paso: pruebas de integración de cuotas/reportes, importación de Postman y despliegue en cuentas externas.

### 2026-11-06 — Refactorización funcional del frontend

- Arquitectura frontend separada en cliente API, componentes y páginas.
- Sesión persistente durante la pestaña mediante `sessionStorage` y cierre automático ante 401.
- Errores de red traducidos a instrucciones claras para encender FastAPI.
- Usuarios y catálogo usan formularios modales completos; se eliminaron prompts del navegador.
- Catálogo administrativo incluye activos/inactivos, búsqueda, edición, desactivación y reactivación.
- Reportes muestran cuatro métricas y filtros administrativos.
- CORS validado para `localhost` y `127.0.0.1`.
- Render Blueprint agregado sin secretos y con health check.
- Pruebas: 15 correctas; frontend compilado con 25 módulos.
- Próximo paso: revisión visual, Postman, Power BI y despliegue externo.

### 2026-11-06 — Cierre del código local

- Servicios desactivados visibles y no invocables desde frontend ni API.
- Consumo personal muestra cuota, tokens usados y saldo mensual.
- Logout ejecuta el endpoint y elimina la sesión local.
- Sesión restaurada revalida usuario y rol mediante `/auth/me`.
- Postman incluye pruebas HTTP globales, JWT automático y datos únicos por ejecución.
- Scripts PowerShell agregados para iniciar y verificar el proyecto.
- Verificación HTTP real: servicios, resumen personal, catálogo admin y reporte respondieron 200.
- Pruebas: 17 correctas; colección Postman válida; frontend compilado.
- Estado: código local de la rúbrica preparado; quedan acciones externas y evidencias.
