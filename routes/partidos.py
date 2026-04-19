from flask import Blueprint, request, jsonify

from data.db import get_connection

from database.queries import (
    crear_partido_db,
    listar_partidos_db,
    reemplazar_partido_db,
    buscar_partido_id_db,
    actualizar_db,
    eliminar_db,
)

from utils.validations import (
    validar_fecha,
    validar_fase,
    validar_no_nulos,
    validar_paginado,
    validar_campos_obligatorios,
)

from utils.helpers import pagination_links

partidos_bp = Blueprint("partidos", __name__)


# endpoint 1(moya) lo cambie me mostraba solo por id
@partidos_bp.route("/", methods=["GET"])
def listar_partidos():
    limit = request.args.get("_limit", 10)
    offset = request.args.get("_offset", 0)
    equipo = request.args.get("equipo")
    fecha = request.args.get("fecha")
    fase = request.args.get("fase")

    paginado = validar_paginado(limit, offset)

    if not paginado:
        return jsonify({"error": "Paginado inválido"}), 400
    limit, offset = paginado
    if fecha and not validar_fecha(fecha):
        return jsonify({"error": "Formato de fecha inválido"}), 400
    if fase and not validar_fase(fase):
        return jsonify({"error": "Fase inválida"}), 400
    conn = None
    try:
        conn = get_connection()
        partidos, total = listar_partidos_db(conn, limit, offset, equipo, fecha, fase)
        campos = [("equipo", equipo), ("fecha", fecha), ("fase", fase)]
        extra_params = {}
        for key, value in campos:
            if value:
                extra_params[key] = value

        links = pagination_links(request.base_url, limit, offset, total, extra_params=extra_params)
        if not partidos:
            return "", 204
        return jsonify({"partidos": partidos, "total": total, "_links": links}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500
    finally:
        if conn:
            conn.close()


# endpoint 2(moya) usaba el methods get
@partidos_bp.route("/", methods=["POST"])
def crear_partido():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Body vacío"}), 400

    faltantes = validar_campos_obligatorios(data, ["equipo_local", "equipo_visitante", "fecha", "fase"])

    if faltantes:
        return jsonify({"error": "Campos obligatorios inválidos", "campos": faltantes}), 400

    if not validar_fecha(data["fecha"]):
        return jsonify({"error": "Fecha inválida"}), 400

    if not validar_fase(data["fase"]):
        return jsonify({"error": "Fase inválida"}), 400

    conn = None
    try:
        conn = get_connection()

        nuevo_id = crear_partido_db(conn, data["equipo_local"], data["equipo_visitante"], data["fecha"], data["fase"])

        return (
            jsonify(
                {
                    "id": nuevo_id,
                    "equipo_local": data["equipo_local"],
                    "equipo_visitante": data["equipo_visitante"],
                    "fecha": data["fecha"],
                    "fase": data["fase"],
                }
            ),
            201,
        )

    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
        if conn:
            conn.close()


# endpoint 3
@partidos_bp.route("/<int:id>", methods=["GET"])
def obtener_partido(id: int):
    if id <= 0:
        return jsonify({"error": "ID inválido"}), 400

    conn = None
    cursor = None

    try:
        conn = get_connection()
        row = buscar_partido_id_db(id, conn)

        if row is None:
            return jsonify({"error": "Partido no encontrado"}), 404

        if not validar_fecha(row["fecha"]):
            return jsonify({"error": "Fecha inválida (YYYY-MM-DD)"}), 400

        if not validar_fase(row["fase"]):
            return jsonify({"error": "Fase inválida"}), 400

        # 👉 conversión simple de fecha (sin isoformat para evitar errores)
        fecha = row["fecha"]
        fecha = str(fecha) if fecha else None

        resultado = None
        if row["goles_local"] is not None and row["goles_visitante"] is not None:
            resultado = {
                "local": row["goles_local"],
                "visitante": row["goles_visitante"],
            }

        response = {
            "id": row["id"],
            "equipo_local": row["equipo_local"],
            "equipo_visitante": row["equipo_visitante"],
            "fecha": fecha,
            "fase": row["fase"],
            "resultado": resultado,
        }

        return jsonify(response), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# endpoint 4
@partidos_bp.route("/<int:id>", methods=["PUT"])
def reemplazar_partido(id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "Body vacío"}), 400

    faltantes = validar_campos_obligatorios(data, ["equipo_local", "equipo_visitante", "fecha", "fase"])

    if faltantes:
        return jsonify({"error": "Faltan campos obligatorios", "campos": faltantes}), 400

    if not validar_fecha(data["fecha"]):
        return jsonify({"error": "Fecha inválida (YYYY-MM-DD)"}), 400

    if not validar_fase(data["fase"]):
        return jsonify({"error": "Fase inválida"}), 400

    conn = None
    try:
        conn = get_connection()

        partido = buscar_partido_id_db(id, conn)
        if not partido:
            return jsonify({"error": "Partido no encontrado"}), 404

        remplazado = reemplazar_partido_db(
            conn, id, data["equipo_local"], data["equipo_visitante"], data["fecha"], data["fase"]
        )

        if remplazado:
            return "", 204

        return jsonify({"error": "No se pudo actualizar"}), 500

    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
        if conn:
            conn.close()


# endpoint 5
@partidos_bp.route("/<int:id>", methods=["PATCH"])
def actualizar_partido(id):

    data = request.get_json()

    if not data:
        return jsonify({"error": "body vacio"}), 400

    campos_permitidos = ["equipo_local", "equipo_visitante", "fecha", "fase"]
    cambios = {campo: data.get(campo) for campo in campos_permitidos if campo in data}

    if not cambios:
        return jsonify({"error": "Al menos un campo debe estar presente"}), 400

    nulos = validar_no_nulos(cambios, cambios.keys())
    if nulos:
        return jsonify({"error": "Campos inválidos", "campos": nulos}), 400

    if "fecha" in cambios and not validar_fecha(cambios["fecha"]):
        return jsonify({"error": "Formato de fecha inválido. Use YYYY-MM-DD"}), 400

    if "fase" in cambios and not validar_fase(cambios["fase"]):
        return jsonify({"error": "Fase inválida"}), 400

    conn = None
    try:
        conn = get_connection()

        partido = buscar_partido_id_db(id, conn)
        if not partido:
            return jsonify({"error": "Partido no encontrado"}), 404

        partido_actualizado = actualizar_db(id, cambios, conn)

        if partido_actualizado:
            return "", 204
        else:
            return jsonify({"error": "Error interno del servidor"}), 500

    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
        if conn:
            conn.close()


# endpoint 6
@partidos_bp.route("/<int:id>", methods=["DELETE"])
def eliminar_partido(id):
    conn = None
    try:
        conn = get_connection()

        partido = buscar_partido_id_db(id, conn)
        if not partido:
            return jsonify({"error": "Partido no encontrado"}), 404

        partido_eliminado = eliminar_db(id, conn)

        if partido_eliminado:
            return "", 204
        else:
            return jsonify({"error": "Error interno del servidor"}), 500

    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
        if conn:
            conn.close()


# endpoint 7 luna
@partidos_bp.route("/<int:id>/resultado", methods=["PUT"])
def cargar_resultado(id):
    conn = None
    cur = None

    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Body vacío"}), 400

        if "local" not in data or "visitante" not in data:
            return jsonify({"error": "Faltan datos"}), 400

        try:
            goles_local = int(data["local"])
            goles_visitante = int(data["visitante"])
        except (ValueError, TypeError):
            return jsonify({"error": "Goles deben ser enteros"}), 400

        if goles_local < 0 or goles_visitante < 0:
            return jsonify({"error": "Goles inválidos"}), 400

        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT goles_local, goles_visitante FROM partidos WHERE id = %s", (id,))

        partido = cur.fetchone()

        if not partido:
            return jsonify({"error": "Partido no encontrado"}), 404

        if partido["goles_local"] is not None or partido["goles_visitante"] is not None:
            return jsonify({"error": "Resultado ya cargado"}), 400

        cur.execute(
            """
            UPDATE partidos
            SET goles_local = %s, goles_visitante = %s
            WHERE id = %s
            """,
            (goles_local, goles_visitante, id),
        )

        conn.commit()

        return "", 204

    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
