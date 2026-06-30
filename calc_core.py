"""
Núcleo de cálculo - Diseño de Muro de Contención en Voladizo + Sismo
Replica la lógica y fórmulas del archivo Excel "Libro1.xlsx" (Hoja1)
Unidades: Ton, m, kg, cm (se indica en cada sección)
"""
import math


def cot(x):
    return 1 / math.tan(x)


def acot(x):
    # ACOT(x) = atan(1/x), igual que Excel _xlfn.ACOT
    return math.atan(1 / x)


# ---------- Tabla de varillas de acero (D508:F521) ----------
REBAR_TABLE = {
    'Ø 6mm':    {'As': math.pi * 0.6 ** 2 / 4, 'db': 0.6},
    'Ø 8mm':    {'As': math.pi * 0.8 ** 2 / 4, 'db': 0.8},
    'Ø 1/4"':   {'As': math.pi * (1/4*2.54) ** 2 / 4, 'db': 1/4*2.54},
    'Ø 3/8"':   {'As': math.pi * (3/8*2.54) ** 2 / 4, 'db': 3/8*2.54},
    'Ø12mm':    {'As': math.pi * 1.2 ** 2 / 4, 'db': 1.2},
    'Ø 1/2"':   {'As': math.pi * (1/2*2.54) ** 2 / 4, 'db': 1/2*2.54},
    'Ø 5/8"':   {'As': math.pi * (5/8*2.54) ** 2 / 4, 'db': 5/8*2.54},
    'Ø 3/4"':   {'As': math.pi * (3/4*2.54) ** 2 / 4, 'db': 3/4*2.54},
    'Ø 7/8"':   {'As': math.pi * (7/8*2.54) ** 2 / 4, 'db': 7/8*2.54},
    'Ø 1"':     {'As': math.pi * (1*2.54) ** 2 / 4, 'db': 1*2.54},
    'Ø 1 1/8"': {'As': math.pi * (1.125*2.54) ** 2 / 4, 'db': 1.125*2.54},
    'Ø 1 1/4"': {'As': math.pi * (1.25*2.54) ** 2 / 4, 'db': 1.25*2.54},
    'Ø 1 3/8"': {'As': math.pi * (1.375*2.54) ** 2 / 4, 'db': 1.375*2.54},
    'Ø 1 1/2"': {'As': math.pi * (1.5*2.54) ** 2 / 4, 'db': 1.5*2.54},
}


def espaciamiento(barra, b_cm, Asd_cm2):
    """ S = ROUNDDOWN( (As_barra*(b/100)/Asd) * 100 / 2.5, 0) * 2.5 / 100   -> en metros """
    As = REBAR_TABLE[barra]['As']
    raw = (As * (b_cm / 100) / Asd_cm2) * 100
    s = math.floor(raw / 2.5) * 2.5 / 100
    return s


def asr(barra, b_cm, S_m):
    As = REBAR_TABLE[barra]['As']
    return As * (b_cm / 100) / S_m


def cumple(cond):
    return "Cumple" if cond else "¡No Cumple!"


def calcular(inp):
    """
    inp: dict con todas las variables de entrada (ver DEFAULT_INPUTS).
    Devuelve un dict gigante 'r' con todos los resultados intermedios,
    organizados por sección, replicando el Excel.
    """
    r = {}
    rad = math.radians

    # ============ I. DATOS DE ENTRADA ============
    gamma_muro = inp['gamma_muro'] / 1000.0   # Ton/m3
    fc = inp['fc']
    fy = inp['fy']
    Es = 2.04e6
    beta1 = 0.85 if fc <= 280 else max(0.85 - ((fc - 280) / 70) * 0.05, 0.65)
    H = inp['H']
    D = inp['D']
    SC = inp['SC']  # kg/m2
    gamma1 = inp['gamma1'] / 1000.0
    phi1 = inp['phi1']
    alpha = inp['alpha']
    delta = (2/3) * phi1
    gamma2 = inp['gamma2'] / 1000.0
    phi2 = inp['phi2']
    alpha2 = inp['alpha2']
    delta2 = (2/3) * phi2
    c2 = inp['c2']  # kg/cm2
    sigma_u = inp['sigma_u']  # kg/cm2
    mu = math.tan(rad(phi2))
    FSV = inp['FSV']
    FSD = inp['FSD']
    CE = inp['CE']
    CS = inp['CS']

    efecto_dinamico = inp['efecto_dinamico']  # bool
    Z = inp['Z']
    S = inp['S']
    Kho = 0 if not efecto_dinamico else Z * S
    Kh = 0 if not efecto_dinamico else 0.5 * Kho
    Kv = 0.5 * Kh
    theta = math.degrees(math.atan(Kh / (1 - Kv))) if efecto_dinamico else 0
    phi_flex = inp['phi_flex']
    phi_cort = inp['phi_cort']
    b = inp['b']  # ancho de análisis, m (=1)

    r['I'] = dict(gamma_muro=gamma_muro, fc=fc, beta1=beta1, fy=fy, Es=Es, H=H, D=D, SC=SC,
                  gamma1=gamma1, phi1=phi1, alpha=alpha, delta=delta,
                  gamma2=gamma2, phi2=phi2, alpha2=alpha2, delta2=delta2, c2=c2, sigma_u=sigma_u,
                  mu=mu, FSV=FSV, FSD=FSD, CE=CE, CS=CS, Kho=Kho, Kh=Kh, Kv=Kv, theta=theta,
                  phi_flex=phi_flex, phi_cort=phi_cort, b=b)

    # ============ II. PREDIMENSIONAMIENTO ============
    t1 = inp['t1']
    B = inp['B']
    hz = inp['hz']
    Hp = H - hz
    b1 = inp['b1']
    t2 = inp['t2']
    Sreal = (t2 - t1) / Hp
    b2 = B - b1 - t2
    beta2 = math.degrees(acot((t2 - t1) / Hp))
    beta = inp['beta']  # = 90
    r1 = inp['r1']
    r2 = inp['r2']

    r['II'] = dict(t1=t1, B=B, hz=hz, Hp=Hp, b1=b1, t2=t2, Sreal=Sreal, b2=b2,
                    beta2=beta2, beta=beta, r1=r1, r2=r2)

    # ============ III. COEFICIENTES DE EMPUJE ============
    metodo_activo = inp['metodo_activo']  # 'Coulomb' o 'Rankine'
    if metodo_activo == 'Coulomb':
        Ka = (math.sin(rad(beta + phi1)) ** 2) / (
            (math.sin(rad(beta)) ** 2) * math.sin(rad(beta - delta)) *
            (1 + math.sqrt(
                math.sin(rad(phi1 + delta)) * math.sin(rad(phi1 - alpha)) /
                (math.sin(rad(beta - delta)) * math.sin(rad(alpha + beta)))
            )) ** 2
        )
    else:  # Rankine (requiere beta=90)
        Ka = math.cos(rad(alpha)) * (
            (math.cos(rad(alpha)) - math.sqrt(math.cos(rad(alpha)) ** 2 - math.cos(rad(phi1)) ** 2)) /
            (math.cos(rad(alpha)) + math.sqrt(math.cos(rad(alpha)) ** 2 - math.cos(rad(phi1)) ** 2))
        )

    metodo_pasivo = inp['metodo_pasivo']  # 'Coulomb' o 'Rankine'
    if metodo_pasivo == 'Coulomb':
        Kp = (math.sin(rad(beta2 - phi2)) ** 2) / (
            (math.sin(rad(beta2)) ** 2) * math.sin(rad(beta2 + delta2)) *
            (1 - math.sqrt(
                math.sin(rad(phi2 + delta2)) * math.sin(rad(phi2 + alpha2)) /
                (math.sin(rad(beta2 + delta2)) * math.sin(rad(alpha2 + beta2)))
            )) ** 2
        )
    else:
        Kp = math.cos(rad(alpha2)) * (
            (math.cos(rad(alpha2)) + math.sqrt(math.cos(rad(alpha2)) ** 2 - math.cos(rad(phi2)) ** 2)) /
            (math.cos(rad(alpha2)) - math.sqrt(math.cos(rad(alpha2)) ** 2 - math.cos(rad(phi2)) ** 2))
        )

    if efecto_dinamico:
        Kae = (math.sin(rad(phi1 + beta - theta)) ** 2) / (
            math.cos(rad(theta)) * (math.sin(rad(beta)) ** 2) * math.sin(rad(beta - theta - delta)) *
            (1 + math.sqrt(
                math.sin(rad(phi1 + delta)) * math.sin(rad(phi1 - theta - alpha)) /
                (math.sin(rad(beta - delta - theta)) * math.sin(rad(alpha + beta)))
            )) ** 2
        )
        Kpe = (math.sin(rad(-phi2 + beta2 + theta)) ** 2) / (
            math.cos(rad(theta)) * (math.sin(rad(beta2)) ** 2) * math.sin(rad(beta2 + theta + delta2)) *
            (1 - math.sqrt(
                math.sin(rad(phi2 + delta2)) * math.sin(rad(phi2 - theta + alpha2)) /
                (math.sin(rad(beta2 + delta2 + theta)) * math.sin(rad(alpha2 + beta2)))
            )) ** 2
        )
    else:
        Kae = 0
        Kpe = 0

    r['III'] = dict(Ka=Ka, Kp=Kp, Kae=Kae, Kpe=Kpe, metodo_activo=metodo_activo, metodo_pasivo=metodo_pasivo)

    # ============ IV. FUERZAS Y MOMENTOS EN BASE A PANTALLA (t2) ============
    H100 = b2 * math.tan(rad(alpha))  # altura adicional por talud sobre talón (si Rankine)
    I114 = Hp if metodo_activo == 'Coulomb' else Hp + H100  # Hp efectivo

    Ea_p = (0.5 * Ka * gamma1 * I114 ** 2)
    if metodo_activo == 'Coulomb':
        Eah_p = Ea_p * math.cos(rad(90 - beta + delta))
    else:
        Eah_p = Ea_p * math.cos(rad(alpha))

    Fsc_p = Ka * I114 * (SC / 1000) * (math.sin(rad(beta)) / math.sin(rad(beta + alpha)))
    EAE_p = 0.5 * Kae * gamma1 * I114 ** 2 * (1 - Kv) if efecto_dinamico else 0
    dAE_p = abs(EAE_p - Eah_p) if EAE_p != 0 else 0

    Pw1_p = ((t2 - t1) * Hp / 2) * gamma_muro * Kh
    Pw2_p = t1 * Hp * gamma_muro * Kh

    # brazos y momentos (pantalla)
    P118, Q118 = Eah_p * b, I114 / 3
    P119, Q119 = Fsc_p * b, I114 / 2
    P120, Q120 = dAE_p * b, I114 * 2 / 3
    P121, Q121 = Pw1_p * b, Hp / 3
    P122, Q122 = Pw2_p * b, Hp / 2
    R118, R119, R120, R121, R122 = P118*Q118, P119*Q119, P120*Q120, P121*Q121, P122*Q122

    sum_Vd_p = P118 + P119 + P120 + P121 + P122
    sum_Mmax_p = R118 + R119 + R120 + R121 + R122
    Mu_p = abs(CE * (R118 + R119) + CS * (R120 + R121 + R122))
    Vdu_p = (CE * (P118 + P119) + CS * (P120 + P121 + P122)) / phi_cort

    r['IV'] = dict(H100=H100, Hp_efectiva=I114, Ea=Ea_p, Eah=Eah_p, Fsc=Fsc_p, EAE=EAE_p, dAE=dAE_p,
                    Pw1=Pw1_p, Pw2=Pw2_p, fuerzas=[
                        ('Ea', P118, Q118, R118, '←'), ('Fsc', P119, Q119, R119, '←'),
                        ('∆AE', P120, Q120, R120, '←'), ('Pw1', P121, Q121, R121, '←'),
                        ('Pw2', P122, Q122, R122, '←')],
                    sum_Vd=sum_Vd_p, sum_Mmax=sum_Mmax_p, Mu=Mu_p, Vdu=Vdu_p)

    # ============ V. FUERZAS Y MOMENTOS TOTALES (toda la estructura) ============
    W1_area = (t2 - t1) * Hp / 2
    W1 = gamma_muro * W1_area * b
    W1_brazo = b1 + 2*(t2 - t1)/3
    W1_mom = W1 * W1_brazo

    W2_area = t1 * Hp
    W2 = gamma_muro * W2_area * b
    W2_brazo = b1 + (t2 - t1) + t1/2
    W2_mom = W2 * W2_brazo

    W3_area = B * hz
    W3 = gamma_muro * W3_area * b
    W3_brazo = B / 2
    W3_mom = W3 * W3_brazo

    W4_area = b2 * Hp
    W4 = gamma1 * W4_area * b
    W4_brazo = b1 + t2 + b2/2
    W4_mom = W4 * W4_brazo

    J137 = inp.get('J137', 0.0)
    W5_area = b2 * J137 / 2
    W5 = gamma1 * W5_area * b
    W5_brazo = b1 + t2 + 2*b2/3
    W5_mom = W5 * W5_brazo

    W6 = b2 * (SC / 1000) * b
    W6_brazo = b1 + t2 + b2/2
    W6_mom = W6 * W6_brazo

    W7_area = b1 * max(D - hz, 0)
    W7 = gamma2 * W7_area * b
    W7_brazo = b1 / 2
    W7_mom = W7 * W7_brazo

    W8 = 0.0
    W8_mom = 0.0

    I172 = H if metodo_activo == 'Coulomb' else H + H100
    Ea_t = 0.5 * Ka * gamma1 * I172 ** 2
    if metodo_activo == 'Coulomb':
        Eah_t = Ea_t * math.cos(rad(90 - beta + delta))
    else:
        Eah_t = Ea_t * math.cos(rad(alpha))

    Ep_t = 0.5 * Kp * gamma2 * D ** 2 + 2 * (c2 * 10) * math.sqrt(Kp) * D
    Fsc_t = Ka * I172 * (SC / 1000) * (math.sin(rad(beta)) / math.sin(rad(beta + alpha)))
    EAE_t = 0.5 * Kae * gamma1 * I172 ** 2 * (1 - Kv) if efecto_dinamico else 0
    dAE_t = (EAE_t - Eah_t) if EAE_t != 0 else 0

    Pw1_t = (W1 / b) * Kh
    Pw2_t = (W2 / b) * Kh
    Pw3_t = (W3 / b) * Kh

    if metodo_activo == 'Coulomb':
        EaV = Ea_t * math.sin(rad(90 - beta + delta))
        EaV_brazo = b1 + t2
    else:
        EaV = Ea_t * math.sin(rad(alpha))
        EaV_brazo = B
    EaV_mom = EaV * EaV_brazo

    direccion_sismo = inp['direccion_sismo']  # 'Arriba' o 'Abajo'
    signo = -1 if direccion_sismo == 'Arriba' else 1

    Wss1 = signo * W1 * Kv
    Wss1_mom = Wss1 * W1_brazo
    Wss2 = signo * W2 * Kv
    Wss2_mom = Wss2 * W2_brazo
    Wss3 = signo * W3 * Kv
    Wss3_mom = Wss3 * W3_brazo
    Wss4 = signo * W4 * Kv
    Wss4_mom = Wss4 * W4_brazo
    Wss5 = signo * W5 * Kv
    Wss5_mom = Wss5 * W5_brazo

    sum_N_full = (W1 + W2 + W3 + W4 + W5 + W6 + W7 + W8 + EaV +
                  Wss1 + Wss2 + Wss3 + Wss4 + Wss5)

    Me_estatico = W1_mom + W2_mom + W3_mom + W4_mom + W7_mom + EaV_mom
    Me_estatico_sc = Me_estatico + W6_mom
    Me_sismo = (W1_mom + W2_mom + W3_mom + W4_mom + W7_mom +
                Wss1_mom + Wss2_mom + Wss3_mom + Wss4_mom + Wss5_mom) if efecto_dinamico else None
    Me_total = (W1_mom+W2_mom+W3_mom+W4_mom+W5_mom+W6_mom+W7_mom+W8_mom+EaV_mom +
                Wss1_mom+Wss2_mom+Wss3_mom+Wss4_mom+Wss5_mom) if efecto_dinamico else None

    sum_N_estatico = W1 + W2 + W3 + W4 + W7
    sum_N_estatico_sc = sum_N_estatico + W6
    sum_N_sismo = (W1+W2+W3+W4+W7+Wss1+Wss2+Wss3+Wss4+Wss5) if efecto_dinamico else None
    sum_N_total_full = sum_N_full if efecto_dinamico else None

    R181 = Eah_t * (I172/3)
    Mv_estatico = R181
    Mv_estatico_sc = R181 + Fsc_t * (I172/2)
    Mv_total = None
    Mv_sismo = None
    if efecto_dinamico:
        Mv_sismo = R181 + dAE_t*(I172*2/3) + Pw1_t*(hz+Hp/3) + Pw2_t*(hz+Hp/2) + Pw3_t*(hz/2)
        Mv_total = R181 + Fsc_t*(I172/2) + dAE_t*(I172*2/3) + Pw1_t*(hz+Hp/3) + Pw2_t*(hz+Hp/2) + Pw3_t*(hz/2)

    sum_Vd_estatico = Eah_t
    sum_Vd_estatico_sc = Eah_t + Fsc_t
    sum_Vd_sismo = None
    sum_Vd_total = None
    if efecto_dinamico:
        sum_Vd_sismo = Eah_t + dAE_t + Pw1_t + Pw2_t + Pw3_t
        sum_Vd_total = Eah_t + Fsc_t + dAE_t + Pw1_t + Pw2_t + Pw3_t

    r['V'] = dict(
        pesos=[('W1', W1, W1_brazo, W1_mom), ('W2', W2, W2_brazo, W2_mom), ('W3', W3, W3_brazo, W3_mom),
               ('W4', W4, W4_brazo, W4_mom), ('W5', W5, W5_brazo, W5_mom), ('W6 (Sc)', W6, W6_brazo, W6_mom),
               ('W7', W7, W7_brazo, W7_mom), ('Ea V', EaV, EaV_brazo, EaV_mom)],
        Ea=Ea_t, Eah=Eah_t, Ep=Ep_t, Fsc=Fsc_t, EAE=EAE_t, dAE=dAE_t,
        Pw1=Pw1_t, Pw2=Pw2_t, Pw3=Pw3_t, H_efectiva=I172,
        sum_N_estatico=sum_N_estatico, sum_N_estatico_sc=sum_N_estatico_sc,
        sum_N_sismo=sum_N_sismo, sum_N_total=sum_N_total_full,
        Me_estatico=Me_estatico, Me_estatico_sc=Me_estatico_sc, Me_sismo=Me_sismo, Me_total=Me_total,
        Mv_estatico=Mv_estatico, Mv_estatico_sc=Mv_estatico_sc, Mv_sismo=Mv_sismo, Mv_total=Mv_total,
        sum_Vd_estatico=sum_Vd_estatico, sum_Vd_estatico_sc=sum_Vd_estatico_sc,
        sum_Vd_sismo=sum_Vd_sismo, sum_Vd_total=sum_Vd_total,
    )

    # ============ VI. VERIFICACIÓN POR VOLTEO ============
    estados = ['Es', 'Es+Sc', 'Es+S', 'Es+Sc+S']
    volteo = {}
    Me_list = [Me_estatico, Me_estatico_sc, Me_sismo, Me_total]
    Mv_list = [Mv_estatico, Mv_estatico_sc, Mv_sismo, Mv_total]
    for est, Me, Mv in zip(estados, Me_list, Mv_list):
        if Me is None or Mv is None:
            volteo[est] = None
            continue
        FS = Me / Mv
        volteo[est] = dict(Me=Me, Mv=Mv, FS=FS, FSV=FSV, ok=FS > FSV)
    r['VI'] = volteo

    # ============ VII. VERIFICACIÓN POR DESLIZAMIENTO ============
    ca = (2/3) * c2  # kg/cm2 (factor de adherencia * cohesión)
    Ep_friccion_extra = inp.get('Ep_friccion_extra', 0.0)  # dato externo no disponible -> manual

    desliz = {}
    sumN_list = [sum_N_estatico, sum_N_estatico_sc, sum_N_sismo, sum_N_total_full]
    Kv_list = [0, 0, Kv, Kv]
    Vd_list = [sum_Vd_estatico, sum_Vd_estatico_sc, sum_Vd_sismo, sum_Vd_total]
    for est, sN, kv_e, Vd in zip(estados, sumN_list, Kv_list, Vd_list):
        if sN is None or Vd is None:
            desliz[est] = None
            continue
        Fr = sN * mu * (1 - kv_e) + B * ca * 10 * b + Ep_friccion_extra
        FS = Fr / Vd
        desliz[est] = dict(Fr=Fr, Ph=Vd, FS=FS, FSD=FSD, ok=FS > FSD)
    r['VII'] = dict(estados=desliz, ca=ca)

    # ============ VIII. VERIFICACIÓN POR CAPACIDAD DE CARGA ============
    capacidad = {}
    Bt3 = B / 3
    Bt6 = B / 6
    Bt2 = B / 2
    sumN_list2 = [sum_N_estatico, sum_N_estatico_sc, sum_N_sismo, sum_N_total_full]
    for est, Me, Mv, sN in zip(estados, Me_list, Mv_list, sumN_list2):
        if Me is None or Mv is None or sN is None:
            capacidad[est] = None
            continue
        Xo = (Me - Mv) / sN
        ok_resultante = Bt3 < Xo < 2 * Bt3
        e = Bt2 - Xo
        ok_exc = e < Bt6
        incremento = inp['incremento_sigma']
        factor = 1.3 if (incremento and est in ('Es+S', 'Es+Sc+S')) else 1.0
        sigma_adm = factor * sigma_u * 10  # Ton/m2
        q1 = (sN / B) * (1 + 6 * e / B)
        q2 = (sN / B) * (1 - 6 * e / B)
        ok_presion = max(q1, q2) < sigma_adm
        capacidad[est] = dict(Xo=Xo, ok_resultante=ok_resultante, e=e, ok_exc=ok_exc,
                               q1=q1, q2=q2, sigma_adm=sigma_adm, ok_presion=ok_presion, N=sN)
    r['VIII'] = capacidad

    # ============ IX. DISEÑO DE PANTALLA ============
    rho_min_a = 0.7 * math.sqrt(fc) / fy
    rho_min_b = 14.1 / fy
    rho_min_c = 0.0015
    criterio = inp['criterio_rho_min']
    rho_min = {'a': rho_min_a, 'b': rho_min_b, 'c': rho_min_c}[criterio]

    rho_b = 0.85 * fc * beta1 / fy * (6120 / (6120 + fy))
    rho_max = min(0.5 * rho_b, 0.025)

    r['IX_cuantias'] = dict(rho_min_a=rho_min_a, rho_min_b=rho_min_b, rho_min_c=rho_min_c,
                             rho_min=rho_min, rho_b=rho_b, rho_max=rho_max)

    def disenar_flexion(Mu_tnm, b_cm, d_cm, rho_min_local):
        denom = phi_flex * fc * b_cm * d_cm ** 2
        arg = Mu_tnm * 1e5 / denom
        disc = max(1 - 4 * 0.59 * arg, 0)
        w1 = (1 + math.sqrt(disc)) / (2 * 0.59)
        w2 = (1 - math.sqrt(disc)) / (2 * 0.59)
        rho_d = min(w1, w2) * fc / fy
        Asd = max(rho_d, rho_min_local) * b_cm * d_cm
        return dict(w1=w1, w2=w2, rho_d=rho_d, Asd=Asd)

    b_cm = b * 100
    # Nota: el Excel usa el recubrimiento r1 (no r2) y el espesor t2 (base de pantalla)
    # para calcular 'd' tanto en la cara interior como en la cara exterior de la pantalla.
    d_interior = t2 * 100 - r1 - REBAR_TABLE[inp['barra_interior']]['db'] / 2
    f91 = disenar_flexion(Mu_p, b_cm, d_interior, rho_min)
    barra_int = inp['barra_interior']
    S_int = espaciamiento(barra_int, b_cm, f91['Asd'])
    Asr_int = asr(barra_int, b_cm, S_int)
    Asmax_int = rho_max * b_cm * d_interior
    ok_int = (f91['Asd'] <= Asr_int <= Asmax_int)
    r['IX_interior'] = dict(d=d_interior, Mu=Mu_p, **f91, barra=barra_int, S=S_int, Asr=Asr_int,
                             Asmax=Asmax_int, ok=ok_int)

    rho_min_ext = 0.0015
    d_ext = t2 * 100 - r1 - REBAR_TABLE[inp['barra_exterior']]['db'] / 2
    db_m_cm = REBAR_TABLE[inp['barra_exterior']]['db']
    Lm = 36 * db_m_cm / 100
    Asm = REBAR_TABLE[inp['barra_exterior']]['As'] * (b_cm / 100) / Lm
    Asd_ext = max(rho_min_ext * b_cm * d_ext, Asm)
    barra_ext = inp['barra_exterior']
    S_ext = espaciamiento(barra_ext, b_cm, Asd_ext)
    Asr_ext = asr(barra_ext, b_cm, S_ext)
    r['IX_exterior'] = dict(d=d_ext, Asm=Asm, Asd=Asd_ext, barra=barra_ext, S=S_ext, Asr=Asr_ext)

    rho_t = 0.002
    Ast_top = rho_t * b_cm * (t1 * 100)
    Ast_mid = rho_t * b_cm * ((t1 + t2) / 2 * 100)
    Ast_bot = rho_t * b_cm * (t2 * 100)
    horiz = {}
    for nombre, Ast in [('Arriba (1/3 sup)', Ast_top), ('Medio (1/3 cent)', Ast_mid), ('Abajo (1/3 inf)', Ast_bot)]:
        ext_b = inp['barra_horiz_ext']
        int_b = inp['barra_horiz_int']
        Ast_ext = (2/3) * Ast
        Ast_int = (1/3) * Ast
        S_ext_h = espaciamiento(ext_b, b_cm, Ast_ext)
        Asr_ext_h = asr(ext_b, b_cm, S_ext_h)
        S_int_h = espaciamiento(int_b, b_cm, Ast_int)
        Asr_int_h = asr(int_b, b_cm, S_int_h)
        horiz[nombre] = dict(Ast=Ast, ext=dict(barra=ext_b, Ast_req=Ast_ext, S=S_ext_h, Asr=Asr_ext_h),
                              interior=dict(barra=int_b, Ast_req=Ast_int, S=S_int_h, Asr=Asr_int_h))
    r['IX_horizontal'] = horiz

    lam = 1.0
    Vc_pantalla = 0.53 * lam * math.sqrt(fc) * b_cm * d_interior / 1000
    Vce_pantalla = (2/3) * Vc_pantalla
    ok_cortante_pantalla = Vdu_p < Vce_pantalla
    r['IX_cortante'] = dict(Vdu=Vdu_p, Vc=Vc_pantalla, Vce=Vce_pantalla, ok=ok_cortante_pantalla,
                             ratio=(Vdu_p/Vce_pantalla if Vce_pantalla else None))

    psi_e = inp['psi_e']
    psi_c = inp['psi_c']
    psi_r = inp['psi_r']
    lam_ldg = 1.0
    db_ancla_cm = REBAR_TABLE[barra_int]['db']
    Ldg = (0.075 * psi_e * psi_c * psi_r * lam_ldg * fy / math.sqrt(fc)) * db_ancla_cm
    sin_resp_sismica = inp['sin_resp_sismica']
    factor_r = (f91['Asd'] / Asr_int) if sin_resp_sismica else 1.0
    ldg_final = max(Ldg * factor_r, 8 * db_ancla_cm, 15)
    hz_cm = hz * 100
    ok_anclaje = ldg_final < hz_cm
    r['IX_anclaje'] = dict(Ldg=Ldg, factor_r=factor_r, ldg_final=ldg_final, hz_cm=hz_cm, ok=ok_anclaje)

    # ============ X. DISEÑO DE ZAPATA BASE ============
    est_critico = 'Es+Sc+S' if efecto_dinamico else 'Es+Sc'
    cap_crit = capacidad[est_critico]
    q1c, q2c = cap_crit['q1'], cap_crit['q2']

    qa = ((q2c - q1c) * (b1 - 0) / (B - 0)) + q1c
    qb = ((q2c - q1c) * (b1 + t2 - 0) / (B - 0)) + q1c

    direccion = inp['direccion_sismo']
    Wpp = -b1 * hz * gamma_muro * b
    Wpp_brazo = b1 / 2
    Wpp_mom = Wpp * Wpp_brazo

    Wr_rect = -b1 * max(D - hz, 0) * gamma2 * b
    Wr_mom = Wr_rect * Wpp_brazo

    qtri = ((q1c - qa) if (q1c - qa) > 0 else (-q1c + qa)) * b1 / 2 * b
    qtri_brazo = 2 * b1 / 3
    qtri_mom = qtri * qtri_brazo

    qrect = qa * b1 * b
    qrect_brazo = b1 / 2
    qrect_mom = qrect * qrect_brazo

    signo_p = 1 if direccion == 'Arriba' else -1
    Wsspp = signo_p * abs(Wpp * Kv)
    Wsspp_mom = Wsspp * Wpp_brazo

    Fr_punt = Wpp + Wr_rect + qtri + qrect + Wsspp
    Mmax_punt = Wpp_mom + Wr_mom + qtri_mom + qrect_mom + Wsspp_mom

    Vdu_punt = abs(CE * (Wpp + Wr_rect + qtri + qrect) + CS * Wsspp) / phi_cort
    d_punt = hz * 100 - r2 - REBAR_TABLE[inp['barra_puntera']]['db'] / 2
    Vc_punt = 0.53 * lam * math.sqrt(fc) * b_cm * d_punt / 1000
    Vce_punt = 1.0 * Vc_punt
    ok_cortante_punt = Vdu_punt < Vce_punt

    Mua_punt = abs(CE * (Wpp_mom + Wr_mom + qtri_mom + qrect_mom) + CS * Wsspp_mom)
    rho_min_zap = 0.0018
    f_punt = disenar_flexion(Mua_punt, b_cm, d_punt, rho_min_zap)
    barra_punt = inp['barra_puntera']
    S_punt = espaciamiento(barra_punt, b_cm, f_punt['Asd'])
    Asr_punt = asr(barra_punt, b_cm, S_punt)
    Asmax_punt = rho_max * b_cm * d_punt
    ok_punt_flex = f_punt['Asd'] <= Asr_punt <= Asmax_punt

    r['X_puntera'] = dict(qa=qa, qb=qb, Fr=Fr_punt, Mmax=Mmax_punt, Vdu=Vdu_punt, Vc=Vc_punt, Vce=Vce_punt,
                           ok_cortante=ok_cortante_punt, Mua=Mua_punt, d=d_punt, barra=barra_punt,
                           S=S_punt, Asr=Asr_punt, Asd=f_punt['Asd'], Asmax=Asmax_punt, ok_flexion=ok_punt_flex)

    Wpp_t = -b2 * hz * gamma_muro * b
    Wpp_t_brazo = b2 / 2
    Wpp_t_mom = Wpp_t * Wpp_t_brazo

    qtri_t = ((qb - q2c) if (qb - q2c) > 0 else (-qb + q2c)) * b2 / 2 * b
    qtri_t_brazo = b2 / 3
    qtri_t_mom = qtri_t * qtri_t_brazo

    qrect_t = b2 * q2c * b
    qrect_t_brazo = b2 / 2
    qrect_t_mom = qrect_t * qrect_t_brazo

    Wsc_t = -SC/1000 * b2 * b
    Wsc_t_mom = Wsc_t * qrect_t_brazo

    Wr_t = -b2 * Hp * gamma1 * b
    Wr_t_mom = Wr_t * qrect_t_brazo

    Wtalud_t = -(b2 * H100 / 2) * gamma1 * b
    Wtalud_t_brazo = 2 * b2 / 3
    Wtalud_t_mom = Wtalud_t * Wtalud_t_brazo

    signo_t = 1 if direccion == 'Arriba' else -1
    Wsspp_t = signo_t * abs(Wpp_t * Kv)
    Wsspp_t_mom = Wsspp_t * Wpp_t_brazo
    Wssrect_t = signo_t * abs(Wr_t * Kv)
    Wssrect_t_mom = Wssrect_t * qrect_t_brazo
    Wsstalud_t = signo_t * abs(Wtalud_t * Kv)
    Wsstalud_t_mom = Wsstalud_t * Wtalud_t_brazo

    Fr_tal = Wpp_t + qtri_t + qrect_t + Wsc_t + Wr_t + Wtalud_t + Wsspp_t + Wssrect_t + Wsstalud_t
    Mmax_tal = (Wpp_t_mom + qtri_t_mom + qrect_t_mom + Wsc_t_mom + Wr_t_mom + Wtalud_t_mom +
                Wsspp_t_mom + Wssrect_t_mom + Wsstalud_t_mom)

    Vdu_tal = abs(CE * (Wpp_t + qtri_t + qrect_t + Wsc_t + Wr_t + Wtalud_t) +
                  CS * (Wsspp_t + Wssrect_t + Wsstalud_t)) / phi_cort
    d_tal = hz * 100 - r2 - REBAR_TABLE[inp['barra_talon']]['db'] / 2
    Vc_tal = 0.53 * lam * math.sqrt(fc) * b_cm * d_tal / 1000
    Vce_tal = 1.0 * Vc_tal
    ok_cortante_tal = Vdu_tal < Vce_tal

    Mua_tal = abs(CE * (Wpp_t_mom + qtri_t_mom + qrect_t_mom + Wsc_t_mom + Wr_t_mom + Wtalud_t_mom) +
                  CS * (Wsspp_t_mom + Wssrect_t_mom + Wsstalud_t_mom))
    f_tal = disenar_flexion(Mua_tal, b_cm, d_tal, rho_min_zap)
    barra_tal = inp['barra_talon']
    S_tal = espaciamiento(barra_tal, b_cm, f_tal['Asd'])
    Asr_tal = asr(barra_tal, b_cm, S_tal)
    Asmax_tal = rho_max * b_cm * d_tal
    ok_tal_flex = f_tal['Asd'] <= Asr_tal <= Asmax_tal

    r['X_talon'] = dict(Fr=Fr_tal, Mmax=Mmax_tal, Vdu=Vdu_tal, Vc=Vc_tal, Vce=Vce_tal, ok_cortante=ok_cortante_tal,
                         Mua=Mua_tal, d=d_tal, barra=barra_tal, S=S_tal, Asr=Asr_tal, Asd=f_tal['Asd'],
                         Asmax=Asmax_tal, ok_flexion=ok_tal_flex)

    rho_t_zap = 0.0018
    barra_trans = inp['barra_transversal']
    db_mz_cm = REBAR_TABLE[barra_trans]['db']
    Lm_zap = 36 * db_mz_cm / 100
    Asm_zap = REBAR_TABLE[barra_trans]['As'] * (b_cm / 100) / Lm_zap
    Asd_trans = max(rho_t_zap * b_cm * (hz * 100), Asm_zap)
    S_trans = espaciamiento(barra_trans, b_cm, Asd_trans)
    Asr_trans = asr(barra_trans, b_cm, S_trans)
    r['X_transversal'] = dict(Asd=Asd_trans, barra=barra_trans, S=S_trans, Asr=Asr_trans)

    r['RESUMEN'] = dict(
        pantalla_cortante=ok_cortante_pantalla, pantalla_flexion=ok_int, pantalla_anclaje=ok_anclaje,
        puntera_cortante=ok_cortante_punt, puntera_flexion=ok_punt_flex,
        talon_cortante=ok_cortante_tal, talon_flexion=ok_tal_flex,
        volteo=volteo, deslizamiento=desliz, capacidad=capacidad,
    )

    return r


DEFAULT_INPUTS = dict(
    gamma_muro=2400, fc=210, fy=4200, H=5.65, D=1.0, SC=500,
    gamma1=1800, phi1=30, alpha=10, gamma2=1800, phi2=30, alpha2=0, c2=0, sigma_u=3,
    FSV=1.5, FSD=1.25, CE=1.7, CS=1.0,
    efecto_dinamico=True, Z=0.10, S=1.00, phi_flex=0.90, phi_cort=0.85, b=1.0,
    t1=0.30, B=3.5, hz=0.65, b1=0.55, t2=0.65, beta=90, r1=4, r2=7.5,
    metodo_activo='Coulomb', metodo_pasivo='Coulomb',
    direccion_sismo='Arriba', incremento_sigma=True,
    criterio_rho_min='a',
    barra_interior='Ø 5/8"', barra_exterior='Ø 5/8"',
    barra_horiz_ext='Ø 1/2"', barra_horiz_int='Ø 3/8"',
    psi_e=1.0, psi_c=0.7, psi_r=0.8, sin_resp_sismica=True,
    barra_puntera='Ø 5/8"', barra_talon='Ø 1"', barra_transversal='Ø 5/8"',
    Ep_friccion_extra=0.0, J137=0.0,
)


if __name__ == '__main__':
    res = calcular(DEFAULT_INPUTS)
    print("Ka =", res['III']['Ka'], " (esperado 0.34002)")
    print("Kp =", res['III']['Kp'], " (esperado 5.30497)")
    print("Kae =", res['III']['Kae'], " (esperado 0.384295)")
    print("Kpe =", res['III']['Kpe'], " (esperado 5.07289)")
    print("Mu pantalla =", res['IV']['Mu'], " (esperado 28.8005)")
    print("Vdu pantalla =", res['IV']['Vdu'], " (esperado 17.9003)")
    print("sum_N_total (Es+Sc+S) =", res['V']['sum_N_total'], " (esperado 35.9089)")
    print("Me total =", res['V']['Me_total'], " (esperado 68.8459)")
    print("Mv total =", res['V']['Mv_total'], " (esperado 26.9135)")
    print("Volteo Es+Sc+S:", res['VI']['Es+Sc+S'])
    print("Deslizamiento Es:", res['VII']['estados']['Es'])
    print("Capacidad Es+Sc+S:", res['VIII']['Es+Sc+S'])
    print("IX interior Asd:", res['IX_interior']['Asd'], "(esperado 14.5412)")
    print("IX interior S:", res['IX_interior']['S'])
    print("Cortante pantalla:", res['IX_cortante'])
    print("Anclaje:", res['IX_anclaje'])
    print("Puntera:", res['X_puntera'])
    print("Talon:", res['X_talon'])
