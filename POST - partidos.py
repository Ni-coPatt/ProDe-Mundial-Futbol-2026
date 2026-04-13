from flask import request, jsonify
from flask import Blueprint
from data.db import get_connection

bp = Blueprint("partidos", __name__)

@bp.route("/partidos", methods=["GET"])
def crear_partido(id):
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

        # falta insert, se necesita la base de datos
        # cur.execute("INSERT ", (id))
        # conn.commit()
            
        return jsonify({"mensaje": "Partido guardado"}),200

    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()