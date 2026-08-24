# Separación de generación IA y persistencia de presupuestos

> "La IA asiste, no decide."

Antes, un único endpoint (`POST /presupuestos/ia-rag`) generaba el presupuesto con
IA **y lo guardaba** en la base de datos en la misma llamada. El usuario no tenía
oportunidad de revisar nada antes de que quedara persistido.

Ahora el flujo tiene dos pasos:

1. `POST /api/v1/presupuestos/ia-rag` → la IA genera la estructura y la devuelve. **No toca la BD.**
2. El frontend muestra el JSON, el usuario lo revisa/edita.
3. `POST /api/v1/presupuestos/` → persiste la estructura revisada y genera el embedding.

---

## 1. `src/app/services/presupuesto_service.py`

### `generar_presupuesto_ia(db, solicitud) -> dict` (nueva)

Sustituye a `crear_presupuesto_con_rag` como función del flujo de generación.

- Determina la modalidad de trabajo (`OBRA COMPLETA` / `SOLO MANO DE OBRA`).
- Llama a `PresupuestoRAGService.generar_presupuesto_con_rag`.
- Valida y recalcula todos los totales con `validar_y_recalcular_presupuesto`.
- Normaliza las claves con `normalizar_estructura`.
- **No hace `db.add` ni `db.commit`. No genera embedding.**
- Devuelve:

```jsonc
{
  "presupuesto": { /* cabecera + capitulos + detalles */ },
  "referencias_usadas": 0,
  "similitud_promedio": 0.0,
  "contexto_usado": [],
  "persistido": false
}
```

`db` se sigue recibiendo porque el RAG lo necesita para la **lectura** vectorial
(buscar presupuestos similares); no se escribe nada con él.

### `crear_presupuesto_desde_estructura(db, datos) -> Presupuestos` (nueva)

Recibe un dict o un schema Pydantic (`EstructuraPresupuesto`) y persiste:

1. Recalcula los totales (`validar_y_recalcular_presupuesto`) — el usuario ha
   podido editar cantidades o precios, así que los importes se recomputan en
   servidor en lugar de confiar en los que llegan del cliente.
2. Normaliza claves (`normalizar_estructura`).
3. `db.add(Presupuestos)` + `flush` para obtener el `id`.
4. Itera capítulos: `db.add(Capitulos)` + `flush` por cada uno.
5. Itera detalles de cada capítulo: `db.add(Detalles)`.
6. Construye el texto RAG y lo guarda en `presupuesto.contexto_rag`.
7. **Genera el embedding** con `EmbeddingService` y lo guarda en
   `PresupuestoEmbedding` (dentro de `try/except`: si falla el proveedor de
   embeddings, el presupuesto se guarda igualmente).
8. `db.commit()` + `db.refresh()`.
9. Retorna el modelo `Presupuestos` con sus relaciones.

Los flags `generado_por_ia`, `precio_confirmado` y `es_externo` ahora se toman
del payload en vez de estar fijados a `True/False/False`, para que un detalle
añadido a mano por el usuario no quede marcado como generado por IA.

### `normalizar_estructura(datos, titulo="", descripcion="")` (nueva, auxiliar)

La IA devuelve claves alternativas (`capitulo.titulo` además de `nombre`,
`detalle.concepto` además de `descripcion`, `detalle.importe` además de
`subtotal`). Antes esas variantes se resolvían al persistir; ahora se resuelven
**al generar**, para que el JSON que ve el frontend tenga exactamente la misma
forma que el que debe reenviar. También aplica valores por defecto
(`condiciones_pago`, `validez_dias`, `numero`, `orden`, `unidad`).

### `crear_presupuesto_con_rag(...)` (conservada, deprecada)

No se ha borrado. Se ha reimplementado como envoltorio de las dos funciones
nuevas, así que mantiene su firma y su respuesta anterior pero sin duplicar
lógica. Ya no la usa ningún endpoint; queda disponible por compatibilidad y
puede eliminarse cuando el frontend esté migrado.

---

## 2. `src/app/routers/presupuestos.py`

### `POST /api/v1/presupuestos/ia-rag` (modificado)

- `response_model=PresupuestoGeneradoResponse`.
- Llama a `generar_presupuesto_ia`. No persiste.
- `ValueError` → 400 con el mensaje de incoherencia aritmética.
- Se ha quitado el `db.rollback()` del manejador genérico: ya no hay transacción
  que revertir.

### `POST /api/v1/presupuestos/` (nuevo)

- Body: `EstructuraPresupuesto`.
- `response_model=PresupuestoCompletoResponse`, `status_code=201`.
- Llama a `crear_presupuesto_desde_estructura`.
- `ValueError` → 400; cualquier otro error → `db.rollback()` + 400.

> Nota: la ruta se registra con `"/"`, por lo que en Swagger aparece como
> `/api/v1/presupuestos/`. Una petición a `/api/v1/presupuestos` (sin barra)
> funciona igualmente vía el redirect 307 de FastAPI, que conserva método y
> cuerpo.

### Endpoints no tocados

`GET /metricas`, `GET /{id}`, `GET ''`, `PUT /{id}`, `DELETE /{id}` quedan
exactamente igual. Tampoco se han tocado los routers de capítulos ni detalles.

---

## 3. `src/app/schemas/presupuestos_ia.py`

Schemas nuevos:

| Schema | Uso |
|---|---|
| `DetalleEstructura` | Partida anidada dentro de un capítulo |
| `CapituloEstructura` | Capítulo con su lista de `DetalleEstructura` |
| `EstructuraPresupuesto` | Cabecera + `List[CapituloEstructura]`. Body de `POST /` y contenido de la respuesta de `/ia-rag` |
| `ReferenciaRAG` | Presupuesto similar usado como contexto |
| `PresupuestoGeneradoResponse` | Respuesta de `/ia-rag`: `presupuesto` + metadatos RAG + `persistido: false` |

`SolicitudIAPresupuesto` se mantiene sin cambios funcionales.

**Sobre la reutilización de schemas:** `CapituloCreate` y `DetalleCreate` no se
pueden componer aquí porque exigen `presupuesto_id` y `capitulo_id`
respectivamente, y esos IDs no existen todavía cuando la estructura viaja
anidada y sin persistir. Por eso se definen variantes anidadas; los schemas
existentes siguen usándose tal cual en los CRUD individuales de capítulos y
detalles.

`src/app/schemas/__init__.py` exporta los cinco schemas nuevos.

---

## 4. Verificación realizada

Ejecutado contra la base de datos real; los presupuestos de prueba se
eliminaron después.

| Comprobación | Resultado |
|---|---|
| La app importa y `openapi()` se genera sin errores | OK |
| Swagger lista `POST /ia-rag` y `POST /` con sus schemas | OK (`EstructuraPresupuesto` / `PresupuestoGeneradoResponse`) |
| `POST /ia-rag` devuelve 8 capítulos y **no crea filas** | OK — conteos de `presupuestos`/`capitulos`/`detalles` idénticos antes y después |
| La salida de `/ia-rag` valida como body de `POST /` | OK |
| `POST /` persiste cabecera + capítulos + detalles | OK, 201 |
| `POST /` recalcula totales en servidor | OK — enviado `subtotal: 999`, guardado `362.00` / total `438.02` |
| Round-trip completo (generar → editar precio → guardar) | OK — el precio editado se refleja en el total |
| `GET /{id}`, `DELETE /{id}` siguen funcionando | OK |

**Pendiente de entorno (no de código):** el token de Hugging Face configurado
devuelve `403 — This authentication method does not have sufficient permissions
to call Inference Providers`, así que el embedding no llega a guardarse. Es un
problema de credenciales preexistente que afecta igual al código anterior; la
llamada está dentro de `try/except` y el presupuesto se persiste correctamente
sin él. Con un token válido, `PresupuestoEmbedding` se creará en el paso 7 de
`crear_presupuesto_desde_estructura`.

---

## 5. Contrato para el frontend

```http
POST /api/v1/presupuestos/ia-rag
{ "titulo": "Reforma baño", "descripcion": "Baño 6m² completo", "materiales_por_cliente": false }
```

Devuelve `{ presupuesto, referencias_usadas, similitud_promedio, contexto_usado, persistido: false }`.

El usuario edita `presupuesto` y se reenvía **ese mismo objeto** tal cual:

```http
POST /api/v1/presupuestos/
{ ...presupuesto }
```

Devuelve el `PresupuestoCompletoResponse` con `id`, `codigo` y las relaciones.
Los `subtotal`/`total` enviados son informativos: el servidor los recalcula.
