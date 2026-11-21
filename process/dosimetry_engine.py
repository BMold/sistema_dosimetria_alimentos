import math

def calcular_dosis_emision_3d(dosis_biologica_ia, producto, volumen_cm3):
    """
    Recibe la dosis continua de la IA, el producto y el volumen de la malla 3D.
    Retorna la dosis de emisión exacta de la máquina (I_0), la energía absorbida
    y todos los indicadores nucleares definidos en el contrato del diccionario.
    """
    COEFICIENTE_ATENUACION_MASICO = 0.063  # cm^2/g (Aprox. para Co-60 en tejido vegetal)
    
    DENSIDADES = {
        "papa": 1.08,    # g/cm^3
        "manzana": 0.82  # g/cm^3
    }
    
    # D10 biológico por producto (kGy necesarios para 1 log de reducción microbiana)
    D10_VALORES = {
        "papa": 0.14,    # Patógenos de tubérculo (Erwinia, Fusarium)
        "manzana": 0.35  # Patógenos de fruta (Penicillium, Botrytis)
    }
    
    producto = producto.lower()
    if producto not in DENSIDADES:
        raise ValueError(f"No hay datos de densidad para el producto: {producto}")
        
    densidad = DENSIDADES[producto]
    d10 = D10_VALORES.get(producto, 0.25)
    
    # 1. Masa dinámica desde el volumen 3D
    masa_gramos = volumen_cm3 * densidad
    masa_kg = masa_gramos / 1000.0
    
    # 2. Radio esférico equivalente para calcular la profundidad de penetración
    # V = (4/3) * pi * r^3  -->  r = cbrt( 3V / 4pi )
    radio_cm = ( (3 * volumen_cm3) / (4 * math.pi) ) ** (1/3)
    
    # 3. Física de Atenuación (Beer-Lambert Volumétrica)
    mu_lineal = COEFICIENTE_ATENUACION_MASICO * densidad
    profundidad_centro_cm = radio_cm  # Queremos que la dosis llegue al núcleo
    
    # I_0 = D_centro * exp(μ * d)  -->  La máquina debe emitir más para compensar la atenuación
    dosis_emision_kGy = dosis_biologica_ia * math.exp(mu_lineal * profundidad_centro_cm)
    
    # 4. Energía depositada: E(J) = D(Gy) × m(kg)
    dosis_emision_Gy = dosis_emision_kGy * 1000
    energia_joules = dosis_emision_Gy * masa_kg
    
    # 5. Perfil de atenuación por capas (superficie → centro, 8 capas equidistantes)
    num_capas = 8
    perfil_atenuacion = []
    for i in range(num_capas):
        profundidad = (i / (num_capas - 1)) * profundidad_centro_cm
        dosis_en_capa = dosis_emision_kGy * math.exp(-mu_lineal * profundidad)
        perfil_atenuacion.append(round(dosis_en_capa, 4))
    
    # 6. Uniformidad dosimétrica: Dmax/Dmin = I_0 / D_centro
    uniformidad = round(dosis_emision_kGy / dosis_biologica_ia, 2) if dosis_biologica_ia > 0 else 1.0
    
    # 7. Reducción logarítmica bacteriana: log_red = D_centro / D10
    reduccion_log = round(dosis_biologica_ia / d10, 1) if d10 > 0 else 0.0
    
    return {
        "dosis_emision_requerida_kGy": round(dosis_emision_kGy, 3),
        "profundidad_penetrada_cm": round(profundidad_centro_cm, 2),
        "energia_depositada_total_Joules": round(energia_joules, 2),
        "masa_calculada_kg": round(masa_kg, 4),
        "mu_lineal_cm_inv": round(mu_lineal, 4),
        "densidad_g_cm3": densidad,
        "perfil_atenuacion_kGy": perfil_atenuacion,
        "uniformidad_dosis_ratio": uniformidad,
        "reduccion_logaritmica_bacteriana": reduccion_log
    }

def calcular_dosis_emision_3d_limite(dosis_biologica_ia, producto, volumen_cm3_json):
    """
    Motor físico SciML: Calcula emisión, DUR y Mapeo Virtual de Dosis con límites de seguridad legal.
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
    
    # DUR = Dmax (Superficie) / Dmin (Centro)
    dur_calculado = dosis_emision_kGy / dosis_biologica_ia if dosis_biologica_ia > 0 else 1.0
    
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
        dur_calculado = dosis_emision_kGy / dosis_biologica_ia if dosis_biologica_ia > 0 else 1.0

    # VIRTUAL DOSE MAPPING (Mapeo por capas)
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
            "capa": "Superficie" if i == 0 else "Núcleo" if i == (pasos - 1) else f"Intermedia {int((i/pasos)*100)}%"
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

# --- PRUEBA CON EL FLUJO COMPLETO ---
if __name__ == "__main__":
    # Dato que viene de tu Pilar 1 (Traductor Biológico)
    dosis_necesaria_superficie = 0.12 
    
    # Dato que viene de la visión artificial (ejemplo-json-data.json)
    volumen_detectado = 132.5 
    
    resultado_fisico = calcular_dosis_emision_3d(dosis_necesaria_superficie, "papa", volumen_detectado)
    
    print("=== MOTOR FÍSICO 3D ===")
    print(f"La dosis biológica requerida es: {dosis_necesaria_superficie} kGy")
    print(f"Para penetrar un radio de {resultado_fisico['profundidad_penetrada_cm']} cm...")
    print(f"La máquina debe emitir: {resultado_fisico['dosis_emision_requerida_kGy']} kGy")
    print(f"Energía total inyectada: {resultado_fisico['energia_depositada_total_Joules']} Joules")
    print(f"Perfil de atenuación: {resultado_fisico['perfil_atenuacion_kGy']}")
    print(f"Uniformidad Dmax/Dmin: {resultado_fisico['uniformidad_dosis_ratio']}")
    print(f"Reducción log bacteriana: {resultado_fisico['reduccion_logaritmica_bacteriana']}")
