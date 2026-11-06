import json
import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from supabase import create_client

from utils import load_css

load_css()

PROV = "Provinsi Lampung"
SEMUA = "Semua Kabupaten/Kota"

DAFTAR_KABKOTA = [
    "Bandar Lampung", "Metro", "Lampung Barat", "Lampung Selatan", "Lampung Tengah",
    "Lampung Timur", "Lampung Utara", "Mesuji", "Pesawaran", "Pesisir Barat",
    "Pringsewu", "Tanggamus", "Tulang Bawang", "Tulang Bawang Barat", "Way Kanan",
]

# Koreksi ejaan nama yang berbeda antar tabel (setelah di-title-case)
KOREKSI_NAMA = {"Tulangbawang": "Tulang Bawang", "Tulangbawang Barat": "Tulang Bawang Barat"}

# ============================================================
# KONFIGURASI INDIKATOR
# tabel/kolom = sumber di Supabase, satuan = label, warna = skala peta
# ============================================================

INDIKATOR = {
    "Jumlah Penduduk": dict(tabel="jumlah_penduduk", kolom="nilai", satuan="ribu jiwa", warna="Blues"),
    "Kepadatan Penduduk": dict(tabel="kepadatan_penduduk", kolom="nilai", satuan="jiwa/km²", warna="Purples"),
    "Laju Pertumbuhan Penduduk": dict(tabel="laju_pertumbuhan_penduduk", kolom="nilai", satuan="%", warna="Oranges"),
    "Rasio Jenis Kelamin": dict(tabel="rasio_jenis_kelamin", kolom="nilai", satuan="per 100 perempuan", warna="Teal"),
    "Persentase Penduduk Miskin": dict(tabel="p0_persen_pend_miskin", kolom="nilai", satuan="%", warna="Reds", khusus="kemiskinan"),
    "Jumlah Penduduk Miskin": dict(tabel="jumlah_penduduk_miskin", kolom="nilai", satuan="ribu jiwa", warna="Reds"),
    # TPT dihitung: pengangguran terbuka / angkatan kerja x 100 (lihat catatan)
    "Tingkat Pengangguran Terbuka": dict(khusus="tpt", satuan="%", warna="OrRd"),
    "Angkatan Kerja": dict(tabel="angkatan_kerja", kolom="nilai", satuan="jiwa", warna="Greens", desimal=0),
    "APS 7–12 Tahun": dict(tabel="aps", kolom="usia_7_12", satuan="%", warna="YlGn"),
    "APS 13–15 Tahun": dict(tabel="aps", kolom="usia_13_15", satuan="%", warna="YlGn"),
    "APK SMA (2025)": dict(tabel="apk_kabko_2025", kolom="apk_sma", satuan="%", warna="YlGnBu"),
    "Porsi Pengeluaran Makanan": dict(tabel="pengeluaran_makanan", kolom="miskin_dan_tidak_miskin", satuan="%", warna="YlOrBr"),
    "Akses Air Layak": dict(tabel="fasilitas_perumahan", kolom="air_layak", satuan="%", warna="Blues"),
    "Akses Jamban Sendiri/Bersama": dict(tabel="fasilitas_perumahan", kolom="jamban_sendiri_bersama", satuan="%", warna="Purples"),
}

KPI = [  # (label, indikator, warna delta)
    ("👥 Jumlah Penduduk", "Jumlah Penduduk", "normal"),
    ("📉 Penduduk Miskin", "Persentase Penduduk Miskin", "inverse"),
    ("💼 Pengangguran (TPT)", "Tingkat Pengangguran Terbuka", "inverse"),
    ("🎓 APS 13–15 Tahun", "APS 13–15 Tahun", "normal"),
]

KELOMPOK = {
    "👥 Kependudukan": ["Jumlah Penduduk", "Kepadatan Penduduk", "Laju Pertumbuhan Penduduk", "Rasio Jenis Kelamin"],
    "📉 Kemiskinan": ["Persentase Penduduk Miskin", "Jumlah Penduduk Miskin"],
    "💼 Ketenagakerjaan": ["Tingkat Pengangguran Terbuka", "Angkatan Kerja"],
    "🎓 Pendidikan": ["APS 7–12 Tahun", "APS 13–15 Tahun"],
    "🏠 Perumahan & Konsumsi": ["Akses Air Layak", "Akses Jamban Sendiri/Bersama", "Porsi Pengeluaran Makanan"],
}

# ============================================================
# DATA
# ============================================================


@st.cache_resource
def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


@st.cache_data(ttl=3600, show_spinner=False)
def ambil_tabel(nama_tabel):
    """Ambil seluruh baris tabel (dengan paginasi, batas default Supabase 1000 baris)."""
    sb, baris, awal, ukuran = get_supabase(), [], 0, 1000
    try:
        while True:
            data = (
                sb.table(nama_tabel).select("*").order("id")
                .range(awal, awal + ukuran - 1).execute().data or []
            )
            baris += data
            if len(data) < ukuran:
                break
            awal += ukuran
    except Exception:
        return pd.DataFrame()
    return pd.DataFrame(baris)


def normalisasi_nama(nama):
    """'Kab. Lampung Barat', 'KOTA METRO', 'TULANGBAWANG' -> nama baku seperti di GeoJSON."""
    nama = re.sub(r"(?i)^(kabupaten|kab\.?|kota)\s+", "", str(nama).strip()).title()
    return KOREKSI_NAMA.get(nama, nama)


def standar(df, kolom):
    """Ubah tabel apa pun menjadi kolom: kabupaten_kota, tahun, nilai."""
    if df.empty or kolom not in df.columns:
        return pd.DataFrame(columns=["kabupaten_kota", "tahun", "nilai"])
    out = pd.DataFrame({
        "kabupaten_kota": df["kabupaten_kota"].map(normalisasi_nama),
        "tahun": pd.to_numeric(df["tahun"], errors="coerce"),
        "nilai": pd.to_numeric(df[kolom], errors="coerce"),
    }).dropna()
    out["tahun"] = out["tahun"].astype(int)
    return out.drop_duplicates(["kabupaten_kota", "tahun"], keep="last")


@st.cache_data(ttl=3600, show_spinner=False)
def muat_indikator(nama):
    cfg = INDIKATOR[nama]

    if cfg.get("khusus") == "tpt":
        ak = standar(ambil_tabel("angkatan_kerja"), "nilai")
        pg = standar(ambil_tabel("tpt"), "nilai")  # berisi jumlah pengangguran terbuka
        m = ak.merge(pg, on=["kabupaten_kota", "tahun"], suffixes=("_ak", "_pg"))
        prov = m.groupby("tahun", as_index=False)[["nilai_ak", "nilai_pg"]].sum()
        prov["kabupaten_kota"] = PROV
        m = pd.concat([m, prov], ignore_index=True)
        m["nilai"] = m["nilai_pg"] / m["nilai_ak"] * 100
        return m[["kabupaten_kota", "tahun", "nilai"]].dropna()

    df = standar(ambil_tabel(cfg["tabel"]), cfg["kolom"])

    if cfg.get("khusus") == "kemiskinan":  # angka provinsi dari tabel 'kemiskinan'
        k = ambil_tabel("kemiskinan")
        if not k.empty and "p0_kota_desa" in k.columns:
            k["periode"] = pd.to_datetime(k["periode"], errors="coerce")
            k = k.sort_values("periode").groupby("tahun").tail(1)  # periode terakhir tiap tahun
            prov = pd.DataFrame({
                "kabupaten_kota": PROV,
                "tahun": pd.to_numeric(k["tahun"], errors="coerce"),
                "nilai": pd.to_numeric(k["p0_kota_desa"], errors="coerce"),
            }).dropna()
            prov["tahun"] = prov["tahun"].astype(int)
            df = pd.concat([df, prov], ignore_index=True).drop_duplicates(["kabupaten_kota", "tahun"])
    return df


@st.cache_data
def muat_geojson():
    here = Path(__file__).resolve().parent
    for p in (Path("data/lampung.geojson"), here.parent / "data" / "lampung.geojson", here / "data" / "lampung.geojson"):
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    return None


# ============================================================
# UTILITAS
# ============================================================


def fmt(nilai, desimal=2, satuan="", tanda=False):
    if nilai is None or pd.isna(nilai):
        return "—"
    teks = format(float(nilai), f"{'+' if tanda else ''},.{desimal}f")
    teks = teks.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{teks} {satuan}".strip()


def nilai_kpi(nama, tahun_acuan, wilayah):
    """Nilai terbaru (<= tahun acuan), selisih dari data sebelumnya, dan tahun datanya."""
    df = muat_indikator(nama)
    target = PROV if wilayah == SEMUA else wilayah
    d = df[(df["kabupaten_kota"] == target) & (df["tahun"] <= tahun_acuan)].sort_values("tahun")
    if d.empty:
        return None, None, None
    delta = d.iloc[-1]["nilai"] - d.iloc[-2]["nilai"] if len(d) > 1 else None
    return d.iloc[-1]["nilai"], delta, int(d.iloc[-1]["tahun"])


def grafik_tren(nama, wilayah):
    cfg, df = INDIKATOR[nama], muat_indikator(nama)
    if wilayah == SEMUA:
        d = df[df["kabupaten_kota"] == PROV]
        if d.empty:
            d = df[df["kabupaten_kota"] != PROV]
    else:
        d = df[df["kabupaten_kota"].isin([wilayah, PROV])]
    if d.empty:
        st.info(f"Data {nama} belum tersedia untuk pilihan ini.")
        return
    fig = px.line(
        d.sort_values("tahun"), x="tahun", y="nilai", color="kabupaten_kota",
        markers=True, title=f"{nama} ({cfg['satuan']})",
    )
    fig.update_layout(
        xaxis_title=None, yaxis_title=None, legend_title_text=None,
        hovermode="x unified", margin=dict(l=0, r=0, t=40, b=0), height=340,
    )
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# HALAMAN
# ============================================================

st.title("📊 Dashboard Statistik Sosial")
st.caption(
    "Gambaran umum kondisi dan perkembangan statistik sosial "
    "Provinsi Lampung berdasarkan tahun dan Kabupaten/Kota."
)

geojson = muat_geojson()
daftar_wilayah = (
    sorted(f["properties"]["kabupaten_kota"] for f in geojson["features"])
    if geojson else sorted(DAFTAR_KABKOTA)
)

tahun_kpi = sorted(
    {int(t) for _, nama, _ in KPI for t in muat_indikator(nama)["tahun"].unique()}, reverse=True
)
if not tahun_kpi:
    st.error("Data belum dapat dimuat dari Supabase.")
    st.stop()

# ---------------- Filter ----------------
st.markdown("---")
f1, f2 = st.columns(2)
tahun_pilih = f1.selectbox("📅 Tahun acuan", tahun_kpi)
wilayah_pilih = f2.selectbox("📍 Kabupaten/Kota", [SEMUA] + daftar_wilayah)

# ---------------- KPI ----------------
st.subheader("📌 Ringkasan Statistik")
st.caption(
    f"Menampilkan {PROV if wilayah_pilih == SEMUA else wilayah_pilih}. "
    "Bila data tahun acuan belum ada, dipakai data terbaru sebelumnya (tahun tertera di label)."
)

for kolom, (label, nama, warna_delta) in zip(st.columns(4), KPI):
    cfg = INDIKATOR[nama]
    d = cfg.get("desimal", 2)
    nilai, delta, thn = nilai_kpi(nama, tahun_pilih, wilayah_pilih)
    sat_delta = "poin" if cfg["satuan"] == "%" else cfg["satuan"]
    kolom.metric(
        f"{label} ({thn})" if thn else label,
        fmt(nilai, d, cfg["satuan"]),
        fmt(delta, d, sat_delta, tanda=True) if delta is not None else None,
        delta_color=warna_delta,
        help="Selisih terhadap data tahun sebelumnya yang tersedia.",
    )

# ---------------- Peta + ranking ----------------
st.markdown("---")
st.subheader("🗺️ Peta Sebaran Antar Kabupaten/Kota")

ci, ct = st.columns([3, 1])
nama_ind = ci.selectbox("📊 Indikator", list(INDIKATOR))
cfg = INDIKATOR[nama_ind]
desimal = cfg.get("desimal", 2)
df_ind = muat_indikator(nama_ind)
df_kab = df_ind[df_ind["kabupaten_kota"] != PROV]
tahun_ind = sorted(df_kab["tahun"].unique().tolist(), reverse=True)

if not tahun_ind:
    st.info(f"Data {nama_ind.lower()} belum tersedia.")
else:
    tahun_peta = ct.selectbox("📅 Tahun", tahun_ind)
    d = df_kab[df_kab["tahun"] == tahun_peta].sort_values("nilai").copy()

    kiri, kanan = st.columns([3, 2])

    with kiri:
        if geojson is None:
            st.warning("File `data/lampung.geojson` tidak ditemukan.")
        else:
            if hasattr(px, "choropleth_map"):
                fn, gaya = px.choropleth_map, {"map_style": "carto-positron"}
            else:  # plotly < 5.24
                fn, gaya = px.choropleth_mapbox, {"mapbox_style": "carto-positron"}
            fig_peta = fn(
                d, geojson=geojson, locations="kabupaten_kota",
                featureidkey="properties.kabupaten_kota", color="nilai",
                color_continuous_scale=cfg["warna"],
                center={"lat": -4.85, "lon": 105.0}, zoom=7, opacity=0.8, height=520,
                hover_name="kabupaten_kota", hover_data={"kabupaten_kota": False, "nilai": ":,.2f"},
                labels={"nilai": cfg["satuan"] or "nilai"}, **gaya,
            )
            fig_peta.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                coloraxis_colorbar=dict(title=cfg["satuan"], thickness=12),
            )
            st.plotly_chart(fig_peta, use_container_width=True)
            tidak_cocok = sorted(set(d["kabupaten_kota"]) - set(daftar_wilayah))
            if tidak_cocok:
                st.warning("Nama berikut tidak cocok dengan peta: " + ", ".join(tidak_cocok))

    with kanan:
        if d.empty:
            st.info("Tidak ada data pada tahun ini.")
        else:
            d["sorot"] = d["kabupaten_kota"].eq(wilayah_pilih).map({True: "Dipilih", False: "Lainnya"})
            fig_bar = px.bar(
                d, x="nilai", y="kabupaten_kota", orientation="h", color="sorot",
                color_discrete_map={"Dipilih": "#d62728", "Lainnya": "#4c78a8"},
                text=d["nilai"].map(lambda v: fmt(v, desimal)),
            )
            fig_bar.update_traces(textposition="outside", cliponaxis=False)
            fig_bar.update_layout(
                showlegend=False, xaxis_title=cfg["satuan"], yaxis_title=None,
                height=520, margin=dict(l=0, r=40, t=10, b=0),
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    if not d.empty:
        tinggi, rendah = d.iloc[-1], d.iloc[0]
        teks = (
            f"Pada {tahun_peta}, **{nama_ind.lower()}** tertinggi di **{tinggi['kabupaten_kota']}** "
            f"({fmt(tinggi['nilai'], desimal, cfg['satuan'])}) dan terendah di **{rendah['kabupaten_kota']}** "
            f"({fmt(rendah['nilai'], desimal, cfg['satuan'])})."
        )
        prov = df_ind[(df_ind["kabupaten_kota"] == PROV) & (df_ind["tahun"] == tahun_peta)]
        if not prov.empty:
            teks += f" Angka {PROV}: {fmt(prov.iloc[0]['nilai'], desimal, cfg['satuan'])}."
        st.info(teks)

        with st.expander("Lihat tabel data"):
            tabel = d.sort_values("nilai", ascending=False)[["kabupaten_kota", "nilai"]].rename(
                columns={"kabupaten_kota": "Kabupaten/Kota", "nilai": f"{nama_ind} ({cfg['satuan']})"}
            )
            st.dataframe(tabel, hide_index=True, use_container_width=True)
            st.download_button(
                "⬇️ Unduh CSV", tabel.to_csv(index=False).encode("utf-8"),
                file_name=f"indikator_{tahun_peta}.csv", mime="text/csv",
            )

# ---------------- Tren ----------------
st.markdown("---")
st.subheader("📈 Perkembangan Statistik")
st.caption(
    "Menampilkan Provinsi Lampung"
    if wilayah_pilih == SEMUA
    else f"Menampilkan {wilayah_pilih} dibandingkan dengan {PROV} (bila tersedia)."
)

for tab, daftar in zip(st.tabs(list(KELOMPOK)), KELOMPOK.values()):
    with tab:
        for i in range(0, len(daftar), 2):
            for kol, nama in zip(st.columns(2), daftar[i:i + 2]):
                with kol:
                    grafik_tren(nama, wilayah_pilih)

st.markdown("---")
st.caption("Sumber data: Badan Pusat Statistik (BPS) Provinsi Lampung.")