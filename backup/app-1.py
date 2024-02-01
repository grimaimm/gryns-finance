
# >> Library
import os
import pyodbc
import sqlite3
import locale
import mysql.connector
from mysql.connector import errorcode
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    g,
)
from flask import send_from_directory
from flask_login import (
    LoginManager,
    login_user,
    current_user,
    login_required,
    logout_user,
    UserMixin,
    login_manager,
    user_loaded_from_request,
)
from flask import send_from_directory, send_file
from babel.numbers import format_currency
from datetime import datetime, timedelta
from math import ceil

# ---------------------------------------------------------------
# >> My Module
from gryans.getPengeluaran_Harian import pengeluaranHarian
from gryans.getPengeluaran_Bulanan import pengeluaranBulanan
from gryans.getPemasukan_Bulanan import pemasukanBulanan
from gryans.getAll_Transaksi import keseluruhanTransaksi
from gryans.getAdmin_Transaksi import totalPengeluaranAdmin
from gryans.getAdmin_Transaksi import totalPemasukanAdmin

app = Flask(__name__)
date = datetime.now()
login_manager = LoginManager(app)
login_manager.login_view = "login"
app.secret_key = "your_secret_key"


# Fungsi untuk menghubungkan ke database
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="",
            database="gryans_finance"
        )
        
        if connection.is_connected():
            print("====================================")
            print("== BERHASIL TERHUBUNG KE DATABASE ==")
            print("====================================")
            return connection
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    
@app.before_request
def before_request():
    g.db = connect_to_database()
    
@app.route('/static/js/manifest.json')
def serve_manifest():
    return send_from_directory(
        os.path.join(app.root_path, "static", "js"), "manifest.json", mimetype='application/manifest+json'
    )

@app.route("/static/js/service-worker.js")
def serve_service_worker():
    return send_from_directory(
        os.path.join(app.root_path, "static", "js"), "service-worker.js"
    )

# ---------------------------------------------------------------
# Inisialisasi Flask-Login
@login_manager.user_loader
def load_user(id_user):
    connect = connect_to_database()
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM users WHERE id_user = %s", (id_user,))
    user_data = cursor.fetchone()
    if user_data:
        return User(user_data[0], user_data[2], user_data[3], user_data[1])
    return None


class User(UserMixin):
    def __init__(self, id, username, password, fullname):
        self.id = id
        self.username = username
        self.password = password
        self.fullname = fullname


# ---------------------------------------------------------------
# Function Get User Info
def userInfo():
    userInfo = {
        "id": current_user.id,
        "username": current_user.username,
        "fullname": current_user.fullname,
    }
    return userInfo


# ---------------------------------------------------------------
# >> Function Get Monthly Data Pemasukan and Pengeluaran
def get_monthly_data(year):
    monthly_data = []
    connect = connect_to_database()
    cursor = connect.cursor()

    for month in range(1, 13):
        start_date = f"{year:04d}-{month:02d}-01"
        end_date = (
            (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=32))
            .replace(day=1)
            .strftime("%Y-%m-%d")
        )

        query = f"""
            SELECT 
                COALESCE(SUM(jumlah_pengeluaran), 0) AS total_pengeluaran,
                COALESCE(SUM(jumlah_pemasukan), 0) AS total_pemasukan
            FROM (
                SELECT jumlah_pengeluaran, 0 AS jumlah_pemasukan
                FROM pengeluaran
                WHERE MONTH(tanggal_pengeluaran) = {month} AND YEAR(tanggal_pengeluaran) = {year}
                UNION ALL
                SELECT 0 AS jumlah_pengeluaran, jumlah_pemasukan
                FROM pemasukan
                WHERE MONTH(tanggal_pemasukan) = {month} AND YEAR(tanggal_pemasukan) = {year}
            ) AS combined_data
        """

        cursor.execute(query)
        result = cursor.fetchone()

        monthly_data.append(
            {
                "month": month,
                "total_pengeluaran": result[0],
                "total_pemasukan": result[1],
            }
        )

    return monthly_data



# ---------------------------------------------------------------
# >> Chart Route
@app.route("/monthly_data/<int:year>")
def monthly_data(year):
    monthly_data = get_monthly_data(year)
    return jsonify(monthly_data)
# ---------------------------------------------------------------
# >> Route Index / Log In
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        connect = connect_to_database()
        cursor = connect.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND password = %s", (username, password)
        )
        user = cursor.fetchone()
        connect.close()

        if user:
            user_obj = User(user[0], user[2], user[3], user[1])
            login_user(user_obj)

            session["loggedin"] = True
            session["id_user"] = user[0]
            session["username"] = user[2]
            session["fullname"] = user[1]

            return redirect(url_for("dashboard"))
        else:
            error_message = "Invalid username or password. Please try again."
            return render_template("users/login.html", error_message=error_message)

    return render_template("users/login.html")

# ---------------------------------------------------------------
# >> Dashboard route
@app.route("/dashboard")
@login_required
def dashboard():
    user_info = userInfo()
    connect = connect_to_database()
    cursor = connect.cursor()
    yesterday, total_yesterday, today, total_today = pengeluaranHarian(cursor)
    last_month, total_last_month, this_month, total_this_month = pengeluaranBulanan(
        cursor
    )
    (
        last_month_income,
        total_last_month_income,
        this_month_income,
        total_this_month_income,
    ) = pemasukanBulanan(cursor)
    total_statistics = keseluruhanTransaksi(cursor)

    admin_names = ["Aim", "Dhian"]
    total_statistics_admins = []

    for admin_name in admin_names:
        total_pengeluaran = totalPengeluaranAdmin(cursor, admin_name)
        total_pemasukan = totalPemasukanAdmin(cursor, admin_name)

        if total_pengeluaran is not None and total_pemasukan is not None:
            admin_stats = {
                "input_nama": admin_name,
                "total_pengeluaran": total_pengeluaran,
                "total_pemasukan": total_pemasukan,
            }
            total_statistics_admins.append(admin_stats)

    connect.close()
    return render_template(
        "dashboard/dashboard.html",
        user_info=user_info,
        yesterday=yesterday,
        total_yesterday=total_yesterday,
        today=today,
        total_today=total_today,
        last_month=last_month,
        total_last_month=total_last_month,
        this_month=this_month,
        total_this_month=total_this_month,
        last_month_income=last_month_income,
        total_last_month_income=total_last_month_income,
        this_month_income=this_month_income,
        total_this_month_income=total_this_month_income,
        total_statistics=total_statistics,
        total_statistics_admins=total_statistics_admins,
    )

# ---------------------------------------------------------------
# >> Pengeluaran Route
@app.route("/pengeluaran", methods=["GET"])
@login_required
def pengeluaran():
    locale.setlocale(locale.LC_TIME, "id_ID")
    page = request.args.get('page', 1, type=int)
    per_page = 50

    connect = connect_to_database()
    cursor = connect.cursor()

    cursor.execute(
        """
        SELECT 
            ROW_NUMBER() OVER (ORDER BY tanggal_pengeluaran ASC) AS nomor,
            pengeluaran.id_pengeluaran,
            pengeluaran.id_user,
            pengeluaran.tanggal_pengeluaran,
            pengeluaran.deskripsi,
            kategori.nama_kategori,
            pengeluaran.jumlah_pengeluaran,
            name.input_nama
        FROM pengeluaran
        INNER JOIN kategori ON pengeluaran.id_kategori = kategori.id_kategori
        INNER JOIN name ON pengeluaran.id_name = name.id_name
        ORDER BY 
            pengeluaran.tanggal_pengeluaran ASC
        """
    )

    all_rows = cursor.fetchall()
    total_rows = len(all_rows)
    total_pages = (total_rows + per_page - 1) // per_page

    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_rows = all_rows[start_index:end_index]

    column_names = [desc[0] for desc in cursor.description]
    pengeluaran = [dict(zip(column_names, row)) for row in paginated_rows]

    for data in pengeluaran:
        if "tanggal_pengeluaran" in data:
            data["tanggal_pengeluaran"] = data["tanggal_pengeluaran"].strftime(
                "%A, %d %B %Y"
            )

        if "jumlah_pengeluaran" in data:
            formatted_currency = format_currency(
                data["jumlah_pengeluaran"], "IDR", locale="id_ID"
            )
            formatted_currency = formatted_currency.replace(",00", "")
            data["jumlah_pengeluaran"] = formatted_currency.replace(".", ".")

    connect.close()
    return render_template(
        "pengeluaran/pengeluaran.html",
        pengeluaran=pengeluaran,
        pagination={"page": page, "per_page": per_page, "total_pages": total_pages}
    )

# ---------------------------------------------------------------
# >> Pemasukan Route
@app.route("/pemasukan", methods=["GET"])
@login_required
def pemasukan():
    locale.setlocale(locale.LC_TIME, "id_ID")
    page = request.args.get('page', 1, type=int)
    per_page = 50

    connect = connect_to_database()
    cursor = connect.cursor()

    cursor.execute(
        """
        SELECT 
            ROW_NUMBER() OVER (ORDER BY tanggal_pemasukan ASC) AS nomor,
            pemasukan.id_pemasukan,
            pemasukan.id_user,
            pemasukan.tanggal_pemasukan,
            pemasukan.deskripsi,
            pemasukan.jumlah_pemasukan,
            name.input_nama
        FROM pemasukan
        INNER JOIN name ON pemasukan.id_name = name.id_name
        ORDER BY 
            pemasukan.tanggal_pemasukan ASC
        """
    )

    all_rows = cursor.fetchall()
    total_rows = len(all_rows)
    total_pages = (total_rows + per_page - 1) // per_page

    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_rows = all_rows[start_index:end_index]

    column_names = [desc[0] for desc in cursor.description]
    pemasukan = [dict(zip(column_names, row)) for row in paginated_rows]

    for data in pemasukan:
        if "tanggal_pemasukan" in data:
            data["tanggal_pemasukan"] = data["tanggal_pemasukan"].strftime(
                "%A, %d %B %Y"
            )

        if "jumlah_pemasukan" in data:
            formatted_currency = format_currency(
                data["jumlah_pemasukan"], "IDR", locale="id_ID"
            )
            formatted_currency = formatted_currency.replace(",00", "")
            data["jumlah_pemasukan"] = formatted_currency.replace(".", ".")

    connect.close()
    return render_template(
        "pemasukan/pemasukan.html",
        pemasukan=pemasukan,
        pagination={"page": page, "per_page": per_page, "total_pages": total_pages}
    )

# ---------------------------------------------------------------
# >> Tambah Pengeluaran Route
@app.route("/pengeluaran/tambah", methods=["GET", "POST"])
@login_required
def tambahPengeluaran():
    connect = connect_to_database()
    cursor = connect.cursor()

    cursor.execute("SELECT * FROM kategori")
    kategori_data = cursor.fetchall()

    cursor.execute("SELECT * FROM name")
    name_data = cursor.fetchall()

    if request.method == "POST":
        tanggal_pengeluaran = request.form["tanggal_pengeluaran"]
        deskripsi = request.form["deskripsi"]
        kategori_id = request.form["kategori"]
        jumlah_pengeluaran = request.form["jumlah_pengeluaran"]
        name_id = request.form["name"]

        cursor.execute(
            """
            INSERT INTO pengeluaran (
                id_user, 
                tanggal_pengeluaran, 
                deskripsi, 
                id_kategori, 
                jumlah_pengeluaran, 
                id_name
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                session["id_user"],
                tanggal_pengeluaran,
                deskripsi,
                kategori_id,
                jumlah_pengeluaran,
                name_id,
            ),
        )

        connect.commit()
        return redirect(url_for("pengeluaran"))
    else:
        tanggal_pengeluaran = datetime.now().strftime("%Y-%m-%d")

    connect.close()
    return render_template(
        "pengeluaran/tambah-pengeluaran.html",
        kategori_data=kategori_data,
        name_data=name_data,
        tanggal_pengeluaran=tanggal_pengeluaran,
    )

# ---------------------------------------------------------------
# >> Tambah Pemasukan Route
@app.route("/pemasukan/tambah", methods=["GET", "POST"])
@login_required
def tambahPemasukan():
    connect = connect_to_database()
    cursor = connect.cursor()

    cursor.execute("SELECT * FROM name")
    name_data = cursor.fetchall()

    if request.method == "POST":
        tanggal_pemasukan = request.form["tanggal_pemasukan"]
        deskripsi = request.form["deskripsi"]
        jumlah_pemasukan = request.form["jumlah_pemasukan"]
        name_id = request.form["name"]

        cursor.execute(
            """
            INSERT INTO pemasukan (
                id_user, 
                tanggal_pemasukan, 
                deskripsi, 
                jumlah_pemasukan, 
                id_name
            ) VALUES (%s, %s, %s, %s, %s)
            """,
            (
                session["id_user"],
                tanggal_pemasukan,
                deskripsi,
                jumlah_pemasukan,
                name_id,
            ),
        )

        connect.commit()
        return redirect(url_for("pemasukan"))
    else:
        tanggal_pemasukan = datetime.now().strftime("%Y-%m-%d")

    connect.close()
    return render_template(
        "pemasukan/tambah-pemasukan.html",
        name_data=name_data,
        tanggal_pemasukan=tanggal_pemasukan,
    )

# ---------------------------------------------------------------
# >> Edit Pengeluaran Route
@app.route("/pengeluaran/edit/<id_pengeluaran>", methods=["GET", "POST"])
@login_required
def editPengeluaran(id_pengeluaran):
    connect = connect_to_database()
    cursor = connect.cursor()
    cursor.execute(
        "SELECT * FROM pengeluaran WHERE id_pengeluaran = %s", (id_pengeluaran,)
    )
    pengeluaran_data = cursor.fetchone()
    cursor.execute("SELECT * FROM kategori")
    kategori_data = cursor.fetchall()
    cursor.execute("SELECT * FROM name")
    name_data = cursor.fetchall()

    if request.method == "POST":
        tanggal_pengeluaran = request.form["tanggal_pengeluaran"]
        deskripsi = request.form["deskripsi"]
        kategori_id = request.form["kategori"]
        jumlah_pengeluaran = request.form["jumlah_pengeluaran"]
        name_id = request.form["name"]

        cursor.execute(
            """
            UPDATE pengeluaran SET
                tanggal_pengeluaran = %s,
                deskripsi = %s,
                id_kategori = %s,
                jumlah_pengeluaran = %s,
                id_name = %s
            WHERE id_pengeluaran = %s
            """,
            (
                tanggal_pengeluaran,
                deskripsi,
                kategori_id,
                jumlah_pengeluaran,
                name_id,
                id_pengeluaran,
            ),
        )

        connect.commit()
        print(
            f"Updated pengeluaran_data: {tanggal_pengeluaran}, {deskripsi}, {kategori_id}, {jumlah_pengeluaran}, {name_id}"
        )
        return redirect(url_for("pengeluaran"))
    
    connect.close()
    return render_template(
        "pengeluaran/edit-pengeluaran.html",
        kategori_data=kategori_data,
        name_data=name_data,
        pengeluaran_data=pengeluaran_data,
    )


# ---------------------------------------------------------------
# >> Edit Pemasukan Route
@app.route("/pemasukan/edit/<id_pemasukan>", methods=["GET", "POST"])
@login_required
def editPemasukan(id_pemasukan):
    connect = connect_to_database()
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM pemasukan WHERE id_pemasukan = %s", (id_pemasukan,))
    pemasukan_data = cursor.fetchone()
    cursor.execute("SELECT * FROM name")
    name_data = cursor.fetchall()

    if request.method == "POST":
        tanggal_pemasukan = request.form["tanggal_pemasukan"]
        deskripsi = request.form["deskripsi"]
        jumlah_pemasukan = request.form["jumlah_pemasukan"]
        name_id = request.form["name"]

        cursor.execute(
            """
            UPDATE pemasukan SET
                tanggal_pemasukan = %s,
                deskripsi = %s,
                jumlah_pemasukan = %s,
                id_name = %s
            WHERE id_pemasukan = %s
            """,
            (
                tanggal_pemasukan,
                deskripsi,
                jumlah_pemasukan,
                name_id,
                id_pemasukan,
            ),
        )

        connect.commit()
        print(
            f"Updated pemasukan_data: {tanggal_pemasukan}, {deskripsi}, {jumlah_pemasukan}, {name_id}"
        )
        return redirect(url_for("pemasukan"))
    
    connect.close()
    return render_template(
        "pemasukan/edit-pemasukan.html",
        name_data=name_data,
        pemasukan_data=pemasukan_data,
    )


# ---------------------------------------------------------------
# >> Hapus Pengeluaran Route
@app.route("/pengeluaran/delete/<id_pengeluaran>", methods=["GET"])
@login_required
def hapusPengeluaran(id_pengeluaran):
    connect = connect_to_database()
    cursor = connect.cursor()
    cursor.execute(
        "DELETE FROM pengeluaran WHERE id_pengeluaran = %s", (id_pengeluaran,)
    )
    connect.commit()
    connect.close()
    return redirect(url_for("pengeluaran"))


# ---------------------------------------------------------------
# >> Hapus Pemasukan Route
@app.route("/pemasukan/delete/<id_pemasukan>", methods=["GET"])
@login_required
def hapusPemasukan(id_pemasukan):
    connect = connect_to_database()
    cursor = connect.cursor()
    cursor.execute(
        "DELETE FROM pemasukan WHERE id_pemasukan = %s", (id_pemasukan,)
    )
    connect.commit()
    connect.close()
    return redirect(url_for("pemasukan"))

# ---------------------------------------------------------------
# >> Keuangan Route
@app.route("/keuangan", methods=["GET"])
@login_required
def keuangan():
    locale.setlocale(locale.LC_TIME, "id_ID")
    page = request.args.get('page', 1, type=int)
    per_page = 50

    connect = connect_to_database()
    cursor = connect.cursor()

    cursor.execute(
        """
        SELECT
            ROW_NUMBER() OVER (ORDER BY tanggal) AS nomor,
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
        """
    )

    all_rows = cursor.fetchall()
    total_rows = len(all_rows)
    total_pages = (total_rows + per_page - 1) // per_page

    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_rows = all_rows[start_index:end_index]

    column_names = [desc[0] for desc in cursor.description]
    keuangan = [dict(zip(column_names, row)) for row in paginated_rows]

    for data in keuangan:
        if "tanggal" in data:
            data["tanggal"] = data["tanggal"].strftime(
                "%A, %d %B %Y"
            )

        if "total_pemasukan" in data:
            formatted_currency = format_currency(
                data["total_pemasukan"], "IDR", locale="id_ID"
            )
            formatted_currency = formatted_currency.replace(",00", "")
            data["total_pemasukan"] = formatted_currency.replace(".", ".")

        if "total_pengeluaran" in data:
            formatted_currency = format_currency(
                data["total_pengeluaran"], "IDR", locale="id_ID"
            )
            formatted_currency = formatted_currency.replace(",00", "")
            data["total_pengeluaran"] = formatted_currency.replace(".", ".")

    connect.close()
    return render_template(
        "keuangan/keuangan.html",
        keuangan=keuangan,
        pagination={"page": page, "per_page": per_page, "total_pages": total_pages}
    )

# ---------------------------------------------------------------
# >> Profile Route
@app.route("/profile")
@login_required
def profil():
    connect = connect_to_database()
    cursor = connect.cursor()

    cursor.execute("SELECT * FROM users WHERE id_user = %s", (session["id_user"],))
    profile = cursor.fetchone()

    connect.close()
    return render_template("users/profile.html", profile=profile)


# ---------------------------------------------------------------
# >> Log Out Route
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

# ---------------------------------------------------------------
# Apps Running
if __name__ == "__main__":
    app.run(debug=True)
