def pagination_links(base_url, limit, offset, total_count, extra_params=None):
    if limit <= 0:
        raise ValueError("limit debe ser mayor a 0")

    extra_params = extra_params or {}
    params_base = {**extra_params, "limit": limit}

    def make_query(params):
        # construcción manual del query string
        parts = []
        for k, v in params.items():
            if v is not None:
                parts.append(f"{k}={v}")
        return "&".join(parts)

    def make_url(new_offset):
        params = {**params_base, "offset": new_offset}
        query = make_query(params)
        return f"{base_url}?{query}"

    # calcular last
    if total_count > 0:
        last_offset = ((total_count - 1) // limit) * limit
    else:
        last_offset = 0

    links = {
        "first": make_url(0),
        "last": make_url(last_offset),
    }

    # prev → solo si no estás en la primera página
    if offset > 0:
        prev_offset = max(0, offset - limit)
        links["prev"] = make_url(prev_offset)

    # next → solo si hay más resultados
    if offset + limit < total_count:
        next_offset = offset + limit
        links["next"] = make_url(next_offset)

    return links
