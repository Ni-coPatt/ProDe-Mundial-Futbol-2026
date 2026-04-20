from flask import Blueprint, request, jsonify

from data.db import get_connection

from database.queries import (
    crear_partido_db,
    listar_partidos_db,
    actualizar_partido_db,
    buscar_partido_db,
    actualizar_partido_parcial_db,
    eliminar_partido_db,
    contar_partidos_db,
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

    faltantes = validar_campos_obligatorios(data, ["equipo_local", "equipo_visitante", "fecha", "fase", "estadio", "ciudad"])

    if faltantes:
        return jsonify({"error": "Campos obligatorios inválidos", "campos": faltantes}), 400

    if not validar_fecha(data["fecha"]):
        return jsonify({"error": "Fecha inválida"}), 400

    if not validar_fase(data["fase"]):
        return jsonify({"error": "Fase inválida"}), 400

    conn = None
    try:
        conn = get_connection()

        nuevo_id = crear_partido_db(conn, data["equipo_local"], data["equipo_visitante"], data["fecha"], data["fase"], data["estadio"], data["ciudad"])

        return (
            jsonify(
                {
                    "id": nuevo_id,
                    "equipo_local": data["equipo_local"],
                    "equipo_visitante": data["equipo_visitante"],
                    "fecha": data["fecha"],
                    "fase": data["fase"],
                    "estadio": data["estadio"],
                    "ciudad": data["ciudad"],
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
        row = buscar_partido_db(conn, id)

        if row is None:
            return jsonify({"error": "Partido no encontrado"}), 404

        if not validar_fase(row["fase"]):
            return jsonify({"error": "Fase inválida"}), 400

   
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
            "estadio": row.get("estadio"),  # <-- AGREGADO
            "ciudad": row.get("ciudad"),    # <-- AGREGADO
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

    faltantes = validar_campos_obligatorios(data, ["equipo_local", "equipo_visitante", "fecha", "fase", "estadio", "ciudad"])

    if faltantes:
        return jsonify({"error": "Faltan campos obligatorios", "campos": faltantes}), 400

    if not validar_fecha(data["fecha"]):
        return jsonify({"error": "Fecha inválida (YYYY-MM-DD)"}), 400

    if not validar_fase(data["fase"]):
        return jsonify({"error": "Fase inválida"}), 400

    conn = None
    try:
        conn = get_connection()

        partido = buscar_partido_db(conn, id)
        if not partido:
            return jsonify({"error": "Partido no encontrado"}), 404

        remplazado = actualizar_partido_db(
            conn, id, data["equipo_local"], data["equipo_visitante"], data["fecha"], data["fase"], data["estadio"], data["ciudad"]
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

    campos_permitidos = ["equipo_local", "equipo_visitante", "fecha", "fase", "estadio", "ciudad"]
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

        partido = buscar_partido_db(conn, id)
        if not partido:
            return jsonify({"error": "Partido no encontrado"}), 404

        partido_actualizado = actualizar_partido_parcial_db(conn, id, cambios)

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

        partido = buscar_partido_db(conn, id)
        if not partido:
            return jsonify({"error": "Partido no encontrado"}), 404

        partido_eliminado = eliminar_partido_db(conn, id)

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

    conn = None
    cur = None
    
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        
        # Verificar que el partido existe
        cur.execute("SELECT id FROM partidos WHERE id = %s", (id,))
        partido = cur.fetchone()

        if not partido:
            return jsonify({"error": "Partido no encontrado"}), 404

        # Verificar si ya existe resultado
        cur.execute("SELECT goles_local, goles_visitante FROM resultados WHERE partido_id = %s", (id,))
        resultado_existente = cur.fetchone()

        if resultado_existente and (resultado_existente["goles_local"] is not None or resultado_existente["goles_visitante"] is not None):
            return jsonify({"error": "Resultado ya cargado"}), 400

        # Guardar resultado
        if resultado_existente:
            # UPDATE si ya existe registro
            cur.execute(
                """
                UPDATE resultados
                SET goles_local = %s, goles_visitante = %s
                WHERE partido_id = %s
                """,
                (goles_local, goles_visitante, id),
            )
        else:
            # INSERT si es nuevo
            cur.execute(
                """
                INSERT INTO resultados (partido_id, goles_local, goles_visitante)
                VALUES (%s, %s, %s)
                """,
                (id, goles_local, goles_visitante),
            )

        conn.commit()

        return "", 204

    except Exception as e:
        if conn:
            conn.rollback()
        print(e)
        return jsonify({"error": "Error interno del servidor"}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@partidos_bp.route("/<int:id>/prediccion", methods=["POST"])
def registrar_prediccion(id):
    conn = None
    cur = None
    try:
        data = request.get_json()
        
        # 1. Validaciones básicas
        if not data:
            return jsonify({"error": "Body vacío"}), 400
            
        if "usuario_id" not in data or "goles_local" not in data or "goles_visitante" not in data:
            return jsonify({"error": "Faltan datos obligatorios (usuario_id, goles_local, goles_visitante)"}), 400

        u_id = data["usuario_id"]
        g_local = data["goles_local"]
        g_vis = data["goles_visitante"]

        if g_local < 0 or g_vis < 0:
            return jsonify({"error": "Los goles no pueden ser negativos"}), 400

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # 2. Verificar que el partido existe
        cur.execute("SELECT id FROM partidos WHERE id = %s", (id,))
        if not cur.fetchone():
            return jsonify({"error": "El partido no existe"}), 404

        # 3. Verificar que el partido NO se haya jugado (si está en resultados, ya se jugó)
        cur.execute("SELECT id FROM resultados WHERE partido_id = %s", (id,))
        if cur.fetchone():
            return jsonify({"error": "El partido ya finalizó. No se aceptan predicciones."}), 400

        # 4. Verificar que el usuario NO haya predicho ya este partido
        cur.execute("SELECT predicciones_id FROM predicciones WHERE usuario_id = %s AND partido_id = %s", (u_id, id))
        if cur.fetchone():
            return jsonify({"error": "Este usuario ya registró una predicción para este partido"}), 400

        # 5. Insertar la predicción
        cur.execute(
            """
            INSERT INTO predicciones (usuario_id, partido_id, goles_local, goles_visitante)
            VALUES (%s, %s, %s, %s)
            """,
            (u_id, id, g_local, g_vis)
        )
        conn.commit()

        return jsonify({"mensaje": "Predicción registrada correctamente"}), 201

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()
