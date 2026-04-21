# Rayito Pharmacy Backend

Django REST backend for the Rayito Pharmacy web platform. It provides the API layer for authentication, catalog administration, product images, services, contact data, history, and the admin dashboard used by the React frontend.

## Tech Stack

- Python 3.12
- Django
- Django REST Framework
- JWT authentication
- SQLite for local development
- PostgreSQL / Neon for production
- Cloudinary for product image uploads

## Current Scope

- Admin authentication with JWT
- Product, category, service, contact, and history modules
- Image upload support through Cloudinary
- Local SQLite support
- Production-ready PostgreSQL configuration through `DATABASE_URL`
- CORS/CSRF configuration for a separated frontend

## Getting Started

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies and run migrations:

```powershell
cd backend
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The API runs locally at:

```text
http://127.0.0.1:8000
```

## Environment Variables

```env
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
POSTGRES_CONN_MAX_AGE=60
POSTGRES_SSLMODE=require
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
CLOUDINARY_UPLOAD_FOLDER=rayito-pharmacy
```

## Migrating From SQLite To Neon PostgreSQL

Export local data:

```powershell
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.permission > data.json
```

Apply migrations on PostgreSQL:

```powershell
python manage.py migrate
```

Import the exported data:

```powershell
python manage.py loaddata data.json
```

## Quality Checks

```powershell
python manage.py check
python manage.py test
```

## Related Repository

- Frontend: https://github.com/LuisOvalleH/Frontend-rayito-Pharmacy
