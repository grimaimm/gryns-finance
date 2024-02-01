from datetime import datetime, timedelta

def pengeluaranBulanan(cursor):
    # Total Data Pengeluaran Bulan Lalu
    last_month_start = (datetime.now() - timedelta(days=datetime.now().day + 30)).replace(day=1).strftime('%Y-%m-%d')
    last_month_end = (datetime.now() - timedelta(days=datetime.now().day)).strftime('%Y-%m-%d')
    query_last_month = f"SELECT SUM(jumlah_pengeluaran) FROM pengeluaran WHERE tanggal_pengeluaran BETWEEN '{last_month_start}' AND '{last_month_end}'"
    cursor.execute(query_last_month)
    total_last_month = cursor.fetchone()[0] or 0
    last_month_formatted = datetime.strptime(last_month_start, '%Y-%m-%d').strftime('%B %Y')

    # Total Data Pengeluaran Bulan Ini
    this_month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')
    this_month_end = datetime.now().strftime('%Y-%m-%d')
    query_this_month = f"SELECT SUM(jumlah_pengeluaran) FROM pengeluaran WHERE tanggal_pengeluaran BETWEEN '{this_month_start}' AND '{this_month_end}'"
    cursor.execute(query_this_month)
    total_this_month = cursor.fetchone()[0] or 0
    this_month_formatted = datetime.strptime(this_month_start, '%Y-%m-%d').strftime('%B %Y')

    return last_month_formatted, total_last_month, this_month_formatted, total_this_month