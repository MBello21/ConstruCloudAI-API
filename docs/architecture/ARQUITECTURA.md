# Arquitectura de ConstruCloudAI - Guía Técnica Completa

## 📋 Resumen Ejecutivo

**ConstruCloudAI** es una plataforma inteligente de gestión de presupuestos construcción que utiliza **Retrieval-Augmented Generation (RAG)** para generar presupuestos precisos y contextualizados. El sistema combina:

- **SQLAlchemy ORM** con PostgreSQL para persistencia
- **pgvector** para búsqueda semántica mediante embeddings
- **Modelos de IA** para generación de contenido contextual
- **Arquitectura modular** de presupuestos → capítulos → detalles

---

## 🏗️ 1. Entidades Principales

### 1.1 **Presupuestos** (Tabla: `presupuestos`)
Entidad central del sistema. Representa un proyecto o propuesta de construcción completa.

```python
# Campos principales
id: int                           # ID único (PK)
codigo: str(50)                   # Código único: "PRES-2024-001"
titulo: str(300)                  # Nombre del proyecto
descripcion: str                  # Descripción detallada
estado: EstadoPresupuesto        # BORRADOR → ENVIADO → ACEPTADO/RECHAZADO
subtotal: Numeric                # Suma de todos los detalles
iva: Numeric(21.00)              # Porcentaje IVA aplicado
total: Numeric                    # subtotal + IVA
condiciones_pago: str            # Términos de pago
validez_dias: int                # Días de validez de la oferta (default: 30)
contexto_rag: str                # Contexto acumulado para RAG
created_at, updated_at: datetime # Auditoría temporal
```

**Relaciones:**
- 1:N → Capítulos (un presupuesto tiene muchos capítulos)
- 1:1 → PresupuestoEmbedding (embedding único por presupuesto)
- 1:N → ChatHistorial (historial de conversaciones)

---

### 1.2 **Capítulos** (Tabla: `capitulos`)
Subdivisiones principales del presupuesto. Agrupan detalles por categoría o fase constructiva.

```python
# Campos principales
id: int                        # ID único (PK)
presupuesto_id: int           # FK a presupuestos
numero: int                    # Número secuencial (1, 2, 3...)
nombre: str(300)              # "Cimientos", "Estructura", "Acabados"
orden: int                     # Orden de presentación (default: 0)
created_at: datetime          # Marca temporal
```

**Relaciones:**
- N:1 ← Presupuestos (cada capítulo pertenece a un presupuesto)
- 1:N → Detalles (un capítulo contiene muchos detalles)

---

### 1.3 **Detalles** (Tabla: `detalles`)
Items específicos de trabajo con costo unitario. Nivel más granular del presupuesto.

```python
# Campos principales
id: int                        # ID único (PK)
capitulo_id: int              # FK a capítulos
numero: int                    # Número en el capítulo (1.1, 1.2, etc.)
descripcion: str              # "Excavación manual 0-1m"
unidad: str(20)               # "m³", "m²", "kg", "ud"
cantidad: Numeric             # 15.5
precio_unitario: Numeric      # 45.00
subtotal: Numeric             # cantidad × precio_unitario = 697.50
generado_por_ia: bool         # Indicador de generación automática
precio_confirmado: bool       # Precio validado por usuario
es_externo: bool              # Subcontrata vs. interno
created_at, updated_at: datetime
```

**Relaciones:**
- N:1 ← Capítulos (cada detalle pertenece a un capítulo)

---

### 1.4 **PresupuestoEmbedding** (Tabla: `presupuestos_embeddings`)
Vectores semánticos para búsqueda RAG. Permite encontrar presupuestos similares por contexto.

```python
# Campos principales
id: int                        # ID único (PK)
presupuesto_id: int (unique)  # FK a presupuestos (relación 1:1)
contenido_indexado: str        # Texto completo indexado del presupuesto
embedding: Vector(384)         # Vector de 384 dimensiones (pgvector)
modelo_embedding: str          # "sentence-transformers/all-MiniLM-L6-v2"
created_at, updated_at: datetime
```

**Relaciones:**
- 1:1 ← Presupuestos (cada presupuesto tiene 1 embedding)

**Características técnicas:**
- Utiliza extensión PostgreSQL `pgvector`
- Dimensiones: 384 (sentence-transformers)
- Índice HNSW/IVFFlat para búsqueda rápida
- Se actualiza automáticamente al modificar presupuesto

---

### 1.5 **Users** (Tabla: `users`)
Autenticación y autorización del sistema.

```python
# Campos principales
id: int                        # ID único (PK)
email: str(120, unique)       # Email único
password_hash: str(256)       # Hash seguro de contraseña
is_active: bool               # Usuario activo/inactivo
```

---

### 1.6 **ChatHistorial** (Mencionado, pendiente de detalles)
Registro de conversaciones entre usuarios e IA para refinar presupuestos.

```python
# Estructura esperada
presupuesto_id: int           # FK a presupuestos
usuario_id: int               # FK a users
mensaje: str                  # Pregunta/respuesta
rol: str                       # "user" o "assistant"
created_at: datetime
```

---

## 🔄 2. Flujo de Datos Completo

```
┌─────────────────────────────────────────────────────────────┐
│                    CICLO DE VIDA PRESUPUESTO               │
└─────────────────────────────────────────────────────────────┘

[1] CREACIÓN INICIAL
    └─> Usuario inicia un nuevo presupuesto
        ├─> Presupuestos (estado: BORRADOR)
        ├─> Se genera embedding del título/descripción
        └─> PresupuestoEmbedding se indexa en pgvector

[2] GENERACIÓN AUTOMÁTICA (RAG)
    └─> Usuario solicita generar capítulos/detalles
        ├─> RETRIEVE: Buscar presupuestos similares
        │   └─> Búsqueda vectorial contra PresupuestoEmbedding
        ├─> AUGMENT: Enriquecer contexto
        │   └─> Obtener capítulos/detalles de presupuestos similares
        │   └─> Contexto guardado en Presupuestos.contexto_rag
        └─> GENERATE: Crear nuevos capítulos/detalles
            ├─> IA genera Capítulos con estructura similar
            ├─> IA genera Detalles con precios contextualizados
            └─> Flags: generado_por_ia=true

[3] REFINAMIENTO INTERACTIVO
    └─> Usuario conversa con IA para ajustar
        ├─> ChatHistorial registra conversación
        ├─> Usuario modifica detalles, precios, capítulos
        ├─> Flags actualizados: precio_confirmado, es_externo
        └─> Embedding se regenera con nuevo contexto

[4] FINALIZACIÓN
    └─> Usuario revisa y confirma presupuesto
        ├─> Cálculo automático: subtotal = Σ(detalles.subtotal)
        ├─> total = subtotal × (1 + iva/100)
        ├─> Estado → ENVIADO
        ├─> Embedding se reindexan (para futuras búsquedas)
        └─> Auditoría temporal registrada (updated_at)

[5] REUTILIZACIÓN
    └─> Futuro presupuesto similar busca contexto
        └─> Encontrado vía embedding similarity search
            └─> Ciclo regresa a [2] RETRIEVE
```

---

## 🤖 3. Flujo RAG: RETRIEVE → AUGMENT → GENERATE

### 3.1 **RETRIEVE** (Búsqueda Semántica)

```python
# Pseudocódigo del flujo RETRIEVE

def retrieve_similar_budgets(query: str, top_k: int = 5):
    """
    Busca presupuestos similares sin dependencia de palabras clave exactas
    """
    
    # [1] Generar embedding de la consulta
    query_embedding = embedding_model.encode(query)
    
    # [2] Búsqueda en pgvector (similitud coseno)
    similar = db.query(PresupuestoEmbedding)\
        .order_by(PresupuestoEmbedding.embedding.cosine_distance(query_embedding))\
        .limit(top_k)\
        .all()
    
    # [3] Recuperar presupuestos completos con estructura
    results = []
    for emb in similar:
        presupuesto = emb.presupuesto
        results.append({
            'id': presupuesto.id,
            'titulo': presupuesto.titulo,
            'capitulos': presupuesto.capitulos,  # Todos los capítulos
            'detalles': [d for c in presupuesto.capitulos for d in c.detalles],
            'similarity_score': compute_similarity(query_embedding, emb.embedding)
        })
    
    return results
```

**Características:**
- Búsqueda por similitud semántica (no búsqueda exacta por palabras)
- Recupera presupuestos similares incluso si la redacción es diferente
- Ejemplo: "casa moderna en Madrid" ≈ "vivienda residencial M-40"

---

### 3.2 **AUGMENT** (Enriquecimiento de Contexto)

```python
# Pseudocódigo del flujo AUGMENT

def augment_context(presupuesto_actual: Presupuestos, similar_budgets: list):
    """
    Enriquece el presupuesto actual con contexto de presupuestos similares
    """
    
    # [1] Extraer estructura de presupuestos similares
    capitulos_template = {}
    detalles_template = {}
    
    for similar in similar_budgets:
        for cap in similar['capitulos']:
            if cap.nombre not in capitulos_template:
                capitulos_template[cap.nombre] = {
                    'numero': cap.numero,
                    'detalles_count': len(cap.detalles),
                    'avg_subtotal': sum(d.subtotal for d in cap.detalles) / len(cap.detalles)
                }
        
        for det in similar['detalles']:
            key = (det.descripcion[:50], det.unidad)
            if key not in detalles_template:
                detalles_template[key] = {
                    'precio_medio': det.precio_unitario,
                    'cantidad_media': det.cantidad,
                    'subcontrata': det.es_externo
                }
    
    # [2] Guardar contexto enriquecido
    presupuesto_actual.contexto_rag = json.dumps({
        'capitulos_similares': capitulos_template,
        'detalles_similares': detalles_template,
        'total_referencias': len(similar_budgets),
        'retrieved_at': datetime.now().isoformat()
    })
    
    db.commit()
    
    return presupuesto_actual.contexto_rag
```

**Datos Enriquecidos:**
- Estructura de capítulos típica para el tipo de proyecto
- Rangos de precios por concepto
- Tendencias (subcontratas vs. trabajo interno)
- Estadísticas de presupuestos similares

---

### 3.3 **GENERATE** (Generación Automática)

```python
# Pseudocódigo del flujo GENERATE

def generate_budget_structure(presupuesto: Presupuestos, ia_model):
    """
    Genera capítulos y detalles usando el contexto RAG
    """
    
    # [1] Construcción del prompt contextualizado
    prompt = f"""
    Eres un experto en presupuestos de construcción.
    
    Proyecto: {presupuesto.titulo}
    Descripción: {presupuesto.descripcion}
    
    Contexto de presupuestos similares:
    {presupuesto.contexto_rag}
    
    Genera una estructura de capítulos y detalles realista:
    - Sigue la estructura de presupuestos similares
    - Usa precios del contexto como referencia
    - Incluye unidades y cantidades coherentes
    """
    
    # [2] Llamada a IA (Claude, GPT, etc.)
    response = ia_model.generate(prompt, temperature=0.7)
    
    # [3] Parsing de respuesta en estructura DB
    parsed = parse_ia_response(response)  # JSON parsing
    
    # [4] Creación de Capítulos
    for cap_data in parsed['capitulos']:
        capitulo = Capitulos(
            presupuesto_id=presupuesto.id,
            numero=cap_data['numero'],
            nombre=cap_data['nombre'],
            orden=cap_data['orden']
        )
        db.add(capitulo)
        db.flush()  # Obtener ID
        
        # [5] Creación de Detalles
        for det_data in cap_data['detalles']:
            detalle = Detalles(
                capitulo_id=capitulo.id,
                numero=det_data['numero'],
                descripcion=det_data['descripcion'],
                unidad=det_data['unidad'],
                cantidad=det_data['cantidad'],
                precio_unitario=det_data['precio_unitario'],
                subtotal=det_data['cantidad'] * det_data['precio_unitario'],
                generado_por_ia=True,  # ← Marca generación automática
                precio_confirmado=False,  # Requiere validación
                es_externo=det_data.get('es_externo', False)
            )
            db.add(detalle)
    
    # [6] Recalcular totales
    presupuesto.subtotal = sum(d.subtotal for c in presupuesto.capitulos for d in c.detalles)
    presupuesto.total = presupuesto.subtotal * (1 + presupuesto.iva / 100)
    
    # [7] Regenerar embedding
    nuevo_embedding = embedding_model.encode(
        f"{presupuesto.titulo} {presupuesto.descripcion} {presupuesto.contexto_rag}"
    )
    presupuesto.embedding.embedding = nuevo_embedding
    
    db.commit()
    
    return presupuesto
```

**Resultado:**
- Capítulos con estructura lógica y jerarquía
- Detalles con descripciones coherentes
- Precios realistas basados en datos históricos
- Flags de auditoría: `generado_por_ia=true`

---

## 📊 4. Relaciones entre Tablas

### 4.1 Diagrama Entidad-Relación

```
┌──────────────────────────┐
│       PRESUPUESTOS       │
├──────────────────────────┤
│ id (PK)                  │
│ codigo (UNIQUE)          │
│ titulo                   │
│ descripcion              │
│ estado (ENUM)            │ ◄─────── Estados:
│ subtotal                 │          - BORRADOR
│ iva (21%)                │          - ENVIADO
│ total                    │          - ACEPTADO
│ condiciones_pago         │          - RECHAZADO
│ validez_dias             │
│ contexto_rag             │◄─────── JSON con contexto
│ created_at               │
│ updated_at               │
└──────────────────────────┘
         │        ▲
      1:N│        │1:1
         │        │
         ▼        │
┌──────────────────────────┐    ┌──────────────────────────┐
│      CAPÍTULOS           │    │ PRESUPUESTO_EMBEDDINGS   │
├──────────────────────────┤    ├──────────────────────────┤
│ id (PK)                  │    │ id (PK)                  │
│ presupuesto_id (FK)      │    │ presupuesto_id (FK,UQ)   │
│ numero                   │    │ contenido_indexado       │
│ nombre                   │    │ embedding (Vector 384)   │
│ orden                    │    │ modelo_embedding         │
│ created_at               │    │ created_at               │
└──────────────────────────┘    │ updated_at               │
         │                       └──────────────────────────┘
      1:N│                       (Búsqueda semántica RAG)
         │
         ▼
┌──────────────────────────┐
│      DETALLES            │
├──────────────────────────┤
│ id (PK)                  │
│ capitulo_id (FK)         │
│ numero                   │
│ descripcion              │
│ unidad                   │◄─────── m², m³, kg, ud, etc.
│ cantidad                 │
│ precio_unitario          │
│ subtotal (calculated)    │
│ generado_por_ia          │◄─────── Auditoría IA
│ precio_confirmado        │◄─────── Validación usuario
│ es_externo               │◄─────── Subcontrata
│ created_at               │
│ updated_at               │
└──────────────────────────┘
```

### 4.2 Cardinalidades

| Relación | Tipo | Descripción |
|----------|------|-------------|
| Presupuestos → Capítulos | 1:N | Un presupuesto tiene muchos capítulos |
| Capítulos → Detalles | 1:N | Un capítulo contiene muchos detalles |
| Presupuestos → PresupuestoEmbedding | 1:1 | Un presupuesto tiene un embedding único |
| Presupuestos → ChatHistorial | 1:N | Conversaciones sobre el presupuesto |

### 4.3 Cascadas

```python
# En Presupuestos
embedding = relationship(
    "PresupuestoEmbedding",
    cascade="all, delete-orphan",  # Elimina embedding si presupuesto se borra
    uselist=False
)

capitulos = relationship(
    "Capitulos",
    cascade="all, delete-orphan",  # Elimina capítulos si presupuesto se borra
    uselist=True                    # Lista porque es 1:N
)

# En Capítulos
detalles = relationship(
    "Detalles",
    cascade="all, delete-orphan"   # Elimina detalles si capítulo se borra
)
```

---

## 🗃️ 5. Gestión de Datos

### 5.1 Ciclo de Vida de un Registro

```
PRESUPUESTO
├─ created_at (servidor)    ← Generado en INSERT
├─ updated_at (servidor)    ← Igual a created_at en INSERT
│                           ← Actualizado en UPDATE automático
└─ deleted_at (soft delete) ← NO implementado (borrado físico)

DETALLE
├─ generado_por_ia          ← TRUE si IA lo creó
├─ precio_confirmado        ← Usuario debe confirmar antes de final
└─ es_externo               ← Ayuda a filtrar subcontratas
```

### 5.2 Cálculos Automáticos

```python
# Presupuesto.subtotal
subtotal = SUM(detalles.subtotal)

# Presupuesto.total
total = subtotal × (1 + iva / 100)

# Detalle.subtotal
subtotal = cantidad × precio_unitario
```

### 5.3 Validaciones

```python
# Campos NOT NULL
- Presupuestos: titulo, subtotal, iva, total
- Capítulos: presupuesto_id, numero, nombre
- Detalles: capitulo_id, numero, descripcion, unidad, cantidad, 
           precio_unitario, subtotal, generado_por_ia, 
           precio_confirmado, es_externo

# Campos UNIQUE
- Presupuestos.codigo
- Users.email

# Foreign Keys
- Capítulos.presupuesto_id → Presupuestos.id (nullable: sí)
- Detalles.capitulo_id → Capítulos.id (nullable: sí)
- PresupuestoEmbedding.presupuesto_id → Presupuestos.id (ondelete CASCADE)
```

---

## 🔍 6. Búsqueda RAG Técnica Profunda

### 6.1 Configuración pgvector

```sql
-- Extensión requerida
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabla presupuestos_embeddings con índice
CREATE TABLE presupuestos_embeddings (
    id INTEGER PRIMARY KEY,
    presupuesto_id INTEGER UNIQUE NOT NULL REFERENCES presupuestos(id) ON DELETE CASCADE,
    contenido_indexado TEXT NOT NULL,
    embedding vector(384) NOT NULL,
    modelo_embedding VARCHAR(255) DEFAULT 'sentence-transformers/all-MiniLM-L6-v2',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índice HNSW para búsqueda rápida
CREATE INDEX ON presupuestos_embeddings USING hnsw (embedding vector_cosine_ops);

-- Alternativa: Índice IVFFlat (más escalable)
-- CREATE INDEX ON presupuestos_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

### 6.2 Operadores de Similitud

```python
# SQLAlchemy con pgvector

# Distancia coseno (0 = idéntico, 2 = opuesto)
order_by(PresupuestoEmbedding.embedding.cosine_distance(query_embedding))

# Similitud coseno (1 = idéntico, -1 = opuesto)
order_by(PresupuestoEmbedding.embedding.cosine_similarity(query_embedding).desc())

# Distancia L2 euclidiana
order_by(PresupuestoEmbedding.embedding.l2_distance(query_embedding))

# Distancia Manhattan (L1)
order_by(PresupuestoEmbedding.embedding.manhattan_distance(query_embedding))
```

### 6.3 Modelo de Embeddings

```python
from sentence_transformers import SentenceTransformer

# Configuración actual
modelo = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Características
- Dimensiones: 384
- Entrenado con: 215M pares sentencia-similar
- Velocidad: ~7000 sentencias/s (GPU)
- Tamaño: 90MB
- Lenguajes: Multilingüe (incluyendo español)
```

---

## 📈 7. Ejemplo Práctico de Flujo Completo

### Escenario: Generación de Presupuesto de Reforma Integral

```python
# [PASO 1] Usuario crea presupuesto inicial
presupuesto = Presupuestos(
    codigo="PRES-2024-REFORMA-001",
    titulo="Reforma Integral Vivienda - Calle Mayor 45, Madrid",
    descripcion="Reforma completa de vivienda unifamiliar de 150 m² incluyendo estructura, 
                 plomería, electricidad y acabados. Incluye ampliación de 30 m² en planta baja.",
    estado=EstadoPresupuesto.BORRADOR,
    iva=21.00,
    validez_dias=30
)
db.add(presupuesto)
db.commit()

# [PASO 2] Sistema genera embedding
contenido_indexado = f"""
{presupuesto.titulo}
{presupuesto.descripcion}
Reforma de vivienda
Ampliación de planta baja
Trabajo integral
""" 
embedding_vector = embedding_model.encode(contenido_indexado)
presupuesto_emb = PresupuestoEmbedding(
    presupuesto_id=presupuesto.id,
    contenido_indexado=contenido_indexado,
    embedding=embedding_vector
)
db.add(presupuesto_emb)
db.commit()

# [PASO 3] Usuario solicita "Generar presupuesto automáticamente"
# Sistema RETRIEVE
query = "reforma integral vivienda 150 m² con ampliación"
similar = retrieve_similar_budgets(query, top_k=5)
# Encuentra:
# - PRES-2023-REFORMA-APARTAMENTO (similitud: 0.87)
# - PRES-2023-REFORMA-CASA-RURAL (similitud: 0.82)
# - PRES-2024-REFORMA-CHALET (similitud: 0.79)
# - PRES-2023-AMPLIACION-VIVIENDA (similitud: 0.76)
# - PRES-2024-REFORMA-BLOQUES (similitud: 0.71)

# [PASO 4] AUGMENT - Enriquecer contexto
contexto = augment_context(presupuesto, similar)
# Extrae estructura típica:
# {
#   "capitulos_similares": {
#     "Cimientos y estructuras": {"avg_cost": 45000},
#     "Albañilería": {"avg_cost": 32000},
#     "Plomería": {"avg_cost": 18000},
#     "Electricidad": {"avg_cost": 16000},
#     "Acabados": {"avg_cost": 28000}
#   },
#   "detalles_similares": { ... }
# }

# [PASO 5] GENERATE - Crear estructura
presupuesto_generado = generate_budget_structure(presupuesto, ia_model)
# Resultado:
# Presupuestos
# ├─ Capítulo 1: Cimientos y estructuras
# │  ├─ Detalle 1.1: Excavación y movimiento de tierras
# │  ├─ Detalle 1.2: Cimentación de hormigón armado
# │  └─ Detalle 1.3: Estructura de acero/hormigón (ampliación)
# ├─ Capítulo 2: Albañilería
# │  ├─ Detalle 2.1: Mampostería de ladrillo cerámico
# │  ├─ Detalle 2.2: Trabajos de revoco y enfoscado
# │  └─ Detalle 2.3: Paredes divisorias (ampliación)
# ├─ Capítulo 3: Plomería
# │  └─ Detalle 3.1: Instalación sanitaria completa
# ├─ Capítulo 4: Electricidad
# │  ├─ Detalle 4.1: Red eléctrica empotrada
# │  └─ Detalle 4.2: Cuadro de distribución
# └─ Capítulo 5: Acabados
#    ├─ Detalle 5.1: Pintura interior
#    ├─ Detalle 5.2: Revestimientos cerámicos
#    └─ Detalle 5.3: Carpintería

# [PASO 6] Usuario revisa y ajusta vía ChatHistorial
# Usuario: "¿Por qué está tan cara la electricidad?"
# IA: "Debido a la ampliación de 30m² se necesita mayor infraestructura. 
#     Los presupuestos similares muestran €16-20k para viviendas de este tamaño."
# Usuario: "Reduce cantidad de tomas de corriente en planta alta"
# Sistema: Actualiza Detalle 4.1, recalcula subtotales

# [PASO 7] Validación y cierre
presupuesto.estado = EstadoPresupuesto.ENVIADO
presupuesto.total = 139500.00  # Calculado: 115000 + 21% IVA
db.commit()

# Resultado final almacenado en base de datos
print(f"✅ Presupuesto generado: {presupuesto.codigo}")
print(f"   Capítulos: {len(presupuesto.capitulos)}")
print(f"   Detalles: {sum(len(c.detalles) for c in presupuesto.capitulos)}")
print(f"   Total: €{presupuesto.total:,.2f}")
```

---

## 📡 8. Flujo de Datos en Operaciones CRUD

### CREATE (Crear Presupuesto)
```
API POST /presupuestos
  ↓
Validar entrada
  ↓
Crear Presupuestos (estado: BORRADOR)
  ↓
Generar PresupuestoEmbedding (contenido inicial)
  ↓
Indexar en pgvector
  ↓
Response: {"id": 123, "codigo": "PRES-2024-001"}
```

### READ (Obtener Presupuesto)
```
API GET /presupuestos/{id}
  ↓
Query Presupuestos.id = {id}
  ↓
Load related: capitulos, detalles, embedding
  ↓
Calcular totales (si no están en DB)
  ↓
Response: {id, codigo, capitulos[], detalles[], total}
```

### UPDATE (Modificar Presupuesto)
```
API PATCH /presupuestos/{id}
  ↓
Obtener Presupuestos actual
  ↓
Validar cambios
  ↓
Actualizar campos
  ↓
Recalcular subtotales (Σ detalles)
  ↓
Regenerar embedding + reindexar
  ↓
Guardar updated_at = NOW()
  ↓
Response: presupuesto actualizado
```

### DELETE (Eliminar Presupuesto)
```
API DELETE /presupuestos/{id}
  ↓
Validar permisos
  ↓
Eliminar Presupuestos
  ↓
Cascade: Elimina Capítulos, Detalles, PresupuestoEmbedding
  ↓
Response: 204 No Content
```

---

## 🔐 9. Consideraciones de Arquitectura

### 9.1 Escalabilidad
- **pgvector con índice HNSW**: Búsqueda O(log n) en millones de registros
- **Embeddings precalculados**: No requiere compute en tiempo real
- **Particionamiento posible**: Por `created_at` o `presupuesto_id`

### 9.2 Seguridad
- **Validación en DB**: Foreign keys, NOT NULL, UNIQUE, tipos
- **Auditoría temporal**: `created_at`, `updated_at` en todas las tablas
- **Encriptación**: Contraseñas con hash (passwords_hash en Users)
- **Aislamiento**: Roles de usuario (pendiente implementar en modelo)

### 9.3 Performance
- **Índices automáticos**: pgvector en embeddings
- **Relaciones lazy**: SQLAlchemy carga bajo demanda
- **Caché potencial**: Embeddings + embeddings más frecuentes
- **Paginación**: Recomendado en listados de presupuestos

### 9.4 Mantenimiento
- **Migraciones Alembic**: Control de versión de schema
- **Rollback**: Posibilidad de revertir cambios estructurales
- **Soft delete**: Considerar implementar flag `deleted_at` en lugar de borrado físico

---

## 📚 10. Resumen Técnico

| Aspecto | Detalles |
|--------|----------|
| **BD** | PostgreSQL 12+ con pgvector |
| **ORM** | SQLAlchemy 2.0+ (Mapped, relationship) |
| **Embeddings** | sentence-transformers/all-MiniLM-L6-v2 (384 dims) |
| **Búsqueda** | Similitud coseno, índice HNSW |
| **IA** | Claude/GPT para generación de contenido |
| **Patrones** | RAG (Retrieve-Augment-Generate) |
| **Concurrencia** | Timestamps de servidor para evitar race conditions |
| **Cascadas** | Eliminación en cascada de relacionados |

---

## 🎯 Conclusión

**ConstruCloudAI** implementa una arquitectura sofisticada que:

1. ✅ **Centraliza** toda la información en entidades normalizadas
2. ✅ **Vectoriza** contenido para búsqueda semántica inteligente
3. ✅ **Reutiliza** contexto histórico mediante RAG
4. ✅ **Automatiza** generación de presupuestos realistas
5. ✅ **Audita** todos los cambios y origen (IA vs. usuario)
6. ✅ **Escala** con PostgreSQL + pgvector en producción

El flujo **RETRIEVE → AUGMENT → GENERATE** permite que cada nuevo presupuesto aprenda de los anteriores, mejorando precisión y velocidad de generación.

---

*Documento generado: 2026-07-21 | Versión: 1.0*
