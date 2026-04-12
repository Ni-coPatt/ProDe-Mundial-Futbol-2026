from flask import Blueprint, request, jsonify
from datetime import datetime

partidos_bp = Blueprint("partidos", __name__, url_prefix="/partidos")
# ejemplos para el uso de postman
partidos_db = {
    1: {"id": 1, "equipo_local": "Argentina", "equipo_visitante": "Francia", "fecha": "2026-06-15", "fase": "grupos"},
    2: {"id": 2, "equipo_local": "Brasil", "equipo_visitante": "Uruguay", "fecha": "2026-06-16", "fase": "grupos"},
}

FASES_VALIDAS = {"grupos", "dieciseisavos", "octavos", "cuartos", "semis", "final"}


# funciones que pienso agregar en archivos aparte "validations.py"
def validar_fecha(fecha_str):
    try:
        datetime.strptime(fecha_str, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


def validar_fase(fase):

    return str(fase).lower() in FASES_VALIDAS


@partidos_bp.route("/<int:id>", methods=["PATCH"])
def actualizar_partidos(id):
    try:
        data = request.get_json()
        # ver si el campo es valido para cambiar
        datos_validos = ["equipo_local", "equipo_visitante", "fecha", "fase"]
        datos_presentes = [dato for dato in datos_validos if dato in data]

        if not datos_presentes:
            return jsonify({"error": "Al menos un campo debe estar presente"}), 400

        # Validar valores de los campos presentes
        for campo in datos_presentes:
            if data[campo] is None:
                return jsonify({"error": f"El campo '{campo}' no puede ser nulo"}), 400

            if campo == "fecha" and not validar_fecha(data[campo]):
                return jsonify({"error": "Formato de fecha inválido. Use YYYY-MM-DD"}), 400

            if campo == "fase" and not validar_fase(data[campo]):
                return jsonify({"error": f"Fase inválida. Use: {', '.join(sorted(FASES_VALIDAS))}"}), 400

        # ver si existe el partido
        if id not in partidos_db:
            return jsonify({"error": "Partido no encontrado"}), 404

        # actualizo partido
        partido = partidos_db[id]
        for campo in datos_presentes:
            partido[campo] = data[campo]

        return "", 204

    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500


@partidos_bp.route("/<int:id>", methods=["DELETE"])
def eleminiar_partido(id):
    try:
        if id not in partidos_db:
            return jsonify({"error": "partido no encontrado"}), 404
        # elimino el partido
        partidos_db.pop(id)
        return "", 204
    except Exception:
        return jsonify({"error": "Error interno del servidor"}), 500
