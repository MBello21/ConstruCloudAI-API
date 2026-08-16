import json
import os
from typing import Optional
from sqlalchemy.orm import Session
from groq import Groq

from ..models.presupuestos import Presupuestos
from ..models.presupuesto_embedding import PresupuestoEmbedding
from .embedding_service import EmbeddingService
from ..prompts.generacion_presupuestos import PROMPT_GENERAR_PRESUPUESTO
from ..prompts.mejorar_presupuesto import PROMPT_MEJORAR_PRESUPUESTO


class PresupuestoRAGService:

    def __init__(self, db: Session):
        self.db = db
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.embedding_service = EmbeddingService()
        # Modelo activo y de excelente rendimiento en Groq
        self.groq_model = "llama-3.3-70b-versatile"

    def generar_presupuesto_con_rag(
        self,
        descripcion: str,
        titulo: str = "Presupuesto",
        modalidad_trabajo: str = "OBRA COMPLETA",
        materiales_por_cliente: bool = False,
        max_contexto: int = 3,
        empresa_id: Optional[int] = None,
    ) -> dict:
        print(f"\n🚀 Generando presupuesto con RAG para: '{descripcion}'")
        print(f"📋 Modalidad: {modalidad_trabajo}")
        print(f"🔧 Materiales por cliente: {materiales_por_cliente}")

        # 1. RETRIEVE: Buscar presupuestos similares vía pgvector
        presupuestos_similares = []
        try:
            query_embedding = self.embedding_service.generar_embedding(
                descripcion
            )

            if query_embedding:
                distancia_col = PresupuestoEmbedding.embedding.l2_distance(query_embedding).label("distancia")

                contexto_query = (
                    self.db.query(
                        Presupuestos,
                        PresupuestoEmbedding.contenido_indexado,
                        distancia_col
                    )
                    .join(
                        PresupuestoEmbedding,
                        Presupuestos.id == PresupuestoEmbedding.presupuesto_id
                    )
                )

                if empresa_id is None:
                    contexto_query = contexto_query.filter(
                        Presupuestos.empresa_id.is_(None))
                else:
                    contexto_query = contexto_query.filter(
                        Presupuestos.empresa_id == empresa_id)

                presupuestos_similares = (
                    contexto_query
                    .order_by(distancia_col)
                    .limit(max_contexto)
                    .all()
                )

            print(
                f"✅ Encontrados {len(presupuestos_similares)} presupuestos similares"
            )
        except Exception as e:
            print(f"⚠️ Error en búsqueda vectorial: {e}")
            presupuestos_similares = []

        # 2. AUGMENT: Construir contexto para Groq
        contexto_texto = ""
        contexto_usado = []
        similitud_promedio = 0.0

        if presupuestos_similares:
            contexto_texto = "# REFERENCIAS DE PRESUPUESTOS SIMILARES EN BD:\n\n"
            similitudes = []

            for pres, contenido, distancia in presupuestos_similares:
                similitud = max(0.0, 1.0 - (distancia / 2.0))
                similitudes.append(similitud)

                # ✅ Corrección: c.titulo en lugar de c.nombre
                capitulos_info = ""
                if pres.capitulos:
                    capitulos_info = "\n  Capítulos: " + ", ".join(
                        [c.nombre for c in pres.capitulos]
                    )

                contexto_texto += f"• Presupuesto ID {pres.id}:\n"
                contexto_texto += f"  Título: {pres.titulo}\n"
                contexto_texto += f"  Total: €{pres.total}\n"
                contexto_texto += f"  IVA: {pres.iva}%\n"
                contexto_texto += f"  Similitud: {similitud:.0%}\n"
                contexto_texto += capitulos_info + "\n\n"

                contexto_usado.append({
                    "presupuesto_id": pres.id,
                    "titulo": pres.titulo,
                    "total": float(pres.total),
                    "iva": float(pres.iva),
                    "similitud": round(similitud, 2),
                })

            similitud_promedio = sum(similitudes) / len(similitudes)

        # 3. GENERATE: Forzamos la respuesta en formato JSON estructurado
        prompt = PROMPT_GENERAR_PRESUPUESTO.format(
            titulo=titulo,
            descripcion=descripcion,
            modalidad_trabajo=modalidad_trabajo,
            contexto_texto=contexto_texto
        )

        print("📝 Llamando a Groq para generar estructura JSON...")

        response = self.groq_client.chat.completions.create(
            model=self.groq_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=4000,
            response_format={"type": "json_object"},  # 👈 Garantiza respuesta en JSON
        )

        contenido_json = response.choices[0].message.content
        datos_presupuesto = json.loads(contenido_json)

        print("✅ Estructura de presupuesto generada correctamente por Groq")

        return {
            "presupuesto_estructurado": datos_presupuesto,
            "contexto_usado": contexto_usado,
            "similitud_promedio": round(similitud_promedio, 2),
            "cantidad_referencias": len(presupuestos_similares),
            "titulo": titulo,
            "descripcion": descripcion,
        }

    def mejorar_presupuesto_existente(
        self,
        presupuesto_id: int,
        feedback: str,
    ) -> dict:
        presupuesto = (
            self.db.query(Presupuestos)
            .filter(Presupuestos.id == presupuesto_id)
            .first()
        )

        if not presupuesto:
            raise Exception(f"Presupuesto {presupuesto_id} no encontrado")

        print(
            f"Mejorando presupuesto {presupuesto_id} con feedback: {feedback}"
        )

        prompt = PROMPT_GENERAR_PRESUPUESTO.format(
            titulo=presupuesto.titulo,
            descripcion=presupuesto.descripcion,
            contexto_texto=presupuesto.contexto_texto
        )
        response = self.groq_client.chat.completions.create(
            model=self.groq_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=2500,
        )

        presupuesto_mejorado = response.choices[0].message.content
        presupuesto.contexto_rag = presupuesto_mejorado

        self.db.commit()

        return {
            "presupuesto_mejorado": presupuesto_mejorado,
            "presupuesto_id": presupuesto_id,
            "actualizado": True,
        }