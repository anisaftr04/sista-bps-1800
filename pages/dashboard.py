import streamlit as st
import pandas as pd
import plotly.express as px

from supabase import create_client, Client

from utils import load_css


# ============================================================
# KONFIGURASI
# ============================================================

load_css()

st.title("📊 Dashboard Statistik Sosial")

st.caption(
    "Gambaran umum kondisi dan perkembangan statistik sosial "
    "Provinsi Lampung berdasarkan tahun dan Kabupaten/Kota."
)


# ============================================================
# KONEKSI SUPABASE
# ============================================================

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(url, key)


# ============================================================
# DAFTAR KABUPATEN/KOTA
# ============================================================

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


# ============================================================
# DAFTAR TABEL
# ============================================================

DAFTAR_TABEL = {

    "Kependudukan": [
        "jumlah_penduduk",
        "kepadatan_penduduk",
        "laju_pertumbuhan_penduduk",
        "rasio_jenis_kelamin",
        "persentase_penduduk"
    ],

    "Kemiskinan": [
        "kemiskinan"
    ],

    "Ketenagakerjaan": [
        "angkatan_kerja",
        "jam_kerja",
        "lapangan_usaha",
        "pekerja_informal",
        "tpt",
        "tpak"
    ],

    "Pendidikan": [
        "aps",
        "apm",
        "apk_kabko_2025"
    ],

    "Pengeluaran Makanan": [
        "pengeluaran_makanan"
    ],

    "Perumahan": [
        "fasilitas_perumahan"
    ]
}


# ============================================================
# FUNGSI AMBIL DATA
# ============================================================

@st.cache_data(ttl=60)
def ambil_data_tabel(nama_tabel):

    try:

        response = (
            supabase
            .table(nama_tabel)
            .select("*")
            .execute()
        )

        data = response.data

        if not data:
            return pd.DataFrame()

        return pd.DataFrame(data)

    except Exception:
        return pd.DataFrame()


# ============================================================
# KUMPULKAN SEMUA DATA
# ============================================================

semua_data = []

status_tabel = {}


for kategori, daftar_tabel in DAFTAR_TABEL.items():

    for nama_tabel in daftar_tabel:

        df_temp = ambil_data_tabel(nama_tabel)

        if df_temp.empty:
            status_tabel[nama_tabel] = False
            continue

        status_tabel[nama_tabel] = True

        df_temp["kategori"] = kategori
        df_temp["nama_tabel"] = nama_tabel

        semua_data.append(df_temp)


if semua_data:

    df_semua = pd.concat(
        semua_data,
        ignore_index=True
    )

else:

    df_semua = pd.DataFrame()


# ============================================================
# FILTER
# ============================================================

st.markdown("---")

st.subheader("🔎 Filter Dashboard")


col_filter1, col_filter2 = st.columns(2)


# ------------------------------------------------------------
# FILTER TAHUN
# ------------------------------------------------------------

tahun_tersedia = []

if not df_semua.empty and "tahun" in df_semua.columns:

    tahun_tersedia = (
        pd.to_numeric(
            df_semua["tahun"],
            errors="coerce"
        )
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    tahun_tersedia = sorted(
        tahun_tersedia,
        reverse=True
    )


with col_filter1:

    if tahun_tersedia:

        tahun_pilih = st.selectbox(
            "📅 Tahun",
            tahun_tersedia
        )

    else:

        tahun_pilih = None

        st.selectbox(
            "📅 Tahun",
            ["Belum tersedia"]
        )


# ------------------------------------------------------------
# FILTER WILAYAH
# ------------------------------------------------------------

wilayah_tersedia = []

if not df_semua.empty and "kabupaten_kota" in df_semua.columns:

    wilayah_tersedia = sorted(
        df_semua["kabupaten_kota"]
        .dropna()
        .unique()
        .tolist()
    )


with col_filter2:

    pilihan_wilayah = ["Semua Kabupaten/Kota"]

    pilihan_wilayah.extend(
        wilayah_tersedia
    )

    wilayah_pilih = st.selectbox(
        "📍 Kabupaten/Kota",
        pilihan_wilayah
    )


# ============================================================
# FILTER DATA
# ============================================================

if not df_semua.empty:

    df_filter = df_semua.copy()

    df_filter["tahun"] = pd.to_numeric(
        df_filter["tahun"],
        errors="coerce"
    )

    if tahun_pilih is not None:

        df_filter = df_filter[
            df_filter["tahun"] == tahun_pilih
        ]

    if wilayah_pilih != "Semua Kabupaten/Kota":

        df_filter = df_filter[
            df_filter["kabupaten_kota"]
            == wilayah_pilih
        ]

else:

    df_filter = pd.DataFrame()


# ============================================================
# RINGKASAN UTAMA
# ============================================================

st.markdown("---")

st.subheader("📌 Ringkasan Statistik")


# ============================================================
# FUNGSI MENCARI NILAI
# ============================================================

def ambil_nilai_indikator(
    nama_tabel,
    nama_wilayah=None,
    tahun=None
):

    df = ambil_data_tabel(nama_tabel)

    if df.empty:
        return None

    if "tahun" in df.columns:

        df["tahun"] = pd.to_numeric(
            df["tahun"],
            errors="coerce"
        )

        if tahun is not None:

            df = df[
                df["tahun"] == tahun
            ]


    if (
        nama_wilayah is not None
        and nama_wilayah != "Semua Kabupaten/Kota"
        and "kabupaten_kota" in df.columns
    ):

        df = df[
            df["kabupaten_kota"]
            == nama_wilayah
        ]


    if df.empty:
        return None


    # Cari kolom nilai
    if "nilai" in df.columns:

        nilai = pd.to_numeric(
            df["nilai"],
            errors="coerce"
        ).dropna()

        if not nilai.empty:
            return nilai.iloc[0]


    return None


# ============================================================
# CARD 1 — JUMLAH PENDUDUK
# ============================================================

nilai_penduduk = ambil_nilai_indikator(
    "jumlah_penduduk",
    wilayah_pilih,
    tahun_pilih
)


# ============================================================
# CARD 2 — KEMISKINAN
# ============================================================

df_kemiskinan = ambil_data_tabel("kemiskinan")

nilai_kemiskinan = None

if not df_kemiskinan.empty:

    df_kemiskinan["tahun"] = pd.to_numeric(
        df_kemiskinan["tahun"],
        errors="coerce"
    )

    df_kemiskinan = df_kemiskinan[
        df_kemiskinan["tahun"] == tahun_pilih
    ]

    if (
        wilayah_pilih != "Semua Kabupaten/Kota"
        and "kabupaten_kota" in df_kemiskinan.columns
    ):
        df_kemiskinan = df_kemiskinan[
            df_kemiskinan["kabupaten_kota"] == wilayah_pilih
        ]

    if (
        "p0_kota_desa" in df_kemiskinan.columns
        and not df_kemiskinan.empty
    ):
        nilai_kemiskinan = pd.to_numeric(
            df_kemiskinan["p0_kota_desa"],
            errors="coerce"
        ).iloc[0]


# ============================================================
# CARD 3 — KETENAGAKERJAAN
# ============================================================

# ============================================================
# CARD 3 — KETENAGAKERJAAN
# ============================================================

df_ketenagakerjaan = ambil_data_tabel(
    "penduduk_bekerja"
)

nilai_ketenagakerjaan = None

if not df_ketenagakerjaan.empty:

    # FILTER TAHUN
    if "tahun" in df_ketenagakerjaan.columns:

        df_ketenagakerjaan["tahun"] = pd.to_numeric(
            df_ketenagakerjaan["tahun"],
            errors="coerce"
        )

        df_ketenagakerjaan = df_ketenagakerjaan[
            df_ketenagakerjaan["tahun"] == tahun_pilih
        ]

    # FILTER KABUPATEN/KOTA
    if (
        wilayah_pilih != "Semua Kabupaten/Kota"
        and "kabupaten_kota" in df_ketenagakerjaan.columns
    ):

        df_ketenagakerjaan = df_ketenagakerjaan[
            df_ketenagakerjaan["kabupaten_kota"].astype(str).str.strip()
            == str(wilayah_pilih).strip()
        ]

    # AMBIL NILAI
    if (
        not df_ketenagakerjaan.empty
        and "nilai" in df_ketenagakerjaan.columns
    ):

        nilai_ketenagakerjaan = pd.to_numeric(
            df_ketenagakerjaan["nilai"],
            errors="coerce"
        ).iloc[0]


# ============================================================
# CARD 4 — PENDIDIKAN ≥ SMA
# ============================================================

df_pendidikan = ambil_data_tabel(
    "apk_kabko_2025"
)

nilai_pendidikan = None

if not df_pendidikan.empty:

    # --------------------------------------------------------
    # FILTER TAHUN
    # --------------------------------------------------------

    if "tahun" in df_pendidikan.columns:

        df_pendidikan["tahun"] = pd.to_numeric(
            df_pendidikan["tahun"],
            errors="coerce"
        )

        df_pendidikan = df_pendidikan[
            df_pendidikan["tahun"] == tahun_pilih
        ]


    # --------------------------------------------------------
    # FILTER KABUPATEN/KOTA
    # --------------------------------------------------------

    if (
        wilayah_pilih != "Semua Kabupaten/Kota"
        and "kabupaten_kota" in df_pendidikan.columns
    ):

        df_pendidikan = df_pendidikan[
            df_pendidikan["kabupaten_kota"]
            == wilayah_pilih
        ]


    # --------------------------------------------------------
    # HITUNG PENDIDIKAN ≥ SMA
    # SMA + PERGURUAN TINGGI
    # --------------------------------------------------------

    if (
        not df_pendidikan.empty
        and "apk_sma" in df_pendidikan.columns
        and "apk_pt" in df_pendidikan.columns
    ):

        sma = pd.to_numeric(
            df_pendidikan["apk_sma"],
            errors="coerce"
        ).iloc[0]

        perguruan_tinggi = pd.to_numeric(
            df_pendidikan["apk_pt"],
            errors="coerce"
        ).iloc[0]

        nilai_pendidikan = (
            sma + perguruan_tinggi
        )

# ============================================================
# FORMAT NILAI
# ============================================================

def format_nilai(nilai, suffix=""):

    if nilai is None:
        return "—"

    try:

        return (
            f"{float(nilai):,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
            + suffix
        )

    except:

        return "—"


# ============================================================
# TAMPILKAN CARD
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        label="👥 Jumlah Penduduk",
        value=format_nilai(
            nilai_penduduk,
            " jiwa"
        )
    )


with col2:

    st.metric(
        label="📉 Kemiskinan",
        value=format_nilai(
            nilai_kemiskinan,
            "%"
        )
    )


with col3:

    st.metric(
        label="💼 Ketenagakerjaan",
        value=format_nilai(
            nilai_ketenagakerjaan,
            "%"
        )
    )


with col4:

    st.metric(
        label="🎓 Pendidikan ≥ SMA",
        value=format_nilai(
            nilai_pendidikan,
            "%"
        )
    )


# ============================================================
# PERINGATAN DATA
# ============================================================

if df_filter.empty:

    st.info(
        "Belum terdapat data untuk kombinasi "
        "tahun dan wilayah yang dipilih."
    )


# ============================================================
# PERKEMBANGAN STATISTIK
# ============================================================

st.markdown("---")

st.subheader("📈 Perkembangan Statistik")


col_grafik1, col_grafik2 = st.columns(2)


# ============================================================
# GRAFIK KEMISKINAN
# ============================================================

with col_grafik1:

    df_kemiskinan = ambil_data_tabel(
        "kemiskinan"
    )

    if not df_kemiskinan.empty:

        # ==========================================
        # KONVERSI TAHUN
        # ==========================================

        df_kemiskinan["tahun"] = pd.to_numeric(
            df_kemiskinan["tahun"],
            errors="coerce"
        )


        # ==========================================
        # FILTER KABUPATEN/KOTA
        # ==========================================

        if (
            wilayah_pilih != "Semua Kabupaten/Kota"
            and "kabupaten_kota" in df_kemiskinan.columns
        ):

            df_kemiskinan = df_kemiskinan[
                df_kemiskinan["kabupaten_kota"].astype(str).str.strip()
                == str(wilayah_pilih).strip()
            ]


        # ==========================================
        # CEK KOLOM
        # ==========================================

        if "jumlah_miskin_kota_desa" in df_kemiskinan.columns:

            df_kemiskinan["jumlah_miskin_kota_desa"] = pd.to_numeric(
                df_kemiskinan["jumlah_miskin_kota_desa"],
                errors="coerce"
            )


            # ======================================
            # HAPUS DATA KOSONG
            # ======================================

            df_kemiskinan = df_kemiskinan.dropna(
                subset=[
                    "tahun",
                    "jumlah_miskin_kota_desa"
                ]
            )


            # ======================================
            # GRAFIK
            # ======================================

            if not df_kemiskinan.empty:

                fig_kemiskinan = px.line(
                    df_kemiskinan.sort_values("tahun"),
                    x="tahun",
                    y="jumlah_miskin_kota_desa",
                    markers=True,
                    title="Perkembangan Jumlah Penduduk Miskin"
                )


                fig_kemiskinan.update_layout(
                    xaxis_title="Tahun",
                    yaxis_title="Jumlah Penduduk Miskin",
                    hovermode="x unified",
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=False)
                )


                st.plotly_chart(
                    fig_kemiskinan,
                    use_container_width=True
                )

            else:

                st.info(
                    "Data perkembangan kemiskinan belum tersedia."
                )

        else:

            st.info(
                "Kolom `jumlah_miskin_kota_desa` "
                "pada data kemiskinan belum tersedia."
            )

    else:

        st.info(
            "Data kemiskinan belum tersedia."
        )


# ============================================================
# PERBANDINGAN KABUPATEN/KOTA
# ============================================================

st.markdown("---")

st.subheader(
    "📊 Perbandingan Kabupaten/Kota"
)

st.caption(
    "Bandingkan nilai indikator antar Kabupaten/Kota "
    "pada tahun yang dipilih."
)


col_indikator, col_tahun = st.columns(2)


# ============================================================
# PILIH INDIKATOR PERBANDINGAN
# ============================================================

pilihan_indikator = {
    "Jumlah Penduduk": "jumlah_penduduk",
    "Kepadatan Penduduk": "kepadatan_penduduk",
    "Laju Pertumbuhan Penduduk": "laju_pertumbuhan_penduduk",
    "Rasio Jenis Kelamin": "rasio_jenis_kelamin",
    "Persentase Penduduk": "persentase_penduduk",
    "Persentase Kemiskinan": "kemiskinan",
    "Tingkat Pengangguran Terbuka": "tpt"
}


with col_indikator:

    indikator_pilih = st.selectbox(
        "📊 Indikator",
        list(pilihan_indikator.keys())
    )


nama_tabel_indikator = pilihan_indikator[
    indikator_pilih
]


with col_tahun:

    tahun_perbandingan = st.selectbox(
        "📅 Tahun",
        tahun_tersedia if tahun_tersedia else ["Belum tersedia"],
        key="tahun_perbandingan"
    )


# ============================================================
# DATA PERBANDINGAN
# ============================================================

df_perbandingan = ambil_data_tabel(
    nama_tabel_indikator
)


if not df_perbandingan.empty:

    df_perbandingan["tahun"] = pd.to_numeric(
        df_perbandingan["tahun"],
        errors="coerce"
    )

    if tahun_perbandingan != "Belum tersedia":

        df_perbandingan = df_perbandingan[
            df_perbandingan["tahun"]
            == tahun_perbandingan
        ]


    if "nilai" in df_perbandingan.columns:

        df_perbandingan["nilai"] = pd.to_numeric(
            df_perbandingan["nilai"],
            errors="coerce"
        )

        df_perbandingan = df_perbandingan.dropna(
            subset=["nilai"]
        )


    if (
        "kabupaten_kota" in df_perbandingan.columns
        and "nilai" in df_perbandingan.columns
        and not df_perbandingan.empty
    ):

        df_perbandingan = (
            df_perbandingan
            .sort_values(
                "nilai",
                ascending=False
            )
        )


        fig_perbandingan = px.bar(
            df_perbandingan,
            x="nilai",
            y="kabupaten_kota",
            orientation="h",
            title=(
                f"{indikator_pilih} Menurut "
                f"Kabupaten/Kota - {tahun_perbandingan}"
            ),
            text="nilai"
        )


        fig_perbandingan.update_layout(
            xaxis_title="Nilai",
            yaxis_title="Kabupaten/Kota",
            yaxis={
                "categoryorder": "total ascending"
            },
            showlegend=False
        )


        st.plotly_chart(
            fig_perbandingan,
            use_container_width=True
        )


        # ====================================================
        # TERTINGGI DAN TERENDAH
        # ====================================================

        nilai_tertinggi = df_perbandingan.iloc[0]

        nilai_terendah = df_perbandingan.iloc[-1]


        col_tertinggi, col_terendah = st.columns(2)


        with col_tertinggi:

            st.success(
                f"""
                🔴 **Nilai Tertinggi**

                **{nilai_tertinggi['kabupaten_kota']}**

                {format_nilai(nilai_tertinggi['nilai'])}
                """
            )


        with col_terendah:

            st.info(
                f"""
                🟢 **Nilai Terendah**

                **{nilai_terendah['kabupaten_kota']}**

                {format_nilai(nilai_terendah['nilai'])}
                """
            )


    else:

        st.info(
            "Data perbandingan belum tersedia."
        )

else:

    st.info(
        f"Data {indikator_pilih.lower()} belum tersedia."
    )


# ============================================================
# JELAJAHI STATISTIK
# ============================================================

st.markdown("---")

st.subheader(
    "📚 Jelajahi Statistik Sosial"
)

st.caption(
    "Pilih kategori untuk melihat data statistik secara lebih detail."
)


col_a, col_b, col_c = st.columns(3)
col_d, col_e, col_f = st.columns(3)


with col_a:

    st.info(
        """
        ### 📉 Kemiskinan

        Informasi mengenai kondisi dan perkembangan
        kemiskinan masyarakat.
        """
    )


with col_b:

    st.info(
        """
        ### 💼 Ketenagakerjaan

        Informasi mengenai kondisi ketenagakerjaan
        masyarakat.
        """
    )

with col_c:

    st.info(
        """
        ### 🍽️ Pengeluaran Makanan

        Informasi mengenai pengeluaran konsumsi
        makanan masyarakat.
        """
    )

with col_d:

    st.info(
        """
        ### 🎓 Pendidikan

        Informasi mengenai indikator pendidikan
        masyarakat.
        """
    )


with col_e:

    st.info(
        """
        ### 👥 Kependudukan

        Informasi mengenai jumlah dan karakteristik
        penduduk.
        """
    )


with col_f:

    st.info(
        """
        ### 🏠 Perumahan

        Informasi mengenai kondisi dan karakteristik
        perumahan.
        """
    )


# ============================================================
# SUMBER DATA
# ============================================================

st.markdown("---")

st.caption(
    "Sumber data: Badan Pusat Statistik (BPS) Provinsi Lampung."
)