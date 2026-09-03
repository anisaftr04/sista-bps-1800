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

load_css()


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>
    .breadcrumb-container {
        font-size: 15px;
        color: #60758c;
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
    </style>

    <div class="breadcrumb-container">
        <a href="/" target="_self">Beranda</a>
        &gt; Statistik Sosial - Pendidikan
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

is_admin = st.session_state.get("is_admin", False)


# =========================================================
# DAFTAR KABUPATEN/KOTA
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
# KONEKSI SUPABASE
# =========================================================

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
service_key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]

supabase: Client = create_client(url, key)
supabase_admin: Client = create_client(url, service_key)


# =========================================================
# JUDUL
# =========================================================

col_judul, col_edit = st.columns([8, 1])

with col_judul:
    st.title("📚 Indikator Pendidikan")

with col_edit:
    st.write("")
    admin_edit_button()


st.write(
    "Halaman ini menyajikan beberapa indikator pendidikan "
    "di Provinsi Lampung, meliputi Angka Partisipasi Sekolah "
    "(APS), Angka Partisipasi Murni (APM), dan Angka Partisipasi "
    "Kasar (APK)."
)


# =========================================================
# PEMETAAN KODE WILAYAH
# =========================================================

nama_wilayah = {
    "1801": "Lampung Barat",
    "1802": "Tanggamus",
    "1803": "Lampung Selatan",
    "1804": "Lampung Timur",
    "1805": "Lampung Tengah",
    "1806": "Lampung Utara",
    "1807": "Way Kanan",
    "1808": "Tulang Bawang",
    "1809": "Pesawaran",
    "1810": "Pringsewu",
    "1811": "Mesuji",
    "1812": "Tulang Bawang Barat",
    "1813": "Pesisir Barat",
    "1871": "Bandar Lampung",
    "1872": "Metro"
}

kode_dari_nama = {
    v: k for k, v in nama_wilayah.items()
}


# =========================================================
# FUNGSI AMBIL DATA
# =========================================================

@st.cache_data
def get_data(tabel):

    response = (
        supabase
        .table(tabel)
        .select("*")
        .execute()
    )

    return pd.DataFrame(response.data)


# =========================================================
# FUNGSI DOWNLOAD EXCEL
# =========================================================

def tombol_download_excel(
    df_export,
    nama_sheet,
    nama_file
):

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df_export.to_excel(
            writer,
            index=False,
            sheet_name=nama_sheet
        )

    output.seek(0)

    st.download_button(
        label="📥 Download Excel",
        data=output,
        file_name=nama_file,
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )


# =========================================================
# FUNGSI FORMAT TABEL
# =========================================================

def tampilkan_tabel(tabel_df):

    kolom_config = {
        kol: st.column_config.NumberColumn(
            format="%.2f"
        )
        for kol in tabel_df.columns
        if kol != "Tahun"
    }

    st.dataframe(
        tabel_df,
        use_container_width=True,
        hide_index=True,
        column_config=kolom_config
    )


# =========================================================
# AMBIL SEMUA DATA
# =========================================================

df_aps = get_data("aps")
df_aps_2025 = get_data("aps_kabko_2025")
df_apm = get_data("apm_kabko_2025")
df_apk = get_data("apk_kabko_2025")


# =========================================================
# PEMETAAN TABEL
# =========================================================

TABEL_MAP = {

    "aps": df_aps,

    "aps_kabko_2025": df_aps_2025,

    "apm_kabko_2025": df_apm,

    "apk_kabko_2025": df_apk

}


# =========================================================
# NORMALISASI KODE WILAYAH
# =========================================================

for tabel_df in [
    df_aps,
    df_aps_2025,
    df_apm,
    df_apk
]:

    if (
        not tabel_df.empty
        and "kode_wilayah" in tabel_df.columns
    ):

        tabel_df["kode_wilayah"] = (
            tabel_df["kode_wilayah"]
            .astype(str)
            .str.strip()
            .str.replace(
                ".0",
                "",
                regex=False
            )
        )

        tabel_df["nama_wilayah"] = (
            tabel_df["kode_wilayah"]
            .map(nama_wilayah)
        )


# =========================================================
# DAFTAR WILAYAH
# =========================================================

wilayah = set()

for tabel_df in [
    df_aps,
    df_aps_2025,
    df_apm,
    df_apk
]:

    if (
        not tabel_df.empty
        and "nama_wilayah" in tabel_df.columns
    ):

        wilayah.update(
            tabel_df["nama_wilayah"]
            .dropna()
            .unique()
        )

wilayah = sorted(wilayah)


# =========================================================
# FILTER DATA
# =========================================================

st.subheader("⚙️ Filter Data")

col_f1, col_f2, col_f3 = st.columns(3)


# =========================================================
# FILTER INDIKATOR
# =========================================================

with col_f1:

    st.markdown("📊 **Pilih Indikator**")

    indikator_input = st.selectbox(
        "Pilih Data Pendidikan",
        ["APS", "APM", "APK"],
        label_visibility="collapsed"
    )


# =========================================================
# PEMETAAN TABEL BERDASARKAN INDIKATOR
# =========================================================

if indikator_input == "APS":

    tabel_input = "aps"

elif indikator_input == "APM":

    tabel_input = "apm_kabko_2025"

else:

    tabel_input = "apk_kabko_2025"


# =========================================================
# AMBIL TAHUN
# =========================================================

try:

    resp_opt = (
        supabase
        .table(tabel_input)
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

except:

    daftar_tahun_opt = []


# =========================================================
# FILTER TAHUN
# =========================================================

with col_f2:

    st.markdown("📅 **Tahun**")

    semua_tahun_chk = st.checkbox(
        "Pilih Semua",
        value=True,
        key=f"chk_semua_tahun_pendidikan_{indikator_input}"
    )

    prev_key_tahun = (
        f"_prev_chk_semua_tahun_pendidikan_"
        f"{indikator_input}"
    )

    if prev_key_tahun not in st.session_state:

        st.session_state[
            prev_key_tahun
        ] = semua_tahun_chk

    elif (
        st.session_state[prev_key_tahun]
        != semua_tahun_chk
    ):

        for thn in daftar_tahun_opt:

            st.session_state[
                f"thn_pendidikan_{thn}_{indikator_input}"
            ] = semua_tahun_chk

        st.session_state[
            prev_key_tahun
        ] = semua_tahun_chk

    with st.container(height=160):

        tahun_terpilih_input = []

        if daftar_tahun_opt:

            for thn in daftar_tahun_opt:

                cek = st.checkbox(
                    str(thn),
                    value=semua_tahun_chk,
                    key=(
                        f"thn_pendidikan_{thn}_"
                        f"{indikator_input}"
                    )
                )

                if cek:

                    tahun_terpilih_input.append(
                        int(thn)
                    )

        else:

            st.warning(
                "Tidak ada data tahun."
            )


# =========================================================
# FILTER WILAYAH
# =========================================================

try:

    resp_wil_opt = (
        supabase
        .table(tabel_input)
        .select("kode_wilayah")
        .execute()
    )

    df_wil_opt = pd.DataFrame(
        resp_wil_opt.data
    )

    if (
        not df_wil_opt.empty
        and "kode_wilayah" in df_wil_opt.columns
    ):

        df_wil_opt["kode_wilayah"] = (
            df_wil_opt["kode_wilayah"]
            .astype(str)
            .str.strip()
            .str.replace(
                ".0",
                "",
                regex=False
            )
        )

        df_wil_opt["nama_wilayah"] = (
            df_wil_opt["kode_wilayah"]
            .map(nama_wilayah)
        )

        daftar_wilayah_opt = sorted(
            df_wil_opt["nama_wilayah"]
            .dropna()
            .unique()
        )

    else:

        daftar_wilayah_opt = []

except:

    daftar_wilayah_opt = []


with col_f3:

    st.markdown("📍 **Kabupaten/Kota**")

    semua_wilayah_chk = st.checkbox(
        "Pilih Semua",
        value=True,
        key=f"chk_semua_wilayah_pendidikan_{indikator_input}"
    )

    prev_key_wilayah = (
        f"_prev_chk_semua_wilayah_pendidikan_"
        f"{indikator_input}"
    )

    if prev_key_wilayah not in st.session_state:

        st.session_state[
            prev_key_wilayah
        ] = semua_wilayah_chk

    elif (
        st.session_state[prev_key_wilayah]
        != semua_wilayah_chk
    ):

        for wil in daftar_wilayah_opt:

            st.session_state[
                f"wil_pendidikan_{wil}_{indikator_input}"
            ] = semua_wilayah_chk

        st.session_state[
            prev_key_wilayah
        ] = semua_wilayah_chk

    with st.container(height=160):

        wilayah_terpilih_input = []

        if daftar_wilayah_opt:

            for wil in daftar_wilayah_opt:

                cek_wil = st.checkbox(
                    wil,
                    value=semua_wilayah_chk,
                    key=(
                        f"wil_pendidikan_{wil}_"
                        f"{indikator_input}"
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
        "submitted_pendidikan"
    ] = True

    st.session_state[
        "indikator_final_pendidikan"
    ] = indikator_input

    st.session_state[
        "tahun_final_pendidikan"
    ] = tahun_terpilih_input

    st.session_state[
        "wilayah_final_pendidikan"
    ] = wilayah_terpilih_input


# =========================================================
# BELUM SUBMIT
# =========================================================

if not st.session_state.get(
    "submitted_pendidikan",
    False
):

    st.info(
        "👆 Silakan sesuaikan pilihan indikator, "
        "tahun, dan wilayah di atas, lalu klik tombol "
        "**Tampilkan Data**."
    )

    st.stop()


# =========================================================
# AMBIL FILTER FINAL
# =========================================================

indikator = st.session_state.get(
    "indikator_final_pendidikan",
    "APS"
)

tahun_terpilih = st.session_state.get(
    "tahun_final_pendidikan",
    []
)

wilayah_terpilih = st.session_state.get(
    "wilayah_final_pendidikan",
    []
)


# =========================================================
# VALIDASI FILTER
# =========================================================

if (
    not tahun_terpilih
    or not wilayah_terpilih
):

    st.warning(
        "⚠️ Tahun atau Kabupaten/Kota belum ada "
        "yang dicentang. Silakan centang minimal "
        "satu lalu klik Tampilkan Data."
    )

    st.stop()


# =========================================================
# LOGIKA APS
# =========================================================

if indikator == "APS":

    nama_tabel = "aps"

    df = df_aps.copy()

    df_filtered = df[
        df["nama_wilayah"].isin(
            wilayah_terpilih
        )
        & pd.to_numeric(
            df["tahun"],
            errors="coerce"
        ).isin(tahun_terpilih)
    ].copy()

    st.subheader(
        "📚 Angka Partisipasi Sekolah (APS)"
    )

    kategori_aps = st.selectbox(
        "📌 Pilih Kategori APS",
        [
            "Berdasarkan Kelompok Umur",
            "Kabupaten/Kota Tahun 2025"
        ],
        key="kategori_aps_pendidikan"
    )

    # -----------------------------------------------------
    # APS BERDASARKAN KELOMPOK UMUR
    # -----------------------------------------------------

    if kategori_aps == "Berdasarkan Kelompok Umur":

        admin_tabel = "aps"

        admin_kolom_map = {
            "usia_7_12": "7–12 Tahun",
            "usia_13_15": "13–15 Tahun"
        }

        if df_filtered.empty:

            st.info(
                "Data APS berdasarkan kelompok umur "
                "tidak tersedia untuk wilayah/tahun "
                "yang dipilih."
            )

        else:

            df_filtered["tahun"] = pd.to_numeric(
                df_filtered["tahun"],
                errors="coerce"
            )

            df_filtered = df_filtered.sort_values(
                "tahun"
            )

            kolom = [
                c
                for c in [
                    "tahun",
                    "usia_7_12",
                    "usia_13_15"
                ]
                if c in df_filtered.columns
            ]

            tabel = df_filtered[kolom].rename(
                columns={
                    "tahun": "Tahun",
                    "usia_7_12": "7–12 Tahun",
                    "usia_13_15": "13–15 Tahun"
                }
            )

            tampilkan_tabel(tabel)

            tombol_download_excel(
                tabel,
                "APS Kelompok Umur",
                "APS_Kelompok_Umur.xlsx"
            )

            st.subheader(
                "📈 Perkembangan APS"
            )

            tabel_long = tabel.melt(
                id_vars="Tahun",
                var_name="Kelompok Usia",
                value_name="APS"
            )

            fig = px.line(
                tabel_long,
                x="Tahun",
                y="APS",
                color="Kelompok Usia",
                markers=True,
                title=(
                    "Perkembangan APS "
                    "Berdasarkan Kelompok Usia"
                )
            )

            fig.update_layout(
                xaxis_title="Tahun",
                yaxis_title="APS (%)",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False)
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    # -----------------------------------------------------
    # APS KAB/KOTA 2025
    # -----------------------------------------------------

    else:

        admin_tabel = "aps_kabko_2025"

        admin_kolom_map = {
            "aps_7_12": "APS 7–12 Tahun",
            "aps_13_15": "APS 13–15 Tahun",
            "aps_16_18": "APS 16–18 Tahun",
            "aps_19_23": "APS 19–23 Tahun"
        }

        df_filtered = df_aps_2025[
            df_aps_2025["nama_wilayah"].isin(
                wilayah_terpilih
            )
        ].copy()

        df_filtered["tahun"] = pd.to_numeric(
            df_filtered["tahun"],
            errors="coerce"
        )

        df_filtered = df_filtered[
            df_filtered["tahun"].isin(
                tahun_terpilih
            )
        ]

        if df_filtered.empty:

            st.info(
                "Data APS tahun 2025 tidak tersedia "
                "untuk wilayah yang dipilih."
            )

        else:

            kolom = [
                c
                for c in [
                    "tahun",
                    "aps_7_12",
                    "aps_13_15",
                    "aps_16_18",
                    "aps_19_23"
                ]
                if c in df_filtered.columns
            ]

            tabel = df_filtered[kolom].rename(
                columns={
                    "tahun": "Tahun",
                    "aps_7_12": "APS 7–12 Tahun",
                    "aps_13_15": "APS 13–15 Tahun",
                    "aps_16_18": "APS 16–18 Tahun",
                    "aps_19_23": "APS 19–23 Tahun"
                }
            )

            tampilkan_tabel(tabel)

            tombol_download_excel(
                tabel,
                "APS 2025",
                "APS_2025.xlsx"
            )

            st.subheader(
                "📊 APS Berdasarkan Kelompok Umur"
            )

            tabel_long = tabel.melt(
                id_vars="Tahun",
                var_name="Kelompok Usia",
                value_name="APS"
            )

            fig = px.bar(
                tabel_long,
                x="Tahun",
                y="APS",
                color="Kelompok Usia",
                barmode="group",
                title=(
                    "APS Berdasarkan "
                    "Kelompok Umur"
                )
            )

            fig.update_layout(
                xaxis_title="Tahun",
                yaxis_title="APS (%)",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False)
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


# =========================================================
# LOGIKA APM
# =========================================================

elif indikator == "APM":

    nama_tabel = "apm_kabko_2025"

    admin_tabel = "apm_kabko_2025"

    admin_kolom_map = {
        "apm_sd": "APM SD",
        "apm_smp": "APM SMP",
        "apm_sma": "APM SMA",
        "apm_pt": "APM Perguruan Tinggi"
    }

    df = df_apm.copy()

    df["tahun"] = pd.to_numeric(
        df["tahun"],
        errors="coerce"
    )

    df_filtered = df[
        df["nama_wilayah"].isin(
            wilayah_terpilih
        )
        & df["tahun"].isin(
            tahun_terpilih
        )
    ].copy()

    st.subheader(
        f"📚 Angka Partisipasi Murni (APM)"
    )

    if df_filtered.empty:

        st.info(
            "Data APM tidak tersedia "
            "untuk filter yang dipilih."
        )

    else:

        kolom = [
            c
            for c in [
                "tahun",
                "apm_sd",
                "apm_smp",
                "apm_sma",
                "apm_pt"
            ]
            if c in df_filtered.columns
        ]

        tabel = df_filtered[
            ["nama_wilayah"] + kolom
        ].rename(
            columns={
                "nama_wilayah": "Kabupaten/Kota",
                "tahun": "Tahun",
                "apm_sd": "APM SD",
                "apm_smp": "APM SMP",
                "apm_sma": "APM SMA",
                "apm_pt": "APM Perguruan Tinggi"
            }
        )

        tampilkan_tabel(tabel)

        tombol_download_excel(
            tabel,
            "APM",
            "APM.xlsx"
        )

        # -------------------------------------------------
        # METRIC
        # -------------------------------------------------

        st.subheader(
            "📌 Nilai APM"
        )

        rata = df_filtered[
            [
                "apm_sd",
                "apm_smp",
                "apm_sma",
                "apm_pt"
            ]
        ].mean()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "APM SD",
                f"{rata['apm_sd']:.2f}%"
            )

        with col2:
            st.metric(
                "APM SMP",
                f"{rata['apm_smp']:.2f}%"
            )

        with col3:
            st.metric(
                "APM SMA",
                f"{rata['apm_sma']:.2f}%"
            )

        with col4:
            st.metric(
                "APM PT",
                f"{rata['apm_pt']:.2f}%"
            )

        # -------------------------------------------------
        # GRAFIK
        # -------------------------------------------------

        grafik = pd.DataFrame({
            "Jenjang": [
                "SD",
                "SMP",
                "SMA",
                "Perguruan Tinggi"
            ],
            "APM": [
                rata["apm_sd"],
                rata["apm_smp"],
                rata["apm_sma"],
                rata["apm_pt"]
            ]
        })

        st.subheader(
            "📊 Perbandingan APM Berdasarkan Jenjang"
        )

        fig = px.bar(
            grafik,
            x="Jenjang",
            y="APM",
            title=(
                "Perbandingan APM "
                "Berdasarkan Jenjang"
            )
        )

        fig.update_layout(
            xaxis_title="Jenjang",
            yaxis_title="APM (%)",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# =========================================================
# LOGIKA APK
# =========================================================

elif indikator == "APK":

    nama_tabel = "apk_kabko_2025"

    admin_tabel = "apk_kabko_2025"

    admin_kolom_map = {
        "apk_sd": "APK SD",
        "apk_smp": "APK SMP",
        "apk_sma": "APK SMA",
        "apk_pt": "APK Perguruan Tinggi"
    }

    df = df_apk.copy()

    df["tahun"] = pd.to_numeric(
        df["tahun"],
        errors="coerce"
    )

    df_filtered = df[
        df["nama_wilayah"].isin(
            wilayah_terpilih
        )
        & df["tahun"].isin(
            tahun_terpilih
        )
    ].copy()

    st.subheader(
        "📚 Angka Partisipasi Kasar (APK)"
    )

    if df_filtered.empty:

        st.info(
            "Data APK tidak tersedia "
            "untuk filter yang dipilih."
        )

    else:

        kolom = [
            c
            for c in [
                "tahun",
                "apk_sd",
                "apk_smp",
                "apk_sma",
                "apk_pt"
            ]
            if c in df_filtered.columns
        ]

        tabel = df_filtered[
            ["nama_wilayah"] + kolom
        ].rename(
            columns={
                "nama_wilayah": "Kabupaten/Kota",
                "tahun": "Tahun",
                "apk_sd": "APK SD",
                "apk_smp": "APK SMP",
                "apk_sma": "APK SMA",
                "apk_pt": "APK Perguruan Tinggi"
            }
        )

        tampilkan_tabel(tabel)

        tombol_download_excel(
            tabel,
            "APK",
            "APK.xlsx"
        )

        # -------------------------------------------------
        # METRIC
        # -------------------------------------------------

        st.subheader(
            "📌 Nilai APK"
        )

        rata = df_filtered[
            [
                "apk_sd",
                "apk_smp",
                "apk_sma",
                "apk_pt"
            ]
        ].mean()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "APK SD",
                f"{rata['apk_sd']:.2f}%"
            )

        with col2:
            st.metric(
                "APK SMP",
                f"{rata['apk_smp']:.2f}%"
            )

        with col3:
            st.metric(
                "APK SMA",
                f"{rata['apk_sma']:.2f}%"
            )

        with col4:
            st.metric(
                "APK PT",
                f"{rata['apk_pt']:.2f}%"
            )

        # -------------------------------------------------
        # GRAFIK
        # -------------------------------------------------

        grafik = pd.DataFrame({
            "Jenjang": [
                "SD",
                "SMP",
                "SMA",
                "Perguruan Tinggi"
            ],
            "APK": [
                rata["apk_sd"],
                rata["apk_smp"],
                rata["apk_sma"],
                rata["apk_pt"]
            ]
        })

        st.subheader(
            "📊 Perbandingan APK Berdasarkan Jenjang"
        )

        fig = px.bar(
            grafik,
            x="Jenjang",
            y="APK",
            title=(
                "Perbandingan APK "
                "Berdasarkan Jenjang"
            )
        )

        fig.update_layout(
            xaxis_title="Jenjang",
            yaxis_title="APK (%)",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )

        st.plotly_chart(
            fig,
            use_container_width=True
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
    and st.session_state.get(
        "show_admin_panel",
        False
    )
):

    st.markdown("---")

    st.subheader(
        f"⚙️ Panel Admin — {indikator}"
    )

    st.caption(
        f"Mengelola tabel: `{admin_tabel}`"
    )

    admin_df = TABEL_MAP[admin_tabel]

    tab_tambah, tab_edit, tab_hapus = st.tabs(
        [
            "➕ Tambah Data",
            "✏️ Edit Data",
            "🗑 Hapus Data"
        ]
    )


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
            key=f"metode_tambah_{admin_tabel}"
        )

        st.markdown("---")


        # -------------------------------------------------
        # INPUT MANUAL
        # -------------------------------------------------

        if metode == "Input Manual":

            with st.form(
                f"form_tambah_{admin_tabel}",
                clear_on_submit=True
            ):

                col_a, col_b = st.columns(2)

                with col_a:

                    tahun_baru = st.number_input(
                        "Tahun",
                        min_value=2000,
                        max_value=2100,
                        step=1
                    )

                with col_b:

                    wilayah_baru = st.selectbox(
                        "Kabupaten/Kota",
                        DAFTAR_KABKOTA,
                        key=(
                            f"tambah_wilayah_"
                            f"{admin_tabel}"
                        )
                    )

                st.markdown(
                    "**Isi nilai per indikator:**"
                )

                nilai_input = {}

                cols = st.columns(2)

                for i, (
                    raw,
                    label
                ) in enumerate(
                    admin_kolom_map.items()
                ):

                    with cols[i % 2]:

                        nilai_input[raw] = (
                            st.number_input(
                                label,
                                value=0.0,
                                key=(
                                    f"tambah_"
                                    f"{admin_tabel}_"
                                    f"{raw}"
                                )
                            )
                        )

                if st.form_submit_button(
                    "💾 Simpan Data Baru"
                ):

                    data_baru = {
                        "tahun": int(
                            tahun_baru
                        ),
                        "kode_wilayah": (
                            kode_dari_nama[
                                wilayah_baru
                            ]
                        )
                    }

                    data_baru.update(
                        nilai_input
                    )

                    try:

                        (
                            supabase_admin
                            .table(admin_tabel)
                            .insert(data_baru)
                            .execute()
                        )

                        get_data.clear()

                        set_toast(
                            "Data baru berhasil ditambahkan."
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Gagal menyimpan data: {e}"
                        )


        # -------------------------------------------------
        # IMPORT EXCEL/CSV
        # -------------------------------------------------

        else:

            with st.expander(
                "📌 Lihat daftar kode wilayah"
            ):

                st.dataframe(
                    pd.DataFrame({
                        "kode_wilayah": list(
                            nama_wilayah.keys()
                        ),
                        "Kabupaten/Kota": list(
                            nama_wilayah.values()
                        )
                    }),
                    use_container_width=True,
                    hide_index=True
                )

            kolom_wajib = (
                ["tahun", "kode_wilayah"]
                + list(
                    admin_kolom_map.keys()
                )
            )

            admin_import_data(
                supabase_admin=supabase_admin,
                table_name=admin_tabel,
                kolom_wajib=kolom_wajib,
                key_prefix=admin_tabel,
                kolom_teks=["kode_wilayah"],
                on_success=get_data.clear
            )


    # =====================================================
    # EDIT DATA
    # =====================================================

    with tab_edit:

        if admin_df.empty:

            st.info(
                "Belum ada data untuk diedit."
            )

        else:

            opsi_baris = []

            for _, row in admin_df.iterrows():

                nama_wil = row.get(
                    "nama_wilayah",
                    row.get(
                        "kode_wilayah",
                        ""
                    )
                )

                opsi_baris.append({
                    "label": (
                        f"{row['tahun']} - "
                        f"{nama_wil}"
                    ),
                    "tahun": row["tahun"],
                    "kode": row[
                        "kode_wilayah"
                    ]
                })

            pilih_baris = st.selectbox(
                "Pilih data yang mau diedit",
                opsi_baris,
                format_func=lambda x: x[
                    "label"
                ],
                key=(
                    f"pilih_edit_"
                    f"{admin_tabel}"
                )
            )

            if pilih_baris:

                baris_df = admin_df[
                    (
                        admin_df["tahun"]
                        == pilih_baris["tahun"]
                    )
                    &
                    (
                        admin_df[
                            "kode_wilayah"
                        ]
                        == pilih_baris["kode"]
                    )
                ]

                if not baris_df.empty:

                    baris = baris_df.iloc[0]

                    with st.form(
                        f"form_edit_"
                        f"{admin_tabel}"
                    ):

                        st.write(
                            "Mengedit data: "
                            f"**{pilih_baris['label']}**"
                        )

                        nilai_edit = {}

                        cols = st.columns(2)

                        for i, (
                            raw,
                            label
                        ) in enumerate(
                            admin_kolom_map.items()
                        ):

                            with cols[i % 2]:

                                nilai_edit[raw] = (
                                    st.number_input(
                                        label,
                                        value=(
                                            float(
                                                baris[raw]
                                            )
                                            if (
                                                raw
                                                in baris
                                                and pd.notna(
                                                    baris[raw]
                                                )
                                            )
                                            else 0.0
                                        ),
                                        key=(
                                            f"edit_"
                                            f"{admin_tabel}_"
                                            f"{raw}"
                                        )
                                    )
                                )

                        if st.form_submit_button(
                            "💾 Simpan Perubahan"
                        ):

                            try:

                                (
                                    supabase_admin
                                    .table(admin_tabel)
                                    .update(nilai_edit)
                                    .eq(
                                        "tahun",
                                        pilih_baris[
                                            "tahun"
                                        ]
                                    )
                                    .eq(
                                        "kode_wilayah",
                                        pilih_baris[
                                            "kode"
                                        ]
                                    )
                                    .execute()
                                )

                                get_data.clear()

                                set_toast(
                                    "Data berhasil diperbarui."
                                )

                                st.rerun()

                            except Exception as e:

                                st.error(
                                    "Gagal memperbarui data: "
                                    f"{e}"
                                )


    # =====================================================
    # HAPUS DATA
    # =====================================================

    with tab_hapus:

        if admin_df.empty:

            st.info(
                "Belum ada data untuk dihapus."
            )

        else:

            opsi_hapus = []

            for _, row in admin_df.iterrows():

                nama_wil = row.get(
                    "nama_wilayah",
                    row.get(
                        "kode_wilayah",
                        ""
                    )
                )

                opsi_hapus.append({
                    "label": (
                        f"{row['tahun']} - "
                        f"{nama_wil}"
                    ),
                    "tahun": row["tahun"],
                    "kode": row[
                        "kode_wilayah"
                    ]
                })

            pilih_hapus = st.selectbox(
                "Pilih data yang mau dihapus",
                opsi_hapus,
                format_func=lambda x: x[
                    "label"
                ],
                key=(
                    f"pilih_hapus_"
                    f"{admin_tabel}"
                )
            )

            if st.button(
                "🗑 Hapus Data Ini",
                key=(
                    f"tombol_hapus_"
                    f"{admin_tabel}"
                )
            ):

                st.session_state[
                    f"konfirmasi_hapus_"
                    f"{admin_tabel}"
                ] = pilih_hapus


            konfirmasi_key = (
                f"konfirmasi_hapus_"
                f"{admin_tabel}"
            )

            if st.session_state.get(
                konfirmasi_key
            ):

                target = st.session_state[
                    konfirmasi_key
                ]

                st.warning(
                    "Yakin ingin menghapus data "
                    f"**{target['label']}**? "
                    "Tindakan ini tidak bisa dibatalkan."
                )

                col_ya, col_batal = st.columns(2)


                # -------------------------------------------------
                # KONFIRMASI HAPUS
                # -------------------------------------------------

                with col_ya:

                    if st.button(
                        "✅ Ya, Hapus Permanen",
                        key=(
                            f"ya_hapus_"
                            f"{admin_tabel}"
                        )
                    ):

                        try:

                            (
                                supabase_admin
                                .table(admin_tabel)
                                .delete()
                                .eq(
                                    "tahun",
                                    target["tahun"]
                                )
                                .eq(
                                    "kode_wilayah",
                                    target["kode"]
                                )
                                .execute()
                            )

                            get_data.clear()

                            del st.session_state[
                                konfirmasi_key
                            ]

                            set_toast(
                                "Data berhasil dihapus."
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                f"Gagal menghapus data: {e}"
                            )


                # -------------------------------------------------
                # BATAL HAPUS
                # -------------------------------------------------

                with col_batal:

                    if st.button(
                        "❌ Batal",
                        key=(
                            f"batal_hapus_"
                            f"{admin_tabel}"
                        )
                    ):

                        del st.session_state[
                            konfirmasi_key
                        ]

                        st.rerun()