from mysql.connector import Error


def crear_partido_db(conn, equipo_local, equipo_visitante, fecha, fase):
    cur = None
    try:
        cur = conn.cursor()
        query = """
            INSERT INTO partidos (equipo_local, equipo_visitante,fecha,fase)
            VALUES(%s,%s,%s,%s)
        """
        cur.execute(query, (equipo_local, equipo_visitante, fecha, fase))
        conn.commit()
        return cur.lastrowid
    finally:
        if cur:
            cur.close()


def buscar_partido_id_db(id, conn):
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
    finally:
        if cur:
            cur.close()


def reemplazar_partido_db(conn, id, equipo_local, equipo_visitante, fecha, fase):
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

    finally:
        if cur:
            cur.close()


def actualizar_db(id, cambios, conn):
    cur = None
    try:
        cur = conn.cursor()

        campos = ", ".join([f"{k} = %s" for k in cambios.keys()])
        valores = list(cambios.values())
        valores.append(id)

        query = f"""
            UPDATE partidos
            SET {campos}
            WHERE id = %s
        """

        cur.execute(query, valores)
        conn.commit()

        return cur.rowcount > 0

    finally:
        if cur:
            cur.close()


def eliminar_db(id, conn):
    cur = None
    try:
        cur = conn.cursor()

        query = "DELETE FROM partidos WHERE id = %s"
        cur.execute(query, (id,))
        conn.commit()

        return cur.rowcount > 0

    finally:
        if cur:
            cur.close()


def listar_partidos_db(conn, limit, offset, equipo=None, fecha=None, fase=None):
    cur = None
    try:
        cur = conn.cursor(dictionary=True)
        filtros = []
        params = []
        if equipo:
            filtros.append("(equipo_local=%s OR equipo_visitante=%s)")
            params.extend([equipo, equipo])
        if fecha:
            filtros.append("fecha=%s")
            params.append(fecha)
        if fase:
            filtros.append("fase=%s")
            params.append(fase)
        where = "WHERE " + " AND ".join(filtros) if filtros else ""
        query = f"SELECT * FROM partidos {where} LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cur.execute(query, params)
        partidos = cur.fetchall()
        return partidos
    finally:
        if cur:
            cur.close()


def contar_partidos_db(conn):
    cur = None
    try:
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT COUNT(*) as total FROM partidos")
        return cur.fetchone()["total"]

    finally:
        if cur:
            cur.close()
