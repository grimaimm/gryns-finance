from datetime import datetime, timedelta

def keseluruhanTransaksi(cursor):
    cursor.execute('''
        SELECT
            tanggal,
            COALESCE(SUM(jumlah_pengeluaran), 0) AS total_pengeluaran,
            COALESCE(SUM(jumlah_pemasukan), 0) AS total_pemasukan
        FROM (
            SELECT
                tanggal_pengeluaran AS tanggal,
                jumlah_pengeluaran,
                0 AS jumlah_pemasukan
            FROM pengeluaran
            UNION ALL
            SELECT
                tanggal_pemasukan AS tanggal,
                0 AS jumlah_pengeluaran,
                jumlah_pemasukan
            FROM pemasukan
        ) AS combined_data
        GROUP BY tanggal;
    ''')
    result = cursor.fetchall()
    return result


# def keseluruhanTransaksi(cursor):
#     cursor.execute('''
#         SELECT
#             ROW_NUMBER() OVER (ORDER BY tanggal) AS nomor,
#             'Total' AS tanggal,
#             COALESCE(SUM(jumlah_pengeluaran), 0) AS total_pengeluaran,
#             COALESCE(SUM(jumlah_pemasukan), 0) AS total_pemasukan
#         FROM (
#             SELECT
#                 tanggal_pengeluaran AS tanggal,
#                 jumlah_pengeluaran,
#                 0 AS jumlah_pemasukan
#             FROM pengeluaran
#             UNION ALL
#             SELECT
#                 tanggal_pemasukan AS tanggal,
#                 0 AS jumlah_pengeluaran,
#                 jumlah_pemasukan
#             FROM pemasukan
#         ) AS combined_data;
#     ''')

#     column_names = [desc[0] for desc in cursor.description]
#     result = [dict(zip(column_names, row)) for row in cursor.fetchall()]

#     return result[0] if result else None