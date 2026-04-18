from flask import Blueprint, jsonify
from data.db import get_connection

ranking_bp = Blueprint("ranking", __name__)

@ranking_bp.route("/ranking")

from data.predicciones import predicciones
from data.partidos import partidos

def calcular_ranking():
    ranking = {}

    for pred in predicciones:

        # buscar partido
        partido = None
        for p in partidos:
            if p["id"] == pred["partido_id"]:
                partido = p
                break

        if not partido:
            continue

        # ignorar si no tiene resultado
        if partido["goles_local"] is None:
            continue

        puntos = 0

        # resultado exacto
        if (pred["goles_local"] == partido["goles_local"] and
            pred["goles_visitante"] == partido["goles_visitante"]):
            puntos = 3

        else:
            # comparar ganador
            def resultado(gl, gv):
                if gl > gv:
                    return "local"
                elif gl < gv:
                    return "visitante"
                else:
                    return "empate"

            if resultado(pred["goles_local"], pred["goles_visitante"]) == \
               resultado(partido["goles_local"], partido["goles_visitante"]):
                puntos = 1

        # sumar puntos al usuario
        usuario = pred["usuario_id"]

        if usuario not in ranking:
            ranking[usuario] = 0

        ranking[usuario] += puntos

    # convertir a lista ordenada
    resultado_final = []

    for usuario, puntos in ranking.items():
        resultado_final.append({
            "usuario_id": usuario,
            "puntos": puntos
        })

    resultado_final.sort(key=lambda x: x["puntos"], reverse=True)

    return resultado_final
