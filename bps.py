import os
import streamlit as st
from utils import (
    load_css,
    login_dialog,
    show_login_dialog_if_requested
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
show_login_dialog_if_requested()

# ============================================================
# SESSION STATE
# ============================================================

if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

if "mobile_nav_open" not in st.session_state:
    st.session_state["mobile_nav_open"] = False

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

statistik_lainnya = st.Page(
    "pages/Statistik_Sosial_Lainnya.py",
    title="Statistik Sosial Lainnya",
    icon=":material/category:"
)

upload = st.Page(
    "pages/Upload.py",
    title="Upload",
    icon=":material/upload:"
)

# ============================================================
# CEK HALAMAN STATISTIK SOSIAL YANG AKTIF
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
        statistik_lainnya,
        upload
    ],
    position="hidden"
)

# ------------------------------------------------------------
# True jika sedang berada di salah satu halaman Statistik Sosial
# ------------------------------------------------------------
statistik_sosial_aktif = pg in [
    kemiskinan,
    ketenagakerjaan,
    pendidikan,
    penduduk,
    pengeluaran,
    perumahan,
    statistik_lainnya,
]

# ============================================================
# DATA PENCARIAN
# ============================================================
# Format: "Nama Halaman": (halaman, "kata kunci dipisah spasi")
# Tambahkan kata kunci sesuai indikator yang ada di tiap halaman.

HALAMAN_CARI = {
    "Dashboard": (
        dashboard,
        "ringkasan grafik indikator utama"
    ),
    "Kemiskinan": (
        kemiskinan,
        "miskin garis p0 p1 p2 kedalaman keparahan gini"
    ),
    "Ketenagakerjaan": (
        ketenagakerjaan,
        "kerja tenaga pengangguran tpt tpak sakernas upah"
    ),
    "Pendidikan": (
        pendidikan,
        "sekolah apm apk rls hls literasi melek huruf"
    ),
    "Kependudukan": (
        penduduk,
        "penduduk populasi kepadatan jiwa laju pertumbuhan"
    ),
    "Pengeluaran Makanan": (
        pengeluaran,
        "makan makanan pengeluaran konsumsi pangan"
    ),
    "Perumahan": (
        perumahan,
        "rumah hunian sanitasi air minum listrik atap lantai"
    ),
    "Statistik Sosial Lainnya": (
        statistik_lainnya,
        "lainnya sosial"
    ),
    "Dokumen": (
        dokumen,
        "dokumen publikasi unduh download file"
    ),
}

PANDUAN_FILE = "panduan_sista.pdf"


# ============================================================
# FUNGSI PANEL PENCARIAN
# ============================================================

def panel_pencarian(prefix):

    q = st.text_input(
        "Cari halaman",
        placeholder="mis. miskin, sekolah, rumah",
        key=f"{prefix}_q"
    ).strip().lower()

    if not q:
        st.caption("Ketik kata kunci lalu tekan Enter.")
        return

    kata_dicari = q.split()

    cocok = []

    for nama, (halaman, kata_kunci) in HALAMAN_CARI.items():

        teks = f"{nama.lower()} {kata_kunci}"

        if any(k in teks for k in kata_dicari):
            cocok.append((nama, halaman))

    if cocok:

        st.caption("Halaman yang cocok:")

        for nama, halaman in cocok:
            st.page_link(halaman, label=nama)

    else:

        st.caption(
            "Tidak ada halaman yang cocok. "
            "Coba kata lain, misalnya: miskin, sekolah, rumah."
        )


# ============================================================
# FUNGSI PANEL PANDUAN
# ============================================================

def panel_panduan(prefix):

    # Penanda agar popover panduan dilebarkan oleh CSS
    st.markdown(
        '<div class="panduan-lebar"></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
**Panduan Singkat SISTA**

1. **Beranda**: pengantar dan jalan pintas.
2. **Dashboard**: ringkasan visual indikator utama.
3. **Statistik Sosial**: pilih bidang, lalu atur tahun dan wilayah.
4. **Dokumen**: baca dan unduh dokumen.
5. **Pencarian**: cari halaman dengan kata kunci.
6. **Login Admin**: khusus petugas pengelola data.

Panduan lengkap dapat diunduh di bawah ini.
        """
    )

    if os.path.exists(PANDUAN_FILE):

        with open(PANDUAN_FILE, "rb") as f:

            st.download_button(
                "Unduh Panduan",
                data=f.read(),
                file_name=PANDUAN_FILE,
                mime="application/pdf",
                icon=":material/download:",
                key=f"{prefix}_unduh",
                use_container_width=True
            )

    else:

        st.caption("File panduan belum tersedia.")


# ============================================================
# FUNGSI DAFTAR LINK STATISTIK SOSIAL
# ============================================================

def link_statistik_sosial():

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
        statistik_lainnya,
        label="Statistik Sosial Lainnya",
        icon=":material/category:"
    )


# ============================================================
# HEADER STICKY
# ============================================================
header_container = st.container(key="sista_sticky_header")

with header_container:
    header_logo, header_menu, header_login = st.columns(
        [2.0, 5.0, 0.7],
        vertical_alignment="center"
    )

    # ========================================================
    # LOGO BPS
    # ========================================================
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

    # ========================================================
    # MENU NAVBAR
    # ========================================================
    with header_menu:
        menu1, menu2, menu3, menu4, menu5, menu6 = st.columns(
            [0.8, 0.8, 1.15, 1.15, 0.65, 0.65],
            vertical_alignment="center"
        )

        # ====================================================
        # BERANDA
        # ====================================================
        with menu1:

            if pg == home:
                with st.container(key="beranda_aktif"):
                    st.page_link(
                        home,
                        label="Beranda",
                        icon=":material/home:"
                    )
            else:
                with st.container(key="beranda_normal"):
                    st.page_link(
                        home,
                        label="Beranda",
                        icon=":material/home:"
                    )

        # ====================================================
        # DASHBOARD
        # ====================================================
        with menu2:

            if pg == dashboard:
                with st.container(key="dashboard_aktif"):
                    st.page_link(
                        dashboard,
                        label="Dashboard",
                        icon=":material/dashboard:"
                    )
            else:
                with st.container(key="dashboard_normal"):
                    st.page_link(
                        dashboard,
                        label="Dashboard",
                        icon=":material/dashboard:"
                    )

        # ====================================================
        # STATISTIK SOSIAL
        # ====================================================
        with menu3:

            container_key = (
                "statistik_sosial_aktif"
                if statistik_sosial_aktif
                else "statistik_sosial_normal"
            )

            with st.container(key=container_key):

                with st.popover(
                    "Statistik Sosial",
                    use_container_width=True
                ):
                    link_statistik_sosial()

        # ====================================================
        # DOKUMEN
        # ====================================================
        with menu4:

            if pg == dokumen:
                with st.container(key="dokumen_aktif"):
                    st.page_link(
                        dokumen,
                        label="Dokumen",
                        icon=":material/description:"
                    )
            else:
                with st.container(key="dokumen_normal"):
                    st.page_link(
                        dokumen,
                        label="Dokumen",
                        icon=":material/description:"
                    )

        # ====================================================
        # PENCARIAN
        # ====================================================
        with menu5:

            with st.popover(
                "🔎Pencarian",
                use_container_width=True,
                key="desktop_search_button"
            ):
                panel_pencarian("desktop_search")

        # ====================================================
        # PANDUAN (menggantikan tombol lokasi)
        # key "desktop_location_button" sengaja dipertahankan
        # agar CSS ukuran & gaya yang lama tetap berlaku.
        # ====================================================
        with menu6:

            with st.popover(
                "📖Panduan",
                use_container_width=True,
                key="desktop_location_button"
            ):
                panel_panduan("desktop_panduan")

    # ========================================================
    # AKSI HEADER / LOGIN
    # ========================================================

    with header_login:

        with st.container(
            key="mobile_header_actions",
            horizontal=True,
            horizontal_alignment="right",
            vertical_alignment="center",
            gap="small"
        ):

            # ------------------------------------------------
            # PENCARIAN MOBILE
            # ------------------------------------------------

            with st.popover(
                "Cari",
                icon=":material/search:",
                key="mobile_search_button",
                help="Cari halaman",
                use_container_width=True
            ):
                panel_pencarian("mobile_search")

            # ------------------------------------------------
            # TOMBOL MENU MOBILE
            # ------------------------------------------------

            if st.button(
                "Menu",
                icon=":material/menu:",
                key="mobile_menu_open",
                help="Buka navigasi",
                use_container_width=True
            ):

                st.session_state["mobile_nav_open"] = True
                st.rerun()

        # ----------------------------------------------------
        # LOGIN / LOGOUT ADMIN
        # ----------------------------------------------------

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
# FUNGSI NAVIGASI MOBILE
# ============================================================

def mobile_navigation_button(
    label,
    page,
    icon,
    key
):

    is_active = pg == page

    container_key = (
        f"mobile_nav_item_{key}_active"
        if is_active
        else f"mobile_nav_item_{key}"
    )

    with st.container(
        key=container_key
    ):

        if st.button(
            label,
            icon=icon,
            key=f"mobile_go_{key}",
            type="tertiary",
            use_container_width=True
        ):

            st.session_state["mobile_nav_open"] = False
            st.switch_page(page)

# ============================================================
# NAVIGASI DRAWER MOBILE
# ============================================================

if st.session_state["mobile_nav_open"]:

    with st.container(key="mobile_nav_overlay"):

        with st.container(key="mobile_nav_drawer"):

            drawer_title, drawer_close = st.columns(
                [5, 1],
                vertical_alignment="center"
            )

            # ------------------------------------------------
            # JUDUL DRAWER
            # ------------------------------------------------
            with drawer_title:

                st.markdown(
                    """
                    <div class="mobile-drawer-brand">
                        <div class="mobile-drawer-brand-name">
                            SISTA
                        </div>
                        <div class="mobile-drawer-brand-subtitle">
                            BPS Provinsi Lampung
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


            # ------------------------------------------------
            # TOMBOL TUTUP
            # ------------------------------------------------

            with drawer_close:

                if st.button(
                    "Tutup",
                    icon=":material/close:",
                    key="mobile_menu_close",
                    help="Tutup navigasi",
                    use_container_width=True
                ):

                    st.session_state["mobile_nav_open"] = False
                    st.rerun()


            # ------------------------------------------------
            # LABEL NAVIGASI
            # ------------------------------------------------
            st.markdown(
                '<div class="mobile-nav-label">Navigasi</div>',
                unsafe_allow_html=True
            )

            # ------------------------------------------------
            # BERANDA
            # ------------------------------------------------
            mobile_navigation_button(
                "Beranda",
                home,
                ":material/home:",
                "home"
            )

            # ------------------------------------------------
            # DASHBOARD
            # ------------------------------------------------
            mobile_navigation_button(
                "Dashboard",
                dashboard,
                ":material/dashboard:",
                "dashboard"
            )

            # ------------------------------------------------
            # DOKUMEN
            # ------------------------------------------------
            mobile_navigation_button(
                "Dokumen",
                dokumen,
                ":material/description:",
                "dokumen"
            )

            # ------------------------------------------------
            # STATISTIK SOSIAL MOBILE
            # ------------------------------------------------
            with st.expander(
                "Statistik Sosial",
                expanded=statistik_sosial_aktif,
                icon=":material/bar_chart:",
                key="mobile_stats_dropdown"
            ):

                mobile_navigation_button(
                    "Kemiskinan",
                    kemiskinan,
                    ":material/payments:",
                    "kemiskinan"
                )

                mobile_navigation_button(
                    "Ketenagakerjaan",
                    ketenagakerjaan,
                    ":material/work:",
                    "ketenagakerjaan"
                )

                mobile_navigation_button(
                    "Pendidikan",
                    pendidikan,
                    ":material/school:",
                    "pendidikan"
                )

                mobile_navigation_button(
                    "Kependudukan",
                    penduduk,
                    ":material/groups:",
                    "penduduk"
                )

                mobile_navigation_button(
                    "Pengeluaran Makanan",
                    pengeluaran,
                    ":material/restaurant:",
                    "pengeluaran"
                )

                mobile_navigation_button(
                    "Perumahan",
                    perumahan,
                    ":material/home:",
                    "perumahan"
                )

                mobile_navigation_button(
                    "Statistik Sosial Lainnya",
                    statistik_lainnya,
                    ":material/category:",
                    "statistik_sosial_lainnya"
                )


            # ------------------------------------------------
            # FOOTER DRAWER
            # ------------------------------------------------
            with st.container(key="mobile_nav_footer"):

                # --------------------------------------------
                # PANDUAN (menggantikan pilihan wilayah)
                # --------------------------------------------
                with st.expander(
                    "Panduan Penggunaan",
                    icon=":material/help:",
                    key="mobile_guide_dropdown"
                ):
                    panel_panduan("mobile_panduan")


                # --------------------------------------------
                # ADMIN MOBILE
                # --------------------------------------------
                if st.session_state["is_admin"]:

                    if st.button(
                        "Logout Admin",
                        icon=":material/logout:",
                        key="mobile_admin_logout",
                        type="primary",
                        use_container_width=True
                    ):

                        st.session_state["is_admin"] = False
                        st.session_state["mobile_nav_open"] = False
                        st.rerun()

                else:

                    if st.button(
                        "Login Admin",
                        icon=":material/login:",
                        key="mobile_admin_login",
                        type="primary",
                        use_container_width=True
                    ):

                        st.session_state["mobile_nav_open"] = False
                        st.session_state["mobile_login_requested"] = True
                        st.rerun()


# ============================================================
# LOGIN MOBILE
# ============================================================

if st.session_state.pop("mobile_login_requested", False):
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