def set_search_path(sender, **kwargs):
    conn = kwargs.get('connection')

    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("SET search_path=saleor")
