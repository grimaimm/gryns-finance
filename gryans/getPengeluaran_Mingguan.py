from datetime import datetime, timedelta

def pengeluaranMingguan(cursor):
    # Total Data Pengeluaran Minggu Lalu
    last_week_start = (datetime.now() - timedelta(days=datetime.now().weekday() + 7)).strftime('%Y-%m-%d')
    last_week_end = (datetime.now() - timedelta(days=datetime.now().weekday() + 1)).strftime('%Y-%m-%d')
    query_last_week = f"SELECT SUM(jumlah_pengeluaran) FROM pengeluaran WHERE tanggal_pengeluaran BETWEEN '{last_week_start}' AND '{last_week_end}'"
    cursor.execute(query_last_week)
    total_last_week = cursor.fetchone()[0] or 0
    last_week_formatted = f'Minggu {datetime.strptime(last_week_start, "%Y-%m-%d").strftime("%d %B %Y")} - {datetime.strptime(last_week_end, "%Y-%m-%d").strftime("%d %B %Y")}'

    # Total Data Pengeluaran Minggu Ini
    this_week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
    this_week_end = datetime.now().strftime('%Y-%m-%d')
    query_this_week = f"SELECT SUM(jumlah_pengeluaran) FROM pengeluaran WHERE tanggal_pengeluaran BETWEEN '{this_week_start}' AND '{this_week_end}'"
    cursor.execute(query_this_week)
    total_this_week = cursor.fetchone()[0] or 0
    this_week_formatted = f'Minggu {datetime.strptime(this_week_start, "%Y-%m-%d").strftime("%d %B %Y")} - {datetime.strptime(this_week_end, "%Y-%m-%d").strftime("%d %B %Y")}'

    return last_week_formatted, total_last_week, this_week_formatted, total_this_week