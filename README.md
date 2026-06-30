# Diseño de Muro de Contención en Voladizo + Sismo — Versión Flask (Vercel)

Esta es la versión **Flask** de la app (en vez de Streamlit), pensada para
desplegarse en **Vercel** como función serverless. El motor de cálculo
(`calc_core.py`) es exactamente el mismo que en la versión Streamlit — solo
cambió la interfaz: un formulario HTML clásico en vez de widgets de Streamlit.

## Estructura del proyecto

```
vercel_app/
├── api/
│   ├── index.py        ← App Flask (entrypoint que detecta Vercel)
│   └── calc_core.py     ← Motor de cálculo (idéntico al de la versión Streamlit)
├── templates/
│   └── index.html       ← Formulario + tablas de resultados (una sola página)
├── static/               ← (vacío, reservado por si agregas CSS/JS/imágenes)
├── vercel.json           ← Configuración de build/rutas para Vercel
└── requirements.txt       ← Dependencias (solo Flask)
```

## Probarlo en local antes de desplegar

```bash
cd vercel_app
pip install -r requirements.txt
python3 api/index.py
```

Abre `http://localhost:5000` en tu navegador.

## Desplegar en Vercel

**Opción A — con la CLI de Vercel:**
```bash
npm i -g vercel
cd vercel_app
vercel
```
Sigue las instrucciones (te pedirá iniciar sesión con tu cuenta de Vercel).
Cuando termine, te dará una URL pública (`https://tu-proyecto.vercel.app`).

**Opción B — conectando GitHub:**
1. Sube esta carpeta (`vercel_app`) a un repositorio de GitHub.
2. En vercel.com → "Add New Project" → importa el repo.
3. Vercel detecta automáticamente `vercel.json` y el runtime de Python.
4. Deploy. Cada `git push` vuelve a desplegar automáticamente.

## Cómo funciona (por qué esto sí corre en Vercel)

A diferencia de Streamlit (que necesita un proceso persistente con WebSocket
abierto), esta versión es un **request → response clásico**: el usuario
llena el formulario, lo envía (`POST /`), la función serverless ejecuta
`calcular()` con esos datos y devuelve una página HTML completa con todos
los resultados. Cada envío del formulario es una invocación independiente
de la función — exactamente el modelo que Vercel soporta de forma nativa.

## Diferencias frente a la versión Streamlit

- La interfaz es un formulario HTML simple (con CSS propio) en vez de los
  widgets nativos de Streamlit — visualmente más sobria, pero 100%
  funcional y mucho más liviana.
- No hay actualización en vivo mientras escribes: debes presionar
  "🔄 Calcular" para recalcular (es el modelo normal de un formulario web).
- La lógica de cálculo (`calc_core.py`) es **idéntica** a la versión
  Streamlit — mismas fórmulas, mismas validaciones contra el Excel
  original.

## Limitaciones (las mismas que la versión Streamlit)

1. **Hoja externa vinculada ("[1]T2")** del Excel original (geometría del
   dentellón y aporte extra de fricción en deslizamiento) no está
   disponible — se asume 0 por defecto. Puedes ingresar ese valor
   manualmente en el campo correspondiente del formulario.
2. **Punto de corte del refuerzo vertical** (sección 9.1.2 del Excel, tabla
   iterativa cada 0.5 m de altura) no está incluido; se calcula el
   refuerzo en la sección crítica (base de la pantalla).
3. La sección XI (detalle gráfico final de armado) del Excel es un dibujo,
   no una tabla de cálculo, así que no se replicó.
