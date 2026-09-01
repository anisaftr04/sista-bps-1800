import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from io import BytesIO

from utils import (
    load_css,
    admin_edit_button,
    set_toast,
    admin_import_data
)


# =========================================================
# LOAD CSS
# =========================================================

load_css()


# =========================================================
# BREADCRUMB
# =========================================================

st.markdown(
    """
    <style>

    div[data-baseweb="popover"] {
        margin-top: 8px !important;
    }

    .breadcrumb-container {
        font-size: 15px;
        color: #555555;
        margin-bottom: 15px;
        margin-top: -10px;
    }

    .breadcrumb-container a {
        color: #0067b9;
        text-decoration: none;
        font-weight: 600;
    }

    .breadcrumb-container a:hover {
        text-decoration: underline;
    }

    /* =====================================================
       TABEL WEB
       ===================================================== */

    .tabel-perumahan-wrapper {
        width: 100%;
        overflow-x: auto;
        margin-top: 10px;
        border: 1px solid #d5dbe0;
        border-radius: 8px;
    }

    .tabel-perumahan {
        width: 100%;
        border-collapse: collapse;
        min-width: 650px;
        font-size: 14px;
    }

    .tabel-perumahan th,
    .tabel-perumahan td {
        border: 1px solid #d5dbe0;
        padding: 10px 12px;
        text-align: center;
        white-space: nowrap;
    }

    .tabel-perumahan thead th {
        background-color: #f1f4f7;
        font-weight: 600;
    }

    .tabel-perumahan thead tr:first-child th {
        background-color: #e8eef4;
        font-size: 15px;
    }

    .tabel-perumahan th:first-child,
    .tabel-perumahan td:first-child {
        text-align: left;
        font-weight: 500;
        position: sticky;
        left: 0;
        background-color: white;
        z-index: 2;
    }

    .tabel-perumahan thead th:first-child {
        background-color: #e8eef4;
        z-index: 3;
    }

    .tabel-perumahan tbody tr:hover td {
        background-color: #f7f9fb;
    }

    /* =====================================================
       FILTER
       ===================================================== */

    .filter-title {
        font-weight: 600;
        font-size: 15px;
        margin-bottom: 6px;
    }

    </style>

    <div class="breadcrumb-container">
        <a href="/" target="_self">Beranda</a>
        &gt; Statistik Sosial - Perumahan
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# STATUS ADMIN
# =========================================================

is_admin = st.session_state.get(
    "is_admin",
    False
)


# =========================================================
# DAFTAR KABUPATEN / KOTA
# =========================================================

DAFTAR_KABKOTA = [
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


# =========================================================
# DAFTAR KATEGORI
# =========================================================

DAFTAR_KATEGORI = {
    "air_layak": "Air Layak",
    "jamban_sendiri_bersama": "Jamban Sendiri/Bersama"
}


# =========================================================
# JUDUL
# =========================================================

col_judul, col_edit = st.columns([8, 1])

with col_judul:

    st.title(
        "🏠 Fasilitas Perumahan"
    )

with col_edit:

    st.write("")
    admin_edit_button()


# =========================================================
# KONEKSI SUPABASE
# =========================================================

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
service_key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]

supabase: Client = create_client(
    url,
    key
)

supabase_admin: Client = create_client(
    url,
    service_key
)


# =========================================================
# DAFTAR DATA
# =========================================================

daftar_data = {
    "Fasilitas Perumahan":
        "fasilitas_perumahan"
}


# =========================================================
# FILTER DATA
# =========================================================

st.subheader(
    "⚙️ Filter Data"
)


# =========================================================
# TIGA KOLOM UTAMA
# =========================================================

col_f1, col_f2, col_f3 = st.columns(
    [1, 1, 1]
)


# =========================================================
# PILIH INDIKATOR
# =========================================================

with col_f1:

    st.markdown(
        "📊 **Pilih Indikator**"
    )

    indikator_input = st.selectbox(
        "Pilih Data Perumahan",
        list(daftar_data.keys()),
        label_visibility="collapsed",
        key="indikator_perumahan"
    )

    nama_tabel_input = daftar_data[
        indikator_input
    ]


    # =====================================================
    # PILIH KATEGORI
    # =====================================================

    col_kat_title, col_kat_all = st.columns(
        [1.25, 1]
    )

    with col_kat_title:

        st.markdown(
            "🏷️ **Kategori**"
        )

    with col_kat_all:

        semua_kategori_chk = st.checkbox(
            "Pilih Semua",
            value=True,
            key=(
                "chk_semua_kategori_"
                "perumahan"
            )
        )


    # -----------------------------------------------------
    # DETEKSI PERUBAHAN PILIH SEMUA
    # -----------------------------------------------------

    prev_key_kategori = (
        "_prev_chk_semua_kategori_"
        "perumahan"
    )

    if prev_key_kategori not in st.session_state:

        st.session_state[
            prev_key_kategori
        ] = semua_kategori_chk

    elif (
        st.session_state[
            prev_key_kategori
        ]
        != semua_kategori_chk
    ):

        for kode_kategori in DAFTAR_KATEGORI:

            st.session_state[
                f"kat_perumahan_{kode_kategori}"
            ] = semua_kategori_chk

        st.session_state[
            prev_key_kategori
        ] = semua_kategori_chk


    # -----------------------------------------------------
    # LIST KATEGORI
    # -----------------------------------------------------

    with st.container(height=100, key="box_kategori_perumahan"):

        kategori_terpilih_input = []

        for kode_kategori, nama_kategori in (
            DAFTAR_KATEGORI.items()
        ):

            cek_kategori = st.checkbox(
                nama_kategori,
                value=semua_kategori_chk,
                key=(
                    f"kat_perumahan_"
                    f"{kode_kategori}"
                )
            )

            if cek_kategori:

                kategori_terpilih_input.append(
                    kode_kategori
                )


# =========================================================
# AMBIL DAFTAR TAHUN
# =========================================================

try:

    resp_opt = (
        supabase
        .table(nama_tabel_input)
        .select("tahun")
        .execute()
    )

    df_opt = pd.DataFrame(
        resp_opt.data
    )

    if (
        not df_opt.empty
        and "tahun" in df_opt.columns
    ):

        df_opt["tahun"] = pd.to_numeric(
            df_opt["tahun"],
            errors="coerce"
        )

        daftar_tahun_opt = sorted(
            df_opt["tahun"]
            .dropna()
            .unique()
            .astype(int),
            reverse=True
        )

    else:

        daftar_tahun_opt = []

except Exception:

    daftar_tahun_opt = []


# =========================================================
# PILIH TAHUN
# =========================================================

with col_f2:

    col_thn_title, col_thn_all = st.columns(
        [1.25, 1]
    )

    with col_thn_title:

        st.markdown(
            "📅 **Tahun**"
        )

    with col_thn_all:

        semua_tahun_chk = st.checkbox(
            "Pilih Semua",
            value=True,
            key=(
                "chk_semua_tahun_"
                "perumahan"
            )
        )


    # -----------------------------------------------------
    # DETEKSI PERUBAHAN
    # -----------------------------------------------------

    prev_key_tahun = (
        "_prev_chk_semua_tahun_"
        "perumahan"
    )

    if prev_key_tahun not in st.session_state:

        st.session_state[
            prev_key_tahun
        ] = semua_tahun_chk

    elif (
        st.session_state[
            prev_key_tahun
        ]
        != semua_tahun_chk
    ):

        for thn in daftar_tahun_opt:

            st.session_state[
                f"thn_perumahan_{thn}"
            ] = semua_tahun_chk

        st.session_state[
            prev_key_tahun
        ] = semua_tahun_chk


    # -----------------------------------------------------
    # LIST TAHUN
    # -----------------------------------------------------

    with st.container(height=200, key="box_tahun_perumahan"):

        tahun_terpilih_input = []

        if daftar_tahun_opt:

            for thn in daftar_tahun_opt:

                cek_tahun = st.checkbox(
                    str(thn),
                    value=semua_tahun_chk,
                    key=(
                        f"thn_perumahan_"
                        f"{thn}"
                    )
                )

                if cek_tahun:

                    tahun_terpilih_input.append(
                        int(thn)
                    )

        else:

            st.warning(
                "Tidak ada data tahun."
            )


# =========================================================
# AMBIL DAFTAR WILAYAH
# =========================================================

try:

    resp_wil_opt = (
        supabase
        .table(nama_tabel_input)
        .select("kabupaten_kota")
        .execute()
    )

    df_wil_opt = pd.DataFrame(
        resp_wil_opt.data
    )

    if (
        not df_wil_opt.empty
        and
        "kabupaten_kota"
        in df_wil_opt.columns
    ):

        daftar_wilayah_opt = sorted(
            df_wil_opt[
                "kabupaten_kota"
            ]
            .dropna()
            .unique()
        )

    else:

        daftar_wilayah_opt = []

except Exception:

    daftar_wilayah_opt = []


# =========================================================
# PILIH WILAYAH
# =========================================================

with col_f3:

    col_wil_title, col_wil_all = st.columns(
        [1.25, 1]
    )

    with col_wil_title:

        st.markdown(
            "📍 **Kabupaten/Kota**"
        )

    with col_wil_all:

        semua_wilayah_chk = st.checkbox(
            "Pilih Semua",
            value=True,
            key=(
                "chk_semua_wilayah_"
                "perumahan"
            )
        )


    # -----------------------------------------------------
    # DETEKSI PERUBAHAN
    # -----------------------------------------------------

    prev_key_wilayah = (
        "_prev_chk_semua_wilayah_"
        "perumahan"
    )

    if prev_key_wilayah not in st.session_state:

        st.session_state[
            prev_key_wilayah
        ] = semua_wilayah_chk

    elif (
        st.session_state[
            prev_key_wilayah
        ]
        != semua_wilayah_chk
    ):

        for wil in daftar_wilayah_opt:

            st.session_state[
                f"wil_perumahan_{wil}"
            ] = semua_wilayah_chk

        st.session_state[
            prev_key_wilayah
        ] = semua_wilayah_chk


    # -----------------------------------------------------
    # LIST WILAYAH
    # -----------------------------------------------------

    with st.container(height=200, key="box_wilayah_perumahan"):

        wilayah_terpilih_input = []

        if daftar_wilayah_opt:

            for wil in daftar_wilayah_opt:

                cek_wil = st.checkbox(
                    wil,
                    value=semua_wilayah_chk,
                    key=(
                        f"wil_perumahan_"
                        f"{wil}"
                    )
                )

                if cek_wil:

                    wilayah_terpilih_input.append(
                        wil
                    )

        else:

            st.warning(
                "Tidak ada data wilayah."
            )


# =========================================================
# TOMBOL TAMPILKAN DATA
# =========================================================

st.markdown("")

submitted = st.button(
    "🔍 Tampilkan Data",
    use_container_width=True
)


# =========================================================
# SIMPAN FILTER
# =========================================================

if submitted:

    st.session_state[
        "submitted_perumahan"
    ] = True

    st.session_state[
        "indikator_final_perumahan"
    ] = indikator_input

    st.session_state[
        "kategori_final_perumahan"
    ] = kategori_terpilih_input

    st.session_state[
        "tahun_final_perumahan"
    ] = tahun_terpilih_input

    st.session_state[
        "wilayah_final_perumahan"
    ] = wilayah_terpilih_input


# =========================================================
# JIKA BELUM SUBMIT
# =========================================================

if not st.session_state.get(
    "submitted_perumahan",
    False
):

    st.info(
        "👆 Silakan sesuaikan pilihan kategori, "
        "tahun, dan wilayah di atas, lalu klik "
        "**Tampilkan Data**."
    )

    st.stop()


# =========================================================
# AMBIL FILTER FINAL
# =========================================================

indikator = st.session_state.get(
    "indikator_final_perumahan",
    list(daftar_data.keys())[0]
)

nama_tabel = daftar_data[
    indikator
]

kategori_terpilih = (
    st.session_state.get(
        "kategori_final_perumahan",
        list(DAFTAR_KATEGORI.keys())
    )
)

tahun_terpilih = (
    st.session_state.get(
        "tahun_final_perumahan",
        []
    )
)

wilayah_terpilih = (
    st.session_state.get(
        "wilayah_final_perumahan",
        []
    )
)


# =========================================================
# VALIDASI FILTER
# =========================================================

if not kategori_terpilih:

    st.warning(
        "⚠️ Silakan pilih minimal satu kategori."
    )

    st.stop()


if not tahun_terpilih:

    st.warning(
        "⚠️ Silakan pilih minimal satu tahun."
    )

    st.stop()


if not wilayah_terpilih:

    st.warning(
        "⚠️ Silakan pilih minimal satu "
        "Kabupaten/Kota."
    )

    st.stop()


# =========================================================
# AMBIL DATA UTAMA
# =========================================================

try:

    response = (
        supabase
        .table(nama_tabel)
        .select("*")
        .execute()
    )

    data = response.data

except Exception as e:

    st.error(
        f"Gagal mengambil data dari Supabase: {e}"
    )

    st.stop()


# =========================================================
# CEK DATA
# =========================================================

if not data:

    st.warning(
        "Data Fasilitas Perumahan belum tersedia."
    )

    st.stop()


df = pd.DataFrame(data)


# =========================================================
# VALIDASI KOLOM
# =========================================================

kolom_wajib_data = [
    "tahun",
    "kabupaten_kota",
    "air_layak",
    "jamban_sendiri_bersama"
]

kolom_tidak_ada = [
    kolom
    for kolom in kolom_wajib_data
    if kolom not in df.columns
]

if kolom_tidak_ada:

    st.error(
        "Kolom berikut tidak ditemukan di tabel "
        f"`{nama_tabel}`: "
        f"{', '.join(kolom_tidak_ada)}"
    )

    st.stop()


# =========================================================
# KONVERSI DATA
# =========================================================

df["tahun"] = pd.to_numeric(
    df["tahun"],
    errors="coerce"
)

df["air_layak"] = pd.to_numeric(
    df["air_layak"],
    errors="coerce"
)

df["jamban_sendiri_bersama"] = pd.to_numeric(
    df["jamban_sendiri_bersama"],
    errors="coerce"
)

df = df.dropna(
    subset=[
        "tahun"
    ]
)

df["tahun"] = df[
    "tahun"
].astype(int)


# =========================================================
# FILTER DATA
# =========================================================

df_filtered = df[
    df["kabupaten_kota"].isin(
        wilayah_terpilih
    )
    &
    df["tahun"].isin(
        tahun_terpilih
    )
].copy()


# =========================================================
# JUDUL HASIL
# =========================================================

st.markdown("---")

st.subheader(
    ":material/home: Fasilitas Perumahan"
)

st.write(
    f"Menampilkan "
    f"{len(wilayah_terpilih)} wilayah, "
    f"{len(tahun_terpilih)} tahun, dan "
    f"{len(kategori_terpilih)} kategori."
)


# =========================================================
# TABEL
# =========================================================

if not df_filtered.empty:

    # =====================================================
    # URUTAN DATA
    # =====================================================

    df_filtered = df_filtered.sort_values(
        [
            "kabupaten_kota",
            "tahun"
        ]
    )


    # =====================================================
    # MEMBUAT DATAFRAME UNTUK TABEL
    # =====================================================

    kolom_kategori = [
        kategori
        for kategori in kategori_terpilih
        if kategori in df_filtered.columns
    ]


    # =====================================================
    # PIVOT
    #
    # HASIL PANDAS DEFAULT:
    #
    # (kategori, tahun) -> kita balik jadi (tahun, kategori)
    # =====================================================

    df_pivot = df_filtered.pivot_table(
        index="kabupaten_kota",
        columns="tahun",
        values=kolom_kategori,
        aggfunc="first"
    )

    # PENTING: pandas bikin urutan level kolom jadi
    # (kategori, tahun). Kita balik jadi (tahun, kategori)
    # supaya cocok dengan kolom_multi di bawah.
    df_pivot.columns = df_pivot.columns.swaplevel(0, 1)


    # =====================================================
    # SUSUN URUTAN KOLOM
    # =====================================================

    tahun_urut = sorted(
        tahun_terpilih,
        reverse=True
    )

    kategori_urut = [
        kategori
        for kategori in DAFTAR_KATEGORI
        if kategori in kategori_terpilih
    ]


    # =====================================================
    # MEMBUAT MULTIINDEX SESUAI URUTAN
    # =====================================================

    kolom_multi = []

    for tahun in tahun_urut:

        for kategori in kategori_urut:

            kolom_multi.append(
                (tahun, kategori)
            )


    # =====================================================
    # REINDEX
    # =====================================================

    df_pivot = df_pivot.reindex(
        columns=pd.MultiIndex.from_tuples(
            kolom_multi
        )
    )


    # =====================================================
    # TABEL HTML UNTUK WEB
    # =====================================================

    st.subheader(
        ":material/list_alt: Data"
    )


    html = """
    <div class="tabel-perumahan-wrapper">
    <table class="tabel-perumahan">
    <thead>
    <tr>
        <th rowspan="2">Kabupaten/Kota</th>
    """


    # -----------------------------------------------------
    # HEADER TAHUN
    # -----------------------------------------------------

    for tahun in tahun_urut:

        html += (
            f'<th colspan="{len(kategori_urut)}">'
            f'{tahun}'
            f'</th>'
        )

    html += "</tr><tr>"


    # -----------------------------------------------------
    # HEADER KATEGORI
    # -----------------------------------------------------

    for tahun in tahun_urut:

        for kategori in kategori_urut:

            nama_kategori = (
                DAFTAR_KATEGORI[
                    kategori
                ]
            )

            # Pendekkan supaya tabel lebih rapi
            if kategori == "air_layak":

                nama_header = "Air Layak"

            elif (
                kategori
                == "jamban_sendiri_bersama"
            ):

                nama_header = "Jamban Sendiri/Bersama"

            else:

                nama_header = nama_kategori

            html += (
                f"<th>{nama_header}</th>"
            )

    html += "</tr></thead><tbody>"


    # -----------------------------------------------------
    # ISI TABEL
    # -----------------------------------------------------

    for wilayah in df_pivot.index:

        html += (
            f"<tr>"
            f"<td>{wilayah}</td>"
        )

        for tahun in tahun_urut:

            for kategori in kategori_urut:

                try:

                    nilai = df_pivot.loc[
                        wilayah,
                        (tahun, kategori)
                    ]

                    if pd.isna(nilai):

                        tampilan = "-"

                    else:

                        tampilan = (
                            f"{float(nilai):,.2f}"
                            .replace(",", "X")
                            .replace(".", ",")
                            .replace("X", ".")
                        )

                except Exception:

                    tampilan = "-"

                html += (
                    f"<td>{tampilan}</td>"
                )

        html += "</tr>"


    html += """
    </tbody>
    </table>
    </div>
    """


    st.markdown(
        html,
        unsafe_allow_html=True
    )


    # =====================================================
    # DOWNLOAD EXCEL
    # =====================================================

    output = BytesIO()


    # -----------------------------------------------------
    # DATA EXCEL
    # -----------------------------------------------------

    df_excel = df_pivot.copy()


    # Nama kategori untuk Excel
    df_excel.columns = pd.MultiIndex.from_tuples(
        [
            (
                tahun,
                DAFTAR_KATEGORI[
                    kategori
                ]
            )
            for tahun, kategori
            in df_excel.columns
        ]
    )


    # =====================================================
    # TULIS EXCEL
    # =====================================================

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df_excel.to_excel(
            writer,
            sheet_name="Fasilitas Perumahan",
            index=True,
            index_label="Kabupaten/Kota"
        )


        # -------------------------------------------------
        # FORMAT EXCEL
        # -------------------------------------------------

        worksheet = writer.sheets[
            "Fasilitas Perumahan"
        ]


        # Lebar kolom Kabupaten/Kota
        worksheet.column_dimensions[
            "A"
        ].width = 25


        for col in worksheet.iter_cols(
            min_col=2,
            max_col=worksheet.max_column
        ):

            worksheet.column_dimensions[
                col[0].column_letter
            ].width = 18


        # -------------------------------------------------
        # BOLD HEADER
        # -------------------------------------------------

        for cell in worksheet[1]:

            cell.font = cell.font.copy(
                bold=True
            )


        for cell in worksheet[2]:

            cell.font = cell.font.copy(
                bold=True
            )


        # -------------------------------------------------
        # ALIGNMENT
        # -------------------------------------------------

        for row in worksheet.iter_rows():

            for cell in row:

                cell.alignment = cell.alignment.copy(
                    horizontal="center",
                    vertical="center"
                )


        # Kabupaten/Kota rata kiri
        for row in range(
            3,
            worksheet.max_row + 1
        ):

            worksheet.cell(
                row=row,
                column=1
            ).alignment = (
                worksheet.cell(
                    row=row,
                    column=1
                ).alignment.copy(
                    horizontal="left"
                )
            )


    output.seek(0)


    # =====================================================
    # TOMBOL DOWNLOAD
    # =====================================================

    st.download_button(
        label="📥 Download Excel",
        data=output,
        file_name=(
            "Fasilitas_Perumahan.xlsx"
        ),
        mime=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        use_container_width=False
    )


    # =====================================================
    # GRAFIK
    # =====================================================

    st.subheader(
        ":material/show_chart: Grafik"
    )


    # -----------------------------------------------------
    # DATA GRAFIK
    # -----------------------------------------------------

    df_grafik = df_filtered.melt(
        id_vars=[
            "kabupaten_kota",
            "tahun"
        ],
        value_vars=kolom_kategori,
        var_name="kategori",
        value_name="nilai"
    )


    df_grafik[
        "kategori"
    ] = df_grafik[
        "kategori"
    ].map(
        DAFTAR_KATEGORI
    )


    # -----------------------------------------------------
    # GRAFIK
    # -----------------------------------------------------

    fig = px.line(
        df_grafik,
        x="tahun",
        y="nilai",
        color="kabupaten_kota",
        line_dash="kategori",
        markers=True,
        title=(
            "Perkembangan Fasilitas "
            "Perumahan Berdasarkan Wilayah"
        )
    )


    fig.update_layout(
        xaxis_title="Tahun",
        yaxis_title="Persentase (%)",
        hovermode="x unified",
        xaxis=dict(
            showgrid=False
        ),
        yaxis=dict(
            showgrid=False
        )
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


else:

    st.warning(
        "Tidak ada data yang sesuai dengan "
        "filter yang dipilih."
    )


# =========================================================
# INFORMASI
# =========================================================

st.caption(
    "Sumber data: Badan Pusat Statistik (BPS)."
)


# =========================================================
# PANEL ADMIN
# =========================================================

if (
    is_admin
    and
    st.session_state.get(
        "show_admin_panel",
        False
    )
):

    st.markdown("---")

    st.subheader(
        "⚙️ Panel Admin — Fasilitas Perumahan"
    )

    st.caption(
        f"Mengelola tabel: `{nama_tabel}`"
    )


    # =====================================================
    # AMBIL DATA ADMIN TERBARU
    # =====================================================

    try:

        response_admin = (
            supabase_admin
            .table(nama_tabel)
            .select("*")
            .execute()
        )

        data_admin = response_admin.data

    except Exception as e:

        st.error(
            f"Gagal mengambil data admin: {e}"
        )

        data_admin = []


    # =====================================================
    # DATA ADMIN
    # =====================================================

    if data_admin:

        admin_df = pd.DataFrame(
            data_admin
        )

        admin_df["tahun"] = pd.to_numeric(
            admin_df["tahun"],
            errors="coerce"
        )

        admin_df["air_layak"] = pd.to_numeric(
            admin_df["air_layak"],
            errors="coerce"
        )

        admin_df[
            "jamban_sendiri_bersama"
        ] = pd.to_numeric(
            admin_df[
                "jamban_sendiri_bersama"
            ],
            errors="coerce"
        )

    else:

        admin_df = pd.DataFrame(
            columns=[
                "tahun",
                "kabupaten_kota",
                "air_layak",
                "jamban_sendiri_bersama"
            ]
        )


    ada_data_admin = (
        not admin_df.empty
    )


    # =====================================================
    # TAB ADMIN
    # =====================================================

    if ada_data_admin:

        tab_tambah, tab_edit, tab_hapus = (
            st.tabs(
                [
                    "➕ Tambah Data",
                    "✏️ Edit Data",
                    "🗑 Hapus Data"
                ]
            )
        )

    else:

        st.info(
            "Belum ada data. Silakan "
            "tambahkan data terlebih dahulu."
        )

        tab_tambah = st.container()

        tab_edit = None
        tab_hapus = None


    # =====================================================
    # TAMBAH DATA
    # =====================================================

    with tab_tambah:

        metode = st.radio(
            "Metode Input",
            [
                "Input Manual",
                "Import Excel/CSV"
            ],
            horizontal=True,
            key=(
                "metode_tambah_"
                "fasilitas_perumahan"
            )
        )

        st.markdown("---")


        # =================================================
        # INPUT MANUAL
        # =================================================

        if metode == "Input Manual":

            with st.form(
                "form_tambah_perumahan",
                clear_on_submit=True
            ):

                col_a, col_b = st.columns(2)


                # -----------------------------------------
                # TAHUN
                # -----------------------------------------

                with col_a:

                    tahun_baru = st.number_input(
                        "Tahun",
                        min_value=2000,
                        max_value=2100,
                        step=1,
                        value=2024
                    )


                # -----------------------------------------
                # WILAYAH
                # -----------------------------------------

                with col_b:

                    kabkota_baru = st.selectbox(
                        "Kabupaten/Kota",
                        DAFTAR_KABKOTA,
                        key=(
                            "tambah_kabkota_"
                            "perumahan"
                        )
                    )


                # -----------------------------------------
                # AIR
                # -----------------------------------------

                col_c, col_d = st.columns(2)

                with col_c:

                    air_baru = st.number_input(
                        "Air Layak (%)",
                        value=0.0,
                        step=0.01,
                        format="%.2f"
                    )


                # -----------------------------------------
                # JAMBAN
                # -----------------------------------------

                with col_d:

                    jamban_baru = st.number_input(
                        "Jamban "
                        "Sendiri/Bersama (%)",
                        value=0.0,
                        step=0.01,
                        format="%.2f"
                    )


                # -----------------------------------------
                # SIMPAN
                # -----------------------------------------

                if st.form_submit_button(
                    "💾 Simpan Data Baru"
                ):

                    data_baru = {

                        "tahun":
                            int(tahun_baru),

                        "kabupaten_kota":
                            kabkota_baru,

                        "air_layak":
                            air_baru,

                        "jamban_sendiri_bersama":
                            jamban_baru
                    }


                    try:

                        (
                            supabase_admin
                            .table(nama_tabel)
                            .insert(data_baru)
                            .execute()
                        )

                        set_toast(
                            "✅ Data baru berhasil "
                            "ditambahkan."
                        )

                        st.rerun()


                    except Exception as e:

                        st.error(
                            f"Gagal menyimpan data: {e}"
                        )


        # =================================================
        # IMPORT EXCEL / CSV
        # =================================================

        else:

            kolom_wajib = [
                "tahun",
                "kabupaten_kota",
                "air_layak",
                "jamban_sendiri_bersama"
            ]

            kolom_teks = [
                "kabupaten_kota"
            ]


            admin_import_data(
                supabase_admin=supabase_admin,
                table_name=nama_tabel,
                kolom_wajib=kolom_wajib,
                key_prefix=nama_tabel,
                kolom_teks=kolom_teks
            )


    # =====================================================
    # EDIT DATA
    # =====================================================

    if ada_data_admin:

        with tab_edit:

            opsi_baris = [

                f"{int(row['tahun'])} - "
                f"{row['kabupaten_kota']}"

                for _, row
                in admin_df.iterrows()
            ]


            pilih_baris = st.selectbox(
                "Pilih data yang mau diedit",
                opsi_baris,
                key=(
                    "pilih_edit_"
                    "perumahan"
                )
            )


            if pilih_baris:

                tahun_pilih, kabkota_pilih = (
                    pilih_baris.split(
                        " - ",
                        1
                    )
                )

                tahun_pilih = int(
                    tahun_pilih
                )


                baris = admin_df[
                    (
                        admin_df["tahun"]
                        == tahun_pilih
                    )
                    &
                    (
                        admin_df[
                            "kabupaten_kota"
                        ]
                        == kabkota_pilih
                    )
                ].iloc[0]


                with st.form(
                    "form_edit_perumahan"
                ):

                    st.write(
                        "Mengedit data: "
                        f"**{pilih_baris}**"
                    )


                    col_c, col_d = st.columns(2)


                    with col_c:

                        air_edit = st.number_input(
                            "Air Layak (%)",
                            value=(
                                float(
                                    baris[
                                        "air_layak"
                                    ]
                                )
                                if pd.notna(
                                    baris[
                                        "air_layak"
                                    ]
                                )
                                else 0.0
                            ),
                            step=0.01,
                            format="%.2f"
                        )


                    with col_d:

                        jamban_edit = st.number_input(
                            "Jamban "
                            "Sendiri/Bersama (%)",
                            value=(
                                float(
                                    baris[
                                        "jamban_sendiri_bersama"
                                    ]
                                )
                                if pd.notna(
                                    baris[
                                        "jamban_sendiri_bersama"
                                    ]
                                )
                                else 0.0
                            ),
                            step=0.01,
                            format="%.2f"
                        )


                    if st.form_submit_button(
                        "💾 Simpan Perubahan"
                    ):

                        try:

                            (
                                supabase_admin
                                .table(nama_tabel)
                                .update({
                                    "air_layak":
                                        air_edit,

                                    "jamban_sendiri_bersama":
                                        jamban_edit
                                })
                                .eq(
                                    "tahun",
                                    tahun_pilih
                                )
                                .eq(
                                    "kabupaten_kota",
                                    kabkota_pilih
                                )
                                .execute()
                            )


                            set_toast(
                                "✅ Data berhasil "
                                "diperbarui."
                            )

                            st.rerun()


                        except Exception as e:

                            st.error(
                                "Gagal memperbarui "
                                f"data: {e}"
                            )


    # =====================================================
    # HAPUS DATA
    # =====================================================

    if ada_data_admin:

        with tab_hapus:

            opsi_hapus = [

                f"{int(row['tahun'])} - "
                f"{row['kabupaten_kota']}"

                for _, row
                in admin_df.iterrows()
            ]


            pilih_hapus = st.selectbox(
                "Pilih data yang mau dihapus",
                opsi_hapus,
                key=(
                    "pilih_hapus_"
                    "perumahan"
                )
            )


            # ---------------------------------------------
            # TOMBOL HAPUS
            # ---------------------------------------------

            if st.button(
                "🗑 Hapus Data Ini",
                key=(
                    "tombol_hapus_"
                    "perumahan"
                )
            ):

                st.session_state[
                    "konfirmasi_hapus_"
                    "perumahan"
                ] = pilih_hapus


            konfirmasi_key = (
                "konfirmasi_hapus_"
                "perumahan"
            )


            # ---------------------------------------------
            # KONFIRMASI
            # ---------------------------------------------

            if st.session_state.get(
                konfirmasi_key
            ):

                target = st.session_state[
                    konfirmasi_key
                ]


                st.warning(
                    f"Yakin ingin menghapus data "
                    f"**{target}**? "
                    "Tindakan ini tidak bisa "
                    "dibatalkan."
                )


                col_ya, col_batal = (
                    st.columns(2)
                )


                # -----------------------------------------
                # YA
                # -----------------------------------------

                with col_ya:

                    if st.button(
                        "✅ Ya, Hapus Permanen",
                        key=(
                            "ya_hapus_"
                            "perumahan"
                        )
                    ):

                        (
                            tahun_hapus,
                            kabkota_hapus
                        ) = target.split(
                            " - ",
                            1
                        )


                        try:

                            (
                                supabase_admin
                                .table(nama_tabel)
                                .delete()
                                .eq(
                                    "tahun",
                                    int(
                                        tahun_hapus
                                    )
                                )
                                .eq(
                                    "kabupaten_kota",
                                    kabkota_hapus
                                )
                                .execute()
                            )


                            del st.session_state[
                                konfirmasi_key
                            ]


                            set_toast(
                                "✅ Data berhasil "
                                "dihapus."
                            )


                            st.rerun()


                        except Exception as e:

                            st.error(
                                "Gagal menghapus "
                                f"data: {e}"
                            )


                # -----------------------------------------
                # BATAL
                # -----------------------------------------

                with col_batal:

                    if st.button(
                        "❌ Batal",
                        key=(
                            "batal_hapus_"
                            "perumahan"
                        )
                    ):

                        del st.session_state[
                            konfirmasi_key
                        ]

                        st.rerun()