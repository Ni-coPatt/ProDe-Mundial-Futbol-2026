from flask import request, jsonify
from flask import Blueprint
from data.db import get_connection

bp = Blueprint("resultados", __name__)

@bp.route("/partidos/<int:id>/resultado", methods=["PUT"])
def cargar_resultado(id):
    conn = None
    cur = None

    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Body vacío"}), 400

        if "goles_local" not in data or "goles_visitante" not in data:
            return jsonify({"error": "Faltan datos"}), 400

        if data["goles_local"] < 0 or data["goles_visitante"] < 0:
            return jsonify({"error": "Goles inválidos"}), 400

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # verificar partido
        cur.execute("SELECT goles_local FROM partidos WHERE id = %s", (id,))
        partido = cur.fetchone()

        if not partido:
            return jsonify({"error": "Partido no encontrado"}), 404

        # verificar si ya tiene resultado
        if partido["goles_local"] is not None:
            return jsonify({"error": "Resultado ya cargado"}), 400

        # actualizar resultado
        cur.execute("""
            UPDATE partidos
            SET goles_local = %s, goles_visitante = %s
            WHERE id = %s
        """, (data["goles_local"], data["goles_visitante"], id))

        conn.commit()

        return jsonify({"mensaje": "Resultado cargado correctamente"}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()