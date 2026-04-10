from flask import request, jsonify
from flask import Blueprint
from data.db import get_connection

bp = Blueprint("resultados", __name__)

@bp.route("/partidos/<int:id>/prediccion", methods=["POST"])
def crear_prediccion(id):
    conn = None
    cur = None

    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Body vacío"}), 400

        if "usuario_id" not in data or "goles_local" not in data or "goles_visitante" not in data:
            return jsonify({"error": "Faltan datos"}), 400

        if data["goles_local"] < 0 or data["goles_visitante"] < 0:
            return jsonify({"error": "Goles inválidos"}), 400

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # verificar partido
        cur.execute("SELECT goles_local FROM partidos WHERE id = %s", (id,))
        partido = cur.fetchone()

        if not partido:
            return jsonify({"error": "Partido no existe"}), 404

        # verificar si ya fue jugado
        if partido["goles_local"] is not None:
            return jsonify({"error": "El partido ya fue jugado"}), 400

        # verificar predicción duplicada
        cur.execute("""
            SELECT id FROM predicciones
            WHERE usuario_id = %s AND partido_id = %s
        """, (data["usuario_id"], id))

        existe = cur.fetchone()

        if existe:
            return jsonify({"error": "Ya existe una predicción para este usuario"}), 400

        # insertar predicción
        cur.execute("""
            INSERT INTO predicciones (usuario_id, partido_id, goles_local, goles_visitante)
            VALUES (%s, %s, %s, %s)
        """, (data["usuario_id"], id, data["goles_local"], data["goles_visitante"]))

        conn.commit()

        return jsonify({"mensaje": "Predicción registrada correctamente"}), 201

    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()