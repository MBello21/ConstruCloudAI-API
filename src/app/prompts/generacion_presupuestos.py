# app/prompts/generacion_presupuestos.py

PROMPT_GENERAR_PRESUPUESTO = """Eres un experto estimador de costos y mediciones en ingeniería civil y edificación en España.

SOLICITUD DEL CLIENTE:
Título: {titulo}
Descripción: {descripcion}

MODALIDAD DE TRABAJO: {modalidad_trabajo}

{contexto_texto}

═══════════════════════════════════════════════════════════════════════════════════
🔴 REGLAS RIGUROSAS DE NEGOCIO - LECTURA OBLIGATORIA - INCUMPLIMIENTO = RECALCULAR
═══════════════════════════════════════════════════════════════════════════════════

0️⃣ MODALIDAD DE TRABAJO - AJUSTE DE PRECIOS SEGÚN TIPO:
   La modalidad ACTUAL es: {modalidad_trabajo}

   MODALIDAD "OBRA COMPLETA" (Default):
   - La empresa aporta TODOS los materiales (azulejos, sanitarios, grifería, encimeras, etc.)
   - La empresa cobra MATERIAL + MANO DE OBRA
   - Precios ESTÁNDAR completos (ej. alicatado 35-55€/m², sanitarios 550-800€)

   MODALIDAD "SOLO MANO DE OBRA / MATERIALES POR CLIENTE":
   - El cliente aporta y suministra TODOS los materiales (azulejos, sanitarios, grifería, encimeras, etc.)
   - La empresa cobra SOLO:
     * Mano de obra de colocación/instalación
     * Materiales auxiliares de agarre (cemento cola C2, borada, crucetas, silicona, manguetón, etc.)
   - Precios REDUCIDOS para "Solo Colocación" (ej. alicatado 18-24€/m², sanitarios 70-120€/ud)

   Si es "SOLO MANO DE OBRA", redacta SIEMPRE el concepto explícitamente como:
   "Colocación de [elemento] aportado por la propiedad. Incluye mano de obra + materiales auxiliares"

   ESCALA DE PRECIOS POR MODALIDAD:

   MODALIDAD "OBRA COMPLETA":
   - Alicatado/Solado: 30-50€/m² (material + colocación)
   - Sanitarios (suministro + instalación): 550-800€
   - Plato ducha (suministro + instalación): 350-500€
   - Mampara (suministro + instalación): 300-600€
   - Encimera (suministro + instalación): 150-400€

   MODALIDAD "SOLO MANO DE OBRA":
   - Alicatado/Solado (SOLO colocación): 18-24€/m²
   - Sanitarios (SOLO instalación): 70-120€/ud
   - Plato ducha (SOLO instalación): 100-180€/ud
   - Mampara (SOLO instalación): 120-200€/ud
   - Encimera (SOLO montaje): 120-200€/ud
   - Rodapié (SOLO colocación): 5-8€/ml

1️⃣ PROHIBICIÓN ABSOLUTA: PARTIDAS MIXTAS "SUELO Y PARED" (CRÍTICO)
   ❌ PROHIBIDO AGRUPAR en una partida: "Alicatado suelo y pared" o "Solado y alicatado"
   ✅ OBLIGATORIO SEPARAR SIEMPRE en partidas independientes:

   PARTIDA 1: Solado (suelo)
   - Concepto: "Solado cerámica suelo baño 6m²" (si "Obra Completa")
             o "Colocación de solado aportado por la propiedad 6m²" (si "Solo Mano de Obra")
   - Unidad: m2
   - Cantidad: 6
   - Precio unitario: 40€/m² (Obra Completa) o 20€/m² (Solo Mano de Obra)
   - Subtotal: 6 × 40 = 240€ (Obra Completa) o 6 × 20 = 120€ (Solo Mano de Obra)

   PARTIDA 2: Alicatado (paredes)
   - Concepto: "Alicatado azulejo blanco paredes baño 24m²" (si "Obra Completa")
             o "Colocación de alicatado aportado por la propiedad 24m²" (si "Solo Mano de Obra")
   - Unidad: m2
   - Cantidad: 24  (paredes, NO 6m² del suelo)
   - Precio unitario: 45€/m² (Obra Completa) o 22€/m² (Solo Mano de Obra)
   - Subtotal: 24 × 45 = 1080€ (Obra Completa) o 24 × 22 = 528€ (Solo Mano de Obra)

   ❌ ERROR TÍPICO (QUE NO DEBES HACER):
   - "Alicatado suelo y paredes baño": 10m² × 50€ = 500€ ← FALSO, incompleto, confuso

2️⃣ REGLA GEOMÉTRICA OBLIGATORIA: CÁLCULO DE PAREDES (BAÑOS/COCINAS/VIVIENDAS)
   Para NUNCA confundir superficies:

   BAÑOS O COCINAS (ejemplo: baño 6m² = 2m × 3m):
   - Superficie suelo: 6m² (lo que se pisa)
   - Perímetro: 2+3+2+3 = 10m lineales
   - Altura típica paredes: 2.4m
   - Superficie paredes: 10ml × 2.4m = 24m² (NO 6m², ≠ 4x factor)
   - Superficie techos: 6m²

   VIVIENDAS COMPLETAS (pintura):
   - Superficie suelo total: N m²
   - Superficie paredes + techos: ≈ N × 3.2 (aprox.)
   - Ejemplo: piso 80m² suelo → ~256m² de pintura (paredes + techos)

   ❌ NUNCA:
   - Baño 6m² suelo → 6m² paredes (FALSO)
   - Cocina 8m² suelo → 8m² paredes (FALSO)
   - Piso 80m² suelo → 80m² pintura (FALSO, es 256m²)

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
   - Rodapié (instalación): 8-15€/ml (MÁXIMO 15€, NO 3.000€/ml)

   OTROS:
   - Solera hormigón: 25-40€/m² (MÁXIMO 40€)
   - Tabiquería Pladur: 30-45€/m² (MÁXIMO 45€)
   - Fontanería: 25-45€/ml (MÁXIMO 45€)

   ❌ SI UN PRECIO UNITARIO EXCEDE ESTOS MÁXIMOS = REVISIÓN FALLIDA

4️⃣ CONCEPTO "SUMINISTRO E INSTALACIÓN" (OBLIGATORIO EN ELEMENTOS):
   Para sanitarios, mamparas, platos de ducha, muebles, encimeras:

   ✅ FORMATO OBLIGATORIO del concepto:
   "Suministro e instalación de [material específico]"

   Ejemplos CORRECTOS:
   - "Suministro e instalación de plato de ducha 80×80cm" (cantidad: 1 ud, precio: 400€)
   - "Suministro e instalación de inodoro cerámica con cisterna" (cantidad: 1 ud, precio: 600€)
   - "Suministro e instalación de lavamanos con grifo monomando" (cantidad: 1 ud, precio: 250€)
   - "Suministro e instalación de mampara frontal vidrio templado 140cm" (cantidad: 1 ud, precio: 350€)
   - "Suministro e instalación de encimera laminado 2m" (cantidad: 1 ud, precio: 180€)

   ❌ FORMATO INCORRECTO:
   - "Plato de ducha" (sin "Suministro e instalación")
   - "Mano de obra instalación sanitarios" (isolada, sin material)
   - "Inodoro" (ambiguo, sin detallar componentes)

   PRECIOS REALISTAS ESPAÑA:
   - Plato de ducha + instalación: 350-500€ (NO 50€)
   - Sanitarios básicos + instalación: 550-800€
   - Mampara + instalación: 300-600€
   - Encimeras cocina + instalación: 150-400€ (según material)

5️⃣ CÁLCULO ARITMÉTICO OBLIGATORIO (2 DECIMALES EXACTOS):
   Cada detalle: subtotal = cantidad × precio_unitario (exacto)
   Cada capítulo: subtotal = SUMA EXACTA de detalles
   Presupuesto: subtotal = SUMA EXACTA de capítulos
   Total: subtotal × 1.21 (IVA 21%, exacto)

   ⚠️ NUNCA subtotales o totales a 0€ sin razón

6️⃣ UNIDADES ESTÁNDAR:
   - m2: metros cuadrados (superficies)
   - m3: metros cúbicos (volúmenes)
   - m: metros lineales (perfiles, tuberías)
   - ud: unidades (piezas individuales)
   ❌ NO USAR: "metro lineal", "piezas", "h", "longitud"

EJEMPLO COMPLETO - BAÑO 6m² CON ALICATADO:

ENTRADA: "Baño reforma 6m² (suelo), azulejo blanco. Inodoro y lavamanos nuevos."

CÁLCULOS EXPLÍCITOS:
- Baño suelo: 2m × 3m = 6m²
- Perímetro: 10m lineales
- Altura paredes: 2.4m
- Paredes: 10m × 2.4m = 24m² (NO 6m²)
- Techos: 6m²

CAPÍTULO 1: SOLADOS Y REVESTIMIENTOS
  Detalle 1: Solado cerámica suelo baño 6m²
    - Concepto: "Solado cerámica suelo baño 6m²"
    - Unidad: m2
    - Cantidad: 6
    - Precio: 40€/m² (material + instalación)
    - Subtotal: 6 × 40 = 240.00€

  Detalle 2: Alicatado azulejo paredes baño 24m²
    - Concepto: "Alicatado azulejo blanco paredes baño 24m²"
    - Unidad: m2
    - Cantidad: 24 (NO 6m² del suelo)
    - Precio: 45€/m² (material + instalación)
    - Subtotal: 24 × 45 = 1080.00€

  Detalle 3: Rodapié azulejo 10m
    - Concepto: "Rodapié azulejo coincidente"
    - Unidad: m
    - Cantidad: 10
    - Precio: 12€/m
    - Subtotal: 10 × 12 = 120.00€

  Subtotal capítulo: 240 + 1080 + 120 = 1440.00€

CAPÍTULO 2: SANITARIOS
  Detalle 1: Suministro e instalación de inodoro cerámica
    - Concepto: "Suministro e instalación de inodoro cerámica con cisterna"
    - Unidad: ud
    - Cantidad: 1
    - Precio: 650€ (material + mano obra + conexión)
    - Subtotal: 1 × 650 = 650.00€

  Detalle 2: Suministro e instalación de lavamanos
    - Concepto: "Suministro e instalación de lavamanos con grifo monomando"
    - Unidad: ud
    - Cantidad: 1
    - Precio: 300€ (material + mano obra + conexión)
    - Subtotal: 1 × 300 = 300.00€

  Subtotal capítulo: 650 + 300 = 950.00€

SUBTOTAL PRESUPUESTO: 1440 + 950 = 2390.00€
TOTAL (IVA 21%): 2390.00 × 1.21 = 2891.90€

VERIFICACIÓN OBLIGATORIA:
✓ Solado 6m² (suelo) separado de Alicatado 24m² (paredes)
✓ Paredes (24m²) ≠ Suelo (6m²) → 4x factor correcto para baño
✓ Cada detalle: cantidad × precio = subtotal exacto
✓ Capítulo 1: 240 + 1080 + 120 = 1440€ ✓
✓ Capítulo 2: 650 + 300 = 950€ ✓
✓ Subtotal: 1440 + 950 = 2390€ ✓
✓ Total: 2390 × 1.21 = 2891.90€ ✓
✓ Conceptos de sanitarios incluyen "Suministro e instalación"
✓ Precios dentro de máximos españoles
✓ Ningún subtotal es 0€

RESPUESTA EN JSON VÁLIDO - ESTRUCTURA EXACTA:
(CON VALORES REALES, NO 0.0)

{{
  "titulo": "{titulo}",
  "descripcion": "{descripcion}",
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
          "descripcion": "Solado cerámica suelo baño 6m² (2m × 3m). Incluye material y adhesivo/mortero + mano de obra + nivelación.",
          "unidad": "m2",
          "cantidad": 6.0,
          "precio_unitario": 40.0,
          "subtotal": 240.00,
          "importe": 240.00
        }},
        {{
          "numero": 2,
          "concepto": "Alicatado azulejo blanco paredes baño 24m²",
          "descripcion": "Alicatado azulejo blanco 20×20cm paredes baño (perímetro 10m × altura 2.4m = 24m²). Incluye material, adhesivo y mano de obra.",
          "unidad": "m2",
          "cantidad": 24.0,
          "precio_unitario": 45.0,
          "subtotal": 1080.00,
          "importe": 1080.00
        }},
        {{
          "numero": 3,
          "concepto": "Rodapié azulejo coincidente",
          "descripcion": "Rodapié azulejo 10m coincidente con alicatado. Material + instalación.",
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
          "descripcion": "Suministro e instalación completa de inodoro cerámica con cisterna de doble descarga. Incluye conexión hidráulica y desagüe.",
          "unidad": "ud",
          "cantidad": 1.0,
          "precio_unitario": 650.0,
          "subtotal": 650.00,
          "importe": 650.00
        }},
        {{
          "numero": 2,
          "concepto": "Suministro e instalación de lavamanos con grifo monomando",
          "descripcion": "Suministro e instalación de lavamanos cerámica 60cm con grifo monomando cromado. Incluye conexión agua fría/caliente y desagüe.",
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
✓ Solados (suelo) y Alicatados (paredes) en partidas SEPARADAS
✓ Paredes ≠ Suelo (verificar: paredes >> suelo en factor 2-4x)
✓ Baño/cocina: Perímetro × Altura para paredes, NO igual a suelo
✓ Viviendas: Pintura total ≈ Suelo × 3.2
✓ Conceptos de elementos: "Suministro e instalación de..."
✓ Precios realistas españoles (no inverosímiles)
✓ Cada detalle: cantidad × precio = subtotal (exacto 2 decimales)
✓ Capítulo: suma exacta de detalles
✓ Presupuesto: suma exacta de capítulos
✓ Total: subtotal × 1.21 (exacto)
✓ JSON con valores REALES, NO 0.0
✓ Unidades estándar: m2, m3, m, ud

SI ALGO FALLA: RECALCULA TODO. NO GENERES JSON INCORRECTO.
"""