PROMPT_MEJORAR_PRESUPUESTO = """Eres un experto estimador de costes y mediciones en edificación y reformas en España.

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

4️⃣ PRECIOS CERRADOS - SIN PARTIDAS DE MANO DE OBRA AISLADAS:
   - El 'precio_unitario' DEBE incluir material + instalación
   - ❌ PROHIBIDO crear partidas de "Mano de obra", "Horas de trabajo", "Instaladores"
   - ❌ PROHIBIDO precios por "h" (horas) aisladas sin especificar concepto

5️⃣ ESTRUCTURA DETALLADA Y SEPARADA:
   - Raspado gotelé: PARTIDA ÚNICA (solo si existe gotelé)
   - Lijado: PARTIDAS SEPARADAS (lijado post-gotelé vs. lijado normal)
   - Imprimación: PARTIDAS SEPARADAS (blanca vs. gris, etc.)
   - Pintura: PARTIDAS SEPARADAS POR MANO Y COLOR
   - Acabados diferentes: PARTIDAS SEPARADAS
   - Color diferente = partida separada
   - Zona diferente = partida separada
   NO AGRUPES trabajos diferentes en una partida.

6️⃣ UNIDADES ESTÁNDAR DE CONSTRUCCIÓN:
   Utilizar SIEMPRE: m2 (superficie), m3 (volumen), m (metro lineal), ud (unidad)
   ❌ NO USAR: "metro lineal", "longitud", "piezas", "h", textos largos

7️⃣ LÍMITES REALISTAS DE PRESUPUESTO TOTAL (ESPAÑA - GAMA MEDIA):
   - Reforma cocina (10-12m²): 8.000€ - 12.000€ TOTAL
   - Reforma baño: 4.000€ - 7.000€ TOTAL
   - Reforma integral piso 80m²: 30.000€ - 45.000€ TOTAL
   - Acondicionamiento local comercial (60m²): 20.000€ - 35.000€ TOTAL

CÁLCULO DETALLADO - EJEMPLO COMPLETO:

ENTRADA: "Piso 80m², 3 dormitorios, salón, cocina, 2 baños. Lijar, imprimación, 2 manos pintura. Algunas paredes con gotele. Blanco excepto dormitorio principal gris."

CÁLCULOS EXPLÍCITOS:
- Perímetro estimado: 40ml (piso ~8×12m)
- Altura paredes: 2.6m
- Superficie paredes: 40ml × 2.6m = 104m²
- Superficie techos: 80m²
- Total: 184m²
- 30% paredes con gotelé = 0.30 × 104 = 31m² gotelé, 73m² sin gotelé
- Color blanco: 150m² (salón, cocina, baños, 2 dormitorios secundarios)
- Color gris: 34m² (dormitorio principal)

CAPÍTULO 1: PREPARACIÓN (subtotal debe ser suma de detalles)
  Detalle 1: Raspar gotelé 31m² × 14€/m² = 434.00€
  Detalle 2: Lijar post-gotelé 31m² × 3€/m² = 93.00€
  Detalle 3: Lijar normal 73m² × 2€/m² = 146.00€
  Subtotal cap 1: 434.00 + 93.00 + 146.00 = 673.00€

CAPÍTULO 2: PINTURA BLANCA (subtotal debe ser suma de detalles)
  Detalle 1: Imprimación blanca 150m² × 2.50€/m² = 375.00€
  Detalle 2: Pintura blanca mano 1: 150m² × 4€/m² = 600.00€
  Detalle 3: Pintura blanca mano 2: 150m² × 4€/m² = 600.00€
  Subtotal cap 2: 375.00 + 600.00 + 600.00 = 1.575.00€

CAPÍTULO 3: PINTURA GRIS (subtotal debe ser suma de detalles)
  Detalle 1: Imprimación gris 34m² × 2.50€/m² = 85.00€
  Detalle 2: Pintura gris mano 1: 34m² × 4€/m² = 136.00€
  Detalle 3: Pintura gris mano 2: 34m² × 4€/m² = 136.00€
  Subtotal cap 3: 85.00 + 136.00 + 136.00 = 357.00€

SUBTOTAL PRESUPUESTO: 673.00 + 1.575.00 + 357.00 = 2.605.00€
TOTAL (IVA 21%): 2.605.00 × 1.21 = 3.152.05€

VERIFICACIÓN MATEMÁTICA OBLIGATORIA (NO PUEDES OMITIR):
Antes de generar JSON, DEBES verificar MANUALMENTE:

  1. Cada detalle: cantidad × precio_unitario = subtotal (exacto a 2 decimales)
  2. Cada capítulo: suma de detalles = subtotal capítulo
  3. Presupuesto: suma de capítulos = subtotal presupuesto
  4. Total: subtotal × 1.21 = total (2 decimales)
  5. Ningún subtotal es 0€ (salvo que no haya partidas, lo que es error)
  6. Superficies de paredes ≠ superficies de suelo
  7. Precios unitarios están dentro de máximos
  8. NO hay partidas de "Mano de obra" aisladas

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
          "concepto": "Descripción técnica",
          "descripcion": "Descripción técnica",
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
✓ Unidades son: m2, m3, m, ud (NO h, NO "metro lineal")
✓ Ningún valor es 0€ sin razón
✓ NO hay partidas de "Mano de obra" aisladas

SI ALGO FALLA: NO COPIES EL ERROR. RECALCULA.
"""