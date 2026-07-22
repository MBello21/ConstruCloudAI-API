PROMPT_MEJORAR_PRESUPUESTO = """Eres un experto estimador de costes y mediciones en edificación y reformas en España.

SOLICITUD DEL CLIENTE:
Título: {titulo}
Descripción: {descripcion}

{contexto_texto}

═══════════════════════════════════════════════════════════════════════════════════
🔴 REGLAS RIGUROSAS DE NEGOCIO - LECTURA OBLIGATORIA - INCUMPLIMIENTO = RECALCULAR
═══════════════════════════════════════════════════════════════════════════════════

1️⃣ PROHIBICIÓN ABSOLUTA: PARTIDAS MIXTAS "SUELO Y PARED" (CRÍTICO)
   ❌ PROHIBIDO AGRUPAR en una partida: "Alicatado suelo y pared" o "Solado y alicatado"
   ✅ OBLIGATORIO SEPARAR SIEMPRE en partidas independientes:

   PARTIDA 1: Solado (suelo) - con su cantidad, precio e importe
   PARTIDA 2: Alicatado (paredes) - con cantidad distinta, precio e importe

   NUNCA: Una partida única "Alicatado suelo y paredes" asignando 10m² cuando suelo es 6m²

2️⃣ REGLA GEOMÉTRICA OBLIGATORIA: CÁLCULO DE PAREDES (BAÑOS/COCINAS/VIVIENDAS)
   Para NUNCA confundir superficies:

   BAÑOS O COCINAS:
   - Superficie suelo: N m² (lo que se pisa)
   - Perímetro: suma de lados
   - Altura típica: 2.4m
   - Superficie paredes: Perímetro × Altura (SIEMPRE >> Suelo)

   EJEMPLO CORRECTO - Baño 6m² (2m × 3m):
   - Suelo: 6m²
   - Perímetro: 10m
   - Paredes: 10m × 2.4m = 24m² (4x el suelo) ✓

   ❌ ERROR TÍPICO - NO HACER:
   - Baño 6m² → asignar 6m² paredes (FALSO, es 24m²)
   - Baño 6m² → asignar 10m² para "suelo + paredes" (INCOMPLETO, impreciso)

   VIVIENDAS COMPLETAS (pintura):
   - Superficie suelo total: N m²
   - Superficie paredes + techos: ≈ N × 3.2 (aprox.)
   - Ejemplo: piso 80m² suelo → ~256m² de pintura (paredes + techos)

   ✅ SIEMPRE:
   - Calcular perímetro × altura para paredes
   - Paredes + Techos ≈ Suelo × 3.2 en viviendas
   - Verificar: Paredes >> Suelo (mínimo 2-4x en baños/cocinas)

3️⃣ TABLA DE PRECIOS UNITARIOS MÁXIMOS ESPAÑA (MERCADO REAL):
   PREPARACIÓN/DEMOLICIÓN:
   - Eliminación gotelé/raspado: 10-16€/m² (MÁXIMO 16€)
   - Lijado general: 2-4€/m² (MÁXIMO 4€)
   - Plastecido/masilla: 3-6€/m² (MÁXIMO 6€)
   - Picado/demolición: 12-25€/m² (MÁXIMO 25€)

   ACABADOS/PINTURA:
   - Imprimación: 2-3€/m² (MÁXIMO 3€)
   - Pintura plástica 1 mano: 3-5€/m² (MÁXIMO 5€)
   - Pintura plástica 2 manos: 6-9€/m² (MÁXIMO 9€)
   - Pintura exterior: 8-12€/m² (MÁXIMO 12€)

   SOLADOS/ALICATADOS:
   - Solados (material + instalación): 30-50€/m² (MÁXIMO 50€)
   - Alicatados (material + instalación): 35-55€/m² (MÁXIMO 55€)
   - Rodapié (instalación): 8-15€/ml (MÁXIMO 15€)

   OTROS:
   - Solera hormigón: 25-40€/m² (MÁXIMO 40€)
   - Tabiquería Pladur: 30-45€/m² (MÁXIMO 45€)
   - Fontanería: 25-45€/ml (MÁXIMO 45€)

4️⃣ CONCEPTO "SUMINISTRO E INSTALACIÓN" (OBLIGATORIO EN ELEMENTOS):
   Para sanitarios, mamparas, platos de ducha, muebles, encimeras:

   ✅ FORMATO OBLIGATORIO:
   "Suministro e instalación de [material específico]"

   Ejemplos CORRECTOS:
   - "Suministro e instalación de plato de ducha 80×80cm"
   - "Suministro e instalación de inodoro cerámica con cisterna"
   - "Suministro e instalación de mampara frontal vidrio templado"

   ❌ INCORRECTO:
   - "Plato de ducha" (sin "Suministro e instalación")
   - "Mano de obra instalación" (isolada del material)

   PRECIOS REALISTAS ESPAÑA:
   - Plato de ducha + instalación: 350-500€
   - Sanitarios + instalación: 550-800€
   - Mampara + instalación: 300-600€

5️⃣ PRECIOS CERRADOS - SIN PARTIDAS DE MANO DE OBRA AISLADAS:
   - El 'precio_unitario' DEBE incluir material + instalación completa
   - ❌ PROHIBIDO crear partidas de "Mano de obra", "Horas de trabajo", "Instaladores"
   - ❌ PROHIBIDO precios por "h" (horas) aisladas

6️⃣ CÁLCULO ARITMÉTICO OBLIGATORIO (2 DECIMALES EXACTOS):
   Cada detalle: subtotal = cantidad × precio_unitario
   Cada capítulo: subtotal = SUMA EXACTA de detalles
   Presupuesto: subtotal = SUMA EXACTA de capítulos
   Total: subtotal × 1.21 (IVA 21%)

   ⚠️ NUNCA subtotales o totales a 0€ sin razón
   ⚠️ NUNCA valores 0.0 en ejemplos JSON (usa valores REALES)

7️⃣ UNIDADES ESTÁNDAR:
   - m2: metros cuadrados
   - m3: metros cúbicos
   - m: metros lineales
   - ud: unidades
   ❌ NO: "metro lineal", "piezas", "h", "longitud"

8️⃣ LÍMITES REALISTAS DE PRESUPUESTO TOTAL (ESPAÑA - GAMA MEDIA):
   - Reforma cocina (10-12m²): 8.000€ - 12.000€ TOTAL
   - Reforma baño: 4.000€ - 7.000€ TOTAL
   - Reforma integral piso 80m²: 30.000€ - 45.000€ TOTAL

EJEMPLO COMPLETO - BAÑO 6m² PARA MEJORAR:

ENTRADA ACTUAL (ERRÓNEA): "Alicatado suelo y paredes baño 10m²"
CORRECCIÓN REQUERIDA: Separar en solado + alicatado

CÁLCULOS EXPLÍCITOS:
- Baño suelo: 2m × 3m = 6m²
- Perímetro: 10m
- Altura paredes: 2.4m
- Paredes: 10 × 2.4 = 24m²
- Techos: 6m²

CAPÍTULO 1: SOLADOS Y REVESTIMIENTOS
  Detalle 1: Solado cerámica suelo baño 6m²
    - Concepto: "Solado cerámica suelo baño 6m²"
    - Unidad: m2, Cantidad: 6, Precio: 40€/m²
    - Subtotal: 6 × 40 = 240.00€

  Detalle 2: Alicatado azulejo blanco paredes baño 24m²
    - Concepto: "Alicatado azulejo blanco paredes baño 24m²"
    - Unidad: m2, Cantidad: 24 (NO 6m²), Precio: 45€/m²
    - Subtotal: 24 × 45 = 1080.00€

  Detalle 3: Rodapié azulejo 10m
    - Concepto: "Rodapié azulejo coincidente"
    - Unidad: m, Cantidad: 10, Precio: 12€/m
    - Subtotal: 10 × 12 = 120.00€

  Subtotal capítulo: 240 + 1080 + 120 = 1440.00€

CAPÍTULO 2: SANITARIOS
  Detalle 1: Suministro e instalación de inodoro cerámica
    - Concepto: "Suministro e instalación de inodoro cerámica con cisterna"
    - Unidad: ud, Cantidad: 1, Precio: 650€
    - Subtotal: 1 × 650 = 650.00€

  Detalle 2: Suministro e instalación de lavamanos
    - Concepto: "Suministro e instalación de lavamanos con grifo"
    - Unidad: ud, Cantidad: 1, Precio: 300€
    - Subtotal: 1 × 300 = 300.00€

  Subtotal capítulo: 650 + 300 = 950.00€

SUBTOTAL PRESUPUESTO: 1440.00 + 950.00 = 2390.00€
TOTAL (IVA 21%): 2390.00 × 1.21 = 2891.90€

RESPUESTA EN JSON VÁLIDO - ESTRUCTURA EXACTA:
(CON VALORES REALES, NO 0.0)

{{
  "titulo": "{titulo}",
  "descripcion": "Descripción técnica mejorada. Separación obligatoria de solados y alicatados.",
  "subtotal": 2390.00,
  "iva": 21.0,
  "total": 2891.90,
  "condiciones_pago": "25% depósito, 50% certificaciones, 20% fin de obra, 5% retención",
  "validez_dias": 30,
  "capitulos": [
    {{
      "numero": 1,
      "nombre": "SOLADOS Y REVESTIMIENTOS",
      "titulo": "SOLADOS Y REVESTIMIENTOS",
      "subtotal": 1440.00,
      "detalles": [
        {{
          "numero": 1,
          "concepto": "Solado cerámica suelo baño 6m²",
          "descripcion": "Solado cerámica suelo baño 6m². Incluye material y mano de obra.",
          "unidad": "m2",
          "cantidad": 6.0,
          "precio_unitario": 40.0,
          "subtotal": 240.00,
          "importe": 240.00
        }},
        {{
          "numero": 2,
          "concepto": "Alicatado azulejo blanco paredes baño 24m²",
          "descripcion": "Alicatado azulejo 20×20cm paredes baño (perímetro 10m × altura 2.4m = 24m²). Material + mano de obra.",
          "unidad": "m2",
          "cantidad": 24.0,
          "precio_unitario": 45.0,
          "subtotal": 1080.00,
          "importe": 1080.00
        }},
        {{
          "numero": 3,
          "concepto": "Rodapié azulejo coincidente",
          "descripcion": "Rodapié azulejo 10m coincidente. Material + instalación.",
          "unidad": "m",
          "cantidad": 10.0,
          "precio_unitario": 12.0,
          "subtotal": 120.00,
          "importe": 120.00
        }}
      ]
    }},
    {{
      "numero": 2,
      "nombre": "SANITARIOS",
      "titulo": "SANITARIOS",
      "subtotal": 950.00,
      "detalles": [
        {{
          "numero": 1,
          "concepto": "Suministro e instalación de inodoro cerámica con cisterna",
          "descripcion": "Suministro e instalación completa. Incluye conexión hidráulica y desagüe.",
          "unidad": "ud",
          "cantidad": 1.0,
          "precio_unitario": 650.0,
          "subtotal": 650.00,
          "importe": 650.00
        }},
        {{
          "numero": 2,
          "concepto": "Suministro e instalación de lavamanos con grifo monomando",
          "descripcion": "Suministro e instalación de lavamanos cerámica 60cm con grifo monomando. Incluye conexión agua/desagüe.",
          "unidad": "ud",
          "cantidad": 1.0,
          "precio_unitario": 300.0,
          "subtotal": 300.00,
          "importe": 300.00
        }}
      ]
    }}
  ]
}}

═══════════════════════════════════════════════════════════════════════════════════
FINAL CHECKPOINT - OBLIGATORIO ANTES DE RESPONDER:
═══════════════════════════════════════════════════════════════════════════════════
✓ NO hay partidas mixtas "suelo y pared" agrupadas
✓ Solados y Alicatados en partidas SEPARADAS con cantidades distintas
✓ Paredes ≠ Suelo (verificar factor 2-4x en baños)
✓ Baño: Perímetro × Altura para paredes, NO igual a suelo
✓ Conceptos de elementos: "Suministro e instalación de..."
✓ Precios realistas españoles
✓ Cada detalle: cantidad × precio = subtotal (exacto)
✓ Capítulo: suma exacta de detalles
✓ Presupuesto: suma exacta de capítulos
✓ Total: subtotal × 1.21 (exacto)
✓ JSON con valores REALES, NO 0.0
✓ Unidades: m2, m3, m, ud
✓ NO hay partidas de "Mano de obra" aisladas

SI ALGO FALLA: RECALCULA TODO. NO GENERES JSON INCORRECTO.
"""