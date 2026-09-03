import streamlit as st

# Pastikan file utils.py dan fungsi load_css() ada di direktori Anda
from utils import load_css
import base64

# 1. FUNGSI UNTUK MEMBACA GAMBAR (Tulis di atas, setelah import)
def baca_gambar(nama_file):
    try:
        with open(nama_file, "rb") as file:
            encoded = base64.b64encode(file.read()).decode()
            return f"data:image/png;base64,{encoded}"
    except:
        return ""


load_css()

# ============================================================
# CSS KHUSUS BERANDA
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       BACKGROUND
       ======================================================== */
    .stApp {
        background: #f5fbfc;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 0;
        max-width: 1400px;
    }

    /* ========================================================
       HERO
       ======================================================== */
    .sista-hero {
        position: relative;
        margin-top: -50px;
        overflow: hidden;
        min-height: 360px;
        padding: 55px 60px;
        border-radius: 28px;
        background: linear-gradient(115deg, #0067b9 0%, #1684c4 68%, #f39a20 100%);
        color: white;
        box-shadow: 0 12px 35px rgba(0, 75, 150, 0.16);
    }

    .sista-hero::before {
        content: "";
        position: absolute;
        width: 360px;
        height: 360px;
        right: -100px;
        top: -150px;
        border-radius: 50%;
        border: 55px solid rgba(255,255,255,0.08);
    }

    .sista-hero::after {
        content: "";
        position: absolute;
        width: 230px;
        height: 230px;
        right: 180px;
        bottom: -160px;
        border-radius: 50%;
        background: rgba(255,255,255,0.07);
    }

    .hero-content {
        position: relative;
        z-index: 5;
        max-width: 720px;
    }

    .hero-label {
        font-size: 25px;
        font-weight: 600;
        letter-spacing: 1.5px;
        margin-bottom: 12px;
        color: rgba(255,255,255,0.9);
    }

    .hero-title {
        font-size: 40px;
        font-weight: 800;
        line-height: 1.12;
        margin-bottom: 16px;
    }

    .hero-description {
        max-width: 670px;
        font-size: 17px;
        line-height: 1.7;
        color: rgba(255,255,255,0.92);
        margin-bottom: 24px;
    }

    .hero-info {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
    }

    .hero-pill {
        display: inline-block;
        padding: 9px 16px;
        border-radius: 30px;
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.25);
        font-size: 13px;
        color: white;
    }

    /* ========================================================
       GRAFIK DEKORASI
       ======================================================== */
    .hero-chart {
        position: absolute;
        right: 65px;
        bottom: 50px;
        width: 300px;
        height: 210px;
        z-index: 2;
    }

    .chart-line {
        position: absolute;
        left: 20px;
        right: 15px;
        bottom: 20px;
        height: 2px;
        background: rgba(255,255,255,0.35);
    }

    .chart-bar {
        position: absolute;
        bottom: 20px;
        width: 30px;
        border-radius: 7px 7px 0 0;
        background: rgba(255,255,255,0.82);
    }

    .chart-bar-1 { left: 70px; height: 65px; }
    .chart-bar-2 { left: 120px; height: 105px; }
    .chart-bar-3 { left: 170px; height: 135px; }
    .chart-bar-4 { left: 220px; height: 170px; }

    .chart-dot {
        position: absolute;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: white;
        box-shadow: 0 0 0 5px rgba(255,255,255,0.15);
    }

    .dot-1 { left: 78px; bottom: 82px; }
    .dot-2 { left: 128px; bottom: 122px; }
    .dot-3 { left: 178px; bottom: 152px; }
    .dot-4 { left: 228px; bottom: 187px; }

    /* ========================================================
       SECTION
       ======================================================== */
    .home-section {
        margin-top: 45px;
        margin-bottom: 25px;
        text-align: center;
    }

    .home-section-title {
        color: #17365d;
        font-size: 27px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .home-section-description {
        color: #60758c;
        font-size: 14px;
        margin-bottom: 13px;
    }

    .section-line {
        width: 55px;
        height: 4px;
        margin: 0 auto;
        border-radius: 20px;
        background: #f39a20;
    }

    /* ========================================================
       BUTTON LIHAT STATISTIK (Bawah)
       ======================================================== */
    div.stButton > button {
        width: 100%;
        min-height: 38px;
        border-radius: 10px;
        border: 1px solid #d5e3f1;
        background: #0067b9;
        color: white;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    div.stButton > button:hover {
        background: #005a9f;
        border-color: #005a9f;
    }

    /* ========================================================
       INFO SECTION
       ======================================================== */
    .info-card {
        background: linear-gradient(135deg, #edf5fc, #ffffff);
        min-height: 220px;
        border-radius: 20px;
        padding: 28px;
        border: 1px solid #d5e3f1;
        box-shadow: 0 5px 20px rgba(0,50,100,0.05);
    }

    .info-card-title {
        color: #0067b9;
        font-size: 18px;
        font-weight: 800;
        margin-bottom: 15px;
    }

    .info-card-text {
        color: #60758c;
        font-size: 14px;
        line-height: 1.8;
    }

    /* ========================================================
       ANGKA
       ======================================================== */
    .number-card {
        background: linear-gradient(135deg, #edf5fc, #ffffff);
        min-height: 220px;
        border-radius: 20px;
        padding: 28px;
        border: 1px solid #dceafa;
    }

    .number-title {
        color: #0067b9;
        font-size: 18px;
        font-weight: 800;
        margin-bottom: 25px;
    }

    .number-wrapper {
        display: flex;
        justify-content: space-between;
        gap: 15px;
    }

    .number-value {
        color: #17365d;
        font-size: 30px;
        font-weight: 800;
        line-height: 1;
    }

    .number-label {
        color: #60758c;
        font-size: 12px;
        line-height: 1.5;
        margin-top: 8px;
    }

    /* ========================================================
       WILAYAH
       ======================================================== */
    .region-card {
        background: linear-gradient(135deg, #edf5fc, #ffffff);
        min-height: 220px;
        border-radius: 20px;
        padding: 28px;
        border: 1px solid #d5e3f1;
        box-shadow: 0 5px 20px rgba(0,50,100,0.05);
    }

    .region-title {
        color: #0067b9;
        font-size: 18px;
        font-weight: 800;
        margin-bottom: 12px;
    }

    .region-text {
        color: #60758c;
        font-size: 14px;
        line-height: 1.7;
        margin-bottom: 15px;
    }

    /* ========================================================
       FOOTER
       ======================================================== */
    .home-footer {
        margin-top: 50px;
        margin-left: -50px;
        margin-right: -50px;
        padding: 28px 55px;
        background: #0067b9;
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 20px;
    }

    .footer-main { font-size: 14px; font-weight: 800; }
    .footer-sub { margin-top: 4px; font-size: 12px; opacity: 0.8; }
    .footer-right { font-size: 12px; opacity: 0.8; text-align: right; }

    /* ========================================================
       RESPONSIVE
       ======================================================== */
    @media (max-width: 1000px) {
        .hero-chart { opacity: 0.2; right: -20px; }
        .hero-title { font-size: 40px; }
    }

    @media (max-width: 700px) {
        .sista-hero {
            min-height: 0;
            padding: 34px 24px;
        }
        .hero-chart {
            right: -80px;
            bottom: 20px;
        }
        .hero-title { font-size: 34px; }
        .hero-label {
            font-size: 19px;
            letter-spacing: 1px;
        }
        .hero-description { font-size: 15px; }
        .home-section {
            margin-top: 34px;
        }
        .home-section-title {
            font-size: 24px;
        }
        .info-card,
        .number-card,
        .region-card {
            min-height: 0;
            padding: 24px;
        }
        .number-wrapper {
            flex-wrap: wrap;
        }
        .home-footer {
            margin-left: -20px;
            margin-right: -20px;
            padding: 25px;
            flex-direction: column;
            align-items: flex-start;
        }
        .home-footer > div:first-child {
            flex-wrap: wrap;
        }
        .footer-right { text-align: left; }
    }

    @media (max-width: 400px) {
        .sista-hero {
            padding: 30px 20px;
        }
        .hero-title { font-size: 31px; }
        .hero-label { font-size: 17px; }
        .hero-description {
            font-size: 14px;
            line-height: 1.6;
        }
        .hero-pill {
            padding: 8px 12px;
            font-size: 12px;
        }
        .home-section-title {
            font-size: 22px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# HERO
# ============================================================

st.html(
    """
    <div class="sista-hero">
        <div class="hero-content">
            <div class="hero-title"> SISTA
            </div>
            <div class="hero-label">Sistem Informasi Statistik Sosial</div>
            <div class="hero-description">
                SISTA menyajikan berbagai informasi statistik sosial
                Provinsi Lampung secara terstruktur berdasarkan
                indikator dan Kabupaten/Kota.
            </div>
            <div class="hero-info">
                <div class="hero-pill">📊 Statistik Sosial</div>
                <div class="hero-pill">📍 Provinsi Lampung</div>
                <div class="hero-pill">🏛️ Data BPS</div>
            </div>
        </div>
        <div class="hero-chart">
            <div class="chart-line"></div>
            <div class="chart-bar chart-bar-1"></div>
            <div class="chart-bar chart-bar-2"></div>
            <div class="chart-bar chart-bar-3"></div>
            <div class="chart-bar chart-bar-4"></div>
            <div class="chart-dot dot-1"></div>
            <div class="chart-dot dot-2"></div>
            <div class="chart-dot dot-3"></div>
            <div class="chart-dot dot-4"></div>
        </div>
    </div>
    """
)

# ============================================================
# JELAJAHI STATISTIK
# ============================================================

st.html(
    """
    <div class="home-section">
        <div class="home-section-title">Jelajahi Statistik Sosial</div>
        <div class="home-section-description">
            Temukan informasi sosial Provinsi Lampung berdasarkan bidang statistik yang tersedia.
        </div>
        <div class="section-line"></div>
    </div>
    """
)

# ============================================================
# DATA KATEGORI (Modifikasi Warna)
# ============================================================

kategori = [
    {
        "icon": "icon-groups.png",
        "nama": "Kependudukan",
        "deskripsi": "Jumlah dan karakteristik penduduk.",
        "page": "Penduduk", # Sesuaikan URL halaman ini jika perlu (misal: /Penduduk)
        "color_main": "#0067b9",
        "color_bg": "#edf5fc"
    },
    {
        "icon": "icon-poverty.png",
        "nama": "Kemiskinan",
        "deskripsi": "Kondisi dan perkembangan kemiskinan.",
        "page": "Kemiskinan",
        "color_main": "#0067b9",
        "color_bg": "#edf5fc"
    },
    {
        "icon": "icon-work.png",
        "nama": "Ketenagakerjaan",
        "deskripsi": "Kondisi ketenagakerjaan masyarakat.",
        "page": "Ketenagakerjaan",
        "color_main": "#0067b9",
        "color_bg": "#edf5fc"
    },
    {
        "icon": "icon-toga.png",
        "nama": "Pendidikan",
        "deskripsi": "Indikator pendidikan penduduk.",
        "page": "Pendidikan",
        "color_main": "#0067b9",
        "color_bg": "#edf5fc"
    },
    {
        "icon": "icon-food.png",
        "nama": "Pengeluaran Makanan",
        "deskripsi": "Gambaran pengeluaran konsumsi makanan.",
        "page": "Pengeluaran_Makanan",
        "color_main": "#0067b9",
        "color_bg": "#edf5fc"
    },
    {
        "icon": "icon-house.png",
        "nama": "Perumahan",
        "deskripsi": "Kondisi dan karakteristik perumahan.",
        "page": "Perumahan",
        "color_main": "#0067b9",
        "color_bg": "#edf5fc"
    }
]

# ============================================================
# TAMPILKAN KATEGORI CARD BERWARNA
# ============================================================

# 3. MENAMPILKAN KARTU
cols = st.columns(3, gap="medium")

for index, item in enumerate(kategori):
    with cols[index % 3]:
        
        # Mengecek apakah ikonnya berupa file gambar (.png / .jpg) atau emoji
        if item["icon"].endswith(".png") or item["icon"].endswith(".jpg"):
            kode_gambar = baca_gambar(item["icon"])
            if kode_gambar:
                # Jika gambar ketemu, jadikan tag <img>
                tampilan_ikon = f'<img src="{kode_gambar}" style="width: 45px; height: 45px;">'
            else:
                # Jika gambar error/tidak ketemu
                tampilan_ikon = '<span>🖼️</span>' 
        else:
            # Jika icon berupa emoji biasa
            tampilan_ikon = f'<span>{item["icon"]}</span>'

        # Menampilkan HTML Card
        st.html(
            f""" 
            <div style="background: #ffffff; border-radius: 18px; padding: 25px 17px; text-align: center; border: 1px solid #d5e3f1; box-shadow: 0 5px 18px rgba(0,50,100,0.06); min-height: 220px; display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 20px;">
                
                <div>
                    <!-- Latar Belakang Ikon Dinamis -->
                    <div style="width: 90px; height: 85px; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px; border-radius: 50%; font-size: 31px; background: {item['color_bg']};">
                        {tampilan_ikon}
                    </div>
                    
                    <div style="color: #17365d; font-size: 18px; font-weight: 800; margin-bottom: 8px;">
                        {item['nama'].upper()}
                    </div>
                    
                    <div style="color: #60758c; font-size: 16px; line-height: 1.55; min-height: 45px;">
                        {item['deskripsi']}
                    </div>
                </div>

                <!-- Teks Navigasi Dinamis -->
                <a href="{item['page']}" target="_self" style="display: inline-block; margin-top: 12px; font-size: 14px; font-weight: 700; text-decoration: none; color: {item['color_main']};">
                    Jelajahi →
                </a>

            </div>
            """
        )

# ============================================================
# MENGENAL SISTA
# ============================================================

st.html(
    """
    <div class="home-section" style="margin-top: 30px;">
        <div class="home-section-title">Mengenal SISTA</div>
        <div class="home-section-description">
            Satu ruang untuk mengakses dan mengeksplorasi statistik sosial Provinsi Lampung.
        </div>
        <div class="section-line"></div>
    </div>
    """
)

# ============================================================
# TIGA INFORMASI BAWAH
# ============================================================

col1, col2, col3 = st.columns(3, gap="medium")

# 1. SISTA DALAM ANGKA
with col1:
    st.html(
        """
        <div class="number-card">
            <div class="number-title">📊 SISTA dalam Angka</div>
            <div class="number-wrapper">
                <div>
                    <div class="number-value">15</div>
                    <div class="number-label">Kabupaten/<br>Kota</div>
                </div>
                <div>
                    <div class="number-value">6</div>
                    <div class="number-label">Bidang Statistik<br>Sosial</div>
                </div>
                <div>
                    <div class="number-value">BPS</div>
                    <div class="number-label">Sumber<br>Data</div>
                </div>
            </div>
        </div>
        """
    )

# 2. TENTANG SISTA
with col2:
    st.html(
        """
        <div class="info-card">
            <div class="info-card-title">ⓘ Tentang SISTA</div>
            <div class="info-card-text">
                SISTA merupakan Sistem Informasi Statistik Sosial yang dirancang untuk memudahkan pengguna dalam mengakses informasi statistik sosial Provinsi Lampung.
                <br><br>
                Informasi disajikan berdasarkan bidang statistik, indikator, tahun, dan Kabupaten/Kota sehingga pengguna dapat melihat kondisi serta perkembangan sosial secara lebih mudah.
            </div>
        </div>
        """
    )

# 3. JELAJAHI WILAYAH
with col3:
    st.html(
        """
        <div class="region-card" style="padding-bottom: 10px;">
            <div class="region-title">📍 Jelajahi Berdasarkan Wilayah</div>
            <div class="region-text">
                Pilih Kabupaten/Kota untuk melihat informasi statistik sosial secara lebih spesifik melalui Dashboard.
            </div>
        </div>
        """
    )
    
    daftar_wilayah = [
        "Semua Kabupaten/Kota", "Bandar Lampung", "Metro", 
        "Lampung Barat", "Lampung Selatan", "Lampung Tengah", 
        "Lampung Timur", "Lampung Utara", "Mesuji", 
        "Pesawaran", "Pesisir Barat", "Pringsewu", 
        "Tanggamus", "Tulang Bawang", "Tulang Bawang Barat", 
        "Way Kanan"
    ]

    wilayah = st.selectbox(
        "Pilih Kabupaten/Kota",
        daftar_wilayah,
        key="home_wilayah",
        label_visibility="collapsed" # Menyembunyikan label bawaan Streamlit agar lebih bersih
    )

    if st.button("📊 Lihat Statistik →", key="home_lihat_statistik", use_container_width=True):
        st.switch_page("pages/Dashboard.py")

# ============================================================
# FOOTER
# ============================================================


# 1. Panggil gambar logo BPS (pastikan nama file sesuai dengan yang Anda miliki, misalnya "logo-bps.png")
logo_bps = baca_gambar("logo_bps.png") 

# 2. Tampilkan Footer (perhatikan penambahan tag <img> dan style flex di div sebelah kiri)
st.html(
    f"""
    <div class="home-footer">
        
        <!-- Bagian Kiri: Logo dan Teks -->
        <div style="display: flex; align-items: center; gap: 15px;">
            
            <!-- Gambar Logo BPS -->
            <img src="{logo_bps}" style="height: 45px; width: auto; object-fit: contain;" alt="Logo BPS">
            
            <!-- Teks BPS -->
            <div>
                <div class="footer-main">BADAN PUSAT STATISTIK</div>
                <div class="footer-sub">PROVINSI LAMPUNG</div>
            </div>
            
        </div>

        <!-- Bagian Kanan: Copyright -->
        <div class="footer-right">
            © 2026 Badan Pusat Statistik Provinsi Lampung<br>
            Sumber Data: Badan Pusat Statistik
        </div>

    </div>
    """
)