"""
Funciones de acceso a base de datos para partidos.
"""


def crear_partido_db(conn, equipo_local, equipo_visitante, fecha, fase):
    """Crea un nuevo partido en la BD."""
    if not equipo_local or not equipo_visitante or not fecha or not fase:
        raise ValueError("Todos los campos son obligatorios")
    
    cur = None
    try:
        cur = conn.cursor()
        query = """
            INSERT INTO partidos (equipo_local, equipo_visitante, fecha, fase)
            VALUES (%s, %s, %s, %s)
        """
        cur.execute(query, (equipo_local, equipo_visitante, fecha, fase))
        conn.commit()
        return cur.lastrowid
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error creando partido: {e}")
    finally:
        if cur:
            cur.close()


def buscar_partido_db(conn, id):
    """Obtiene un partido por ID con sus goles."""
    if id <= 0:
        raise ValueError("ID debe ser positivo")
    
    cur = None
    try:
        cur = conn.cursor(dictionary=True)
        query = """
            SELECT p.*, r.goles_local, r.goles_visitante 
            FROM partidos p
            LEFT JOIN resultados r ON p.id = r.partido_id
            WHERE p.id = %s
        """
        cur.execute(query, (id,))
        return cur.fetchone()
    except Exception as e:
        raise Exception(f"Error buscando partido: {e}")
    finally:
        if cur:
            cur.close()


def actualizar_partido_db(conn, id, equipo_local, equipo_visitante, fecha, fase):
    """Reemplaza un partido completo (PUT)."""
    if id <= 0:
        raise ValueError("ID debe ser positivo")
    if not equipo_local or not equipo_visitante or not fecha or not fase:
        raise ValueError("Todos los campos son obligatorios")
    
    cur = None
    try:
        cur = conn.cursor()
        query = """
            UPDATE partidos
            SET equipo_local = %s,
                equipo_visitante = %s,
                fecha = %s,
                fase = %s
            WHERE id = %s
        """
        cur.execute(query, (equipo_local, equipo_visitante, fecha, fase, id))
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error actualizando partido: {e}")
    finally:
        if cur:
            cur.close()


def actualizar_partido_parcial_db(conn, id, cambios):
    """Actualiza parcialmente un partido (PATCH)."""
    if id <= 0:
        raise ValueError("ID debe ser positivo")
    if not cambios:
        raise ValueError("Debe enviar al menos un campo a actualizar")
    
    # Validar que solo permite ciertos campos
    campos_permitidos = {"equipo_local", "equipo_visitante", "fecha", "fase"}
    for campo in cambios.keys():
        if campo not in campos_permitidos:
            raise ValueError(f"Campo no permitido: {campo}")
    
    cur = None
    try:
        cur = conn.cursor()
        campos = ", ".join([f"{k} = %s" for k in cambios.keys()])
        valores = list(cambios.values())
        valores.append(id)
        
        query = f"UPDATE partidos SET {campos} WHERE id = %s"
        cur.execute(query, valores)
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error actualizando partido: {e}")
    finally:
        if cur:
            cur.close()


def eliminar_partido_db(conn, id):
    """Elimina un partido."""
    if id <= 0:
        raise ValueError("ID debe ser positivo")
    
    cur = None
    try:
        cur = conn.cursor()
        query = "DELETE FROM partidos WHERE id = %s"
        cur.execute(query, (id,))
        conn.commit()
        return cur.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error eliminando partido: {e}")
    finally:
        if cur:
            cur.close()


def listar_partidos_db(conn, limit, offset, equipo=None, fecha=None, fase=None):
    """Lista partidos con filtros opcionales y paginación."""
    if limit <= 0 or offset < 0:
        raise ValueError("Limit debe ser > 0 y offset >= 0")
    
    cur = None
    try:
        cur = conn.cursor(dictionary=True)
        filtros = []
        params = []
        
        if equipo:
            filtros.append("(equipo_local = %s OR equipo_visitante = %s)")
            params.extend([equipo, equipo])
        if fecha:
            filtros.append("fecha = %s")
            params.append(fecha)
        if fase:
            filtros.append("fase = %s")
            params.append(fase)
        
        where = "WHERE " + " AND ".join(filtros) if filtros else ""
        query = f"SELECT * FROM partidos {where} LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cur.execute(query, params)
        return cur.fetchall()
    except Exception as e:
        raise Exception(f"Error listando partidos: {e}")
    finally:
        if cur:
            cur.close()


def contar_partidos_db(conn):
    """Cuenta el total de partidos."""
    cur = None
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT COUNT(*) as total FROM partidos")
        resultado = cur.fetchone()
        return resultado["total"] if resultado else 0
    except Exception as e:
        raise Exception(f"Error contando partidos: {e}")
    finally:
        if cur:
            cur.close()
