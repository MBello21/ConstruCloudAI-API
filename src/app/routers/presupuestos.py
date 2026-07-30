from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal, ROUND_HALF_UP
import uuid
from datetime import datetime
from dateutil.relativedelta import relativedelta

from ..database import get_db
from ..models.capitulos import Capitulos
from ..models.detalles import Detalles
from ..models.presupuesto_embedding import PresupuestoEmbedding
from ..models.presupuestos import Presupuestos
from ..services.embedding_service import EmbeddingService
from ..services.presupuesto_rag_service import PresupuestoRAGService
from ..schemas.presupuestos import PresupuestoCompletoResponse, PresupuestoCreadoResponse, ActualizarPresupuesto
from ..schemas.presupuestos_ia import SolicitudIAPresupuesto


router = APIRouter()
embedding_service = EmbeddingService()


def to_decimal(val, default=0.0):
    """Convierte un valor a Decimal de forma segura."""
    try:
        return Decimal(str(val if val is not None else default))
    except Exception:
        return Decimal(str(default))


def redondear_decimal(val, decimales=2):
    """Redondea un Decimal a N decimales (half-up)."""
    if val is None:
        return Decimal("0.00")
    d = Decimal(str(val))
    return d.quantize(Decimal(10) ** -decimales, rounding=ROUND_HALF_UP)


def validar_y_recalcular_presupuesto(datos):

    IVA = Decimal("1.21")

    # Procesar capítulos
    for cap_data in datos.get("capitulos", []):
        subtotal_cap = Decimal("0.00")

        # Procesar detalles de cada capítulo
        for det_data in cap_data.get("detalles", []):
            cantidad = redondear_decimal(
                to_decimal(det_data.get("cantidad", 0)))
            precio_unitario = redondear_decimal(
                to_decimal(det_data.get("precio_unitario", 0)))

            # RECALCULAR subtotal: cantidad × precio_unitario
            subtotal_detalle = (
                cantidad * precio_unitario).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            det_data["cantidad"] = float(cantidad)
            det_data["precio_unitario"] = float(precio_unitario)
            det_data["subtotal"] = float(subtotal_detalle)
            det_data["importe"] = float(subtotal_detalle)  # importe = subtotal

            subtotal_cap += subtotal_detalle

            # Validación: si cantidad > 0 pero subtotal es 0, error
            if cantidad > 0 and subtotal_detalle == 0:
                raise ValueError(
                    f"Detalle '{det_data.get('concepto', 'Sin concepto')}': "
                    f"cantidad={cantidad}, precio={precio_unitario}, pero subtotal=0. "
                    f"Posible error de precisión o precio inválido."
                )

        # RECALCULAR subtotal capítulo
        subtotal_cap = redondear_decimal(subtotal_cap)
        cap_data["subtotal"] = float(subtotal_cap)

        # Validación: capítulo con detalles pero subtotal 0
        if cap_data.get("detalles") and subtotal_cap == 0:
            raise ValueError(
                f"Capítulo '{cap_data.get('nombre', 'Sin nombre')}': "
                f"tiene detalles pero subtotal calculado es 0€. "
                f"Revisa los precios unitarios."
            )

    # RECALCULAR subtotal presupuesto: suma de capítulos
    subtotal_pres = Decimal("0.00")
    for cap_data in datos.get("capitulos", []):
        subtotal_pres += to_decimal(cap_data.get("subtotal", 0))

    subtotal_pres = redondear_decimal(subtotal_pres)
    datos["subtotal"] = float(subtotal_pres)

    # Validación: presupuesto con capítulos pero subtotal 0
    if datos.get("capitulos") and subtotal_pres == 0:
        raise ValueError(
            "Presupuesto tiene capítulos pero subtotal total es 0€. "
            "Revisa todos los precios unitarios."
        )

    # RECALCULAR total: subtotal × 1.21 (IVA 21%)
    total = redondear_decimal(subtotal_pres * IVA)
    datos["iva"] = 21.0
    datos["total"] = float(total)

    return datos


@router.post("/ia-rag")
async def crear_presupuesto(
    solicitud: SolicitudIAPresupuesto, db: Session = Depends(get_db)
):
    try:
        # Determinar modalidad de trabajo
        modalidad_trabajo = "SOLO MANO DE OBRA / MATERIALES APORTADOS POR CLIENTE" if solicitud.materiales_por_cliente else "OBRA COMPLETA"

        # 2. Generar la estructura con Groq y RAG
        rag_service = PresupuestoRAGService(db=db)
        resultado_rag = rag_service.generar_presupuesto_con_rag(
            descripcion=solicitud.descripcion,
            titulo=solicitud.titulo,
            modalidad_trabajo=modalidad_trabajo,
            materiales_por_cliente=solicitud.materiales_por_cliente
        )

        datos = resultado_rag["presupuesto_estructurado"]

        # VALIDAR Y RECALCULAR todos los totales para asegurar coherencia aritmética
        try:
            datos = validar_y_recalcular_presupuesto(datos)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error en la coherencia del presupuesto generado: {str(e)}. "
                f"La IA generó datos con inconsistencias aritméticas. "
                f"Por favor, intenta de nuevo con una descripción más detallada."
            )

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

        # 4. Guardar los Capítulos y Detalles (ya recalculados)
        for idx, cap_data in enumerate(datos.get("capitulos", []), start=1):
            nombre_capitulo = cap_data.get("nombre") or cap_data.get(
                "titulo", f"Capítulo {idx}")

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
                # Extraemos el texto del concepto/descripción
                texto_descripcion = det_data.get("descripcion") or det_data.get(
                    "concepto", ""
                )

                detalle = Detalles(
                    capitulo_id=capitulo.id,
                    numero=int(det_data.get("numero", det_idx)),
                    descripcion=texto_descripcion,
                    unidad=det_data.get("unidad", "ud")[:20],
                    cantidad=to_decimal(det_data.get("cantidad"), 0.0),
                    precio_unitario=to_decimal(
                        det_data.get("precio_unitario"), 0.0),
                    subtotal=to_decimal(det_data.get("subtotal"), 0.0),
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


@router.get('/metricas')
async def get_metricas(db: Session = Depends(get_db)):

    total = db.query(Presupuestos).count()
    aprobados = db.query(Presupuestos).filter(
        Presupuestos.estado == 'ACEPTADO').count()
    pendientes = db.query(Presupuestos).filter(
        Presupuestos.estado.notin_(['Aprobado', 'Rechazado'])
    ).count()
    importe_total = db.query(func.sum(Presupuestos.total)).scalar() or 0

    hoy = datetime.now()
    inicio_mes_actual = hoy.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0)
    inicio_mes_anterior = inicio_mes_actual - relativedelta(months=1)
    fin_mes_anterior = inicio_mes_actual - relativedelta(seconds=1)

    total_mes_anterior = db.query(Presupuestos).filter(
        Presupuestos.created_at >= inicio_mes_anterior,
        Presupuestos.created_at < inicio_mes_actual
    ).count()

    aprobados_mes_anterior = db.query(Presupuestos).filter(
        Presupuestos.estado == 'ACEPTADO',
        Presupuestos.created_at >= inicio_mes_anterior,
        Presupuestos.created_at < inicio_mes_actual
    ).count()

    importe_mes_anterior = db.query(func.sum(Presupuestos.total)).filter(
        Presupuestos.created_at >= inicio_mes_anterior,
        Presupuestos.created_at < inicio_mes_actual
    ).scalar() or 0

    variacion_total = total - total_mes_anterior
    variacion_aprobados = aprobados - aprobados_mes_anterior
    variacion_importe = float(importe_total) - float(importe_mes_anterior or 0)

    return {
        "total": total,
        "aprobados": aprobados,
        "pendientes": pendientes,
        "tasa_aprobacion": round(aprobados/total * 100, 1) if total > 0 else 0,
        "importe_total": float(importe_total),
        "variacion_total": variacion_total,
        "variacion_aprobados": variacion_aprobados,
        "variacion_importe": variacion_importe
    }


@router.get('/{presupuesto_id}')
def obtener_presupuesto(
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

    return PresupuestoCompletoResponse.model_validate(presupuesto)


@router.get('')
async def listar_presupuestos(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    presupuestos = db.query(Presupuestos).offset(skip).limit(limit).all()
    total = db.query(Presupuestos).count()

    return {
        "total": total,
        "presupuestos": [{
            "id": p.id,
            "codigo": p.codigo,
            "nombre_cliente": p.cliente.nombre_cliente if p.cliente else None,
            "titulo": p.titulo,
            "total": p.total,
            "estado": p.estado,
            "created_at": p.created_at
        }
            for p in presupuestos
        ]
    }


@router.put('/{presupuesto_id}')
async def actualizar_presupuesto(
    presupuesto_id: int,
    datos: ActualizarPresupuesto,
    db: Session = Depends(get_db)
):

    presupuesto = db.query(Presupuestos).filter(
        Presupuestos.id == presupuesto_id).first()

    if not presupuesto:
        raise HTTPException(
            status_code=404, detail="Presupuesto no encontrado")

    if datos.titulo:
        presupuesto.titulo = datos.titulo
    if datos.descripcion:
        presupuesto.descripcion = datos.descripcion
    if datos.estado:
        presupuesto.estado = datos.estado
    if datos.cliente_id:
        presupuesto.cliente_id = datos.cliente_id

    db.commit()
    db.refresh(presupuesto)

    return {"id": presupuesto.id, "titulo": presupuesto.titulo, "actualizado": True}


@router.delete('/{presupuesto_id}')
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
    db.delete(presupuesto)
    db.commit()

    return {"eliminado": True, "presupuesto_id": presupuesto_id}

