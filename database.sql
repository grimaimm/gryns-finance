mysql -p root -u

gryans_finance

-- Tabel User
CREATE TABLE users (
    id_user INT AUTO_INCREMENT PRIMARY KEY,
    fullname VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

INSERT INTO users (fullname, username, password) VALUES
    ('Aimmm & Dhiannn', 'aimdhian', 'AERO1906');

-- Tabel Name
CREATE TABLE name (
    id_name INT AUTO_INCREMENT PRIMARY KEY,
    input_nama VARCHAR(255) NOT NULL
);

INSERT INTO name (input_nama) VALUES
    ('Aim'),
    ('Dhian');

-- Tabel Kategori
CREATE TABLE kategori (
    id_kategori INT AUTO_INCREMENT PRIMARY KEY,
    nama_kategori VARCHAR(255) NOT NULL
);

INSERT INTO kategori (nama_kategori) VALUES
    ('Jajan'),
    ('Rokok'),
    ('Transportasi'),
    ('Rumah Tangga'),
    ('Bahan Dapur'),
    ('Lainnya');

-- Tabel Pengeluaran
CREATE TABLE pengeluaran (
    id_pengeluaran INT AUTO_INCREMENT PRIMARY KEY,
    id_user INT,
    tanggal_pengeluaran DATE,
    deskripsi VARCHAR(255) NOT NULL,
    id_kategori INT,
    jumlah_pengeluaran DECIMAL(10) NOT NULL,
    id_name INT,
    FOREIGN KEY (id_user) REFERENCES users(id_user),
    FOREIGN KEY (id_kategori) REFERENCES kategori(id_kategori),
    FOREIGN KEY (id_name) REFERENCES name(id_name)
);

-- Tabel Pemasukan
CREATE TABLE pemasukan (
    id_pemasukan INT AUTO_INCREMENT PRIMARY KEY,
    id_user INT,
    tanggal_pemasukan DATE,
    deskripsi VARCHAR(255) NOT NULL,
    jumlah_pemasukan DECIMAL(10) NOT NULL,
    id_name INT,
    FOREIGN KEY (id_user) REFERENCES users(id_user),
    FOREIGN KEY (id_name) REFERENCES name(id_name)
);

-- Tabel Keuangan
CREATE TABLE keuangan (
    id_keuangan INT AUTO_INCREMENT PRIMARY KEY,
    id_user INT,
    tanggal_transaksi DATE,
    deskripsi VARCHAR(255) NOT NULL,
    total_pemasukan DECIMAL(10) NOT NULL,
    total_pengeluaran DECIMAL(10) NOT NULL,
    FOREIGN KEY (id_user) REFERENCES users(id_user)
);


    cursor.execute('SET @count = 0;')
    cursor.execute('UPDATE pemasukan SET id_pemasukan = @count:= @count + 1;')
    cursor.execute('ALTER TABLE pemasukan AUTO_INCREMENT = 1;')