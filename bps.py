import streamlit as st

from utils import load_css, admin_login, show_login_dialog_if_requested


# ============================================================
# KONFIGURASI HALAMAN
# ============================================================

st.set_page_config(
    page_title="SISTA - Sistem Informasi Statistik Sosial",
    page_icon="logo_bps.png",
    layout="wide"
)


# ============================================================
# LOAD CSS DAN ADMIN
# ============================================================

load_css()
admin_login()
show_login_dialog_if_requested()


# ============================================================
# DAFTAR HALAMAN
# ============================================================

home = st.Page(
    "pages/Home.py",
    title="Beranda",
    icon=":material/home:",
    default=True
)

dashboard = st.Page(
    "pages/Dashboard.py",
    title="Dashboard",
    icon=":material/dashboard:"
)

dokumen = st.Page(
    "pages/Dokumen.py",
    title="Dokumen",
    icon=":material/description:"
)

kemiskinan = st.Page(
    "pages/Kemiskinan.py",
    title="Kemiskinan",
    icon=":material/payments:"
)

ketenagakerjaan = st.Page(
    "pages/Ketenagakerjaan.py",
    title="Ketenagakerjaan",
    icon=":material/work:"
)

pendidikan = st.Page(
    "pages/Pendidikan.py",
    title="Pendidikan",
    icon=":material/school:"
)

penduduk = st.Page(
    "pages/Penduduk.py",
    title="Kependudukan",
    icon=":material/groups:"
)

pengeluaran = st.Page(
    "pages/Pengeluaran_Makanan.py",
    title="Pengeluaran Makanan",
    icon=":material/restaurant:"
)

perumahan = st.Page(
    "pages/Perumahan.py",
    title="Perumahan",
    icon=":material/home:"
)

statistik = st.Page(
    "pages/Statistik.py",
    title="Statistik",
    icon=":material/bar_chart:"
)

upload = st.Page(
    "pages/Upload.py",
    title="Upload",
    icon=":material/upload:"
)


# ============================================================
# NAVIGASI
# ============================================================
# position="hidden" WAJIB supaya menu bawaan Streamlit
# tidak muncul lagi dan tidak double dengan menu custom.

pg = st.navigation(
    [
        home,
        dashboard,
        dokumen,
        kemiskinan,
        ketenagakerjaan,
        pendidikan,
        penduduk,
        pengeluaran,
        perumahan,
        statistik,
        upload
    ],
    position="hidden"
)


# ============================================================
# SIDEBAR CUSTOM
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # JUDUL SIDEBAR
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="sidebar-title">
            <span class="sidebar-title-icon">📊</span>
            <span>Statistik Sosial</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-line"></div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # MENU
    # --------------------------------------------------------

    st.page_link(
        home,
        label="Beranda",
        icon=":material/home:"
    )

    st.page_link(
        dashboard,
        label="Dashboard",
        icon=":material/dashboard:"
    )

    st.page_link(
        dokumen,
        label="Dokumen",
        icon=":material/description:"
    )

    st.page_link(
        kemiskinan,
        label="Kemiskinan",
        icon=":material/payments:"
    )

    st.page_link(
        ketenagakerjaan,
        label="Ketenagakerjaan",
        icon=":material/work:"
    )

    st.page_link(
        pendidikan,
        label="Pendidikan",
        icon=":material/school:"
    )

    st.page_link(
        penduduk,
        label="Kependudukan",
        icon=":material/groups:"
    )

    st.page_link(
        pengeluaran,
        label="Pengeluaran Makanan",
        icon=":material/restaurant:"
    )

    st.page_link(
        perumahan,
        label="Perumahan",
        icon=":material/home:"
    )

    st.page_link(
        statistik,
        label="Statistik",
        icon=":material/bar_chart:"
    )

    st.page_link(
        upload,
        label="Upload",
        icon=":material/upload:"
    )


    # --------------------------------------------------------
    # PEMBATAS
    # --------------------------------------------------------

    st.markdown(
        '<div class="sidebar-line"></div>',
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # PENCARIAN
    # --------------------------------------------------------

    st.markdown(
        '<div class="sidebar-section-title">🔎 Pencarian</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-label">Cari dokumen...</div>',
        unsafe_allow_html=True
    )

    cari = st.text_input(
        "Cari dokumen",
        placeholder="Masukkan nama dokumen",
        label_visibility="collapsed"
    )


    # --------------------------------------------------------
    # FILTER KABUPATEN/KOTA
    # --------------------------------------------------------

    st.markdown(
        '<div class="sidebar-section-title">📍 Filter Kabupaten/Kota</div>',
        unsafe_allow_html=True
    )

    kabupaten = [
        "Semua",
        "Bandar Lampung",
        "Metro",
        "Lampung Barat",
        "Lampung Selatan",
        "Lampung Tengah",
        "Lampung Timur",
        "Lampung Utara",
        "Mesuji",
        "Pesawaran",
        "Pesisir Barat",
        "Pringsewu",
        "Tanggamus",
        "Tulang Bawang",
        "Tulang Bawang Barat",
        "Way Kanan"
    ]

    filter_kabupaten = st.selectbox(
        "Pilih Kabupaten/Kota",
        kabupaten,
        label_visibility="collapsed"
    )


    # --------------------------------------------------------
    # FILTER JENIS FILE
    # --------------------------------------------------------

    st.markdown(
        '<div class="sidebar-section-title">📂 Filter Jenis File</div>',
        unsafe_allow_html=True
    )

    filter_jenis = st.selectbox(
        "Pilih jenis file",
        ["Semua", "PDF", "Excel", "Word", "PPT"],
        label_visibility="collapsed"
    )


# ============================================================
# JALANKAN HALAMAN
# ============================================================

pg.run()