# ---------------------------------------------------------------
# >> Library
import os
import sqlite3
import locale
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

# ---------------------------------------------------------------
# >> Inisialisasi Flask
app = Flask(__name__)
date = datetime.now()
login_manager = LoginManager(app)
login_manager.login_view = "login"
app.secret_key = "your_secret_key"
app.config["DATABASE"] = "static/db/gryans_finance.db"

# ---------------------------------------------------------------
# >> Function Connect to Database
def connect_db():
    return sqlite3.connect("static/db/gryans_finance.db")


# ---------------------------------------------------------------
# >> Route Service Work PWA
@app.route("/static/js/service-work.js")
def serve_service_worker():
    return send_from_directory(
        os.path.join(app.root_path, "static", "js"), "service-worker.js"
    )


# ---------------------------------------------------------------
# Inisialisasi Flask-Login
class User(UserMixin):
    def __init__(self, id, username, password, fullname):
        self.id = id
        self.username = username
        self.password = password
        self.fullname = fullname


@login_manager.user_loader
def load_user(id_user):
    print("Loading user with ID:", id_user)
    connect = connect_db()
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM users WHERE id_user = ?", (id_user,))
    user_data = cursor.fetchone()
    cursor.close()
    if user_data:
        return User(user_data[0], user_data[2], user_data[3], user_data[1])
    return None


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
# >> Route Index
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        connect = connect_db()
        cursor = connect.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?", (username, password)
        )
        user = cursor.fetchone()
        connect.close()

        if user:
            user_obj = User(user[0], user[2], user[3], user[1])
            login_user(user_obj)  # Add this line to log in the user

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
# >> Function Get Monthly Data Pemasukan and Pengeluaran
def get_monthly_data(year):
    monthly_data = []
    connect = connect_db()
    cursor = connect.cursor()

    for month in range(1, 13):
        start_date = f"{year}-{month:02d}-01"
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
                WHERE tanggal_pengeluaran BETWEEN '{start_date}' AND '{end_date}'
                UNION ALL
                SELECT 0 AS jumlah_pengeluaran, jumlah_pemasukan
                FROM pemasukan
                WHERE tanggal_pemasukan BETWEEN '{start_date}' AND '{end_date}'
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
# >> Dashboard route
@app.route("/dashboard")
@login_required
def dashboard():
    user_info = userInfo()
    connect = connect_db()
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

    cursor.close()
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

    connect = connect_db()
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
            date_object = datetime.strptime(data["tanggal_pengeluaran"], "%Y-%m-%d")
            formatted_date = date_object.strftime("%A, %d %B %Y")
            data["tanggal_pengeluaran"] = formatted_date

        if "jumlah_pengeluaran" in data:
            formatted_currency = format_currency(
                data["jumlah_pengeluaran"], "IDR", locale="id_ID"
            )
            formatted_currency = formatted_currency.replace(",00", "")
            data["jumlah_pengeluaran"] = formatted_currency.replace(".", ".")

    cursor.close()
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

    connect = connect_db()
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
            date_object = datetime.strptime(data["tanggal_pemasukan"], "%Y-%m-%d")
            formatted_date = date_object.strftime("%A, %d %B %Y")
            data["tanggal_pemasukan"] = formatted_date

        if "jumlah_pemasukan" in data:
            formatted_currency = format_currency(
                data["jumlah_pemasukan"], "IDR", locale="id_ID"
            )
            formatted_currency = formatted_currency.replace(",00", "")
            data["jumlah_pemasukan"] = formatted_currency.replace(".", ".")

    cursor.close()
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
    connect = connect_db()
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
            ) VALUES (?, ?, ?, ?, ?, ?)
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

    cursor.close()
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
    connect = connect_db()
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
            ) VALUES (?, ?, ?, ?, ?)
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

    cursor.close()
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
    connect = connect_db()
    cursor = connect.cursor()
    cursor.execute(
        "SELECT * FROM pengeluaran WHERE id_pengeluaran = ?", (id_pengeluaran,)
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
                tanggal_pengeluaran = ?,
                deskripsi = ?,
                id_kategori = ?,
                jumlah_pengeluaran = ?,
                id_name = ?
            WHERE id_pengeluaran = ?;
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
    
    cursor.close()
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
    connect = connect_db()
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM pemasukan WHERE id_pemasukan = ?", (id_pemasukan,))
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
                tanggal_pemasukan = ?,
                deskripsi = ?,
                jumlah_pemasukan = ?,
                id_name = ?
            WHERE id_pemasukan = ?;
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
    
    cursor.close()
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
    connect = connect_db()
    cursor = connect.cursor()
    cursor.execute(
        "DELETE FROM pengeluaran WHERE id_pengeluaran = ?", (id_pengeluaran,)
    )
    connect.commit()
    cursor.close()
    return redirect(url_for("pengeluaran"))


# ---------------------------------------------------------------
# >> Hapus Pemasukan Route
@app.route("/pemasukan/delete/<id_pemasukan>", methods=["GET"])
@login_required
def hapusPemasukan(id_pemasukan):
    connect = connect_db()
    cursor = connect.cursor()
    cursor.execute("DELETE FROM pemasukan WHERE id_pemasukan = ?", (id_pemasukan))
    connect.commit()
    cursor.close()
    return redirect(url_for("pemasukan"))


# ---------------------------------------------------------------
# >> Keuangan Route
@app.route("/keuangan", methods=["GET"])
@login_required
def keuangan():
    locale.setlocale(locale.LC_TIME, "id_ID")
    page = request.args.get('page', 1, type=int)
    per_page = 50

    connect = connect_db()
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
            date_object = datetime.strptime(data["tanggal"], "%Y-%m-%d")
            formatted_date = date_object.strftime("%A, %d %B %Y")
            data["tanggal"] = formatted_date

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

    cursor.close()
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
    connect = connect_db()
    cursor = connect.cursor()

    cursor.execute("SELECT * FROM users WHERE id_user = ?", (session["id_user"],))
    profile = cursor.fetchone()

    cursor.close()
    return render_template("users/profile.html", profile=profile)


# ---------------------------------------------------------------
# >> Log Out Route
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


# ---------------------------------------------------------------
# >> Apps Running
if __name__ == "__main__":
    app.run()
