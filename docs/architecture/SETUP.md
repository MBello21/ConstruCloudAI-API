# 🚀 SETUP - Guía Completa de Instalación

Instrucciones paso a paso para configurar ConstruCloudAI API en tu máquina local o servidor.

**Tiempo estimado:** 15-20 minutos (con DevContainer: 5 minutos)

---

## 1️⃣ Pre-requisitos

### Windows / macOS / Linux

Verifica que tienes instalado:

```bash
# Docker & Docker Compose
docker --version      # Debe ser 24.0+
docker-compose --version  # Debe ser 2.20+

# Python (opcional si usas DevContainer)
python --version      # Debe ser 3.14+
pip --version

# Git
git --version         # Debe ser 2.40+
```

### Instalación de pre-requisitos (si falta algo)

**Docker Desktop:** https://www.docker.com/products/docker-desktop

**Python 3.14:**
- **Windows:** https://www.python.org/downloads/
- **macOS:** `brew install python@3.14`
- **Linux (Ubuntu/Debian):** 
  ```bash
  sudo apt update
  sudo apt install python3.14 python3.14-venv python3-pip
  ```

**Git:** https://git-scm.com/downloads

---

## 2️⃣ Clonar Repositorio

```bash
# Elegir ubicación (ejemplo: ~/projects)
cd ~/projects

# Clonar repositorio
git clone git@github.com:MBello21/ConstruCloudAI-API.git

# Entrar al directorio
cd ConstruCloudAI-API

# Verificar branch actual
git branch -a
# Deberías ver: main, rag, etc.

# Checkout a la rama principal
git checkout main
```

**Resultado esperado:**
```
ConstruCloudAI-API/
├── src/
├── alembic/
├── .devcontainer/
├── docs/
├── .env.example
├── Pipfile
├── README.md
└── ...
```

---

## 3️⃣ Instalar Dependencias con Pipenv

### Opción A: Setup Automático (DevContainer) ⭐ RECOMENDADO

Si usas **VS Code**:

1. Abre VS Code
2. Abre la carpeta del proyecto
3. Deberías ver un popup: **"Reopen in Container"**
4. Haz clic en él
5. Espera 2-3 minutos a que se construya
6. Listo, todo está instalado automáticamente

**Ventajas:**
- Todo aislado en contenedor
- No contaminas tu máquina local
- Mismo entorno en todos los desarrolladores
- PostgreSQL + pgvector incluidos

### Opción B: Setup Manual (Local)

```bash
# Instalar Pipenv (gestor de dependencias)
pip install pipenv

# Verificar instalación
pipenv --version

# Instalar todas las dependencias del proyecto
pipenv install

# Activar entorno virtual
pipenv shell

# Verificar paquetes instalados
pip list | grep -E "fastapi|sqlalchemy|groq"
```

**Resultado esperado:**
```
fastapi                 0.110.0
SQLAlchemy              2.0.23
groq                    0.7.1
python-dotenv           1.0.0
psycopg2-binary         2.9.9
sentence-transformers   2.5.1
...
```

**Desactivar entorno (cuando termines):**
```bash
exit  # O presiona Ctrl+D
```

---

## 4️⃣ Configurar Variables de Entorno (.env)

### Paso 1: Crear archivo .env

```bash
# Copiar plantilla
cp .env.example .env

# Verificar que se creó
ls -la .env
```

### Paso 2: Editar .env con tus valores

```bash
# Abrir en editor (elige uno)
nano .env
# o vim .env
# o gedit .env
# o VS Code: File > Open > .env
```

### Paso 3: Configurar cada variable

Asegúrate de que tu archivo `.env` contenga exactamente esto (sin comillas en los valores):

```env
# ===== BASE DE DATOS =====
DATABASE_URL=postgresql://construcloud:construcloud123@localhost:5432/construcloud_db

# ===== SEGURIDAD JWT =====
SECRET_KEY=your-super-secret-key-change-this-to-something-long-and-random-at-least-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ===== GROQ API (Obtener de console.groq.com) =====
GROQ_API_KEY=gsk_... (tu clave real aquí)

# ===== EMBEDDINGS =====
EMBEDDING_MODEL=sentence-transformers/multilingual-MiniLM-L6-v2

# ===== FASTAPI CONFIG =====
ENVIRONMENT=development
DEBUG=true

# ===== PUERTO (opcional) =====
PORT=8000
```

### Paso 4: Generar SECRET_KEY seguro (importante)

```bash
# Opción 1: Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Opción 2: OpenSSL
openssl rand -base64 32

# Opción 3: Online (solo desarrollo)
# https://www.uuidgenerator.net/ (copiar varios UUID)
```

**Copiar el resultado en `SECRET_KEY=...`**

### Paso 5: Verificar archivo .env

```bash
# Ver contenido (sin mostrar claves completas)
grep -v "^#" .env | grep -v "^$"

# Resultado esperado:
DATABASE_URL=postgresql://construcloud:construcloud123@localhost:5432/construcloud_db
SECRET_KEY=... (algo largo)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
GROQ_API_KEY=gsk_...
EMBEDDING_MODEL=sentence-transformers/multilingual-MiniLM-L6-v2
ENVIRONMENT=development
DEBUG=true
PORT=8000
```

---

## 5️⃣ Setup de pgvector

### ¿Qué es pgvector?

Extensión de PostgreSQL que permite almacenar y buscar **vectores de embeddings** (números que representan texto). Esencial para la búsqueda RAG.

### Paso 1: Levantar PostgreSQL con pgvector

```bash
# Si estás EN DevContainer: Skip (ya está incluido)

# Si estás LOCAL: Usar Docker
docker compose -f .devcontainer/docker-compose.yml up -d

# Verificar que el contenedor está corriendo
docker ps | grep postgres
```

**Resultado esperado:**
```
pgvector/pgvector:pg17  "docker-entrypoint..."  Up 2 minutes
```

### Paso 2: Conectar a la base de datos

```bash
# Esperar 5 segundos a que PostgreSQL esté listo
sleep 5

# Conectar (sin Pipenv)
psql postgresql://construcloud:construcloud123@localhost:5432/construcloud_db

# O (con Pipenv)
pipenv run psql postgresql://construcloud:construcloud123@localhost:5432/construcloud_db
```

### Paso 3: Verificar que pgvector está instalado

Dentro de psql:

```sql
-- Listar todas las extensiones
\dx

-- Resultado esperado: deberías ver
--  plpgsql
--  pgvector

-- Si NO ves pgvector, instalarlo:
CREATE EXTENSION IF NOT EXISTS vector;

-- Verificar que funciona
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Salir
\q
```

### Paso 4: Crear tabla de prueba (opcional)

```sql
-- Dentro de psql

-- Crear tabla con vector
CREATE TABLE test_embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(384)  -- 384 dimensiones (MiniLM-L6)
);

-- Crear índice para búsqueda rápida
CREATE INDEX ON test_embeddings USING ivfflat (embedding vector_cosine_ops);

-- Ver tabla
\dt test_embeddings

-- Limpiar (opcional)
DROP TABLE test_embeddings;

-- Salir
\q
```

---

## 6️⃣ Setup de Groq API

### Paso 1: Crear cuenta en Groq

1. Accede a https://console.groq.com
2. Haz clic en **"Sign Up"** o **"Sign In"**
3. Completa el registro (email + contraseña)
4. Verifica tu email

### Paso 2: Obtener API Key

```
Dashboard → API Keys → Create New API Key
```

1. Haz clic en **"Create API Key"**
2. Dale un nombre: `ConstruCloudAI-Dev`
3. Copia la clave (formato: `gsk_...`)
4. **IMPORTANTE: Guárdala en un lugar seguro** (no la compartas)

### Paso 3: Agregar a .env

```bash
# Editar .env
nano .env

# Buscar: GROQ_API_KEY=
# Reemplazar con tu clave real
GROQ_API_KEY=gsk_... (tu clave aquí)

# Guardar (Ctrl+O → Enter → Ctrl+X)
```

### Paso 4: Verificar que funciona

```bash
# Con Pipenv
pipenv run python -c "
from groq import Groq
import os
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
response = client.chat.completions.create(
    model='mixtral-8x7b-32768',
    messages=[{'role': 'user', 'content': 'Di hola'}]
)
print('✅ Groq funciona!')
print(response.choices[0].message.content)
"
```

**Resultado esperado:**
```
✅ Groq funciona!
¡Hola! ¿Cómo estás? ¿En qué puedo ayudarte?
```

**Si falla:**
- ❌ `AuthenticationError`: Clave API incorrecta
- ❌ `RateLimitError`: Demasiadas requests (espera un minuto)
- ❌ `APIError`: Servidor de Groq caído (espera y reintenta)

---

## 7️⃣ Setup de Hugging Face

### ¿Qué es?

Librería para descargar modelos de **embeddings** (conversión de texto a vectores).  
Se usa para convertir descripciones de trabajo en vectores que podemos buscar.

### Paso 1: Instalar (ya incluido en Pipenv)

```bash
# Verificar que está instalado
pipenv run pip list | grep sentence-transformers

# Resultado esperado:
# sentence-transformers         2.5.1
```

### Paso 2: Configurar modelo de embeddings

El archivo `.env` ya contiene:
```env
EMBEDDING_MODEL=sentence-transformers/multilingual-MiniLM-L6-v2
```

Este modelo:
- Soporta múltiples idiomas (español, inglés, etc.)
- Tiene 384 dimensiones (tamaño optimizado)
- Pesa ~60MB
- Se descarga automáticamente la primera vez

### Paso 3: Descargar modelo (primera vez)

La primera vez que se ejecuta, el modelo se descarga automáticamente (~60MB).  
Puedes hacerlo manualmente para verificar:

```bash
pipenv run python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/multilingual-MiniLM-L6-v2')
print('✅ Modelo descargado correctamente')
print(f'Dimensiones: {model.get_sentence_embedding_dimension()}')
"
```

**Resultado esperado:**
```
✅ Modelo descargado correctamente
Dimensiones: 384
```

**Ubicación de caché:** `~/.cache/huggingface/hub/`

### Paso 4: Crear un embedding de prueba

```bash
pipenv run python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/multilingual-MiniLM-L6-v2')

# Convertir texto a vector
text = 'Reforma de cocina con azulejos y grifería nueva'
embedding = model.encode(text)

print(f'✅ Embedding creado')
print(f'Dimensiones: {len(embedding)}')
print(f'Primeros 5 valores: {embedding[:5]}')
"
```

**Resultado esperado:**
```
✅ Embedding creado
Dimensiones: 384
Primeros 5 valores: [-0.123, 0.456, -0.789, 0.234, ...]
```

---

## 8️⃣ Alembic Migrations

### ¿Qué es Alembic?

Sistema de control de versiones para bases de datos.  
Permite versionar cambios en el esquema (tablas, columnas) igual que Git.

### Paso 1: Verificar estado actual

```bash
# Ver qué migraciones existen
pipenv run alembic current

# Resultado esperado:
# [current_revision]  (head)

# Ver historial completo
pipenv run alembic history --verbose
```

### Paso 2: Aplicar TODAS las migraciones pendientes

```bash
# Upgrade a la última versión
pipenv run upgrade

# O manualmente:
pipenv run alembic upgrade head

# Resultado esperado:
# INFO [alembic.runtime.migration] Running upgrade ... (paso a paso)
# INFO [alembic.runtime.migration] Running upgrade [hash] -> head, ...
```

### Paso 3: Verificar que funcionó

```bash
# Ver migraciones aplicadas
pipenv run alembic current

# Verificar tablas creadas
psql postgresql://construcloud:construcloud123@localhost:5432/construcloud_db -c "\dt"

# Resultado esperado:
# usuarios
# clientes
# presupuestos
# presupuesto_embeddings
# capitulos
# detalles
# (más tablas...)
```

### Paso 4: Crear una migración nueva (si cambias models)

```bash
# Si cambias algo en src/app/models/
# Generar migración automática:
pipenv run migrate --message "descripcion de cambios"

# Ejemplo:
pipenv run migrate --message "add new column to presupuestos"

# Resultado: nuevo archivo en alembic/versions/

# Luego aplicarla:
pipenv run upgrade
```

### Paso 5: Revertir migración (si algo sale mal)

```bash
# Revertir última migración
pipenv run downgrade -1

# Revertir a una versión específica
pipenv run alembic downgrade [revision_id]

# Ver historiales
pipenv run alembic history
```

---

## 9️⃣ Correr Proyecto

### Opción A: En DevContainer (RECOMENDADO)

```bash
# Dentro del container (ya estás con todo configurado)

# Terminal 1: Iniciar servidor FastAPI
pipenv run start

# Resultado esperado:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete
```

Accede a:
- **API Docs:** http://localhost:8000/docs (Swagger UI)
- **API Redoc:** http://localhost:8000/redoc (ReDoc)
- **Health Check:** http://localhost:8000/health (si existe)

### Opción B: En Local (Manual)

```bash
# Activar entorno
pipenv shell

# Terminal 1: Base de datos (si no está corriendo)
docker compose -f .devcontainer/docker-compose.yml up

# Terminal 2: Servidor
pipenv run start

# O manualmente:
uvicorn src.app.app:app --reload --host 0.0.0.0 --port 8000
```

### Opción C: Con Docker (Producción)

```bash
# Construir imagen
docker compose build

# Iniciar todos los servicios
docker compose up -d

# Ver logs
docker compose logs -f app

# Detener
docker compose down
```

### Paso: Verificar que funciona

```bash
# En otra terminal, hacer request de prueba
curl -X GET http://localhost:8000/docs

# O con Python
python -c "
import requests
response = requests.get('http://localhost:8000/health')
print(f'Status: {response.status_code}')
print(f'Response: {response.json()}')
"
```

---

## 🔟 Verificaciones (Tests)

### Verificación 1: Base de Datos

```bash
# Conectar a PostgreSQL
psql postgresql://construcloud:construcloud123@localhost:5432/construcloud_db

# Ver tablas
\dt

# Ver extensiones
\dx

# Salir
\q
```

**Resultado esperado:**
```
Debería listar: usuarios, clientes, presupuestos, presupuesto_embeddings, etc.
```

### Verificación 2: Groq API

```bash
# Test manual
python -c "
from groq import Groq
import os
client = Groq(api_key=os.getenv('GROQ_API_KEY'))
response = client.chat.completions.create(
    model='mixtral-8x7b-32768',
    messages=[{'role': 'user', 'content': 'Test'}]
)
print('✅ Groq OK')
"
```

### Verificación 3: Embeddings

```bash
# Test modelo
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/multilingual-MiniLM-L6-v2')
embedding = model.encode('test')
print(f'✅ Embeddings OK - Dimensiones: {len(embedding)}')
"
```

### Verificación 4: API Endpoints

```bash
# Registrar usuario
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123",
    "full_name": "Test User"
  }'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'

# Resultado esperado: token JWT
```

### Verificación 5: Ejecutar tests (si existen)

```bash
# Ver si hay tests
find . -name "test_*.py" -o -name "*_test.py"

# Ejecutar todos
pipenv run pytest

# Ejecutar con cobertura
pipenv run pytest --cov

# Test específico
pipenv run pytest tests/test_auth.py -v
```

---

## 1️⃣1️⃣ Solución de Problemas Comunes

### ❌ Error: "database does not exist"

```bash
# Causa: PostgreSQL no tiene la DB creada
# Solución: Crear manualmente

psql postgresql://construcloud:construcloud123@localhost:5432/postgres -c "
CREATE DATABASE construcloud_db;
"

# Luego aplicar migraciones
pipenv run upgrade
```

### ❌ Error: "psycopg2.OperationalError: connection refused"

```bash
# Causa: PostgreSQL no está corriendo
# Solución:

# Opción 1: Si está en Docker
docker compose -f .devcontainer/docker-compose.yml up -d

# Opción 2: Verificar que está corriendo
docker ps | grep postgres

# Opción 3: Ver logs
docker compose -f .devcontainer/docker-compose.yml logs postgres
```

### ❌ Error: "pgvector extension not found"

```bash
# Causa: PostgreSQL no tiene pgvector
# Solución: Usar imagen correcta en docker-compose.yml

# ✓ Correcto:
image: pgvector/pgvector:pg17

# ✗ Incorrecto:
image: postgres:17

# Después, recrear contenedor:
docker compose -f .devcontainer/docker-compose.yml down
docker compose -f .devcontainer/docker-compose.yml up -d
```

### ❌ Error: "port 5432 already in use"

```bash
# Causa: Otro PostgreSQL está corriendo
# Solución:

# Ver qué está usando el puerto
lsof -i :5432

# Detener contenedor viejo
docker compose down

# O cambiar puerto en docker-compose.yml:
# ports: ["5433:5432"]  # Mapear a puerto diferente

# Luego actualizar .env:
DATABASE_URL=postgresql://construcloud:construcloud123@localhost:5433/construcloud_db
```

### ❌ Error: "GROQ_API_KEY not set"

```bash
# Causa: Variable de entorno no configurada
# Solución:

# Verificar archivo .env existe
ls -la .env

# Verificar que contiene GROQ_API_KEY
grep GROQ_API_KEY .env

# Si está vacío, agregarlo
echo "GROQ_API_KEY=gsk_..." >> .env

# Recargar variables (si estás en DevContainer)
# Rebuild el container
```

### ❌ Error: "ModuleNotFoundError: No module named 'fastapi'"

```bash
# Causa: Dependencias no instaladas
# Solución:

# Reinstalar todas
pipenv install --dev

# O actualizar
pipenv update

# O dentro del shell de Pipenv
pipenv shell
pip install -r requirements.txt  # Si existe
```

### ❌ Error: "Could not connect to localhost:5432"

```bash
# Causa: PostgreSQL tarda en iniciar
# Solución: Esperar más tiempo

# Esperar 10 segundos después de levantar Docker
docker compose -f .devcontainer/docker-compose.yml up -d
sleep 10

# Verificar que está listo
docker compose -f .devcontainer/docker-compose.yml exec db pg_isready

# Resultado esperado: "accepting connections"
```

### ❌ Error: "alembic.util.exc.CommandError: Can't locate revision identified"

```bash
# Causa: Historial de migraciones corrupto
# Solución: Sincronizar

# Ver versión actual
pipenv run alembic current

# Forzar a versión específica
pipenv run alembic stamp [revision_id]

# Ver todas las revisiones
pipenv run alembic history
```

### ❌ Error en DevContainer: "Connection refused"

```bash
# Causa: Container tardó en iniciar
# Solución: Rebuild

# Close container
F1 → "Dev Containers: Rebuild Container"

# O desde terminal
docker compose -f .devcontainer/docker-compose.yml down
docker compose -f .devcontainer/docker-compose.yml up -d
```

### ❌ Error: "Uvicorn can't start on port 8000"

```bash
# Causa: Puerto ya está en uso
# Solución:

# Ver qué está usando puerto 8000
lsof -i :8000

# Matar proceso
kill -9 [PID]

# O cambiar puerto
uvicorn src.app.app:app --port 8001

# O en .env
PORT=8001
```

### ❌ Lentitud extrema en embeddings

```bash
# Causa: CPU insuficiente o GPU no detectada
# Solución:

# Usar modelo más pequeño (ya está configurado)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# O descargar en caché antes de usar
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('...')
# Esto precarga en memoria
"
```

---

## ✅ Checklist Final

Cuando termines, verifica que puedas:

- [ ] Acceder a `http://localhost:8000/docs`
- [ ] Registrar un usuario
- [ ] Hacer login
- [ ] Ver tablas en PostgreSQL (`\dt` en psql)
- [ ] Ver extensión pgvector (`\dx` en psql)
- [ ] Ejecutar query Groq sin errores
- [ ] Generar embeddings sin errores
- [ ] (Opcional) Ejecutar tests

---

## 🎯 Próximo Paso

Cuando todo esté funcionando:

1. Lee `/docs/architecture/` para entender la arquitectura
2. Lee `README.md` para overview del proyecto
3. Explora `src/app/` para ver la estructura del código
4. Ve a `src/app/routers/` para entender los endpoints

**¡Listo para desarrollar! 🚀**

---

## 📞 Soporte

- Documentación: `README.md`
- Arquitectura: `docs/architecture/`
- API Docs: `http://localhost:8000/docs`
- Issues: Reporta en GitHub
