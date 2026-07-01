"""
App Flask — Diseño de Muro de Contención en Voladizo + Sismo
"
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template, request
from calc_core import calcular, DEFAULT_INPUTS, REBAR_TABLE

app = Flask(__name__, template_folder=os.path.dirname(__file__))


@app.template_filter('fmt')
def fmt_filter(x, dec=3):
    if x is None:
        return "—"
    if isinstance(x, str):
        return x
    if isinstance(x, bool):
        return "Sí" if x else "No"
    try:
        return f"{x:,.{int(dec)}f}"
    except (TypeError, ValueError):
        return str(x)


@app.template_filter('badge')
def badge_filter(ok):
    if ok is None:
        return "—"
    return "✅ Cumple" if ok else "❌ ¡No Cumple!"


BARRAS = list(REBAR_TABLE.keys())

# ---------------------------------------------------------------
# Definición de los campos del formulario (orden = igual al Excel)
# ---------------------------------------------------------------
FIELD_GROUPS = [
    ("1.1 Materiales", [
        dict(key='gamma_muro', label='γmuro — peso específico del concreto (kg/m3)', type='number', step='10'),
        dict(key='fc', label="f'c — resistencia del concreto (kg/cm2)", type='number', step='10'),
        dict(key='fy', label='fy — fluencia del acero (kg/cm2)', type='number', step='100'),
    ]),
    ("1.1 Geometría general", [
        dict(key='H', label='H — Altura total muro + zapata (m)', type='number', step='0.05'),
        dict(key='D', label='D — Profundidad de desplante (m)', type='number', step='0.05'),
    ]),
    ("1.2 Sobrecarga", [
        dict(key='SC', label='S/C — Sobrecarga (kg/m2)', type='number', step='50'),
    ]),
    ("1.3 Suelo de relleno", [
        dict(key='gamma1', label='γ1 — peso específico relleno (kg/m3)', type='number', step='10'),
        dict(key='phi1', label="φ'1 — ángulo de fricción interna (°)", type='number', step='1'),
        dict(key='alpha', label='α — inclinación del terreno (°)', type='number', step='1'),
    ]),
    ("1.4 Suelo de fundación", [
        dict(key='gamma2', label='γ2 — peso específico suelo base (kg/m3)', type='number', step='10'),
        dict(key='phi2', label="φ'2 — ángulo de fricción interna (°)", type='number', step='1'),
        dict(key='alpha2', label='α2 — inclinación relleno externo (°)', type='number', step='1'),
        dict(key='c2', label="C'2 — cohesión (kg/cm2)", type='number', step='0.1'),
        dict(key='sigma_u', label='σu — capacidad portante (kg/cm2)', type='number', step='0.5'),
    ]),
    ("1.5 / 1.6 Factores de seguridad y mayoración", [
        dict(key='FSV', label='FSV — Factor de seguridad por volteo', type='number', step='0.05'),
        dict(key='FSD', label='FSD — Factor de seguridad por deslizamiento', type='number', step='0.05'),
        dict(key='CE', label='CE — mayoración de empujes laterales', type='number', step='0.05'),
        dict(key='CS', label='CS — mayoración de empujes sísmicos', type='number', step='0.05'),
    ]),
    ("1.7 Efecto dinámico (sismo)", [
        dict(key='efecto_dinamico', label='¿Incluir efecto sísmico?', type='checkbox'),
        dict(key='Z', label='Z — Factor de zona sísmica', type='number', step='0.01'),
        dict(key='S', label='S — Factor de suelo', type='number', step='0.05'),
        dict(key='direccion_sismo', label='Dirección de análisis del sismo (Kv)', type='select',
             options=['Arriba', 'Abajo']),
    ]),
    ("1.8 Factores de resistencia (ɸ)", [
        dict(key='phi_flex', label='ɸ Flexión', type='number', step='0.01'),
        dict(key='phi_cort', label='ɸ Cortante', type='number', step='0.01'),
        dict(key='b', label='b — ancho de análisis (m)', type='number', step='0.1'),
    ]),
    ("2.1 Predimensionamiento", [
        dict(key='t1', label='t1 — corona superior (m)', type='number', step='0.05'),
        dict(key='B', label='B — ancho base zapata (m)', type='number', step='0.05'),
        dict(key='hz', label='hz — peralte de zapata (m)', type='number', step='0.05'),
        dict(key='b1', label='b1 — puntera (m)', type='number', step='0.05'),
        dict(key='t2', label='t2 — base de pantalla (m)', type='number', step='0.05'),
        dict(key='r1', label='r1 — recub. sin contacto c/terreno (cm)', type='number', step='0.5'),
        dict(key='r2', label='r2 — recub. en contacto c/terreno (cm)', type='number', step='0.5'),
    ]),
    ("3. Método de coeficientes", [
        dict(key='metodo_activo', label='Empuje activo', type='select', options=['Coulomb', 'Rankine']),
        dict(key='metodo_pasivo', label='Empuje pasivo', type='select', options=['Coulomb', 'Rankine']),
    ]),
    ("8. Capacidad de carga", [
        dict(key='incremento_sigma', label='Aplicar incremento 30% a σu en Es+S y Es+Sc+S', type='checkbox'),
    ]),
    ("9. Refuerzo — Pantalla", [
        dict(key='criterio_rho_min', label='Criterio ρmín', type='select', options=['a', 'b', 'c'],
             option_labels={'a': "0.70√f'c/fy", 'b': "14.1/fy", 'c': "0.0015"}),
        dict(key='barra_interior', label='Barra cara interior (refuerzo principal)', type='select', options=BARRAS),
        dict(key='barra_exterior', label='Barra cara exterior (montaje)', type='select', options=BARRAS),
        dict(key='barra_horiz_ext', label='Barra horizontal cara externa', type='select', options=BARRAS),
        dict(key='barra_horiz_int', label='Barra horizontal cara interna', type='select', options=BARRAS),
        dict(key='sin_resp_sismica', label='Elemento SIN responsabilidad sísmica (long. anclaje)', type='checkbox'),
    ]),
    ("10. Refuerzo — Zapata", [
        dict(key='barra_puntera', label='Barra puntera (acero inferior)', type='select', options=BARRAS),
        dict(key='barra_talon', label='Barra talón (acero superior)', type='select', options=BARRAS),
        dict(key='barra_transversal', label='Barra transversal zapata', type='select', options=BARRAS),
    ]),
    ("⚠️ Términos de archivo externo no disponible", [
        dict(key='Ep_friccion_extra', label='Aporte adicional fricción/Ep dentellón (Ton) — ver nota abajo',
             type='number', step='0.1'),
    ]),
]

BOOL_KEYS = {'efecto_dinamico', 'incremento_sigma', 'sin_resp_sismica'}
SELECT_KEYS = {'direccion_sismo', 'metodo_activo', 'metodo_pasivo', 'criterio_rho_min',
               'barra_interior', 'barra_exterior', 'barra_horiz_ext', 'barra_horiz_int',
               'barra_puntera', 'barra_talon', 'barra_transversal'}


def parse_inputs(form):
    """Lee el formulario y arma el dict de entrada para calcular()."""
    inp = dict(DEFAULT_INPUTS)
    for group, fields in FIELD_GROUPS:
        for f in fields:
            key = f['key']
            if key in BOOL_KEYS:
                inp[key] = (form.get(key) == 'on')
            elif key in SELECT_KEYS:
                inp[key] = form.get(key, DEFAULT_INPUTS.get(key))
            else:
                raw = form.get(key)
                if raw not in (None, ''):
                    try:
                        inp[key] = float(raw)
                    except ValueError:
                        pass
    return inp


def current_value(inp, key):
    return inp.get(key, DEFAULT_INPUTS.get(key))


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        inp = parse_inputs(request.form)
    else:
        inp = dict(DEFAULT_INPUTS)

    res = calcular(inp)

    estados = ['Es', 'Es+Sc', 'Es+S', 'Es+Sc+S']
    all_ok = []
    for est in estados:
        v = res['VI'].get(est)
        if v is not None:
            all_ok.append(v['ok'])
        d = res['VII']['estados'].get(est)
        if d is not None:
            all_ok.append(d['ok'])
        c = res['VIII'].get(est)
        if c is not None:
            all_ok.append(c['ok_resultante'] and c['ok_exc'] and c['ok_presion'])
    R = res['RESUMEN']
    all_ok += [R['pantalla_cortante'], R['pantalla_flexion'], R['pantalla_anclaje'],
               R['puntera_cortante'], R['puntera_flexion'], R['talon_cortante'], R['talon_flexion']]

    return render_template(
        'index.html',
        field_groups=FIELD_GROUPS,
        bool_keys=BOOL_KEYS,
        select_keys=SELECT_KEYS,
        inp=inp,
        current_value=current_value,
        res=res,
        estados=estados,
        all_ok=all(all_ok) if all_ok else False,
    )


# Vercel (@vercel/python) descubre automáticamente la variable `app` (WSGI)
if __name__ == '__main__':
    app.run(debug=True, port=5000)
