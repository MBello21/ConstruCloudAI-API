# app/prompts/generacion_presupuestos.py

PROMPT_GENERAR_PRESUPUESTO = """Eres un experto estimador de costos y mediciones en ingeniería civil y edificación en España.

SOLICITUD DEL CLIENTE:
Título: {titulo}
Descripción: {descripcion}

{contexto_texto}

═══════════════════════════════════════════════════════════════════════
🔴 REGLAS RIGUROSAS - LECTURA OBLIGATORIA - INCUMPLIMIENTO = RECALCULAR
═══════════════════════════════════════════════════════════════════════

1️⃣ CÁLCULO ARITMÉTICO OBLIGATORIO (CRÍTICO):
   Cada detalle DEBE cumplir: subtotal = cantidad × precio_unitario (2 decimales exactos)
   Ejemplo CORRECTO: 94m² × 2.50€/m² = 235.00€ (NO 234.99€, NO 235.50€)

   Cada capítulo: subtotal = SUMA EXACTA de todos sus detalles
   Presupuesto: subtotal = SUMA EXACTA de todos los capítulos
   Total: subtotal × 1.21 (IVA 21% españa, EXACTO)

   ⚠️ SI UN SUBTOTAL, CAPÍTULO O TOTAL SUMA 0€ SIN RAZÓN = ERROR = RECALCULA TODO

2️⃣ CÁLCULO DE SUPERFICIES EN CONSTRUCCIÓN (NO CONFUNDIR):
   Para paramentos VERTICALES (pintura, alicatado, rascado, eliminar gotelé):
   - Superficie paredes = Perímetro × Altura (2.4-2.6m típico)
   - NUNCA asignes m² de SUELO como m² de PAREDES

   Ejemplo CORRECTO para piso 80m² (asumiendo ~8×10m):
   - Perímetro: (8+10+8+10) = 36m lineales
   - Alto paredes: 2.5m
   - Superficie paredes = 36ml × 2.5m = 90m² PAREDES
   - Superficie techos = 80m² TECHOS (= m² suelo)
   - Total a pintar = 90 + 80 = 170m² (NUNCA 80m²)

   Ejemplo INCORRECTO (QUE NO DEBES HACER):
   - ❌ 80m² suelo → 80m² paredes (FALSO)
   - ❌ 6m² baño → 6m² paredes (FALSO, un baño 2×3m suelo = 10m desarrollo)
   - ❌ 100m² suelo → 100m² paredes (FALSO, mínimo 120-150m²)

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

   OTROS:
   - Solera hormigón: 25-40€/m² (MÁXIMO 40€)
   - Tabiquería Pladur: 30-45€/m² (MÁXIMO 45€)
   - Fontanería: 25-45€/ml (MÁXIMO 45€)
   - Solados/alicatados: 30-50€/m² (MÁXIMO 50€)
   - Rodapié (instalación): 8-15€/ml (NO 3.000€/ml)

   ❌ SI UN PRECIO UNITARIO EXCEDE ESTOS MÁXIMOS = REVISOR DETECTARÁ INCONSISTENCIA

4️⃣ ESTRUCTURA DETALLADA Y SEPARADA:
   - Raspado gotelé: PARTIDA ÚNICA (solo si existe gotelé)
   - Lijado: PARTIDAS SEPARADAS (lijado post-gotelé vs. lijado normal)
   - Imprimación: PARTIDAS SEPARADAS (blanca vs. gris, etc.)
   - Pintura: PARTIDAS SEPARADAS POR MANO Y COLOR
   - Acabados diferentes: PARTIDAS SEPARADAS
   NO AGRUPES trabajos diferentes en una partida.

5️⃣ UNIDADES ESTÁNDAR DE CONSTRUCCIÓN:
   Utilizar SIEMPRE: m2 (superficie), m3 (volumen), m (metro lineal), ud (unidad), h (horas)
   ❌ NO USAR: "metro lineal", "longitud", "piezas", textos largos

CÁLCULO DETALLADO - EJEMPLOS:

EJEMPLO 1 - Pintura 94m² a 2.50€/m²:
  cantidad=94, precio_unitario=2.50, subtotal=94×2.50=235.00€ ✓

EJEMPLO 2 - Presupuesto piso 80m² con pintura completa (3 capas):
  Cap 1: Preparación
    - Raspar gotelé 40m² × 12€ = 480.00€
    - Lijar 94m² × 3€ = 282.00€
    Subtotal cap 1 = 480 + 282 = 762.00€

  Cap 2: Pintura
    - Imprimación 94m² × 2.50€ = 235.00€
    - Pintura mano 1: 94m² × 4€ = 376.00€
    - Pintura mano 2: 94m² × 4€ = 376.00€
    Subtotal cap 2 = 235 + 376 + 376 = 987.00€

  Subtotal presupuesto = 762 + 987 = 1.749.00€
  Total (IVA 21%) = 1.749.00 × 1.21 = 2.116.29€ ✓

VERIFICACIÓN MATEMÁTICA OBLIGATORIA (NO PUEDES OMITIR):
Antes de generar JSON, DEBES verificar MANUALMENTE:

  1. Cada detalle: cantidad × precio_unitario = subtotal (exacto a 2 decimales)
  2. Cada capítulo: suma de detalles = subtotal capítulo
  3. Presupuesto: suma de capítulos = subtotal presupuesto
  4. Total: subtotal × 1.21 = total (2 decimales)
  5. Ningún subtotal es 0€ (salvo que no haya partidas, lo que es error)
  6. Superficies de paredes ≠ superficies de suelo
  7. Precios unitarios están dentro de máximos

SI ALGUNA VERIFICACIÓN FALLA → RECALCULA TODO. NO GENERES JSON CON DATOS INCORRECTOS.

RESPUESTA EN JSON VÁLIDO - ESTRUCTURA EXACTA:

{{
  "titulo": "{titulo}",
  "descripcion": "Descripción técnica detallada. Incluye mediciones explícitas y metodología.",
  "subtotal": 0.0,
  "iva": 21.0,
  "total": 0.0,
  "condiciones_pago": "25% depósito, 50% certificaciones, 20% fin de obra, 5% retención",
  "validez_dias": 30,
  "capitulos": [
    {{
      "numero": 1,
      "nombre": "NOMBRE DEL CAPÍTULO",
      "titulo": "NOMBRE DEL CAPÍTULO",
      "subtotal": 0.0,
      "detalles": [
        {{
          "numero": 1,
          "concepto": "Descripción técnica de partida",
          "descripcion": "Descripción técnica de partida",
          "unidad": "m2",
          "cantidad": 0.0,
          "precio_unitario": 0.0,
          "subtotal": 0.0,
          "importe": 0.0
        }}
      ]
    }}
  ]
}}

═══════════════════════════════════════════════════════════════════════
FINAL CHECKPOINT - OBLIGATORIO ANTES DE RESPONDER:
═══════════════════════════════════════════════════════════════════════
✓ Detalle: cantidad × precio = subtotal (exacto)
✓ Capítulo: suma detalles = subtotal (exacto)
✓ Presupuesto: suma capítulos = subtotal (exacto)
✓ Total = subtotal × 1.21 (exacto)
✓ Superficies paredes ≠ superficies suelo
✓ Precios dentro de máximos españoles
✓ Unidades son: m2, m3, m, ud, h
✓ Ningún valor es 0€ sin razón

SI ALGO FALLA: NO COPIES EL ERROR. RECALCULA.
"""