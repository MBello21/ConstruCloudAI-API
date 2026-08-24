import uuid
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from typing import Optional
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.presupuestos import Presupuestos
from ..models.capitulos import Capitulos
from ..models.detalles import Detalles
from ..models.presupuesto_embedding import PresupuestoEmbedding
from ..schemas.presupuestos import ActualizarPresupuesto
from .embedding_service import EmbeddingService
from .presupuesto_rag_service import PresupuestoRAGService


def _filtrar_por_empresa(query, empresa_id: Optional[int]):
    """Restringe la query a la empresa indicada (o a los registros sin empresa)."""
    if empresa_id is None:
        return query.filter(Presupuestos.empresa_id.is_(None))
    return query.filter(Presupuestos.empresa_id == empresa_id)


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
    """Valida y recalcula todos los totales del presupuesto."""
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
            det_data["importe"] = float(subtotal_detalle)

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


CONDICIONES_PAGO_POR_DEFECTO = (
    "50% a la firma del presupuesto, 50% a la finalización de los trabajos"
)


def normalizar_estructura(datos: dict, titulo: str = "", descripcion: str = "") -> dict:
    """
    Normaliza las claves que la IA puede devolver con nombres alternativos
    (capítulo `titulo`/`nombre`, detalle `concepto`/`descripcion`) para que la
    estructura que ve el frontend coincida con `EstructuraPresupuesto`.
    """
    datos["titulo"] = datos.get("titulo") or titulo
    datos["descripcion"] = datos.get("descripcion") or descripcion
    datos["condiciones_pago"] = (
        datos.get("condiciones_pago") or CONDICIONES_PAGO_POR_DEFECTO
    )
    datos["validez_dias"] = int(datos.get("validez_dias") or 30)

    capitulos = []
    for idx, cap_data in enumerate(datos.get("capitulos", []) or [], start=1):
        cap_data["nombre"] = (
            cap_data.get("nombre") or cap_data.get(
                "titulo") or f"Capítulo {idx}"
        )
        cap_data.pop("titulo", None)
        cap_data["numero"] = int(cap_data.get("numero") or idx)
        cap_data["orden"] = int(cap_data.get("orden") or idx)

        detalles = []
        for det_idx, det_data in enumerate(cap_data.get("detalles", []) or [], start=1):
            det_data["descripcion"] = (
                det_data.get("descripcion") or det_data.get("concepto") or ""
            )
            det_data.pop("concepto", None)
            det_data.pop("importe", None)
            det_data["numero"] = int(det_data.get("numero") or det_idx)
            det_data["unidad"] = (det_data.get("unidad") or "ud")[:20]
            det_data["generado_por_ia"] = True
            det_data["precio_confirmado"] = False
            det_data["es_externo"] = False
            detalles.append(det_data)

        cap_data["detalles"] = detalles
        capitulos.append(cap_data)

    datos["capitulos"] = capitulos
    return datos


def generar_presupuesto_ia(
    db: Session, solicitud, empresa_id: Optional[int] = None
) -> dict:
    """
    Genera con IA + RAG la estructura de un presupuesto SIN persistir nada.

    No hace db.add, ni db.commit, ni genera embedding: solo devuelve el JSON
    estructurado para que el usuario lo revise/edite en el frontend y después
    lo envíe a `crear_presupuesto_desde_estructura`.

    El contexto RAG (presupuestos similares usados como referencia) se
    restringe a la empresa del usuario.

    Lanza ValueError si la estructura generada es aritméticamente incoherente.
    """
    titulo = solicitud.titulo
    descripcion = solicitud.descripcion
    materiales_por_cliente = bool(solicitud.materiales_por_cliente)

    # Determinar modalidad de trabajo
    modalidad_trabajo = (
        "SOLO MANO DE OBRA / MATERIALES APORTADOS POR CLIENTE"
        if materiales_por_cliente
        else "OBRA COMPLETA"
    )

    # Generar la estructura con Groq y RAG
    rag_service = PresupuestoRAGService(db=db)
    resultado_rag = rag_service.generar_presupuesto_con_rag(
        descripcion=descripcion,
        titulo=titulo,
        modalidad_trabajo=modalidad_trabajo,
        materiales_por_cliente=materiales_por_cliente,
        empresa_id=empresa_id,
    )

    datos = resultado_rag["presupuesto_estructurado"]

    # VALIDAR Y RECALCULAR todos los totales
    datos = validar_y_recalcular_presupuesto(datos)

    # Homogeneizar claves antes de entregar el JSON al frontend
    datos = normalizar_estructura(datos, titulo, descripcion)

    return {
        "presupuesto": datos,
        "referencias_usadas": resultado_rag.get("cantidad_referencias", 0),
        "similitud_promedio": resultado_rag.get("similitud_promedio", 0.0),
        "contexto_usado": resultado_rag.get("contexto_usado", []),
        "persistido": False,
    }


def crear_presupuesto_desde_estructura(
    db: Session, datos, empresa_id: Optional[int] = None
) -> Presupuestos:
    """
    Persiste una estructura completa (cabecera + capítulos + detalles).

    Acepta un dict o un schema Pydantic. Recalcula los totales antes de guardar
    (el usuario ha podido editar cantidades o precios) y genera el embedding
    vectorial: la indexación RAG solo ocurre aquí, nunca al generar con IA.

    Lanza ValueError si los totales son incoherentes.
    Retorna el presupuesto creado con sus relaciones.
    """
    if hasattr(datos, "model_dump"):
        datos = datos.model_dump()

    embedding_service = EmbeddingService()

    # Recalcular totales sobre los datos ya revisados por el usuario
    datos = validar_y_recalcular_presupuesto(datos)
    datos = normalizar_estructura(datos)

    # Guardar la cabecera del Presupuesto
    presupuesto = Presupuestos(
        codigo=f"PRES-{uuid.uuid4().hex[:8].upper()}",
        empresa_id=empresa_id,
        cliente_id=datos.get("cliente_id"),
        titulo=datos.get("titulo"),
        descripcion=datos.get("descripcion"),
        estado=datos.get("estado") or "Borrador",
        subtotal=to_decimal(datos.get("subtotal")),
        iva=to_decimal(datos.get("iva"), 21.0),
        total=to_decimal(datos.get("total")),
        condiciones_pago=datos.get("condiciones_pago"),
        validez_dias=int(datos.get("validez_dias", 30)),
    )
    db.add(presupuesto)
    db.flush()

    texto_completo_para_rag = (
        f"Título: {presupuesto.titulo}\nDescripción:"
        f" {presupuesto.descripcion}\n\nCapítulos y Partidas:\n"
    )

    # Guardar los Capítulos y Detalles
    for idx, cap_data in enumerate(datos.get("capitulos", []), start=1):
        capitulo = Capitulos(
            presupuesto_id=presupuesto.id,
            numero=int(cap_data.get("numero", idx)),
            nombre=cap_data.get("nombre"),
            orden=int(cap_data.get("orden", idx))
        )
        db.add(capitulo)
        db.flush()

        texto_completo_para_rag += (
            f"\nCapítulo {capitulo.numero}: {capitulo.nombre}\n"
        )

        for det_idx, det_data in enumerate(
            cap_data.get("detalles", []), start=1
        ):
            detalle = Detalles(
                capitulo_id=capitulo.id,
                numero=int(det_data.get("numero", det_idx)),
                descripcion=det_data.get("descripcion", ""),
                unidad=det_data.get("unidad", "ud")[:20],
                cantidad=to_decimal(det_data.get("cantidad"), 0.0),
                precio_unitario=to_decimal(
                    det_data.get("precio_unitario"), 0.0),
                subtotal=to_decimal(det_data.get("subtotal"), 0.0),
                generado_por_ia=bool(det_data.get("generado_por_ia", False)),
                precio_confirmado=bool(
                    det_data.get("precio_confirmado", False)),
                es_externo=bool(det_data.get("es_externo", False)),
            )
            db.add(detalle)
            texto_completo_para_rag += (
                f"  - {detalle.descripcion} | {detalle.cantidad}"
                f" {detalle.unidad} x {detalle.precio_unitario}€ ="
                f" {detalle.subtotal}€\n"
            )

    # Guardar el contexto RAG enriquecido
    presupuesto.contexto_rag = texto_completo_para_rag.strip()

    # Generar y guardar embedding vectorial
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

    # Confirmar transacción
    db.commit()
    db.refresh(presupuesto)

    return presupuesto


def crear_presupuesto_con_rag(
    db: Session,
    titulo: str,
    descripcion: str,
    materiales_por_cliente: bool = False
) -> dict:
    """
    DEPRECADO: genera y persiste en un solo paso (comportamiento anterior).

    Se conserva por compatibilidad; el flujo actual usa
    `generar_presupuesto_ia` + `crear_presupuesto_desde_estructura` para que la
    IA asista sin decidir. Ya no lo usa ningún endpoint.
    """
    from ..schemas.presupuestos_ia import SolicitudIAPresupuesto

    resultado = generar_presupuesto_ia(
        db,
        SolicitudIAPresupuesto(
            titulo=titulo,
            descripcion=descripcion,
            materiales_por_cliente=materiales_por_cliente,
        ),
    )
    presupuesto = crear_presupuesto_desde_estructura(
        db, resultado["presupuesto"])

    return {
        "mensaje": "Presupuesto, capítulos y detalles creados con éxito",
        "presupuesto_id": presupuesto.id,
        "codigo": presupuesto.codigo,
        "total_capitulos_creados": len(presupuesto.capitulos),
        "referencias_usadas": resultado.get("referencias_usadas", 0),
        "similitud_promedio": resultado.get("similitud_promedio", 0.0),
    }


def _base_query(db: Session, empresa_id: int | None = None):
    q = db.query(Presupuestos)
    if empresa_id is not None:
        q = q.filter(Presupuestos.empresa_id == empresa_id)
    return q


def get_metricas(db: Session, empresa_id: int | None = None) -> dict:
    """Obtiene métricas de presupuestos filtradas por empresa."""
    total = _base_query(db, empresa_id).count()
    aprobados = _base_query(db, empresa_id).filter(
        Presupuestos.estado == 'ACEPTADO').count()
    pendientes = _base_query(db, empresa_id).filter(
        Presupuestos.estado.notin_(['Aprobado', 'Rechazado'])
    ).count()
    importe_total = _base_query(db, empresa_id).with_entities(
        func.sum(Presupuestos.total)).scalar() or 0

    hoy = datetime.now()
    inicio_mes_actual = hoy.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0)
    inicio_mes_anterior = inicio_mes_actual - relativedelta(months=1)

    filtro_mes = [
        Presupuestos.created_at >= inicio_mes_anterior,
        Presupuestos.created_at < inicio_mes_actual
    ]

    total_mes_anterior = _base_query(db, empresa_id).filter(
        *filtro_mes).count()

    aprobados_mes_anterior = _base_query(db, empresa_id).filter(
        Presupuestos.estado == 'ACEPTADO',
        *filtro_mes).count()

    importe_mes_anterior = _base_query(db, empresa_id).with_entities(
        func.sum(Presupuestos.total)).filter(
        *filtro_mes).scalar() or 0

    variacion_total = total - total_mes_anterior
    variacion_aprobados = aprobados - aprobados_mes_anterior
    variacion_importe = float(importe_total) - float(importe_mes_anterior or 0)

    return {
        "total": total,
        "aprobados": aprobados,
        "pendientes": pendientes,
        "tasa_aprobacion": round(aprobados / total * 100, 1) if total > 0 else 0,
        "importe_total": float(importe_total),
        "variacion_total": variacion_total,
        "variacion_aprobados": variacion_aprobados,
        "variacion_importe": variacion_importe
    }


def get_presupuesto_by_id(
    db: Session, presupuesto_id: int, empresa_id: Optional[int] = None
):
    """Obtiene un presupuesto por ID dentro de la empresa. Lanza Exception si no existe."""
    presupuesto = _filtrar_por_empresa(
        db.query(Presupuestos), empresa_id
    ).filter(Presupuestos.id == presupuesto_id).first()

    if not presupuesto:
        raise Exception("Presupuesto no encontrado")

    return presupuesto


def listar_presupuestos(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    estado: str = None,
    empresa_id: Optional[int] = None
) -> dict:
    """Lista presupuestos de la empresa con filtros opcionales."""
    query = _filtrar_por_empresa(db.query(Presupuestos), empresa_id)

    if estado and estado != 'Todos':
        query = query.filter(Presupuestos.estado == estado)

    total = query.count()
    presupuestos = query.order_by(
        Presupuestos.created_at.desc()).offset(skip).limit(limit).all()

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


def actualizar_presupuesto(
    db: Session,
    presupuesto_id: int,
    datos: ActualizarPresupuesto,
    empresa_id: Optional[int] = None
) -> dict:
    """Actualiza un presupuesto de la empresa. Lanza Exception si no existe."""
    presupuesto = _filtrar_por_empresa(
        db.query(Presupuestos), empresa_id
    ).filter(Presupuestos.id == presupuesto_id).first()

    if not presupuesto:
        raise Exception("Presupuesto no encontrado")

    if datos.titulo:
        presupuesto.titulo = datos.titulo
    if datos.descripcion:
        presupuesto.descripcion = datos.descripcion
    if datos.estado:
        presupuesto.estado = datos.estado
    if datos.cliente_id:
        presupuesto.cliente_id = datos.cliente_id
    if datos.validez_dias is not None:
        presupuesto.validez_dias = datos.validez_dias
    if datos.condiciones_pago is not None:
        presupuesto.condiciones_pago = datos.condiciones_pago
    if datos.iva is not None:
        presupuesto.iva = datos.iva
        presupuesto.total = float(
            redondear_decimal(
                to_decimal(presupuesto.subtotal) *
                (1 + to_decimal(datos.iva) / 100)
            )
        )

    db.commit()
    db.refresh(presupuesto)

    return {"id": presupuesto.id, "titulo": presupuesto.titulo, "actualizado": True}


def eliminar_presupuesto(
    db: Session, presupuesto_id: int, empresa_id: Optional[int] = None
) -> dict:
    """Elimina un presupuesto de la empresa. Lanza Exception si no existe."""
    presupuesto = _filtrar_por_empresa(
        db.query(Presupuestos), empresa_id
    ).filter(Presupuestos.id == presupuesto_id).first()

    if not presupuesto:
        raise Exception("Presupuesto no encontrado")

    db.delete(presupuesto)
    db.commit()

    return {"eliminado": True, "presupuesto_id": presupuesto_id}
