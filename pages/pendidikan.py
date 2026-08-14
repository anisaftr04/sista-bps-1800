import streamlit as st
import pandas as pd
from supabase import create_client

# =========================================================
# KONFIGURASI SUPABASE
# =========================================================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# =========================================================
# JUDUL
# =========================================================
st.title("📚 Indikator Pendidikan")

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
# AMBIL SEMUA DATA
# =========================================================
df_aps = get_data("aps")
df_aps_2025 = get_data("aps_kabko_2025")
df_apm = get_data("apm_kabko_2025")
df_apk = get_data("apk_kabko_2025")


# =========================================================
# NORMALISASI KODE WILAYAH
# =========================================================
for df in [
    df_aps,
    df_aps_2025,
    df_apm,
    df_apk
]:

    if not df.empty and "kode_wilayah" in df.columns:

        df["kode_wilayah"] = (
            df["kode_wilayah"]
            .astype(str)
            .str.strip()
            .str.replace(".0", "", regex=False)
        )

        df["nama_wilayah"] = (
            df["kode_wilayah"]
            .map(nama_wilayah)
        )


# =========================================================
# GABUNG DAFTAR WILAYAH
# =========================================================
wilayah = set()

for df in [
    df_aps,
    df_aps_2025,
    df_apm,
    df_apk
]:

    if not df.empty and "nama_wilayah" in df.columns:

        wilayah.update(
            df["nama_wilayah"]
            .dropna()
            .unique()
        )

wilayah = sorted(wilayah)


# =========================================================
# PILIH WILAYAH
# =========================================================
st.subheader("📍 Pilih Kabupaten/Kota")

pilihan_wilayah = st.selectbox(
    "Kabupaten/Kota",
    wilayah
)


# =========================================================
# PILIH INDIKATOR
# =========================================================
st.subheader("📊 Pilih Indikator Pendidikan")

indikator = st.selectbox(
    "Indikator",
    [
        "APS",
        "APM",
        "APK"
    ]
)


# =========================================================
# =========================================================
# APS
# =========================================================
# =========================================================

if indikator == "APS":

    st.divider()

    st.subheader(
        f"📚 Angka Partisipasi Sekolah (APS) — {pilihan_wilayah}"
    )

    # -----------------------------------------------------
    # SUB-KATEGORI APS
    # -----------------------------------------------------
    kategori_aps = st.selectbox(
        "Kategori APS",
        [
            "Berdasarkan Kelompok Umur",
            "Kabupaten/Kota Tahun 2025"
        ]
    )


    # -----------------------------------------------------
    # APS LAMA
    # -----------------------------------------------------
    if kategori_aps == "Berdasarkan Kelompok Umur":

        df = df_aps[
            df_aps["nama_wilayah"] == pilihan_wilayah
        ].copy()

        if df.empty:

            st.info(
                "Data APS berdasarkan kelompok umur "
                "tidak tersedia untuk wilayah ini."
            )

        else:

            df = df.sort_values("tahun")

            kolom = [
                col for col in [
                    "tahun",
                    "usia_7_12",
                    "usia_13_15"
                ]
                if col in df.columns
            ]

            tabel = df[kolom].copy()

            tabel = tabel.rename(
                columns={
                    "tahun": "Tahun",
                    "usia_7_12": "7–12 Tahun",
                    "usia_13_15": "13–15 Tahun"
                }
            )

            st.dataframe(
                tabel,
                use_container_width=True,
                hide_index=True
            )

            if len(tabel.columns) > 1:

                st.subheader(
                    "📈 Perkembangan APS"
                )

                st.line_chart(
                    tabel.set_index("Tahun")
                )


    # -----------------------------------------------------
    # APS 2025
    # -----------------------------------------------------
    else:

        df = df_aps_2025[
            df_aps_2025["nama_wilayah"] == pilihan_wilayah
        ].copy()

        if df.empty:

            st.info(
                "Data APS tahun 2025 "
                "tidak tersedia untuk wilayah ini."
            )

        else:

            kolom = [
                col for col in [
                    "tahun",
                    "aps_7_12",
                    "aps_13_15",
                    "aps_16_18",
                    "aps_19_23"
                ]
                if col in df.columns
            ]

            tabel = df[kolom].copy()

            tabel = tabel.rename(
                columns={
                    "tahun": "Tahun",
                    "aps_7_12": "APS 7–12 Tahun",
                    "aps_13_15": "APS 13–15 Tahun",
                    "aps_16_18": "APS 16–18 Tahun",
                    "aps_19_23": "APS 19–23 Tahun"
                }
            )

            st.dataframe(
                tabel,
                use_container_width=True,
                hide_index=True
            )

            st.subheader(
                "📊 APS Berdasarkan Kelompok Umur Tahun 2025"
            )

            st.bar_chart(
                tabel.set_index("Tahun")
            )


# =========================================================
# =========================================================
# APM
# =========================================================
# =========================================================

elif indikator == "APM":

    st.divider()

    st.subheader(
        f"🎓 Angka Partisipasi Murni (APM) — {pilihan_wilayah}"
    )

    df = df_apm[
        df_apm["nama_wilayah"] == pilihan_wilayah
    ].copy()

    if df.empty:

        st.info(
            "Data APM tidak tersedia untuk wilayah ini."
        )

    else:

        # -------------------------------------------------
        # TABEL APM
        # -------------------------------------------------
        kolom = [
            "tahun",
            "apm_sd",
            "apm_smp",
            "apm_sma",
            "apm_pt"
        ]

        kolom = [
            col for col in kolom
            if col in df.columns
        ]

        tabel = df[kolom].copy()

        tabel = tabel.rename(
            columns={
                "tahun": "Tahun",
                "apm_sd": "APM SD",
                "apm_smp": "APM SMP",
                "apm_sma": "APM SMA",
                "apm_pt": "APM Perguruan Tinggi"
            }
        )

        st.dataframe(
            tabel,
            use_container_width=True,
            hide_index=True
        )

        # -------------------------------------------------
        # KPI
        # -------------------------------------------------
        st.subheader("📌 Nilai APM Tahun 2025")

        data = df.iloc[0]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "APM SD",
                f"{data['apm_sd']:.2f}%"
            )

        with col2:
            st.metric(
                "APM SMP",
                f"{data['apm_smp']:.2f}%"
            )

        with col3:
            st.metric(
                "APM SMA",
                f"{data['apm_sma']:.2f}%"
            )

        with col4:
            st.metric(
                "APM PT",
                f"{data['apm_pt']:.2f}%"
            )

        # -------------------------------------------------
        # GRAFIK
        # -------------------------------------------------
        st.subheader(
            "📊 Perbandingan APM Berdasarkan Jenjang"
        )

        grafik = pd.DataFrame({
            "Jenjang": [
                "SD",
                "SMP",
                "SMA",
                "Perguruan Tinggi"
            ],
            "APM": [
                data["apm_sd"],
                data["apm_smp"],
                data["apm_sma"],
                data["apm_pt"]
            ]
        })

        st.bar_chart(
            grafik.set_index("Jenjang")
        )


# =========================================================
# =========================================================
# APK
# =========================================================
# =========================================================

elif indikator == "APK":

    st.divider()

    st.subheader(
        f"🎒 Angka Partisipasi Kasar (APK) — {pilihan_wilayah}"
    )

    df = df_apk[
        df_apk["nama_wilayah"] == pilihan_wilayah
    ].copy()

    if df.empty:

        st.info(
            "Data APK tidak tersedia untuk wilayah ini."
        )

    else:

        # -------------------------------------------------
        # TABEL APK
        # -------------------------------------------------
        kolom = [
            "tahun",
            "apk_sd",
            "apk_smp",
            "apk_sma",
            "apk_pt"
        ]

        kolom = [
            col for col in kolom
            if col in df.columns
        ]

        tabel = df[kolom].copy()

        tabel = tabel.rename(
            columns={
                "tahun": "Tahun",
                "apk_sd": "APK SD",
                "apk_smp": "APK SMP",
                "apk_sma": "APK SMA",
                "apk_pt": "APK Perguruan Tinggi"
            }
        )

        st.dataframe(
            tabel,
            use_container_width=True,
            hide_index=True
        )

        # -------------------------------------------------
        # KPI
        # -------------------------------------------------
        st.subheader("📌 Nilai APK Tahun 2025")

        data = df.iloc[0]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "APK SD",
                f"{data['apk_sd']:.2f}%"
            )

        with col2:
            st.metric(
                "APK SMP",
                f"{data['apk_smp']:.2f}%"
            )

        with col3:
            st.metric(
                "APK SMA",
                f"{data['apk_sma']:.2f}%"
            )

        with col4:
            st.metric(
                "APK PT",
                f"{data['apk_pt']:.2f}%"
            )

        # -------------------------------------------------
        # GRAFIK
        # -------------------------------------------------
        st.subheader(
            "📊 Perbandingan APK Berdasarkan Jenjang"
        )

        grafik = pd.DataFrame({
            "Jenjang": [
                "SD",
                "SMP",
                "SMA",
                "Perguruan Tinggi"
            ],
            "APK": [
                data["apk_sd"],
                data["apk_smp"],
                data["apk_sma"],
                data["apk_pt"]
            ]
        })

        st.bar_chart(
            grafik.set_index("Jenjang")
        )


# =========================================================
# INFORMASI
# =========================================================
st.divider()

st.caption(
    "Sumber data: Badan Pusat Statistik (BPS)."
)