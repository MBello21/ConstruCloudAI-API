from groq import Groq
from sqlalchemy.orm import Session
from ..models.presupuestos import Presupuestos
from ..models.presupuesto_embedding import PresupuestoEmbedding
from .embedding_service import EmbeddingService
import os

class PresupuestoRAGService:
    
    def __init__(self, db:Session):
        self.db = db
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.embedding_service = EmbeddingService()
        self.groq_model="mixtral-8x7b-32768"
    
    def generar_presupuesto_con_rag(
        self,
        descripcion:str,
        titulo:str="Presupuesto",
        max_contexto:int=3
    )-> dict:
        """
          Genera un presupuesto usando Groq + contexto RAG
 
          Flujo:
          1. Busca presupuestos similares (vectorial)
          2. Extrae contexto de esos presupuestos
          3. Llama a Groq con ese contexto
          4. Groq genera presupuesto con estructura detallada
 
          Args:
            descripcion: Descripción del trabajo solicitado
            titulo: Título del presupuesto
            max_contexto: Máximo de presupuestos similares a incluir
 
          Returns:
            {
                "presupuesto_generado": "Texto generado por Groq",
                "contexto_usado": [lista de presupuestos similares],
                "similitud_promedio": float,
                "cantidad_referencias": int,
                "detalles": [partidas generadas]
            }
          """
 
        print(f"\n🚀 Generando presupuesto con RAG para: '{descripcion}'")          
          
        #   1. Retrieve: Buscar presupuestos similares
        presupuestos_similares=[]
        try:
            query_embedding = self.embedding_service.generar_embedding(descripcion)
            
            presupuestos_similares=self.db.query(
                Presupuestos,
                PresupuestoEmbedding.contenido_indexado,
                (PresupuestoEmbedding.embedding.op('<->', return_type=float)
                 (query_embedding)).label("distancia")
                ).join(
                    PresupuestoEmbedding, 
                    Presupuestos.id == PresupuestoEmbedding.presupuesto_id
                ).order_by(
                    PresupuestoEmbedding.embedding.op('<->', return_type=float)
                    (query_embedding)
                ).limit(max_contexto).all()
                
            print(f"✅ Encontrados {len(presupuestos_similares)} presupuestos similares")
        except Exception as e:
            print(f"⚠️ Error en búsqueda vectorial: {e}")
            presupuestos_similares = []
        
        # 2. Argument: Construir contexto para Groq:
        
        contexto_texto = ""
        contexto_usado = []
        similitud_promedio=0
        
        if presupuestos_similares:
            contexto_texto= "# REFERENCIAS DE PRESUPUESTOS SIMILARES:\n\n"
            
            similitudes=[]
            
            for pres, contenido, distancia in presupuestos_similares:
                similitud = max(0,1 -(distancia/2))
                similitudes.append(similitud)
                
                capitulos_info = ""
                
                if pres.capitulos:
                    capitulos_info="\n Capítulos: " + ", ".join([c.nombre for c in pres.capitulos])
                
                contexto_texto += f"• Presupuesto ID {pres.id}:\n"
                contexto_texto += f"  Título: {pres.titulo}\n"
                contexto_texto += f"  Total: €{pres.total}\n"
                contexto_texto += f"  IVA: {pres.iva}%\n"
                contexto_texto += f"  Similitud: {similitud:.0%}\n"
                contexto_texto += capitulos_info
                contexto_texto += f"\n"
                
                contexto_usado.append({
                    "presupuesto_id": pres.id,
                    "titulo": pres.titulo,
                    "total": float(pres.total),
                    "iva": float(pres.iva),
                    "similitud": round(similitud, 2)
                })
            
            similitud_promedio=sum(similitudes)/len(similitudes)
            
        # 3. Generate: Llamar a Groq con contexto
        
        prompt = f"""Eres un experto en presupuestos de construcción y reformas.
 
                    SOLICITUD DEL CLIENTE:
                    Título: {titulo}
                    Descripción: {descripcion}
                    
                    {contexto_texto}
                    
                    Basándote en los presupuestos similares anteriores como REFERENCIA de precios y estructura, 
                    genera un presupuesto detallado y profesional.
                    
                    El presupuesto DEBE incluir:
                    
                    1. **DESCRIPCIÓN DEL TRABAJO**
                    - Resumen claro de qué se va a hacer
                    
                    2. **DESGLOSE DE PARTIDAS**
                    Para cada partida especifica:
                    - Número y concepto
                    - Unidad de medida
                    - Cantidad
                    - Precio unitario (referenciado de presupuestos similares si aplica)
                    - Subtotal
                    
                    3. **RESUMEN FINANCIERO**
                    - Subtotal
                    - IVA (21%)
                    - Total
                    
                    4. **CONDICIONES**
                    - Validez: 30 días
                    - Plazo estimado de ejecución
                    - Notas especiales o consideraciones
                    
                    Formato de salida:
                    PRESUPUESTO DETALLADO
                    ==================
                    
                    DESCRIPCIÓN:
                    [Resumen del trabajo]
                    
                    PARTIDAS:
                    1. [Concepto] | Unidad: [u.m.] | Cantidad: [qty] | P.U.: €[precio] | Subtotal: €[subtotal]
                    2. ...
                    
                    FINANCIERO:
                    - Subtotal: €[x]
                    - IVA (21%): €[y]
                    - TOTAL: €[z]
                    
                    CONDICIONES:
                    [Plazo, validez, notas]
                """ 
            
        print("📝 Llamando a Groq para generar presupuesto...")

        response = self.groq_client.chat.completions.create(
            model=self.groq_model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=15000
        )
        
        presupuesto_generado=response.choices[0].message.content
        print("✅ Presupuesto generado por Groq")
        
        return{
            "presupuesto_generado": presupuesto_generado,
            "contexto_usado": contexto_usado,
            "similitud_promedio": round(similitud_promedio, 2),
            "cantidad_referencias": len(presupuestos_similares),
            "titulo": titulo,
            "descripcion": descripcion
        }

    def mejorar_presupuesto_existente(
        self,
        presupuesto_id:int,
        feedback:str,
    )->dict:
        presupuesto = self.db.query(Presupuestos).filter(
            Presupuestos.id == presupuesto_id
        ).first()
        
        if not presupuesto:
            raise Exception(f"Presupuesto {presupuesto_id} no encontrado")
        
        print(f"Mejorando presupuesto {presupuesto_id} con feedback: {feedback}")
        
        prompt=f"""Eres experto en presupuestos de construcción.
 
                PRESUPUESTO ORIGINAL:
                Título: {presupuesto.titulo}
                Descripción: {presupuesto.descripcion}
                Total: €{presupuesto.total}
                
                FEEDBACK DEL CLIENTE:
                {feedback}
                
                Basándote en el feedback, mejora y regenera el presupuesto.
                Considera:
                - Cambios en alcance del trabajo
                - Ajustes de precios
                - Mejora de claridad
                - Adiciones o reducciones
                
                Proporciona el presupuesto mejorado en el mismo formato estructurado.
            """
        response= self.groq_client.chat.completions.create(
            model=self.groq_model,
             messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        presupuesto_mejorado = response.choices[0].message.content
        
        presupuesto.contexto_rag = presupuesto_mejorado
        
        self.db.commit()
        
        print(f"Presupuesto mejorado y almacenado")
        
        return {
            "presupuesto_mejorado": presupuesto_mejorado,
            "presupuesto_id": presupuesto_id,
            "actualizado": True
        }
            