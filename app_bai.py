import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import altair as alt

DB_NAME = 'database_bai.db'

# Daftar pertanyaan ditaruh di luar biar bisa diakses Pasien & Admin
DAFTAR_PERTANYAAN = [
    "Mati rasa / terasa gatal", "Merasa panas", "Kaki bergoyang-goyang", 
    "Tidak bisa relaks / tidak bisa santai", "Takut hal buruk terjadi", "Pusing", 
    "Jantung berdenyut cepat", "Sempoyongan / serasa mau jatuh", "Merasa ngeri", 
    "Gelisah / gugup", "Merasa tercekik", "Tangan gemetaran", "Menggigil", 
    "Takut hilang kendali", "Kesulitan bernafas", "Takut mati", "Ketakutan", 
    "Sakit perut", "Serasa mau pingsan / berkunang-kunang", "Muka jadi kemerah-merahan", 
    "Keringat panas / keringat dingin"
]

# 1. KONFIGURASI CSS (Tampilan UI)
def injeksi_css_kustom():
    st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} 
    
    /* Background abu-abu kebiruan */
    .stApp { background-color: #F0F4F8; } 
    
    /* STYLING KUESIONER BAI (Calm & Clean Card UI) */
    [data-testid="stRadio"] {
        background-color: #ffffff; 
        padding: 30px 40px; 
        border-radius: 16px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.03); 
        border-top: 5px solid #457B9D; 
        border-left: 1px solid #E2E8F0;
        border-right: 1px solid #E2E8F0;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 30px; 
    }
    
    /* Font pertanyaan yang diperjelas dengan warna abu-abu gelap */
    [data-testid="stRadio"] label {
        font-size: 1.1rem !important;
        font-weight: 600;
        color: #2D3748;
        margin-bottom: 15px;
    }
    
    /* Styling Kartu Dashboard Admin */
    [data-testid="stMetric"] {
        background-color: #ffffff; border: 1px solid #E1E8ED; padding: 15px 20px;
        border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.04);
        border-top: 5px solid #2A9D8F; 
    }
    
    [data-testid="stTextInput"] div[data-baseweb="input"], 
    [data-testid="stNumberInput"] div[data-baseweb="input"], 
    [data-testid="stSelectbox"] div[data-baseweb="select"] {
        background-color: #ffffff; border-radius: 10px; border: 1px solid #CBD5E1; transition: all 0.3s;
    }
    
    /* Tombol Utama warna Teal */
    .stButton>button {
        background-color: #2A9D8F; color: white !important; border-radius: 10px; border: none;
        font-weight: bold; padding: 15px 20px; transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #21867A; transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(42, 157, 143, 0.25); color: white !important;
    }
    .stButton>button p { color: white !important; }
    </style>
    """, unsafe_allow_html=True)


# 2. FUNGSI DATABASE (SQLite)
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Tambah 21 kolom q1 sampai q21 untuk nyimpen skor tiap pertanyaan
    c.execute('''CREATE TABLE IF NOT EXISTS riwayat (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama TEXT, status TEXT, umur INTEGER, jenis_kelamin TEXT,
                    pekerjaan TEXT, pendidikan TEXT, tanggal TEXT,
                    skor_bai INTEGER, tingkat_cemas TEXT,
                    q1 INTEGER, q2 INTEGER, q3 INTEGER, q4 INTEGER, q5 INTEGER,
                    q6 INTEGER, q7 INTEGER, q8 INTEGER, q9 INTEGER, q10 INTEGER,
                    q11 INTEGER, q12 INTEGER, q13 INTEGER, q14 INTEGER, q15 INTEGER,
                    q16 INTEGER, q17 INTEGER, q18 INTEGER, q19 INTEGER, q20 INTEGER, q21 INTEGER
                )''')
    conn.commit()
    conn.close()

def simpan_data(nama, status, umur, jk, pekerjaan, pendidikan, skor, tingkat, list_jawaban):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Query disiapin nampung 31 value sekaligus
    query = '''INSERT INTO riwayat 
               (nama, status, umur, jenis_kelamin, pekerjaan, pendidikan, tanggal, skor_bai, tingkat_cemas,
                q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, q21) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    
    # Gabungin data diri + list 21 jawaban jadi satu tuple utuh
    data_tuple = (nama, status, umur, jk, pekerjaan, pendidikan, tanggal, skor, tingkat) + tuple(list_jawaban)
    
    c.execute(query, data_tuple)
    conn.commit()
    conn.close()

def hapus_data_pasien(id_pasien):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM riwayat WHERE id = ?', (id_pasien,))
    conn.commit()
    conn.close()

def hapus_semua_data():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM riwayat')
    c.execute('DELETE FROM sqlite_sequence WHERE name="riwayat"')
    conn.commit()
    conn.close()


# 3. LOGIKA ATURAN BAI & SOLUSI EMPATIK
def hitung_tingkatan_bai(skor):
    if skor <= 21: return 'Ringan'
    elif skor <= 35: return 'Sedang'
    else: return 'Berat'

def dapatkan_solusi(tingkat):
    if tingkat == 'Ringan':
        return "Halo! Dari hasil ini, tingkat kecemasanmu masih dalam batas yang wajar dan sangat normal, kok. Wajar banget kalau kadang kita merasa sedikit cemas menghadapi hari-hari, tapi sungguh, tidak ada yang perlu dikhawatirkan secara berlebihan. Tetap jaga pola makan, rutinkan olahraga ringan, dan pastikan istirahatmu cukup ya biar pikiranmu terus fresh. Kamu sudah menjalani hari dengan sangat baik!"
    elif tingkat == 'Sedang':
        return "Halo... Akhir-akhir ini rasanya agak lebih melelahkan dan mengganggu dari biasanya ya? Hasilmu menunjukkan kecemasan di tahap sedang, yang berarti tubuh dan pikiranmu mulai butuh perhatian ekstra. Tarik napas pelan-pelan... Jangan paksakan diri memendam semuanya sendirian. Yuk, luangkan waktu sejenak dari rutinitas yang bikin penat, atau ceritakan perasaanmu ke orang terdekat. Kamu sangat layak untuk istirahat sejenak."
    else:
        return "Halo... Aku tahu apa yang kamu rasakan akhir-akhir ini pasti sangat berat dan menguras energi. Mengalami kecemasan di tahap ini bukanlah hal yang mudah untuk dilewati sendirian, dan itu sama sekali bukan kelemahanmu. Tolong jangan ragu untuk mencari bantuan profesional ya. Segera jadwalkan sesi dengan psikolog atau layanan konseling terdekat. Meminta bantuan adalah langkah paling berani yang bisa kamu lakukan untuk dirimu sendiri saat ini. Kamu berharga."


# 4. ANTARMUKA STREAMLIT (Sistem Role-Based)
st.set_page_config(page_title="Deteksi Kecemasan (BAI)", layout="wide")
injeksi_css_kustom()
init_db()

peran = st.sidebar.selectbox("Masuk Sebagai:", ["Pasien", "Admin Psikolog"])


# HALAMAN PASIEN
if peran == "Pasien":
    st.title("Deteksi Dini Kecemasan")
    st.markdown("Instrumen diadaptasi dari **Beck Anxiety Inventory (BAI)**.")
    
    st.subheader("Data Diri")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: 
        nama = st.text_input("Nama Lengkap")
    with col2: 
        status = st.selectbox("Status", ["Belum Menikah", "Menikah", "Cerai Hidup", "Cerai Mati"])
    with col3: 
        umur = st.number_input("Umur", min_value=10, max_value=80, value=20)
    with col4: 
        jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        
    col5, col6 = st.columns(2)
    with col5:
        opsi_pekerjaan = st.selectbox("Pekerjaan", ["Mahasiswa/Pelajar", "Karyawan Swasta", "Wiraswasta", "PNS/BUMN", "Belum/Tidak Bekerja", "Lainnya (Isi Manual)"])
        if opsi_pekerjaan == "Lainnya (Isi Manual)":
            pekerjaan = st.text_input("Masukkan Pekerjaan Anda:")
        else:
            pekerjaan = opsi_pekerjaan
            
    with col6:
        opsi_pendidikan = st.selectbox("Pendidikan Terakhir", ["SMA / SMK", "Diploma (D1-D4)", "Sarjana (S1)", "Magister (S2)", "Doktor (S3)", "Lainnya (Isi Manual)"])
        if opsi_pendidikan == "Lainnya (Isi Manual)":
            pendidikan = st.text_input("Masukkan Pendidikan Terakhir Anda:")
        else:
            pendidikan = opsi_pendidikan

    st.markdown("---")
    
    st.subheader("Kuesioner Gejala")
    st.info("💡 **Instruksi:** Baca secara cermat dan pilih satu pernyataan (di tiap kelompok) yang paling menggambarkan kerisauan Anda selama sebulan terakhir, termasuk hari ini.")
    
    opsi = {
        "Tidak ada": 0, 
        "Ringan, tidak begitu merisaukan": 1, 
        "Sedang, tidak nyaman sewaktu-waktu": 2, 
        "Parah, begitu merisaukan sekali": 3
    }
    
    jawaban_user = []
    for i, pertanyaan in enumerate(DAFTAR_PERTANYAAN):
        jawaban = st.radio(f"{i+1}. {pertanyaan}", list(opsi.keys()), key=f"q_{i}", width="stretch")
        jawaban_user.append(opsi[jawaban])

    st.markdown("---")

    if st.button("Lihat Hasil", type="primary"):
        if nama.strip() == "":
            st.warning("Mohon isi nama terlebih dahulu ya!")
        elif pekerjaan.strip() == "":
            st.warning("Mohon isi pekerjaan Anda terlebih dahulu!")
        elif pendidikan.strip() == "":
            st.warning("Mohon isi pendidikan terakhir Anda terlebih dahulu!")
        else:
            skor_total = sum(jawaban_user)
            tingkat = hitung_tingkatan_bai(skor_total)
            solusi_empatik = dapatkan_solusi(tingkat)
            
            # Panggil fungsi simpan data beserta list jawabannya
            simpan_data(nama, status, umur, jk, pekerjaan, pendidikan, skor_total, tingkat, jawaban_user)
            
            st.markdown("### Hasil")
            st.metric("Tingkat Kecemasan Anda", tingkat)
            st.success(solusi_empatik)
            st.caption("⚠️ *Disclaimer: Hasil ini merupakan deteksi awal berdasarkan kuesioner mandiri dan belum 100% akurat. Untuk diagnosis medis yang pasti, harap berkonsultasi langsung dengan psikolog atau psikiater profesional.*")


# HALAMAN ADMIN PSIKOLOG

elif peran == "Admin Psikolog":
    st.sidebar.markdown("---")
    password = st.sidebar.text_input("Masukkan Password Admin", type="password")
    
    if password == "pakar123":
        st.title("📊 Dashboard Riwayat Deteksi")
        st.markdown("---")
                
        # 1. FITUR IMPORT CSV 
        st.subheader("📥 Import Data Pasien dari CSV")
        st.markdown("<small>Gunakan fitur ini untuk memasukkan kembali data hasil ekspor (.csv) saat presentasi.</small>", unsafe_allow_html=True)
        
        file_csv = st.file_uploader("Upload File CSV Riwayat Pasien:", type=["csv"], label_visibility="collapsed")
        
        if file_csv is not None:
            if st.button("Proses Import Data", type="primary"):
                try:
                    df_import = pd.read_csv(file_csv)
                    # Syarat kolom sekarang nambah q1 sampai q21
                    kolom_wajib = ['nama', 'status', 'umur', 'jenis_kelamin', 'pekerjaan', 'pendidikan', 'tanggal', 'skor_bai', 'tingkat_cemas'] + [f'q{i}' for i in range(1, 22)]
                    
                    if all(col in df_import.columns for col in kolom_wajib):
                        df_bersih = df_import[kolom_wajib]
                        conn = sqlite3.connect(DB_NAME)
                        df_bersih.to_sql('riwayat', conn, if_exists='append', index=False)
                        conn.close()
                        st.success(f"Hebat! Berhasil meng-import {len(df_bersih)} data pasien ke database!")
                    else:
                        st.error("Format kolom CSV tidak sesuai! Pastikan file CSV tersebut hasil ekspor dari versi aplikasi terbaru ini.")
                except Exception as e:
                    st.error(f"Gagal memproses berkas CSV: {e}")
                    
        st.markdown("---")
        
        # 2. BACA DATABASE
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT * FROM riwayat", conn)
        conn.close()
        
        # 3. TAMPILAN DASHBOARD UTAMA
        if not df.empty:
            st.subheader("Ringkasan Keseluruhan")
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Total Responden", f"{len(df)} Orang")
            kpi2.metric("Rata-rata Skor BAI", round(df['skor_bai'].mean(), 1))
            modus_tingkat = df['tingkat_cemas'].mode()[0]
            kpi3.metric("Kategori Terbanyak", modus_tingkat)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.subheader("Grafik Distribusi Tingkatan Kecemasan")
            chart_data = df['tingkat_cemas'].value_counts().reset_index()
            chart_data.columns = ['Tingkat', 'Jumlah']
            
            grafik = alt.Chart(chart_data).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
                x=alt.X('Tingkat', sort=['Ringan', 'Sedang', 'Berat'], title="Tingkat Kecemasan"),
                y=alt.Y('Jumlah', title="Jumlah Responden"),
                color=alt.Color('Tingkat', scale=alt.Scale(
                    domain=['Ringan', 'Sedang', 'Berat'],
                    range=['#2ecc71', '#f1c40f', '#e74c3c']
                ), legend=None),
                tooltip=['Tingkat', 'Jumlah']
            ).properties(height=350)
            
            st.altair_chart(grafik, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("Tabel Rekap Pasien")
            kolom_tampil = ['id', 'nama', 'status', 'umur', 'jenis_kelamin', 'pekerjaan' ,'pendidikan','tanggal', 'skor_bai', 'tingkat_cemas']
            st.dataframe(df[kolom_tampil], use_container_width=True)

            # FITUR BARU: ANALISIS DETAIL JAWABAN PASIEN
            st.markdown("---")
            st.subheader("🔍 Analisis Detail per Pasien")
            st.markdown("Pilih pasien untuk melihat detail intensitas gejala yang mereka rasakan.")
            
            # Bikin dropdown buat milih nama pasien
            opsi_pasien_detail = [f"{row['id']} - {row['nama']} (Skor: {row['skor_bai']})" for index, row in df.iterrows()]
            pilihan_detail = st.selectbox("Pilih Pasien:", opsi_pasien_detail)
            
            if pilihan_detail:
                # Ambil ID dari pilihan dropdown
                id_terpilih = int(pilihan_detail.split(" - ")[0])
                data_pasien = df[df['id'] == id_terpilih].iloc[0]
                
                terjemahan_opsi = {
                    0: "🟢 Tidak ada",
                    1: "🟡 Ringan",
                    2: "🟠 Sedang",
                    3: "🔴 Parah"
                }
                
                # Tabel rincian
                rincian_jawaban = []
                for i, pertanyaan in enumerate(DAFTAR_PERTANYAAN):
                    skor_soal = data_pasien[f'q{i+1}']
                    rincian_jawaban.append({
                        "No": i + 1,
                        "Gejala (BAI)": pertanyaan,
                        "Intensitas Dirasakan": terjemahan_opsi[skor_soal]
                    })
                
                df_rincian = pd.DataFrame(rincian_jawaban)
                
                with st.expander(f"Lihat Lembar Kuesioner: {data_pasien['nama']}", expanded=True):
                    st.dataframe(df_rincian, use_container_width=True, hide_index=True)
            
            # FITUR BACKUP 
            st.markdown("---")
            st.subheader("💾 Backup Data")
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Seluruh Data (.CSV)",
                data=csv_data,
                file_name=f"backup_data_pasien_bai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime='text/csv',
            )
            
            st.markdown("---")
            
            st.subheader("🗑️ Kelola Data")
            col_del1, col_del2, col_del3 = st.columns([5, 2, 2])
            
            with col_del1:
                opsi_pasien_hapus = [f"{row['id']} - {row['nama']}" for index, row in df.iterrows()]
                pilihan_hapus = st.selectbox("Daftar Pasien:", opsi_pasien_hapus, label_visibility="collapsed")
                
            with col_del2:
                if st.button("Hapus Pasien", type="primary", use_container_width=True):
                    if pilihan_hapus:
                        id_hapus = int(pilihan_hapus.split(" - ")[0])
                        hapus_data_pasien(id_hapus)
                        st.success(f"Data {pilihan_hapus} berhasil dihapus!")
                        st.rerun()
                        
            with col_del3:
                if st.button("Kosongkan Semua", use_container_width=True):
                    hapus_semua_data()
                    st.success("Semua data pasien berhasil dibersihkan!")
                    st.rerun()
        else:
            st.info("Belum ada data pasien yang tersimpan.")
            
    elif password != "":
        st.error("Password salah. Silakan coba lagi.")
    else:
        st.info("Silakan masukkan password di panel kiri untuk mengakses riwayat pasien.")