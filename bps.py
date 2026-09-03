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


# ============================================================
# SESSION STATE
# ============================================================

if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

if "mobile_nav_open" not in st.session_state:
    st.session_state["mobile_nav_open"] = False


# ============================================================
# DAFTAR WILAYAH
# ============================================================

DAFTAR_WILAYAH = [
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
    # MENU HEADER
    # --------------------------------------------------------

    with header_menu:

        menu1, menu2, menu3, menu4, menu5, menu6 = st.columns(
            [0.8, 0.8, 1.15, 1.15, 0.65, 0.65],
            vertical_alignment="center"
        )


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
                use_container_width=True,
                key="desktop_search_button"
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
                use_container_width=True,
                key="desktop_location_button"
            ):
                st.selectbox(
                    "Pilih wilayah",
                    DAFTAR_WILAYAH,
                    key="header_wilayah"
                )


    # --------------------------------------------------------
    # LOGIN ADMIN
    # --------------------------------------------------------

    with header_login:

        with st.container(
            key="mobile_header_actions",
            horizontal=True,
            horizontal_alignment="right",
            vertical_alignment="center",
            gap="small"
        ):

            with st.popover(
                "Cari",
                icon=":material/search:",
                key="mobile_search_button",
                help="Cari dokumen"
            ):

                st.text_input(
                    "Cari dokumen",
                    placeholder="Masukkan nama dokumen",
                    key="mobile_header_search"
                )

            if st.button(
                "Menu",
                icon=":material/menu:",
                key="mobile_menu_open",
                help="Buka navigasi",
                use_container_width=True
            ):

                st.session_state["mobile_nav_open"] = True
                st.rerun()

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
# NAVIGASI DRAWER MOBILE
# ============================================================

def mobile_navigation_button(label, page, icon, key):

    is_active = pg == page
    container_key = (
        f"mobile_nav_item_{key}_active"
        if is_active
        else f"mobile_nav_item_{key}"
    )

    with st.container(key=container_key):

        if st.button(
            label,
            icon=icon,
            key=f"mobile_go_{key}",
            type="tertiary",
            use_container_width=True
        ):

            st.session_state["mobile_nav_open"] = False
            st.switch_page(page)


if st.session_state["mobile_nav_open"]:

    with st.container(key="mobile_nav_overlay"):

        with st.container(key="mobile_nav_drawer"):

            drawer_title, drawer_close = st.columns(
                [5, 1],
                vertical_alignment="center"
            )

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

            st.markdown(
                '<div class="mobile-nav-label">Navigasi</div>',
                unsafe_allow_html=True
            )

            mobile_navigation_button(
                "Beranda",
                home,
                ":material/home:",
                "home"
            )

            mobile_navigation_button(
                "Dashboard",
                dashboard,
                ":material/dashboard:",
                "dashboard"
            )

            mobile_navigation_button(
                "Dokumen",
                dokumen,
                ":material/description:",
                "dokumen"
            )

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

            with st.container(key="mobile_nav_footer"):

                st.markdown(
                    '<div class="mobile-nav-label mobile-location-label">'
                    'Wilayah'
                    '</div>',
                    unsafe_allow_html=True
                )

                st.selectbox(
                    "Pilih wilayah",
                    DAFTAR_WILAYAH,
                    key="mobile_header_wilayah",
                    label_visibility="collapsed"
                )

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