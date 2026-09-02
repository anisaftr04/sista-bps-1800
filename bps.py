import streamlit as st

from utils import (
    load_css,
    login_dialog
)


# ============================================================
# KONFIGURASI HALAMAN
# ============================================================

st.set_page_config(
    page_title="SISTA - Sistem Informasi Statistik Sosial",
    page_icon="logo_bps.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# LOAD CSS
# ============================================================

load_css()

# Trik untuk memaksa browser merefresh koordinat klik navbar saat pertama kali dibuka
st.markdown(
    """
    <script>
        window.addEventListener('load', function() {
            window.dispatchEvent(new Event('resize'));
        });
    </script>
    """,
    unsafe_allow_html=True
)

# ============================================================
# SESSION STATE
# ============================================================

if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False


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

upload = st.Page(
    "pages/Upload.py",
    title="Upload",
    icon=":material/upload:"
)


# ============================================================
# NAVIGASI STREAMLIT
# ============================================================

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
        upload
    ],
    position="hidden"
)


# ============================================================
# HEADER (dibungkus 1 container biar sticky + background nyatu)
# ============================================================

header_container = st.container(key="sista_sticky_header")

with header_container:

    header_logo, header_menu, header_login = st.columns(
        [2.0, 5.0, 0.7],
        vertical_alignment="center"
    )


    # --------------------------------------------------------
    # LOGO BPS
    # --------------------------------------------------------

    with header_logo:

        logo_col, text_col = st.columns(
            [0.5, 2.2],
            vertical_alignment="center"
        )

        with logo_col:

            st.image(
                "logo_bps.png",
                width=48
            )

        with text_col:

            st.markdown(
                """
                <div class="bps-name">
                    BADAN PUSAT STATISTIK
                </div>

                <div class="bps-province">
                    PROVINSI LAMPUNG
                </div>
                """,
                unsafe_allow_html=True
            )


    # --------------------------------------------------------
    # MENU HEADER (Menggunakan st.button & st.switch_page)
    # --------------------------------------------------------
    with header_menu:
        menu1, menu2, menu3, menu4, menu5, menu6 = st.columns(
            [0.8, 0.8, 1.15, 1.15, 0.65, 0.65],
            vertical_alignment="center"
        )

        # BERANDA
        with menu1:
            if st.button("🏠 Beranda", key="nav_home", use_container_width=True):
                st.switch_page("pages/Home.py")

        # DASHBOARD
        with menu2:
            if st.button("📊 Dashboard", key="nav_dash", use_container_width=True):
                st.switch_page("pages/Dashboard.py")

        # STATISTIK SOSIAL
        with menu3:
            with st.popover("Statistik Sosial ▾", use_container_width=True):
                if st.button("💳 Kemiskinan", key="nav_kemiskinan", use_container_width=True):
                    st.switch_page("pages/Kemiskinan.py")
                if st.button("💼 Ketenagakerjaan", key="nav_kerja", use_container_width=True):
                    st.switch_page("pages/Ketenagakerjaan.py")
                if st.button("🎓 Pendidikan", key="nav_pendidikan", use_container_width=True):
                    st.switch_page("pages/Pendidikan.py")
                if st.button("👥 Kependudukan", key="nav_penduduk", use_container_width=True):
                    st.switch_page("pages/Penduduk.py")
                if st.button("🍽️ Pengeluaran Makanan", key="nav_pengeluaran", use_container_width=True):
                    st.switch_page("pages/Pengeluaran_Makanan.py")
                if st.button("🏠 Perumahan", key="nav_perumahan", use_container_width=True):
                    st.switch_page("pages/Perumahan.py")

        # DOKUMEN
        with menu4:
            if st.button("📄 Dokumen", key="nav_dokumen", use_container_width=True):
                st.switch_page("pages/Dokumen.py")


        # ----------------------------------------------------
        # BERANDA
        # ----------------------------------------------------

        with menu1:

            st.page_link(
                home,
                label="Beranda",
                icon=":material/home:"
            )


        # ----------------------------------------------------
        # DASHBOARD
        # ----------------------------------------------------

        with menu2:

            st.page_link(
                dashboard,
                label="Dashboard",
                icon=":material/dashboard:"
            )


        # ----------------------------------------------------
        # STATISTIK SOSIAL
        # ----------------------------------------------------

        with menu3:

        # Tandai jika sedang berada di salah satu halaman Statistik Sosial
            statistik_sosial_aktif = pg in [
                kemiskinan,
                ketenagakerjaan,
                pendidikan,
                penduduk,
                pengeluaran,
                perumahan
            ]

            with st.container(key="statistik_sosial_menu"):

            # Penanda khusus untuk CSS saat menu sedang aktif
                if statistik_sosial_aktif:
                    st.markdown(
                    '<div class="statistik-sosial-active"></div>',
                    unsafe_allow_html=True
                )

                with st.popover(
                    "Statistik Sosial",
                    use_container_width=True
                ):


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
        # ----------------------------------------------------
        # DOKUMEN
        # ----------------------------------------------------

        with menu4:

            st.page_link(
                dokumen,
                label="Dokumen",
                icon=":material/description:"
            )


        # ----------------------------------------------------
        # PENCARIAN
        # ----------------------------------------------------

        with menu5:

            with st.popover(
                "🔎",
                use_container_width=True
            ):

                st.text_input(
                    "Cari dokumen",
                    placeholder="Masukkan nama dokumen",
                    key="header_search"
                )


        # ----------------------------------------------------
        # LOKASI
        # ----------------------------------------------------

        with menu6:

            with st.popover(
                "📍",
                use_container_width=True
            ):
                st.selectbox(
                    "Pilih wilayah",
                    [
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
                    ],
                    key="header_wilayah"
                )


    # --------------------------------------------------------
    # LOGIN ADMIN
    # --------------------------------------------------------

    with header_login:

        if st.session_state["is_admin"]:

            if st.button(
                "Logout",
                key="header_logout",
                use_container_width=True
            ):

                st.session_state["is_admin"] = False
                st.rerun()

        else:

            if st.button(
                "Login Admin",
                key="header_login_button",
                type="primary",
                use_container_width=True
            ):

                login_dialog()


# ============================================================
# PEMBATAS HEADER
# ============================================================

st.markdown(
    '<div class="header-line"></div>',
    unsafe_allow_html=True
)


# ============================================================
# JALANKAN HALAMAN
# ============================================================

pg.run()
