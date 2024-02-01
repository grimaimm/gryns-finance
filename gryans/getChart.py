from datetime import datetime, timedelta
from mysql import connector
from babel.numbers import format_currency

db = connector.connect(
    host     = "localhost",
    user     = "root",
    passwd   = "",
    database = "gryans_finance",
)

def get_monthly_data(year):
    monthly_data = []
    cursor = db.cursor(dictionary=True)  # Menggunakan dictionary cursor agar dapat mengakses hasil dengan nama kolom

    for month in range(1, 13):
        start_date = f"{year}-{month:02d}-01"
        end_date = (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=32)).replace(day=1).strftime('%Y-%m-%d')

        # Gantilah dengan query SQL yang sesuai untuk menghitung total pengeluaran dan pemasukan
        query = f"""
            SELECT 
                COALESCE(SUM(jumlah_pengeluaran), 0) AS total_pengeluaran,
                COALESCE(SUM(jumlah_pemasukan), 0) AS total_pemasukan
            FROM (
                SELECT jumlah_pengeluaran, 0 AS jumlah_pemasukan
                FROM pengeluaran
                WHERE tanggal_pengeluaran BETWEEN '{start_date}' AND '{end_date}'
                UNION ALL
                SELECT 0 AS jumlah_pengeluaran, jumlah_pemasukan
                FROM pemasukan
                WHERE tanggal_pemasukan BETWEEN '{start_date}' AND '{end_date}'
            ) AS combined_data
        """

        cursor.execute(query)
        result = cursor.fetchone()

        monthly_data.append({
            "month": month,
            "total_pengeluaran": result["total_pengeluaran"],
            "total_pemasukan": result["total_pemasukan"]
        })
    return monthly_data
