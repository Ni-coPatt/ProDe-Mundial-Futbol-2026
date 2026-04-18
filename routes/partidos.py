from flask import Blueprint, request, jsonify

from db.connection import get_connection

from db.queries import (
    crear_partido_db,
    listar_partidos,
    reemplazar_partido_db,
    buscar_partido_por_id,
    actualizar_partido,
    eliminar_partido,
)

from utils.validations import (
    validar_fecha,
    validar_fase,
    validar_no_nulos,
    validar_paginado,
    validar_campos_obligatorios,
)

from utils.helpers import build_pagination_links

partidos_bp = Blueprint("partidos", __name__, url_prefix="/partidos")


# endpoint 1(moya) lo cambie me mostraba solo por id
@partidos_bp.route("/", methods=["GET"])
def listar_partidos():
    conn = None
    cur = None

    try:
        limit = request.args.get("limit", 10)
        offset = request.args.get("offset", 0)

        if not str(limit).isdigit() or not str(offset).isdigit():
            return jsonify({"error": "Paginado inválido"}), 400

        limit = int(limit)
        offset = int(offset)

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT * FROM partidos LIMIT %s OFFSET %s", (limit, offset))
        partidos = cur.fetchall()

        cur.execute("SELECT COUNT(*) as total FROM partidos")
        total = cur.fetchone()["total"]

        links = build_pagination_links(request.base_url, limit, offset, total)

        return jsonify({"partidos": partidos, "total": total, "_links": links}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
        if cur:
            cur.close()
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
def get_partido(id):
    if id <= 0:
        return jsonify({"error": "ID inválido"}), 400

    conn = None

    try:
        conn = get_connection()
        row = buscar_partido_por_id(id, conn)

        if not row:
            return jsonify({"error": "Partido no encontrado"}), 404
        
        if not validar_fecha(row["fecha"]):
            return jsonify({"error": "Fecha inválida (YYYY-MM-DD)"}), 400

        if not validar_fase(row["fase"]):
            return jsonify({"error": "Fase inválida"}), 400

        response = {
            "id": row["id"],
            "equipo_local": row["equipo_local"],
            "equipo_visitante": row["equipo_visitante"],
            "fecha": row["fecha"],
            "fase": row["fase"],
        }

        if row["goles_local"] is not None and row["goles_visitante"] is not None:
            response["resultado"] = {"goles_local": row["goles_local"], "goles_visitante": row["goles_visitante"]}
        else:
            response["resultado"] = None

        return jsonify(response), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
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

        partido = buscar_partido_por_id(id, conn)
        if not partido:
            return jsonify({"error": "Partido no encontrado"}), 404

        ok = reemplazar_partido_db(
            conn, id, data["equipo_local"], data["equipo_visitante"], data["fecha"], data["fase"]
        )

        if ok:
            return (
                jsonify(
                    {
                        "id": id,
                        "equipo_local": data["equipo_local"],
                        "equipo_visitante": data["equipo_visitante"],
                        "fecha": data["fecha"],
                        "fase": data["fase"],
                    }
                ),
                200,
            )

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
        return jsonify({"error": "Body vaico"}), 400

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

        partido = buscar_partido_por_id(id, conn)
        if not partido:
            return jsonify({"error": "Partido no encontrado"}), 404

        ok = actualizar_partido(id, cambios, conn)

        if ok:
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

        partido = buscar_partido_por_id(id, conn)
        if not partido:
            return jsonify({"error": "Partido no encontrado"}), 404

        ok = eliminar_partido(id, conn)

        if ok:
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

        if "goles_local" not in data or "goles_visitante" not in data:
            return jsonify({"error": "Faltan datos"}), 400

        try:
            goles_local = int(data["goles_local"])
            goles_visitante = int(data["goles_visitante"])
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

        return jsonify({"mensaje": "Resultado cargado correctamente"}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
