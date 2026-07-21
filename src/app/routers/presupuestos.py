from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from decimal import Decimal
import uuid

from ..database import get_db
from ..models.capitulos import Capitulos
from ..models.detalles import Detalles
from ..models.presupuesto_embedding import PresupuestoEmbedding
from ..models.presupuestos import Presupuestos
from ..services.embedding_service import EmbeddingService
from ..services.presupuesto_rag_service import PresupuestoRAGService
from ..schemas.presupuestos import PresupuestoCompletoResponse, PresupuestoCreadoResponse
from ..schemas.presupuestos_ia import SolicitudIAPresupuesto




router = APIRouter()
embedding_service = EmbeddingService()


@router.post("/presupuesto/ia-rag")
async def crear_presupuesto(
    solicitud: SolicitudIAPresupuesto, db: Session = Depends(get_db)
):
  try:
    # 2. Generar la estructura con Groq y RAG
    rag_service = PresupuestoRAGService(db=db)
    resultado_rag = rag_service.generar_presupuesto_con_rag(
        descripcion=solicitud.descripcion, titulo=solicitud.titulo
    )

    datos = resultado_rag["presupuesto_estructurado"]

    # Función auxiliar para convertir valores a Decimal de forma segura
    def to_decimal(val, default=0.0):
      try:
        return Decimal(str(val if val is not None else default))
      except Exception:
        return Decimal(str(default))

    # 3. Guardar la cabecera del Presupuesto
    presupuesto = Presupuestos(
        codigo=f"PRES-{uuid.uuid4().hex[:8].upper()}",
        titulo=datos.get("titulo", solicitud.titulo),
        descripcion=datos.get("descripcion", solicitud.descripcion),
        subtotal=to_decimal(datos.get("subtotal")),
        iva=to_decimal(datos.get("iva"), 21.0),
        total=to_decimal(datos.get("total")),
        condiciones_pago=datos.get("condiciones_pago"),
        validez_dias=int(datos.get("validez_dias", 30)),
    )
    db.add(presupuesto)
    db.flush()  # Genera presupuesto.id

    texto_completo_para_rag = (
        f"Título: {presupuesto.titulo}\nDescripción:"
        f" {presupuesto.descripcion}\n\nCapítulos y Partidas:\n"
    )

    # 4. Guardar los Capítulos y Detalles desglosados por la IA
    for idx, cap_data in enumerate(datos.get("capitulos", []), start=1):
        nombre_capitulo = cap_data.get("nombre") or cap_data.get("titulo", f"Capítulo {idx}")
        
        capitulo = Capitulos(
          presupuesto_id=presupuesto.id,
          numero=int(cap_data.get("numero", 1)),
          nombre=nombre_capitulo,
          orden=idx
        )
        db.add(capitulo)
        db.flush()  # Genera capitulo.id

        texto_completo_para_rag += (
            f"\nCapítulo {capitulo.numero}: {capitulo.nombre}\n"
        )

        for det_idx, det_data in enumerate(
            cap_data.get("detalles", []), start=1
        ):
            # Extraemos el texto del concepto/descripción que devuelve Groq
            texto_descripcion = det_data.get("descripcion") or det_data.get(
                "concepto", ""
            )
            
            # Calculamos o mapeamos subtotal/importe
            subtotal_val = det_data.get("subtotal") or det_data.get("importe", 0.0)

            detalle = Detalles(
                capitulo_id=capitulo.id,
                numero=int(det_data.get("numero", det_idx)),
                descripcion=texto_descripcion,
                unidad=det_data.get("unidad", "ud")[:20],  # Limita a String(20)
                cantidad=to_decimal(det_data.get("cantidad"), 1.0),
                precio_unitario=to_decimal(det_data.get("precio_unitario")),
                subtotal=to_decimal(subtotal_val),
                generado_por_ia=True,
                precio_confirmado=False,
                es_externo=False,
            )
            db.add(detalle)
            texto_completo_para_rag += (
                f"  - {detalle.descripcion} | {detalle.cantidad}"
                f" {detalle.unidad} x {detalle.precio_unitario}€ ="
                f" {detalle.subtotal}€\n"
            )

    # Guardar el contexto RAG enriquecido
    presupuesto.contexto_rag = texto_completo_para_rag.strip()

    # 5. Generar y guardar embedding vectorial
    embedding_vector = None
    try:
      embedding_vector = embedding_service.generar_embedding(
          texto_completo_para_rag
      )
      if embedding_vector:
        embedding_record = PresupuestoEmbedding(
            presupuesto_id=presupuesto.id,
            contenido_indexado=texto_completo_para_rag.strip(),
            embedding=embedding_vector,
        )
        db.add(embedding_record)
    except Exception as e:
      print(f"⚠️ Error generando embedding final: {e}")

    # Confirmar transacción en la base de datos
    db.commit()
    db.refresh(presupuesto)
    
    datos_respuesta = {
        "mensaje": "Presupuesto, capítulos y detalles creados con éxito",
        "presupuesto_id": presupuesto.id,
        "codigo": presupuesto.codigo,
        "total_capitulos_creados": len(presupuesto.capitulos),
        "referencias_usadas": resultado_rag.get("cantidad_referencias", 0),
        "similitud_promedio": resultado_rag.get("similitud_promedio", 0.0),
    }

    return PresupuestoCreadoResponse.model_validate(datos_respuesta)

  except Exception as e:
    db.rollback()
    # Muestra el error exacto en los logs y en la respuesta HTTP
    print(f"❌ Error en la persistencia de datos: {e}")
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Error guardando presupuesto en BD: {str(e)}",
    )
        
@router.get('/presupuesto/{presupuesto_id}')
def obtener_presupuesto(
    presupuesto_id:int,
    db:Session = Depends(get_db)
):
    presupuesto= db.query(Presupuestos).filter(
        Presupuestos.id == presupuesto_id
    ).first()
    
    if not presupuesto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presupuesto no encontrado"
        )
        
    return PresupuestoCompletoResponse.model_validate(presupuesto)

@router.get('/presupuestos')
async def listar_presupuestos(
    skip:int = 0,
    limit:int = 10,
    db:Session = Depends(get_db)
):
    presupuestos = db.query(Presupuestos).offset(skip).limit(limit).all
    
    return [
        {
            "id": p.id,
            "titulo": p.titulo,
            "total": p.total,
            "estado": p.estado,
            "created_at": p.created_at
        }
        for p in presupuestos
    ]

@router.put('/presupuesto/{presupuesto_id}')
async def actualizar_presupuesto(
    presupuesto_id:int,
    titulo:str = None,
    descripcion:str = None,
    estado:str = None,
    db: Session = Depends(get_db)
):
    presupuesto = db.query(Presupuestos).filter(
        Presupuestos.id == presupuesto_id
    ).first()
    
    if not presupuesto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presupuesto no encontrado"
        )
    
    if titulo:
        presupuesto.titulo = titulo
    
    if descripcion:
        presupuesto.descripcion = descripcion
    if estado:
        presupuesto.estado = estado
    
    if descripcion:
        try:
            contenido = f"Título: {presupuesto.titulo}\nDescripción: {presupuesto.descripcion}\nTotal: {presupuesto.total}"
            
            nuevo_embedding = embedding_service.generar_embedding(contenido)

            embedding_record = db.query(PresupuestoEmbedding).filter(
                PresupuestoEmbedding.presupuesto_id == presupuesto_id
            ).first()

            if embedding_record:
                embedding_record.embedding = nuevo_embedding
                embedding_record.contenido_indexado = contenido
            
            else:
                embedding_record= PresupuestoEmbedding(
                    presupuesto_id=presupuesto_id,
                    contenido_indexado=contenido,
                    embedding=nuevo_embedding
                )
                db.add(embedding_record)
        
        except Exception as e:
            print(f"⚠️ Error regenerando embedding: {e}")
    
    db.commit()
    db.refresh(presupuesto)
    
    return {"id": presupuesto.id, "titulo": presupuesto.titulo, "actualizado": True}

@router.delete('/presupuesto/{presupuesto_id}')
async def eliminar_presupuesto(
    presupuesto_id: int,
    db: Session = Depends(get_db)
):
    presupuesto = db.query(Presupuestos).filter(
        Presupuestos.id == presupuesto_id
    ).first()
    
    if not presupuesto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presupuesto no encontrado"
        )
    db.delete()
    db.commit()
    
    return {"eliminado": True, "presupuesto_id": presupuesto_id}   