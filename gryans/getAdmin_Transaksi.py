
from datetime import datetime, timedelta
from flask import session

def totalPengeluaranAdmin(cursor, admin_name):
    if admin_name:
        query = '''
            SELECT
                COALESCE(SUM(pengeluaran.jumlah_pengeluaran), 0) AS total_pengeluaran
            FROM
                name
            LEFT JOIN pengeluaran ON name.id_name = pengeluaran.id_name
            WHERE
                name.input_nama = ?
        '''

        cursor.execute(query, (admin_name,))
        result = cursor.fetchone()

        if result:
            return result[0] or 0
    return None


def totalPemasukanAdmin(cursor, admin_name):
    if admin_name:
        query = '''
            SELECT
                COALESCE(SUM(pemasukan.jumlah_pemasukan), 0) AS total_pemasukan
            FROM
                name
            LEFT JOIN pemasukan ON name.id_name = pemasukan.id_name
            WHERE
                name.input_nama = ?
        '''

        cursor.execute(query, (admin_name,))
        result = cursor.fetchone()

        if result:
            return result[0] or 0
    return None
