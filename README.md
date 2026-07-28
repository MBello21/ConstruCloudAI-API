# ConstruCloudAI API

**Backend inteligente para generación asistida de presupuestos de construcción con RAG (Retrieval-Augmented Generation).**

---

## 🏗️ ¿Qué es ConstruCloudAI?

ConstruCloudAI es una plataforma cloud-native que revoluciona la creación de presupuestos en la industria de la construcción. Integra **búsqueda vectorial** con **generación de IA**, permitiendo que los presupuestistas generen documentos profesionales en segundos, basándose en contexto histórico de trabajos anteriores.

En lugar de escribir presupuestos desde cero, nuestro sistema busca presupuestos similares en la base de datos y usa esa información como referencia para generar presupuestos nuevos consistentes, completos y con precios alineados.

---

## 🎯 ¿Por Qué RAG?

**Retrieval-Augmented Generation** proporciona ventajas clave:

| Ventaja | Beneficio |
|---------|-----------|
| **Contexto Histórico** | Genera presupuestos consistentes con trabajos anteriores similares |
| **Precisión de Precios** | Los precios se basan en datos reales de la empresa, no en estimaciones |
| **Escalabilidad Inteligente** | A más presupuestos en el historial, mejores son las sugerencias |
| **Rapidez** | De horas a segundos en la creación de presupuestos complejos |
| **Trazabilidad** | Cada presupuesto generado incluye referencias a los trabajos que lo inspiraron |
| **Menos Alucinaciones de IA** | El modelo está anclado a datos reales de la empresa |

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología | Versión |
|------|-----------|---------|
| **Runtime** | Python | 3.14+ |
| **Framework Web** | FastAPI | 0.110+ |
| **ORM & Migraciones** | SQLAlchemy + Alembic | 2.0+ |
| **Base de Datos** | PostgreSQL + pgvector | 17+ |
| **Vector Store** | pgvector (extensión PostgreSQL) | 0.6+ |
| **LLM** | Groq API (Mixtral 8x7B) | - |
| **Embeddings** | Sentence Transformers | multilingual-MiniLM-L6 |
| **Autenticación** | JWT (access/refresh tokens) | - |
| **Contenedorización** | Docker + Docker Compose | 24+ |
| **Gestor de Dependencias** | Pipenv | - |
| **Desarrollo** | VS Code DevContainer | - |

---

## 📦 Instalación

### Requisitos Previos

- Docker & Docker Compose (`docker --version`, `docker-compose --version`)
- Python 3.14+ (si ejecutas sin Docker)
- Git
- Cuenta en [Groq Console](https://console.groq.com/keys)

### Paso 1: Clonar el Repositorio

```bash
git clone git@github.com:MBello21/ConstruCloudAI-API.git
cd ConstruCloudAI-API
```

### Paso 2: Opción A - DevContainer (Recomendado)

Si usas **VS Code**, abre la carpeta y selecciona "Reopen in Container" cuando aparezca la notificación. Esto configurará todo automáticamente.

### Paso 2: Opción B - Setup Manual

```bash
# Instalar dependencias Python
pipenv install

# Copiar plantilla de variables de entorno
cp .env.example .env

# Editar .env con tus valores (ver sección siguiente)
nano .env  # o tu editor preferido
```

### Paso 3: Iniciar la Base de Datos

```bash
# Levanta PostgreSQL + pgvector en Docker
docker compose -f .devcontainer/docker-compose.yml up -d

# Espera ~5 segundos a que PostgreSQL esté listo
sleep 5

# Aplica todas las migraciones
pipenv run upgrade
```

---

## ⚙️ Configuración

### Variables de Entorno (.env)

Copia `.env.example` a `.env` y completa:

```env
# Base de Datos
DATABASE_URL=postgresql://construcloud:construcloud123@localhost:5432/construcloud_db

# JWT
SECRET_KEY=tu_clave_super_secreta_de_256_bits_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Groq API
GROQ_API_KEY=tu_api_key_de_groq_aqui

# Embeddings
EMBEDDING_MODEL=sentence-transformers/multilingual-MiniLM-L6-v2

# FastAPI
ENVIRONMENT=development
DEBUG=true
```

**Obtener `GROQ_API_KEY`:**
1. Accede a [console.groq.com](https://console.groq.com)
2. Inicia sesión / regístrate gratis
3. Ve a **API Keys** → **Create API Key**
4. Copia la clave en `GROQ_API_KEY`

### Docker Compose

El archivo `.devcontainer/docker-compose.yml` levanta:

```yaml
services:
  db:
    image: pgvector/pgvector:pg17
    environment:
      POSTGRES_USER: construcloud
      POSTGRES_PASSWORD: construcloud123
      POSTGRES_DB: construcloud_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

**pgvector** viene preinstalado en la imagen. No necesitas configuración adicional.

### Verificar Conexión

```bash
# Conectar a PostgreSQL directamente
psql postgresql://construcloud:construcloud123@localhost:5432/construcloud_db

# Listar extensiones (pgvector debe estar)
\dx

# Salir
\q
```

---

## 🚀 Correr el Proyecto

### Desarrollo (Local)

```bash
# Terminal 1: Base de datos (si no está corriendo)
docker compose -f .devcontainer/docker-compose.yml up

# Terminal 2: Servidor FastAPI
pipenv run start

# Abre http://localhost:8000/docs (Swagger UI)
```

### Producción (Docker)

```bash
# Construye e inicia todos los servicios
docker compose up --build

# O en background
docker compose up -d --build

# Ver logs
docker compose logs -f app
```

### Scripts Disponibles (Pipfile)

```bash
pipenv run start       # Inicia servidor de desarrollo (uvicorn)
pipenv run migrate     # Crea nueva migración automática
pipenv run upgrade     # Aplica migraciones pendientes
pipenv run downgrade   # Revierte última migración
```

---

## 📡 Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| **POST** | `/auth/register` | Registrar nuevo usuario |
| **POST** | `/auth/login` | Obtener tokens JWT |
| **POST** | `/auth/refresh` | Renovar access token |
| **GET** | `/presupuestos` | Listar presupuestos del usuario |
| **POST** | `/presupuestos` | Crear presupuesto manual |
| **GET** | `/presupuestos/{id}` | Obtener detalles de un presupuesto |
| **PUT** | `/presupuestos/{id}` | Actualizar presupuesto |
| **DELETE** | `/presupuestos/{id}` | Eliminar presupuesto |
| **POST** | `/ia/generar-con-rag` | **Generar presupuesto con RAG** |
| **POST** | `/ia/mejorar-presupuesto` | Mejorar un presupuesto con feedback |
| **GET** | `/capitulos` | Listar capítulos (categorías) |
| **POST** | `/capitulos` | Crear capítulo |
| **GET** | `/clientes` | Listar clientes del usuario |
| **POST** | `/clientes` | Crear nuevo cliente |

**Documentación interactiva completa:** `http://localhost:8000/docs`

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                      Cliente Frontend (React)                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │        FastAPI Backend (Python)       │
        │  ├─ routers/ (endpoints HTTP)        │
        │  ├─ services/ (lógica de negocio)    │
        │  ├─ models/ (SQLAlchemy ORM)         │
        │  └─ core/ (autenticación JWT)        │
        └────────┬─────────────────┬───────────┘
                 │                 │
      ┌──────────▼──────┐   ┌──────▼──────────────┐
      │  PostgreSQL     │   │  Groq API (LLM)    │
      │  + pgvector     │   │                    │
      │                 │   │  - Mixtral 8x7B   │
      │ ┌─────────────┐ │   │  - Generación     │
      │ │ Presupuestos│ │   │  - RAG            │
      │ ├─────────────┤ │   └───────────────────┘
      │ │ Embeddings  │ │   (respuestas en JSON)
      │ │ (pgvector)  │ │
      │ └─────────────┘ │
      │                 │
      │ • Búsqueda      │
      │   vectorial     │
      │ • Almacenamiento│
      │   de contexto   │
      └─────────────────┘

┌─────────────────────────────────────────────────────┐
│  Embeddings Service (Sentence Transformers)         │
│  - Genera embeddings de descripciones de trabajos   │
│  - Busca similitud vectorial en PostgreSQL          │
└─────────────────────────────────────────────────────┘
```

**Flujo RAG:**
1. Usuario envía descripción de trabajo
2. **Embedding Service** convierte el texto a vector
3. **PostgreSQL + pgvector** busca presupuestos similares (búsqueda coseno)
4. Se extraen los 3 presupuestos más parecidos
5. Se construye un prompt con contexto histórico
6. **Groq API** genera presupuesto nuevo basado en referencias
7. Se devuelve presupuesto completo + referencias usadas

---

## 💡 Ejemplo de Uso

### Escenario: Cliente solicita presupuesto de reforma de cocina

#### 1. Crear Cliente (Solo la primera vez)

```bash
curl -X POST http://localhost:8000/clientes \
  -H "Authorization: Bearer <tu_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan García",
    "email": "juan@example.com",
    "telefono": "+34 600 123 456"
  }'
```

#### 2. Generar Presupuesto con RAG

```bash
curl -X POST http://localhost:8000/ia/generar-con-rag \
  -H "Authorization: Bearer <tu_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Reforma Integral Cocina - García",
    "descripcion": "Cliente solicita reforma completa de cocina de 12m2. Incluye: retirada de muebles antiguos, nuevas instalaciones eléctricas, fontanería, alicatados y pintura. Plazo 2 semanas.",
    "max_contexto": 3
  }'
```

#### 3. Respuesta (Ejemplo)

```json
{
  "presupuesto_generado": "PRESUPUESTO DETALLADO\n==================\n\nDESCRIPCIÓN:\nReforma integral de cocina...",
  "contexto_usado": [
    {
      "presupuesto_id": 42,
      "titulo": "Reforma Cocina Apartamento Centro",
      "total": 4500.00,
      "iva": 21,
      "similitud": 0.94
    },
    {
      "presupuesto_id": 51,
      "titulo": "Cocina Nueva Vivienda Unifamiliar",
      "total": 6200.00,
      "iva": 21,
      "similitud": 0.87
    }
  ],
  "similitud_promedio": 0.89,
  "cantidad_referencias": 2,
  "titulo": "Reforma Integral Cocina - García",
  "descripcion": "Cliente solicita reforma..."
}
```

#### 4. Mejorar si Cliente da Feedback

```bash
curl -X POST http://localhost:8000/ia/mejorar-presupuesto \
  -H "Authorization: Bearer <tu_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "presupuesto_id": 99,
    "feedback": "El cliente quiere cambiar los azulejos a marca premium y agregar isla en la cocina. Aumentar presupuesto accordingly."
  }'
```

---

## 🔧 Troubleshooting

### "ERROR: cannot import name 'session' from sqlalchemy.orm"

**Causa:** Versión incompatible de SQLAlchemy.

**Solución:**
```bash
pipenv install SQLAlchemy==2.0.23
pipenv run upgrade
```

### "pgvector extension not found"

**Causa:** PostgreSQL no tiene pgvector instalado.

**Solución:** Usa la imagen Docker correcta:
```bash
# En docker-compose.yml
image: pgvector/pgvector:pg17  # ✓ Correcto
# NO usar: image: postgres:17
```

### "GROQ_API_KEY not found"

**Causa:** Variable de entorno no establecida.

**Solución:**
```bash
# Verificar archivo .env existe
cat .env | grep GROQ_API_KEY

# Si está vacío, agregar clave desde console.groq.com
echo "GROQ_API_KEY=gsk_..." >> .env
```

### "Port 5432 already in use"

**Causa:** PostgreSQL ya está corriendo en ese puerto.

**Solución:**
```bash
# Ver qué está usando el puerto
lsof -i :5432

# Liberar puerto (si es container viejo)
docker compose down

# O cambiar puerto en docker-compose.yml:
# ports: ["5433:5432"]  # Nuevo puerto local
```

### "Connection timeout to database"

**Causa:** PostgreSQL está iniciando. El servicio tarda ~5 segundos.

**Solución:**
```bash
# Esperar explícitamente
docker compose up -d
sleep 10

# Luego correr migraciones
pipenv run upgrade
```

### Migraciones no aplican

**Causa:** Versión de Alembic desincronizada.

**Solución:**
```bash
# Ver historial
pipenv run alembic current

# Forzar a versión específica
pipenv run alembic stamp <revision>

# Luego upgrade
pipenv run upgrade
```

---

## 🚀 Próximos Pasos

- [ ] **Exportación PDF:** Generar PDFs profesionales de presupuestos
- [ ] **Versionado de Presupuestos:** Historial completo con cambios (diff)
- [ ] **Integración Stripe:** Pagos en línea de presupuestos aceptados
- [ ] **Análisis Predictivo:** Predicción de aceptación de presupuestos
- [ ] **Multi-idioma:** Soporte para presupuestos en EN/FR/DE
- [ ] **Auditoría Mejorada:** Logs detallados de quién cambió qué y cuándo
- [ ] **Webhook Events:** Notificaciones en tiempo real a clientes
- [ ] **Dashboard Analytics:** KPIs de presupuestos (tasa aceptación, tiempo medio, etc.)

---

## 📄 Licencia

Proyecto privado desarrollado en colaboración con **4Geeks Academy**.  
Período: Julio - Agosto 2026.

---

## 👥 Soporte

- **Documentación completa:** `http://localhost:8000/docs`
- **Issues:** Reporta problemas en el repositorio de GitHub
- **Email:** Para preguntas técnicas contacta al equipo

---

**Hecho con ❤️ by ConstruCloudAI Team**
