# ConstruCloudAI API

Backend de ConstruCloudAI — plataforma de generación de presupuestos de construcción asistidos por IA.

## Stack

- **Runtime:** Python 3.14
- **Framework:** FastAPI
- **ORM:** SQLAlchemy 2.0 + Alembic (migraciones)
- **Base de datos:** PostgreSQL 17
- **Autenticación:** JWT (access + refresh tokens)
- **IA:** Groq (LLM para sugerencia de partidas)
- **Containerización:** Docker + Docker Compose
- **Entorno:** Pipenv + DevContainer

## Estructura del proyecto

```
construcloudai-api/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── app.py                  # Entry point FastAPI
│       ├── database.py             # Engine, SessionLocal, Base
│       ├── router_global.py        # Router principal
│       ├── models/
│       │   ├── __init__.py
│       │   ├── usuario.py
│       │   ├── cliente.py
│       │   ├── presupuesto.py
│       │   ├── capitulo.py
│       │   ├── detalle.py
│       │   └── tarifa_base.py
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── usuario.py
│       │   ├── cliente.py
│       │   ├── presupuesto.py
│       │   ├── capitulo.py
│       │   ├── detalle.py
│       │   └── tarifa_base.py
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   ├── usuarios.py
│       │   ├── clientes.py
│       │   ├── presupuestos.py
│       │   ├── capitulos.py
│       │   ├── detalles.py
│       │   ├── tarifas.py
│       │   └── ia.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── auth_service.py
│       │   ├── presupuesto_service.py
│       │   ├── ia_service.py
│       │   └── pdf_service.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── security.py         # JWT, hashing
│       │   └── dependencies.py     # get_db, get_current_user
│       └── utils/
│           ├── __init__.py
│           └── exceptions.py
├── alembic/
│   ├── env.py
│   └── versions/
├── .devcontainer/
│   ├── devcontainer.json
│   ├── dockerfile
│   └── docker-compose.yml
├── alembic.ini
├── Pipfile
├── Pipfile.lock
├── Dockerfile
├── .env.example
├── .gitignore
└── README.md
```

## Scripts (Pipfile)

```bash
pipenv run start          # Arranca el servidor de desarrollo
pipenv run migrate        # Genera migración autogenerada
pipenv run upgrade        # Aplica migraciones pendientes
pipenv run downgrade      # Revierte última migración
```

## Setup local

```bash
# Clonar
git clone git@github.com:MBello21/ConstruCloudAI-API.git
cd ConstruCloudAI-API

# Abrir en DevContainer (VS Code)
# O setup manual:

# Dependencias
pipenv install

# Variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Base de datos
docker compose -f .devcontainer/docker-compose.yml up -d db
pipenv run upgrade

# Servidor de desarrollo
pipenv run start
```

## Deploy

Desplegado en Proxmox (homelab) con Docker Compose.

## Licencia

Proyecto privado — Labs by 4Geeks Academy (Jul–Ago 2026).
