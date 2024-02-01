from datetime import datetime, timedelta

def pengeluaranHarian(cursor):
    # Total Data Pengeluaran Kemarin
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    query_yesterday = f"SELECT SUM(jumlah_pengeluaran) FROM pengeluaran WHERE tanggal_pengeluaran = '{yesterday}'"
    cursor.execute(query_yesterday)
    total_yesterday = cursor.fetchone()[0] or 0
    yesterday_formatted = datetime.strptime(yesterday, '%Y-%m-%d').strftime('%A, %d %B %Y')

    # Total Data Pengeluaran Hari ini
    today = datetime.now().strftime('%Y-%m-%d')
    query_today = f"SELECT SUM(jumlah_pengeluaran) FROM pengeluaran WHERE tanggal_pengeluaran = '{today}'"
    cursor.execute(query_today)
    total_today = cursor.fetchone()[0] or 0
    today_formatted = datetime.strptime(today, '%Y-%m-%d').strftime('%A, %d %B %Y')

    return yesterday_formatted, total_yesterday, today_formatted, total_today