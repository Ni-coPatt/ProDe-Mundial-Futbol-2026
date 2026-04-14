from flask import request, jsonify
from flask import Blueprint
from data.db import get_connection

partidos_bp = Blueprint("partidos", __name__)

@partidos_bp.route("/partidos/<int:id>", methods=["GET"])
def get_partido(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT 
                p.id,
                p.equipo_local,
                p.equipo_visitante,
                p.fecha,
                p.fase,
                r.goles_local,
                r.goles_visitante
            FROM partidos p
            LEFT JOIN resultados r ON p.id = r.partido_id
            WHERE p.id = %s
        """
        cursor.execute(query, (id,))
        row = cursor.fetchone()

        if not row:
            return jsonify({"error": "Partido no encontrado"}), 404

        response = {
            "id": row["id"],
            "equipo_local": row["equipo_local"],
            "equipo_visitante": row["equipo_visitante"],
            "fecha": row["fecha"].isoformat() if row["fecha"] else None,
            "fase": row["fase"],
        }

        if row["goles_local"] is not None and row["goles_visitante"] is not None:
            response["resultado"] = {
                "goles_local": row["goles_local"],
                "goles_visitante": row["goles_visitante"]
            }
        else:
            response["resultado"] = None

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": "Error al obtener el partido"}), 500

    finally:
        cursor.close()
        conn.close()

@partidos_bp.route("/partidos/<int:id>", methods=["DELETE"])
def delete_partido(id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Verificar existencia
        cursor.execute("SELECT id FROM partidos WHERE id = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Partido no encontrado"}), 404

        cursor.execute("DELETE FROM resultados WHERE partido_id = %s", (id,))

        cursor.execute("DELETE FROM partidos WHERE id = %s", (id,))

        conn.commit()

        return jsonify({"message": "Partido eliminado correctamente"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Error al eliminar el partido"}), 500

    finally:
        cursor.close()
        conn.close()