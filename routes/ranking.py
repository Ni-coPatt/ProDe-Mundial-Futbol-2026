from flask import Blueprint, jsonify, request
from data.db import get_connection
from utils.helpers import pagination_links
from utils.validations import validar_paginado

ranking_bp = Blueprint("ranking", __name__)

@ranking_bp.route("/")
def calcular_ranking():
    # 1. Validar parámetros de paginación
    limit_str = request.args.get("_limit", 10)
    offset_str = request.args.get("_offset", 0)
    
    paginado = validar_paginado(limit_str, offset_str)
    if not paginado:
        return jsonify({"error": "Paginado inválido"}), 400
    
    limit, offset = paginado

    conn = get_connection()
    cur = None
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM resultados")
        partidos = cur.fetchall()
        
        cur.execute("SELECT * FROM predicciones")
        predicciones = cur.fetchall()
    except Exception as e:
        return jsonify({"error": f"Error buscando datos: {e}"}), 500
    finally:
        if cur: cur.close()
        if conn: conn.close()

    # 2. Lógica de cálculo de puntos
    ranking = {}

    for pred in predicciones:
        partido = next((p for p in partidos if p["partido_id"] == pred["partido_id"]), None)
        if not partido or partido["goles_local"] is None:
            continue

        puntos = 0
        if (pred["goles_local"] == partido["goles_local"] and pred["goles_visitante"] == partido["goles_visitante"]):
            puntos = 3
        else:
            def determinar_ganador(gl, gv):
                if gl > gv: return "local"
                elif gl < gv: return "visitante"
                else: return "empate"

            if determinar_ganador(pred["goles_local"], pred["goles_visitante"]) == \
               determinar_ganador(partido["goles_local"], partido["goles_visitante"]):
                puntos = 1

        usuario = pred["usuario_id"]
        ranking[usuario] = ranking.get(usuario, 0) + puntos

    # 3. Convertir a lista y ordenar
    resultado_final = [{"usuario_id": u, "puntos": p} for u, p in ranking.items()]
    resultado_final.sort(key=lambda x: x["puntos"], reverse=True)

    # 4. Aplicar paginación a la lista
    total_count = len(resultado_final)
    paginated_items = resultado_final[offset : offset + limit]

    # 5. Generar los enlaces HATEOAS con tu helper
    links = pagination_links(request.base_url, limit, offset, total_count)

    return jsonify({
        "ranking": paginated_items,
        "_links": links
    }), 200
