Convenciones del proyecto:
- Patrón: modelo → schema → router
- Imports: modelos desde ..models, schemas desde ..schemas, db desde ..database
- Manejo de errores: HTTPException con status codes correctos (404 para not found, 400 para bad request)
- db.commit() + db.refresh() después de crear/actualizar
- db.delete(objeto) + db.commit() para eliminar