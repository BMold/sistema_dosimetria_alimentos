import math

def calcular_dosis_emision_3d(dosis_biologica_ia, producto, volumen_cm3_json):
    """
    Motor físico SciML: Calcula emisión, DUR y Mapeo Virtual de Dosis.
    """
    COEFICIENTE_ATENUACION_MASICO = 0.063  # cm^2/g (Para Co-60)
    
    LIMITES_LEGALES = {
        "papa": {"densidad": 1.08, "dosis_max_legal": 2.50},  
        "manzana": {"densidad": 0.82, "dosis_max_legal": 3.00}
    }
    
    producto = producto.lower()
    if producto not in LIMITES_LEGALES:
        producto = "papa" # Fallback
        
    densidad = LIMITES_LEGALES[producto]["densidad"]
    dosis_max_legal = LIMITES_LEGALES[producto]["dosis_max_legal"]
    
    # 1. Geometría y Profundidad
    masa_kg = (volumen_cm3_json * densidad) / 1000.0
    radio_cm = ( (3 * volumen_cm3_json) / (4 * math.pi) ) ** (1/3)
    mu_lineal = COEFICIENTE_ATENUACION_MASICO * densidad
    
    # 2. Cálculo Base (Beer-Lambert Inverso)
    # I_0 (Superficie) para que llegue I (Centro)
    dosis_emision_kGy = dosis_biologica_ia * math.exp(mu_lineal * radio_cm)
    
    # ==========================================================
    # NUEVO: CÁLCULO DEL DUR Y LÍMITE DE SEGURIDAD
    # ==========================================================
    # DUR = Dmax (Superficie) / Dmin (Centro)
    dur_calculado = dosis_emision_kGy / dosis_biologica_ia
    
    # Regla de negocio: "Never hit the dangerous maximum dose"
    alerta_sobreexposicion = False
    if dosis_emision_kGy > dosis_max_legal:
        alerta_sobreexposicion = True
        # Si la máquina va a quemar la superficie para salvar el centro,
        # forzamos el límite legal para no violar el Codex Alimentarius.
        dosis_emision_kGy = dosis_max_legal 
        
        # Recalculamos cuánta dosis REAL llegará al centro con este tope legal
        # I = I_0 * e^(-mu * x)
        dosis_biologica_ia = dosis_emision_kGy * math.exp(-mu_lineal * radio_cm)
        dur_calculado = dosis_emision_kGy / dosis_biologica_ia

    # ==========================================================
    # NUEVO: VIRTUAL DOSE MAPPING (Mapeo por capas)
    # ==========================================================
    # Simulamos cómo cae la radiación en 5 capas del alimento para el Frontend
    mapeo_virtual = []
    pasos = 5
    for i in range(pasos):
        profundidad_actual = (radio_cm / (pasos - 1)) * i
        # Atenuación pasiva clásica
        dosis_en_capa = dosis_emision_kGy * math.exp(-mu_lineal * profundidad_actual)
        
        mapeo_virtual.append({
            "profundidad_cm": round(profundidad_actual, 2),
            "dosis_kGy": round(dosis_en_capa, 3),
            "capa": "Superficie" if i == 0 else "Núcleo" if i == (pasos - 1) else f"Intermedia {(i/pasos)*100}%"
        })

    energia_joules = (dosis_emision_kGy * 1000) * masa_kg
    
    return {
        "dosis_emision_requerida_kGy": round(dosis_emision_kGy, 3),
        "dosis_real_nucleo_kGy": round(dosis_biologica_ia, 3),
        "indicadores_seguridad": {
            "DUR_calculado": round(dur_calculado, 2),
            "alerta_limite_legal_excedido": alerta_sobreexposicion,
            "limite_legal_aplicado_kGy": dosis_max_legal
        },
        "mapeo_dosis_virtual": mapeo_virtual,
        "profundidad_penetrada_cm": round(radio_cm, 2),
        "energia_depositada_total_Joules": round(energia_joules, 2),
        "masa_calculada_kg": round(masa_kg, 4)
    }