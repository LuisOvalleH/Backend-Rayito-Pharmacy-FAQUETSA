# Backend Rayito Pharmacy + Frontend

## Estado actual

- Backend Django con autenticacion JWT para admin.
- Frontend React/Vite con login real y rutas admin protegidas.
- Soporte para SQLite en local y PostgreSQL (Neon) por `DATABASE_URL`.

## Requisitos

- Python 3.12
- Node.js 20+

## Ejecutar backend

Desde `c:\Users\luism\Backend-Rayito-Pharmacy-FAQUETSA`:

```powershell
.\venv\Scripts\Activate.ps1
cd backend
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Backend: `http://127.0.0.1:8000`

## Ejecutar frontend

Desde `C:\Users\luism\Frontend-rayito-Pharmacy`:

```powershell
npm install
npm run dev
```

Frontend: `http://localhost:5173`

Login admin: `http://localhost:5173/admin/login`

## Migrar de SQLite a Neon PostgreSQL

1. Crear un proyecto en Neon y copiar la cadena de conexion.
2. En `backend/.env`, configurar:

```env
DJANGO_SECRET_KEY=tu-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
POSTGRES_CONN_MAX_AGE=60
POSTGRES_SSLMODE=require
```

3. Exportar los datos actuales desde SQLite:

```powershell
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.permission > data.json
```

4. Aplicar migraciones sobre Neon:

```powershell
python manage.py migrate
```

5. Importar los datos:

```powershell
python manage.py loaddata data.json
```

6. Verificar:

```powershell
python manage.py check
python manage.py test
```

## Variables de entorno

- `DJANGO_SECRET_KEY`: clave secreta de Django.
- `DJANGO_DEBUG`: `True` en local, `False` en produccion.
- `DJANGO_ALLOWED_HOSTS`: hosts permitidos separados por coma.
- `DJANGO_CORS_ALLOWED_ORIGINS`: origins del frontend separados por coma.
- `DJANGO_CSRF_TRUSTED_ORIGINS`: origins confiables para CSRF.
- `DJANGO_SECURE_SSL_REDIRECT`: forzar HTTPS cuando aplique.
- `DATABASE_URL`: conexion PostgreSQL completa, recomendada para Neon.
- `POSTGRES_*`: alternativa si no se usa `DATABASE_URL`.

## Validacion rapida

Backend:

```powershell
cd backend
python manage.py check
python manage.py test
```

Frontend:

```powershell
cd C:\Users\luism\Frontend-rayito-Pharmacy
npm run lint
npm run build
```
