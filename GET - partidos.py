from flask import request, jsonify
from flask import Blueprint
from data.db import get_connection

bp = Blueprint("partidos", __name__)

@bp.route("/partidos", methods=["GET"])
def obtener_partido(id):
    conn = None
    cur = None

    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Body vacío"}), 400

        if "equipo_local" not in data or "equipo_visitante" not in data or "fecha" not in data or "faseparam" not in data:
            return jsonify({"error": "Faltan datos"}), 400

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        #falta para que seleccione por equipo, fecha y fase.
        cur.execute("SELECT * FROM partidos WHERE id = %s", (id))
        partido = cur.fetchone()

        if not partido:
            return jsonify({"error": "Partido no existe"}), 404

        #devolver el partido, falta la base de datos para saber el formato
        return jsonify({}),200

    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()