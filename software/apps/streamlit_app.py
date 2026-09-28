"""Dashboard del brazo clasificador.

    pip install streamlit
    streamlit run software/apps/streamlit_app.py

Dos modos:
  * Simulación: el ciclo corre en el PC con los mismos módulos del robot.
  * ESP32: manda las órdenes por Wi-Fi al servidor del robot y consulta estado.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from brazo.config import HOME, PINZA_ABIERTA_MM              # noqa: E402
from brazo.controller import Controlador                     # noqa: E402
from brazo.cups import CRITERIOS, Vaso, lote_aleatorio, lote_demo, totales  # noqa: E402
from brazo.kinematics import fk                              # noqa: E402
from brazo.links import EnlaceHTTP, EnlaceNulo               # noqa: E402
from brazo.planner import planificar                         # noqa: E402
from brazo.protocol import trama                             # noqa: E402

st.set_page_config(page_title="Brazo clasificador de monedas", page_icon="🦾",
                   layout="wide")

NOMBRE_CRITERIO = {"denominacion": "Denominación", "cantidad": "Cantidad de monedas",
                   "valor": "Valor total", "peso": "Peso"}


def estado_inicial():
    if "ctrl" not in st.session_state:
        st.session_state.ctrl = Controlador(lote_demo(), enlace=EnlaceNulo())
        st.session_state.registro = []


def responder(pregunta: str, ctrl: Controlador) -> str:
    """Asistente de reglas: responde con los datos que ya tiene el controlador.

    Es el punto de partida del chatbot del proyecto; más adelante se puede
    conectar a un modelo de lenguaje manteniendo estas mismas funciones como
    herramientas.
    """
    q = pregunta.lower()
    t = totales(ctrl.vasos)
    if "cuánto" in q and ("vale" in q or "valor" in q or "plata" in q or "dinero" in q):
        return f"El lote suma ${t['valor']:,}".replace(",", ".") + f" en {t['monedas']} monedas."
    if "pesa" in q or "peso" in q:
        mas = max(ctrl.vasos, key=lambda v: v.peso_g)
        return (f"El lote pesa {t['peso_g']:.1f} g. El más pesado es el de "
                f"{mas} con {mas.peso_g:.1f} g.")
    if "cuántos vasos" in q or "cuantos vasos" in q:
        return f"Hay {len(ctrl.vasos)} vasos, uno por puesto."
    if "pose" in q or "dónde" in q or "donde" in q:
        x, y, z, phi = fk(ctrl.q)
        return f"El TCP está en X {x:.1f} cm, Y {y:.1f} cm, Z {z:.1f} cm, con cabeceo {phi:.0f}°."
    if "trama" in q or "servo" in q:
        return f"La última trama enviada fue {trama(ctrl.q, ctrl.pinza)}."
    if "orden" in q or "criterio" in q:
        return (f"El último orden fue por {NOMBRE_CRITERIO[ctrl.criterio].lower()} "
                f"{'ascendente' if ctrl.sentido == 'asc' else 'descendente'}.")
    if "ayuda" in q or "puedes" in q:
        return ("Puedo contarte el valor, el peso, la cantidad de monedas, la pose del "
                "brazo, la última trama de servos y el criterio de orden aplicado.")
    return ("No tengo ese dato todavía. Prueba con: cuánto vale el lote, cuánto pesa, "
            "dónde está el brazo o cuál fue el último orden.")


def tabla(vasos):
    filas = [{"Puesto": v.puesto.etiqueta if v.puesto else "-",
              "Denominación": f"${v.denominacion:,}".replace(",", "."),
              "Monedas": v.monedas,
              "Valor": v.valor,
              "Peso (g)": round(v.peso_g, 1)} for v in vasos]
    return pd.DataFrame(filas).sort_values("Puesto")


estado_inicial()
ctrl: Controlador = st.session_state.ctrl

# ----------------------------------------------------------------- barra lateral
with st.sidebar:
    st.header("Control")
    modo = st.radio("Modo", ["Simulación", "ESP32 por Wi-Fi"])
    host = st.text_input("IP del ESP32", "192.168.1.50",
                         disabled=(modo == "Simulación"))
    criterio = st.selectbox("Criterio de orden", list(CRITERIOS),
                            format_func=lambda k: NOMBRE_CRITERIO[k], index=2)
    sentido = st.radio("Sentido", ["asc", "desc"],
                       format_func=lambda s: "Ascendente" if s == "asc" else "Descendente",
                       horizontal=True)
    velocidad = st.slider("Velocidad", 0.5, 3.0, 1.0, 0.1)

    if st.button("Nuevo lote de vasos"):
        st.session_state.ctrl = Controlador(lote_aleatorio(), enlace=EnlaceNulo())
        st.session_state.registro = []
        st.rerun()

    ejecutar = st.button("Ordenar", type="primary")

# ----------------------------------------------------------------- encabezado
st.title("Brazo clasificador de vasos de monedas")
st.caption("Módulo 6 del Sistema de Logística de Monedas Inteligentes")

t = totales(ctrl.vasos)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Vasos", len(ctrl.vasos))
c2.metric("Monedas", t["monedas"])
c3.metric("Valor total", f"${t['valor']:,}".replace(",", "."))
c4.metric("Peso total", f"{t['peso_g']:.1f} g")

# ----------------------------------------------------------------- ejecución
if ejecutar:
    ctrl.velocidad = velocidad
    plan = planificar(ctrl.vasos, criterio, sentido)
    barra = st.progress(0.0, text="Planificando")
    if modo == "ESP32 por Wi-Fi":
        try:
            enlace = EnlaceHTTP(host)
            enlace.vasos([v.como_dict() for v in ctrl.vasos])
            respuesta = enlace.ordenar(criterio, sentido)
            st.success(f"Orden enviada al ESP32: {respuesta}")
        except Exception as err:                       # el robot puede estar apagado
            st.error(f"No hubo respuesta del ESP32 ({err}). Se corre en simulación.")
            modo = "Simulación"
    if modo == "Simulación":
        total = max(1, len(plan))
        def avance(_t, q, pinza):
            barra.progress(min(1.0, ctrl.paso / total),
                           text=f"Movimiento {ctrl.paso} de {total}")
        resumen = ctrl.ordenar(criterio, sentido, al_avanzar=avance)
        st.session_state.registro = resumen["movimientos"]
        barra.progress(1.0, text=f"Listo en {resumen['segundos']} s simulados")

# ----------------------------------------------------------------- contenido
izq, der = st.columns([3, 2])

with izq:
    st.subheader("Rack")
    rack = [v for v in ctrl.vasos if v.puesto and v.puesto.zona == "rack"]
    entrada = [v for v in ctrl.vasos if v.puesto and v.puesto.zona == "entrada"]
    st.dataframe(tabla(rack) if rack else tabla(entrada), use_container_width=True,
                 hide_index=True)
    if rack:
        df = tabla(rack).set_index("Puesto")
        st.bar_chart(df[["Valor"]] if criterio != "peso" else df[["Peso (g)"]])

with der:
    st.subheader("Ruta del brazo")
    if st.session_state.registro:
        for i, m in enumerate(st.session_state.registro, 1):
            st.write(f"{i}. {m}")
    else:
        st.info("Pulsa «Ordenar» para generar la secuencia de movimientos.")

    st.subheader("Estado del robot")
    x, y, z, phi = fk(ctrl.q)
    st.write(f"TCP: X {x:.2f} cm, Y {y:.2f} cm, Z {z:.2f} cm, cabeceo {phi:.1f}°")
    st.code(trama(ctrl.q, ctrl.pinza), language="text")

# ----------------------------------------------------------------- asistente
st.subheader("Asistente")
pregunta = st.chat_input("Pregunta algo sobre el lote o el robot")
if pregunta:
    st.chat_message("user").write(pregunta)
    st.chat_message("assistant").write(responder(pregunta, ctrl))
