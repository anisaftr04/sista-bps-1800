"""Modul bersama untuk semua halaman Statistik Sosial.

Setiap halaman (Kemiskinan, Lainnya, dst.) cukup memanggil
`jalankan_menu(konfigurasi)`. Semua fitur (filter, tabel, grafik, Excel,
panel admin tambah/edit/hapus) ada di sini, jadi perbaikan cukup dilakukan
satu kali.

Catatan: isi halaman ditulis di dalam `jalankan_menu` (bukan di tingkat modul)
supaya data tiap pengguna tidak saling tercampur.
"""
import html as html_lib
import json
import re
from datetime import datetime, timezone
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st
from supabase import create_client, Client

from utils import load_css, admin_edit_button, set_toast, buat_template_excel

# ============================================================
# NAMA TABEL
# Jika nama tabel/kolom di Supabase berbeda, ubah di sini saja.
# ============================================================
TABEL_INDIKATOR = "statistik_variabel"
TABEL_DATA = "statistik_data"
KOLOM_FK = "variabel_id"   # kolom di TABEL_DATA yang menunjuk ke TABEL_INDIKATOR.id

# Nama kategori untuk angka yang sudah ada di tabel lama (indikator bawaan).
# Jika sebuah indikator bawaan diberi kategori, angka lamanya menjadi kategori ini.
TOTAL = "Total"

# Kolom metadata yang bisa diedit admin
KOLOM_METADATA = [
    "satuan", "sumber_data", "konsep", "definisi",
    "interpretasi", "mekanisme", "rumus", "ukuran",
]


# ============================================================
# DAFTAR WILAYAH
# ============================================================
URUTAN_KABKO = {
    "Lampung Barat": 1, "Tanggamus": 2, "Lampung Selatan": 3,
    "Lampung Timur": 4, "Lampung Tengah": 5, "Lampung Utara": 6,
    "Way Kanan": 7, "Tulang Bawang": 8, "Tulangbawang": 8,
    "Pesawaran": 9, "Pringsewu": 10, "Mesuji": 11,
    "Tulang Bawang Barat": 12, "Tulangbawang Barat": 12,
    "Pesisir Barat": 13, "Bandar Lampung": 14, "Kota Bandar Lampung": 14,
    "Metro": 15, "Kota Metro": 15, "Provinsi Lampung": 16,
}
DAFTAR_KABKO = [
    "Lampung Barat", "Tanggamus", "Lampung Selatan", "Lampung Timur",
    "Lampung Tengah", "Lampung Utara", "Way Kanan", "Tulang Bawang",
    "Pesawaran", "Pringsewu", "Mesuji", "Tulang Bawang Barat",
    "Pesisir Barat", "Bandar Lampung", "Metro", "Provinsi Lampung",
]
PETA_WILAYAH = {w.lower(): w for w in DAFTAR_KABKO}
PETA_WILAYAH.update({
    "kota bandar lampung": "Bandar Lampung",
    "kota metro": "Metro",
    "tulangbawang": "Tulang Bawang",
    "tulangbawang barat": "Tulang Bawang Barat",
})


# ============================================================
# FUNGSI MURNI
# ============================================================

def urutkan_daftar_wilayah(wilayah):
    return sorted(
        wilayah,
        key=lambda x: (URUTAN_KABKO.get(x, 9999), str(x))
    )


def format_angka_id(x, desimal=2):
    if x is None or pd.isna(x):
        return "-"
    teks = f"{x:,.{desimal}f}"
    return teks.replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")


def daftar_kategori_dari(ind):
    """Baca kolom daftar_kategori (jsonb) menjadi list teks."""
    nilai = ind.get("daftar_kategori") or []
    if isinstance(nilai, str):
        try:
            nilai = json.loads(nilai)
        except Exception:
            nilai = []
    return [str(x).strip() for x in nilai if str(x).strip()]


def punya_kategori(ind):
    return bool(ind.get("memiliki_kategori")) and bool(daftar_kategori_dari(ind))


def kotak_pilihan(judul, prefix, opsi, tinggi, key_box, teks_kosong):
    st.markdown(judul)

    ada = len(opsi) > 0

    semua = st.checkbox(
        "Pilih Semua",
        value=True,
        key=f"chk_semua_{prefix}",
        disabled=not ada
    )

    prev_key = f"_prev_chk_semua_{prefix}"

    if prev_key not in st.session_state:
        st.session_state[prev_key] = semua
    elif st.session_state[prev_key] != semua:
        for o in opsi:
            st.session_state[f"{prefix}_{o}"] = semua
        st.session_state[prev_key] = semua

    terpilih = []

    with st.container(height=tinggi, key=key_box):
        if not ada:
            st.caption(teks_kosong)

        for o in opsi:
            if st.checkbox(str(o), value=semua, key=f"{prefix}_{o}"):
                terpilih.append(o)

    return terpilih


# ============================================================
# TABEL DENGAN KATEGORI (header 2 baris: Tahun -> Kategori)
# ============================================================
CSS_TABEL = """<style>
.tabel-lainnya-wrapper {
    width: 100%;
    overflow-x: auto;
    margin-top: 10px;
    border: 1px solid #d5e3f1;
    border-radius: 8px;
}
.tabel-lainnya {
    width: 100%;
    border-collapse: collapse;
    min-width: 650px;
    font-size: 14px;
}
.tabel-lainnya th,
.tabel-lainnya td {
    border: 1px solid #d5e3f1;
    padding: 10px 12px;
    text-align: center;
    white-space: nowrap;
}
.tabel-lainnya thead th {
    color: #17365d;
    background-color: #edf5fc;
    font-weight: 600;
}
.tabel-lainnya thead tr:first-child th {
    background-color: #dceafa;
    font-size: 15px;
}
/* Hanya kolom Kabupaten/Kota (bukan sel pertama di baris header kedua) */
.tabel-lainnya tbody td:first-child,
.tabel-lainnya thead tr:first-child th:first-child {
    text-align: left;
    font-weight: 500;
    position: sticky;
    left: 0;
    z-index: 2;
}
.tabel-lainnya tbody td:first-child {
    background-color: #ffffff;
}
.tabel-lainnya thead tr:first-child th:first-child {
    background-color: #dceafa;
    z-index: 3;
}
.tabel-lainnya tbody tr:hover td {
    background-color: #f5fbfc;
}
</style>"""


def buat_tabel_html(pivot, tahun_urut, kategori_urut, desimal=2):
    """Tabel HTML: baris atas = Tahun (menyatukan kolom kategori),
    baris bawah = nama kategori. Baris = Kabupaten/Kota."""
    esc = html_lib.escape
    n_kat = len(kategori_urut)

    h = [
        '<div class="tabel-lainnya-wrapper"><table class="tabel-lainnya">'
        '<thead><tr><th rowspan="2">Kabupaten/Kota</th>'
    ]

    for t in tahun_urut:
        h.append(f'<th colspan="{n_kat}">{esc(str(t))}</th>')

    h.append("</tr><tr>")

    for t in tahun_urut:
        for k in kategori_urut:
            h.append(f"<th>{esc(str(k))}</th>")

    h.append("</tr></thead><tbody>")

    for wilayah in pivot.index:
        h.append(f"<tr><td>{esc(str(wilayah))}</td>")

        for t in tahun_urut:
            for k in kategori_urut:
                try:
                    nilai = pivot.loc[wilayah, (t, k)]
                except KeyError:
                    nilai = None
                h.append(f"<td>{format_angka_id(nilai, desimal)}</td>")

        h.append("</tr>")

    h.append("</tbody></table></div>")

    return "".join(h)


def jalankan_menu(cfg):
    """Tampilkan satu halaman menu Statistik Sosial.

    cfg (dict):
      menu             nilai kolom menu_variabel, mis. "Kemiskinan"
      prefix           awalan kunci widget (huruf kecil), mis. "kemiskinan"
      judul            judul halaman, mis. "📉 Kemiskinan"
      breadcrumb       teks breadcrumb, mis. "Statistik Sosial - Kemiskinan"
      nama_menu        nama pendek untuk teks, mis. "Kemiskinan"
      tahun_menurun    True = tahun terbaru di depan
      sumber_default   isian awal kolom sumber untuk indikator baru
      indikator_bawaan daftar indikator yang angkanya sudah ada di tabel
                       sendiri (tabel, nama, satuan, sumber_data, konsep, ...)
    """
    load_css()

    MENU = cfg["menu"]
    PREFIX = cfg["prefix"]
    NAMA_MENU = cfg.get("nama_menu", MENU)
    TAHUN_MENURUN = cfg.get("tahun_menurun", True)
    SUMBER_DEFAULT = cfg.get("sumber_default", "Badan Pusat Statistik (BPS)")
    BAWAAN = cfg.get("indikator_bawaan", [])
    DESIMAL = cfg.get("desimal", 2)
    PETA_KODE = {str(k): v for k, v in cfg.get("peta_wilayah", {}).items()}
    KODE_NAMA = {v: k for k, v in PETA_KODE.items()}

    # Jarak kotak filter (sama dengan halaman lain)
    st.markdown(
        "<style>"
        f".st-key-box_kategori_{PREFIX}, .st-key-box_tahun_{PREFIX}, "
        f".st-key-box_wilayah_{PREFIX} {{margin-top:-12px;}}"
        "</style>",
        unsafe_allow_html=True
    )

    # ------------------------------------------------------------
    # BREADCRUMB
    # ------------------------------------------------------------
    st.markdown(f"""<style>
.breadcrumb-container {{font-size:15px;color:#60758c;margin-bottom:15px;margin-top:-10px;}}
.breadcrumb-container a {{color:#0067b9;text-decoration:none;font-weight:600;}}
.breadcrumb-container a:hover {{text-decoration:underline;}}
</style>
<div class="breadcrumb-container"><a href="/" target="_self">Beranda</a> &gt; {cfg["breadcrumb"]}</div>""", unsafe_allow_html=True)

    is_admin = st.session_state.get("is_admin", False)

    # ------------------------------------------------------------
    # JUDUL + TOMBOL EDIT
    # ------------------------------------------------------------
    col_judul, col_edit = st.columns([8, 1])
    with col_judul:
        st.title(cfg["judul"])
    with col_edit:
        st.write("")
        admin_edit_button()

    # ------------------------------------------------------------
    # KONEKSI SUPABASE
    # ------------------------------------------------------------
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    service_key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
    supabase: Client = create_client(url, key)
    supabase_admin: Client = create_client(url, service_key)


    def ambil_semua(tabel, filter_eq=None, kolom="*", urut="id", klien=None):
        """Ambil seluruh baris (menembus batas 1000 baris per permintaan).

        urut: "id"; "lama" (tahun, kabupaten_kota, kategori - untuk tabel lama
        yang mungkin tidak punya kolom id/kategori); atau None.
        """
        klien = klien or supabase

        def _ambil(kolom_urut):
            hasil, mulai, ukuran = [], 0, 1000
            while True:
                q = klien.table(tabel).select(kolom)
                for k, v in (filter_eq or {}).items():
                    q = q.eq(k, v)
                for ku in kolom_urut or []:
                    q = q.order(ku)
                data = q.range(mulai, mulai + ukuran - 1).execute().data or []
                hasil.extend(data)
                if len(data) < ukuran:
                    break
                mulai += ukuran
            return hasil

        if urut == "id":
            calon = [["id"], None]
        elif isinstance(urut, tuple) and urut[0] == "lama":
            calon = [
                ["tahun", urut[1], "kategori"],
                ["tahun", urut[1]],
                None,
            ]
        else:
            calon = [None]

        ingat = st.session_state.setdefault("_urut_tabel", {})
        kunci_ingat = f"{tabel}|{urut}"
        galat = None

        for i in range(ingat.get(kunci_ingat, 0), len(calon)):
            try:
                hasil = _ambil(calon[i])
                ingat[kunci_ingat] = i
                return hasil
            except Exception as e:
                galat = e

        raise galat


    # ---------------- jenis penyimpanan indikator ----------------
    # tipe tabel lama:
    #   nilai    : kabupaten_kota, tahun, nilai
    #   kategori : kabupaten_kota, tahun, kategori, nilai
    #   lebar    : kabupaten_kota, tahun, satu kolom untuk setiap kategori
    # indikator tambahan (tanpa tabel lama) disimpan di statistik_data.

    def tipe_lama(ind):
        return ind.get("tipe") if ind.get("nama_tabel_lama") else None


    def hibrida(ind):
        """Tabel lama (tipe nilai) yang diberi kategori: Total = tabel lama."""
        return tipe_lama(ind) == "nilai" and bool(ind.get("memiliki_kategori"))


    def di_tabel_lama(ind):
        """Tabel lama tanpa kategori: seluruh angka ada di tabel lama."""
        return tipe_lama(ind) == "nilai" and not ind.get("memiliki_kategori")


    def milik_lama(ind, kategori):
        """Apakah angka kategori ini disimpan di tabel lama?"""
        t = tipe_lama(ind)
        if t is None:
            return False
        if t == "kategori":
            return True
        if t == "lebar":
            return kategori in ind["kolom_kategori"]
        return di_tabel_lama(ind) or kategori == TOTAL


    def punya_stat(ind):
        """Apakah ada angka indikator ini di statistik_data?"""
        if ind.get("id") is None:
            return False
        t = tipe_lama(ind)
        if t is None:
            return True
        if t == "kategori":
            return False
        if t == "lebar":
            return any(
                k not in ind["kolom_kategori"] for k in daftar_kategori_dari(ind)
            )
        return hibrida(ind)


    def kolom_wil(ind):
        """Nama kolom wilayah di tabel lama (kabupaten_kota atau kode_wilayah)."""
        return ind.get("kolom_wilayah") or "kabupaten_kota"


    def wilayah_dari_baris(ind, nilai):
        """Nilai kolom wilayah tabel lama -> nama kabupaten/kota (atau None)."""
        if kolom_wil(ind) == "kabupaten_kota":
            return nilai
        if nilai is None:
            return None
        teks = str(nilai).strip()
        if teks.endswith(".0"):
            teks = teks[:-2]
        return PETA_KODE.get(teks)


    def wilayah_ke_tulis(ind, nama):
        """Nama kabupaten/kota -> nilai yang ditulis ke kolom wilayah tabel lama."""
        if kolom_wil(ind) == "kabupaten_kota":
            return nama
        return KODE_NAMA[nama]


    def baris_lama_mentah(ind, klien=None):
        return ambil_semua(
            ind["nama_tabel_lama"], None, "*",
            urut=("lama", kolom_wil(ind)), klien=klien
        )


    def ambil_data(ind, klien=None):
        """Seluruh angka milik satu indikator dalam bentuk baris panjang.

        Setiap baris: kabupaten_kota, tahun, kategori, nilai, plus penanda
        sumber (_src 'lama'/'stat'), kolom (_kolom, untuk tabel lebar), dan
        uid (unik lintas tabel).
        """
        hasil = []
        t = tipe_lama(ind)

        if t:
            for r in baris_lama_mentah(ind, klien):
                mentah = r.get(kolom_wil(ind))
                wil, thn = wilayah_dari_baris(ind, mentah), r.get("tahun")
                if wil is None or thn is None:
                    continue
                try:
                    thn = int(thn)
                except (TypeError, ValueError):
                    continue

                if t == "lebar":
                    for nama, kol in ind["kolom_kategori"].items():
                        v = r.get(kol)
                        if v is None:
                            continue
                        hasil.append({
                            "kabupaten_kota": wil, "tahun": thn,
                            "kategori": nama, "nilai": v,
                            "_src": "lama", "_kolom": kol, "_wil_raw": mentah,
                            "uid": f"lama:{wil}|{thn}|{nama}",
                        })
                else:
                    if t == "kategori":
                        kat = r.get("kategori") or None
                    else:
                        kat = TOTAL if hibrida(ind) else None
                    hasil.append({
                        "kabupaten_kota": wil, "tahun": thn,
                        "kategori": kat, "nilai": r.get("nilai"),
                        "_src": "lama", "_kolom": None, "_wil_raw": mentah,
                        "uid": f"lama:{wil}|{thn}|{kat or ''}",
                    })

        if punya_stat(ind):
            for r in ambil_semua(
                TABEL_DATA, {KOLOM_FK: ind["id"]}, "*", klien=klien
            ):
                r = dict(r)
                r["_src"] = "stat"
                r["_kolom"] = None
                r["uid"] = f"stat:{r.get('id')}"
                hasil.append(r)

        return hasil


    def kunci_lama(q, ind, row):
        """Batasi query tabel lama ke satu baris (kunci alami, tanpa id)."""
        q = q.eq(
            kolom_wil(ind),
            row["_wil_raw"] if "_wil_raw" in row
            else wilayah_ke_tulis(ind, row["kabupaten_kota"])
        ).eq("tahun", int(row["tahun"]))
        if tipe_lama(ind) == "kategori":
            if row.get("kategori"):
                q = q.eq("kategori", row["kategori"])
            else:
                q = q.is_("kategori", "null")
        return q


    def bersihkan_baris_kosong(klien, ind, tahun=None):
        """Tabel lebar: hapus baris yang semua kolom kategorinya sudah kosong."""
        kolom = list(ind["kolom_kategori"].values())
        filter_eq = {"tahun": tahun} if tahun is not None else None

        for r in ambil_semua(
            ind["nama_tabel_lama"], filter_eq, "*",
            urut=("lama", kolom_wil(ind)), klien=klien
        ):
            if all(r.get(k) is None for k in kolom):
                klien.table(ind["nama_tabel_lama"]).delete().eq(
                    kolom_wil(ind), r[kolom_wil(ind)]
                ).eq("tahun", r["tahun"]).execute()


    def ubah_nilai(klien, ind, row, nilai):
        """Ubah satu angka di tempat penyimpanannya."""
        if row["_src"] == "stat":
            klien.table(TABEL_DATA).update({"nilai": nilai}).eq(
                "id", row["id"]
            ).execute()
        else:
            kolom = row["_kolom"] or "nilai"
            kunci_lama(
                klien.table(ind["nama_tabel_lama"]).update({kolom: nilai}),
                ind, row
            ).execute()


    def hapus_baris(klien, ind, row):
        """Hapus satu angka dari tempat penyimpanannya."""
        if row["_src"] == "stat":
            klien.table(TABEL_DATA).delete().eq("id", row["id"]).execute()
        elif row["_kolom"]:
            # tabel lebar: kosongkan kolom kategori itu, lalu rapikan
            kunci_lama(
                klien.table(ind["nama_tabel_lama"]).update(
                    {row["_kolom"]: None}
                ), ind, row
            ).execute()
            bersihkan_baris_kosong(klien, ind, tahun=int(row["tahun"]))
        else:
            kunci_lama(
                klien.table(ind["nama_tabel_lama"]).delete(), ind, row
            ).execute()


    def hapus_data(klien, ind, tahun=None, kategori=None, hanya_stat=False):
        """Hapus angka milik indikator (opsional per tahun dan/atau kategori)."""
        t = tipe_lama(ind)

        if t and not hanya_stat and (kategori is None or milik_lama(ind, kategori)):
            tabel = ind["nama_tabel_lama"]

            if t == "lebar" and kategori is not None:
                q = klien.table(tabel).update(
                    {ind["kolom_kategori"][kategori]: None}
                ).not_.is_("tahun", "null")
                if tahun is not None:
                    q = q.eq("tahun", tahun)
                q.execute()
                bersihkan_baris_kosong(klien, ind, tahun=tahun)
            else:
                q = klien.table(tabel).delete().not_.is_("tahun", "null")
                if t == "kategori" and kategori is not None:
                    q = q.eq("kategori", kategori)
                if tahun is not None:
                    q = q.eq("tahun", tahun)
                q.execute()

        if punya_stat(ind) and (kategori is None or not milik_lama(ind, kategori)):
            q = klien.table(TABEL_DATA).delete().eq(KOLOM_FK, ind["id"])
            if tahun is not None:
                q = q.eq("tahun", tahun)
            if kategori is not None:
                q = q.eq("kategori", kategori)
            q.execute()


    def deteksi_tipe(b):
        """Tipe tabel lama: dari konfigurasi, atau dideteksi dari kolom kategori."""
        if b.get("kolom_kategori"):
            return "lebar"
        if b.get("tipe"):
            return b["tipe"]

        cache = st.session_state.setdefault("_tipe_tabel", {})
        if b["tabel"] not in cache:
            try:
                supabase.table(b["tabel"]).select("kategori").limit(1).execute()
                cache[b["tabel"]] = "kategori"
            except Exception:
                cache[b["tabel"]] = "nilai"
        return cache[b["tabel"]]


    def bangun_indikator():
        """Gabungkan indikator bawaan (tabel lama) dan indikator tambahan (database)."""
        baris_db = ambil_semua(TABEL_INDIKATOR, {"menu_variabel": MENU})
        per_tabel = {
            r["nama_tabel_lama"]: r for r in baris_db if r.get("nama_tabel_lama")
        }

        hasil, dipakai = [], set()

        for b in BAWAAN:
            tipe = deteksi_tipe(b)
            kolom_kat = dict(b.get("kolom_kategori") or {})

            ind = {
                "id": None,
                "kunci": f"t_{b['tabel']}",
                "bawaan": True,
                "nama_indikator": b["nama"],
                "tipe": tipe,
                "kolom_kategori": kolom_kat,
                "kolom_wilayah": b.get("kolom_wilayah") or "kabupaten_kota",
                "memiliki_kategori": tipe in ("lebar", "kategori"),
                "daftar_kategori": list(kolom_kat),
                "nama_tabel_lama": b["tabel"],
            }
            for k in KOLOM_METADATA:
                ind[k] = b.get(k, "-")

            r = per_tabel.get(b["tabel"])
            if r:
                ind["id"] = r["id"]
                ind["nama_indikator"] = r.get("nama_indikator") or ind["nama_indikator"]
                for k in KOLOM_METADATA:
                    if r.get(k) not in (None, ""):
                        ind[k] = r[k]

                terdaftar = daftar_kategori_dari(r)
                if tipe == "nilai":
                    ind["memiliki_kategori"] = bool(r.get("memiliki_kategori"))
                    ind["daftar_kategori"] = terdaftar
                else:
                    ind["daftar_kategori"] = list(kolom_kat) + [
                        k for k in terdaftar if k not in kolom_kat
                    ]

            dipakai.add(b["tabel"])
            hasil.append(ind)

        for r in baris_db:
            if r.get("nama_tabel_lama") in dipakai:
                continue
            ind = dict(r)
            ind["kunci"] = r["id"]
            ind["bawaan"] = False
            ind["tipe"] = "nilai" if r.get("nama_tabel_lama") else None
            ind["kolom_kategori"] = {}
            hasil.append(ind)

        return hasil


    def muat_data(ind):
        """Data satu indikator -> kolom: kabupaten_kota, tahun, kategori, nilai."""
        baris = ambil_data(ind)

        kolom_std = ["kabupaten_kota", "tahun", "kategori", "nilai"]
        df = pd.DataFrame(baris)
        if df.empty:
            return pd.DataFrame(columns=kolom_std)

        for k in kolom_std:
            if k not in df.columns:
                df[k] = None

        df["tahun"] = pd.to_numeric(df["tahun"], errors="coerce")
        df["nilai"] = pd.to_numeric(df["nilai"], errors="coerce")
        df = df.dropna(subset=["kabupaten_kota", "tahun"]).copy()
        df["tahun"] = df["tahun"].astype(int)
        return df[kolom_std]


    def kategori_efektif(ind, df=None):
        """Daftar kategori indikator (kosong jika tidak memiliki kategori)."""
        if not ind.get("memiliki_kategori"):
            return []

        daftar = daftar_kategori_dari(ind)

        if tipe_lama(ind) == "kategori":
            # kategori bawaan tabel: ikut kategori yang sudah ada di datanya
            if df is None:
                df = muat_data(ind)
            daftar = daftar + sorted(
                k for k in df["kategori"].dropna().unique() if k not in daftar
            )

        return daftar


    def tampilkan_halaman():

        if not indikator_list:
            st.info(
                f"Belum ada indikator pada variabel {NAMA_MENU}. "
                "Admin dapat menambahkannya melalui tombol **Edit**."
            )
            return

        ind_map = {i["kunci"]: i for i in indikator_list}

        # --------------------------------------------------------
        # FILTER DATA
        # --------------------------------------------------------
        st.subheader("⚙️ Filter Data")

        col_f1, col_f2, col_f3 = st.columns(3)

        # ---- Kolom 1: indikator + kategori
        with col_f1:
            st.markdown("📊 **Pilih Indikator**")

            ind_id = st.selectbox(
                "Pilih Indikator",
                list(ind_map),
                format_func=lambda i: ind_map[i]["nama_indikator"],
                label_visibility="collapsed",
                key=f"indikator_{PREFIX}"
            )

            ind = ind_map[ind_id]

            try:
                df_all = muat_data(ind)
            except Exception as e:
                st.error(f"Gagal mengambil data indikator: {e}")
                return

            daftar_kat = kategori_efektif(ind, df_all)

            kategori_terpilih = kotak_pilihan(
                "🏷️ **Kategori**",
                f"kat_{PREFIX}_{ind_id}",
                daftar_kat,
                100,
                f"box_kategori_{PREFIX}",
                "Tidak memiliki kategori"
            )

        tahun_opsi = sorted(
            df_all["tahun"].unique().tolist(), reverse=TAHUN_MENURUN
        )
        wilayah_opsi = urutkan_daftar_wilayah(
            df_all["kabupaten_kota"].dropna().unique().tolist()
        )

        # ---- Kolom 2: tahun
        with col_f2:
            tahun_terpilih = kotak_pilihan(
                "📅 **Tahun**",
                f"thn_{PREFIX}_{ind_id}",
                tahun_opsi,
                200,
                f"box_tahun_{PREFIX}",
                "Belum ada data tahun"
            )

        # ---- Kolom 3: kabupaten/kota
        with col_f3:
            wilayah_terpilih = kotak_pilihan(
                "📍 **Kabupaten/Kota**",
                f"wil_{PREFIX}_{ind_id}",
                wilayah_opsi,
                200,
                f"box_wilayah_{PREFIX}",
                "Belum ada data wilayah"
            )

        if df_all.empty:
            st.info(
                "Belum ada data untuk indikator ini. "
                "Admin dapat menambahkannya melalui tombol **Edit**."
            )
            return

        # --------------------------------------------------------
        # TOMBOL TAMPILKAN DATA
        # --------------------------------------------------------
        st.markdown("")

        if st.button(
            "🔍 Tampilkan Data",
            use_container_width=True,
            key=f"tampil_{PREFIX}"
        ):
            st.session_state[f"final_{PREFIX}"] = {
                "ind_id": ind_id,
                "tahun": tahun_terpilih,
                "wilayah": wilayah_terpilih,
                "kategori": kategori_terpilih,
            }

        final = st.session_state.get(f"final_{PREFIX}")

        if not final:
            st.info(
                "👆 Silakan sesuaikan pilihan indikator, kategori, tahun, dan "
                "wilayah di atas, lalu klik **Tampilkan Data**."
            )
            return

        ind_final = ind_map.get(final["ind_id"])

        if ind_final is None:
            st.session_state.pop(f"final_{PREFIX}", None)
            st.info("Indikator yang dipilih sudah tidak tersedia. Pilih ulang.")
            return

        # --------------------------------------------------------
        # DATA FINAL
        # --------------------------------------------------------
        if final["ind_id"] == ind_id:
            df_final = df_all
        else:
            try:
                df_final = muat_data(ind_final)
            except Exception as e:
                st.error(f"Gagal mengambil data indikator: {e}")
                return

        daftar_kat_final = kategori_efektif(ind_final, df_final)
        kat_final_ada = bool(daftar_kat_final)

        if (
            not final["tahun"]
            or not final["wilayah"]
            or (kat_final_ada and not final["kategori"])
        ):
            st.warning(
                "⚠️ Silakan pilih minimal satu Tahun, satu Kabupaten/Kota"
                + (" dan satu Kategori." if kat_final_ada else ".")
            )
            return

        df_f = df_final[
            df_final["tahun"].isin(final["tahun"])
            & df_final["kabupaten_kota"].isin(final["wilayah"])
        ]

        if kat_final_ada:
            df_f = df_f[df_f["kategori"].isin(final["kategori"])]

        if df_f.empty:
            st.info("Tidak ada data untuk kombinasi filter yang dipilih.")
            return

        nama_indikator = ind_final["nama_indikator"]
        satuan = ind_final.get("satuan") or "-"

        # --------------------------------------------------------
        # MATRIKS
        # --------------------------------------------------------
        tahun_urut = sorted(final["tahun"], reverse=TAHUN_MENURUN)
        wilayah_urut = urutkan_daftar_wilayah(final["wilayah"])

        if kat_final_ada:
            pivot = df_f.pivot_table(
                index="kabupaten_kota",
                columns=["tahun", "kategori"],
                values="nilai",
                aggfunc="first"
            )
            kolom = [
                (t, k)
                for t in tahun_urut
                for k in daftar_kat_final
                if k in final["kategori"]
            ]
            pivot = pivot.reindex(
                columns=pd.MultiIndex.from_tuples(
                    kolom, names=["Tahun", "Kategori"]
                )
            )
        else:
            pivot = df_f.pivot_table(
                index="kabupaten_kota",
                columns="tahun",
                values="nilai",
                aggfunc="first"
            ).reindex(columns=tahun_urut)
            pivot.columns.name = "Tahun"

        pivot = pivot.reindex(wilayah_urut)
        pivot.index.name = "Kabupaten/Kota"

        tampil = pivot.apply(lambda s: s.map(lambda v: format_angka_id(v, DESIMAL)))

        st.markdown("---")
        st.subheader(f"📋 Matriks {nama_indikator} ({satuan})")

        st.write(
            "Tabel perbandingan dengan baris berupa Kabupaten/Kota "
            + (
                "dan kolom berupa Tahun serta Kategori."
                if kat_final_ada
                else "dan kolom berupa Tahun."
            )
        )

        if kat_final_ada:
            kategori_urut = [
                k for k in daftar_kat_final if k in final["kategori"]
            ]
            st.markdown(CSS_TABEL, unsafe_allow_html=True)
            st.markdown(
                buat_tabel_html(pivot, tahun_urut, kategori_urut, DESIMAL),
                unsafe_allow_html=True
            )
        else:
            st.dataframe(tampil, use_container_width=True)

        # --------------------------------------------------------
        # SUMBER + METADATA
        # --------------------------------------------------------
        st.markdown("**Sumber:**")
        st.caption(ind_final.get("sumber_data") or "-")

        with st.expander("📋 Metadata Indikator"):
            st.markdown(f"**Satuan:** {ind_final.get('satuan') or '-'}  ")
            st.markdown(f"**Sumber data:** {ind_final.get('sumber_data') or '-'}  ")
            st.markdown(f"**Konsep:** {ind_final.get('konsep') or '-'}  ")
            st.markdown(f"**Definisi:** {ind_final.get('definisi') or '-'}  ")
            st.markdown(f"**Interpretasi:** {ind_final.get('interpretasi') or '-'}  ")
            st.markdown(
                f"**Mekanisme Perhitungan:** {ind_final.get('mekanisme') or '-'}  "
            )
            st.markdown(f"**Rumus:** {ind_final.get('rumus') or '-'}  ")
            st.markdown(f"**Ukuran:** {ind_final.get('ukuran') or '-'}  ")
            st.markdown(
                "**Kategori:** "
                + (", ".join(daftar_kat_final) if kat_final_ada else "Tidak memiliki kategori")
                + "  "
            )

        # --------------------------------------------------------
        # DOWNLOAD EXCEL
        # --------------------------------------------------------
        ekspor = tampil.copy()
        if isinstance(ekspor.columns, pd.MultiIndex):
            ekspor.columns = [f"{t} - {k}" for t, k in ekspor.columns]
        else:
            ekspor.columns = [str(c) for c in ekspor.columns]
        ekspor = ekspor.reset_index()

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            ekspor.to_excel(writer, index=False, sheet_name="Data")
        output.seek(0)

        nama_aman = re.sub(r"[^\w\- ]", "", nama_indikator).strip() or "Indikator"

        st.download_button(
            label="📥 Download Excel",
            data=output,
            file_name=f"Matriks_{nama_aman}.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            key=f"download_{PREFIX}"
        )

        # --------------------------------------------------------
        # GRAFIK
        # --------------------------------------------------------
        st.markdown("---")
        st.subheader(f"📈 Grafik Tren {nama_indikator}")

        fig = px.line(
            df_f.sort_values("tahun"),
            x="tahun",
            y="nilai",
            color="kabupaten_kota",
            line_dash="kategori" if kat_final_ada else None,
            markers=True,
            category_orders={
                "kabupaten_kota": urutkan_daftar_wilayah(
                    df_f["kabupaten_kota"].dropna().unique().tolist()
                )
            },
            title=f"Tren {nama_indikator} Berdasarkan Wilayah"
        )

        fig.update_layout(
            xaxis_title="Tahun",
            yaxis_title=satuan,
            hovermode="x unified",
            xaxis=dict(showgrid=False, dtick=1),
            yaxis=dict(showgrid=False)
        )

        st.plotly_chart(fig, use_container_width=True)


    def isian_indikator(prefix, awal, kategori_wajib=False):
        """Form isian metadata indikator (dipakai untuk tambah dan edit).

        Sengaja tidak memakai st.form supaya pilihan kategori (Ya/Tidak)
        langsung memunculkan kolom isian kategori.
        """
        nama = st.text_input(
            "Nama indikator *",
            value=awal.get("nama_indikator") or "",
            key=f"{prefix}_nama",
            placeholder="Contoh: Persentase Rumah Tangga dengan Akses Internet"
        )

        c1, c2 = st.columns(2)

        with c1:
            satuan = st.text_input(
                "Satuan",
                value=awal.get("satuan") or "",
                key=f"{prefix}_satuan",
                placeholder="Contoh: Persen (%)"
            )
            sumber = st.text_input(
                "Sumber data",
                value=awal.get("sumber_data") or SUMBER_DEFAULT,
                key=f"{prefix}_sumber"
            )
            konsep = st.text_area(
                "Konsep", value=awal.get("konsep") or "", key=f"{prefix}_konsep"
            )
            definisi = st.text_area(
                "Definisi", value=awal.get("definisi") or "", key=f"{prefix}_definisi"
            )

        with c2:
            interpretasi = st.text_area(
                "Interpretasi",
                value=awal.get("interpretasi") or "",
                key=f"{prefix}_interpretasi"
            )
            mekanisme = st.text_area(
                "Mekanisme perhitungan",
                value=awal.get("mekanisme") or "",
                key=f"{prefix}_mekanisme"
            )
            rumus = st.text_input(
                "Rumus", value=awal.get("rumus") or "", key=f"{prefix}_rumus"
            )
            ukuran = st.text_input(
                "Ukuran",
                value=awal.get("ukuran") or "",
                key=f"{prefix}_ukuran",
                placeholder="Contoh: Persentase"
            )

        if kategori_wajib:
            pilihan = "Ya"
            st.caption(
                "Indikator ini memang memiliki kategori. Kategori yang sudah "
                "ada tidak bisa dihapus; Anda dapat menambah kategori baru "
                "di bawah."
            )
        else:
            pilihan = st.radio(
                "Apakah indikator ini memiliki kategori?",
                ["Tidak", "Ya"],
                index=1 if awal.get("memiliki_kategori") else 0,
                horizontal=True,
                key=f"{prefix}_punya_kategori"
            )

        kategori = []

        if pilihan == "Ya":
            teks = st.text_area(
                "Isi kategori (satu kategori per baris)",
                value="\n".join(daftar_kategori_dari(awal)),
                key=f"{prefix}_kategori",
                height=120,
                placeholder="Miskin\nTidak Miskin\nMiskin dan Tidak Miskin"
            )
            kategori = list(dict.fromkeys(
                x.strip() for x in teks.splitlines() if x.strip()
            ))

        def isi(v):
            return v.strip() or "-"

        payload = {
            "nama_indikator": nama.strip(),
            "menu_variabel": MENU,
            "satuan": isi(satuan),
            "sumber_data": isi(sumber),
            "konsep": isi(konsep),
            "definisi": isi(definisi),
            "interpretasi": isi(interpretasi),
            "mekanisme": isi(mekanisme),
            "rumus": isi(rumus),
            "ukuran": isi(ukuran),
            "memiliki_kategori": pilihan == "Ya",
            "daftar_kategori": kategori,
        }

        return payload, kategori


    def simpan_nilai(klien, ind, records):
        """Simpan nilai: perbarui yang sudah ada, tambah yang baru.

        Kunci baris = (kabupaten_kota, tahun, kategori). Angka kategori yang
        tersimpan di tabel lama ditulis ke tabel lama; kategori lain ke
        statistik_data. Mengembalikan (jumlah_baru, jumlah_diperbarui).
        """
        t = tipe_lama(ind)
        ada = ambil_data(ind, klien=klien)

        nilai_ada = {
            (r["kabupaten_kota"], int(r["tahun"]), r.get("kategori") or None)
            for r in ada
        }
        raw_ada = {
            (r["kabupaten_kota"], int(r["tahun"]), r.get("kategori") or None): r["_wil_raw"]
            for r in ada if r["_src"] == "lama"
        }
        stat_ada = {
            (r["kabupaten_kota"], int(r["tahun"]), r.get("kategori") or None): r["id"]
            for r in ada if r["_src"] == "stat"
        }
        baris_lebar_ada = {}
        if t == "lebar":
            for r in baris_lama_mentah(ind, klien):
                nama_w = wilayah_dari_baris(ind, r.get(kolom_wil(ind)))
                if r.get("tahun") is not None and nama_w is not None:
                    baris_lebar_ada[(nama_w, int(r["tahun"]))] = r[kolom_wil(ind)]

        jumlah_baru = jumlah_ubah = 0
        lebar = {}
        lama_baru, lama_ubah = [], []
        stat_baru, stat_ubah = [], []

        for r in records:
            kategori = None if di_tabel_lama(ind) else (r.get("kategori") or None)
            kunci = (r["kabupaten_kota"], r["tahun"], kategori)

            if kunci in nilai_ada:
                jumlah_ubah += 1
            else:
                jumlah_baru += 1

            if milik_lama(ind, kategori):
                if t == "lebar":
                    lebar.setdefault(
                        (r["kabupaten_kota"], r["tahun"]), {}
                    )[ind["kolom_kategori"][kategori]] = r["nilai"]
                    continue

                isi = {
                    "kabupaten_kota": r["kabupaten_kota"],
                    "tahun": r["tahun"],
                    "nilai": r["nilai"],
                }
                if t == "kategori":
                    isi["kategori"] = kategori
                if kunci in nilai_ada:
                    isi["_wil_raw"] = raw_ada[kunci]
                    lama_ubah.append(isi)
                else:
                    lama_baru.append(isi)
            else:
                isi = {
                    KOLOM_FK: ind["id"],
                    "kabupaten_kota": r["kabupaten_kota"],
                    "tahun": r["tahun"],
                    "kategori": kategori,
                    "nilai": r["nilai"],
                }
                if kunci in stat_ada:
                    isi["id"] = stat_ada[kunci]
                    stat_ubah.append(isi)
                else:
                    stat_baru.append(isi)

        def potong(daftar, ukuran=500):
            for i in range(0, len(daftar), ukuran):
                yield daftar[i:i + ukuran]

        if t:
            tabel = ind["nama_tabel_lama"]

            for kelompok in potong(lama_baru):
                klien.table(tabel).insert([
                    {
                        kolom_wil(ind): wilayah_ke_tulis(ind, x["kabupaten_kota"]),
                        **{k: v for k, v in x.items() if k != "kabupaten_kota"},
                    }
                    for x in kelompok
                ]).execute()

            # Tabel lama: ubah kolom nilai saja (tidak menyentuh kolom lain)
            for isi in lama_ubah:
                kunci_lama(
                    klien.table(tabel).update({"nilai": isi["nilai"]}), ind, isi
                ).execute()

            # Tabel lebar: satu baris per (wilayah, tahun), satu kolom per kategori
            for (wil, thn), kolom_nilai in lebar.items():
                if (wil, thn) in baris_lebar_ada:
                    klien.table(tabel).update(kolom_nilai).eq(
                        kolom_wil(ind), baris_lebar_ada[(wil, thn)]
                    ).eq("tahun", thn).execute()
                else:
                    klien.table(tabel).insert({
                        kolom_wil(ind): wilayah_ke_tulis(ind, wil),
                        "tahun": thn,
                        **kolom_nilai,
                    }).execute()

        for kelompok in potong(stat_baru):
            klien.table(TABEL_DATA).insert(kelompok).execute()
        for kelompok in potong(stat_ubah):
            klien.table(TABEL_DATA).upsert(kelompok).execute()

        return jumlah_baru, jumlah_ubah


    def blok_import(supabase_admin, ind_in, kat_in, daftar_kat_in, in_id):
        """Import Excel/CSV untuk satu indikator."""
        kolom_wajib = (
            ["kabupaten_kota", "tahun"]
            + (["kategori"] if kat_in else [])
            + ["nilai"]
        )

        st.caption(f"Kolom yang dibutuhkan: `{', '.join(kolom_wajib)}`")

        st.download_button(
            "📄 Download Template Excel",
            data=buat_template_excel(kolom_wajib, "Data"),
            file_name=f"template_{re.sub(r'[^a-z0-9]+', '_', ind_in['nama_indikator'].lower()).strip('_')}.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            key=f"template_{PREFIX}_{in_id}"
        )

        reset_up = f"reset_upload_{PREFIX}"
        st.session_state.setdefault(reset_up, 0)

        berkas = st.file_uploader(
            "Pilih file Excel (.xlsx) atau CSV (.csv)",
            type=["xlsx", "csv"],
            key=f"upload_{PREFIX}_{in_id}_{st.session_state[reset_up]}"
        )

        if berkas is not None:
            try:
                if berkas.name.lower().endswith(".csv"):
                    df_up = pd.read_csv(berkas)
                else:
                    df_up = pd.read_excel(berkas)
            except Exception as e:
                st.error(f"Gagal membaca file: {e}")
                return

            hilang = [k for k in kolom_wajib if k not in df_up.columns]
            if hilang:
                st.error(
                    f"Kolom berikut tidak ditemukan: {', '.join(hilang)}. "
                    "Pastikan nama kolom persis sama dengan template."
                )
                return

            df_up = df_up[kolom_wajib].dropna(how="all").copy()

            df_up["kabupaten_kota"] = (
                df_up["kabupaten_kota"].astype(str).str.strip()
                .map(lambda x: PETA_WILAYAH.get(x.lower(), x))
            )
            df_up["tahun"] = pd.to_numeric(df_up["tahun"], errors="coerce")
            df_up["nilai"] = pd.to_numeric(df_up["nilai"], errors="coerce")

            if kat_in:
                df_up["kategori"] = df_up["kategori"].astype(str).str.strip()
            else:
                df_up["kategori"] = None

            salah = (
                ~df_up["kabupaten_kota"].isin(DAFTAR_KABKO)
                | df_up["tahun"].isna()
                | df_up["nilai"].isna()
            )
            if kat_in:
                salah = salah | ~df_up["kategori"].isin(daftar_kat_in)

            kunci = ["kabupaten_kota", "tahun"] + (["kategori"] if kat_in else [])
            ganda = df_up.duplicated(subset=kunci, keep=False)

            if salah.any() or ganda.any():
                if salah.any():
                    st.error(
                        f"Ditemukan {int(salah.sum())} baris tidak valid "
                        "(wilayah/kategori tidak dikenal, atau tahun/nilai "
                        "kosong/bukan angka). Perbaiki dulu file-nya:"
                    )
                    st.dataframe(
                        df_up[salah][kolom_wajib],
                        use_container_width=True, hide_index=True
                    )
                if ganda.any():
                    st.error(
                        f"Ditemukan {int(ganda.sum())} baris dengan "
                        "kombinasi wilayah/tahun/kategori ganda di dalam file."
                    )
                    st.dataframe(
                        df_up[ganda][kolom_wajib],
                        use_container_width=True, hide_index=True
                    )
                return

            st.write(
                f"Ditemukan **{len(df_up)} baris** data. "
                "Pratinjau sebelum diimpor:"
            )
            st.dataframe(
                df_up[kolom_wajib],
                use_container_width=True, hide_index=True
            )

            if st.button(
                "📥 Import Semua Data Ini",
                type="primary",
                key=f"import_{PREFIX}"
            ):
                rekaman = [
                    {
                        "kabupaten_kota": r["kabupaten_kota"],
                        "tahun": int(r["tahun"]),
                        "kategori": r["kategori"] if kat_in else None,
                        "nilai": float(r["nilai"]),
                    }
                    for r in df_up.to_dict(orient="records")
                ]
                try:
                    baru, ubah = simpan_nilai(supabase_admin, ind_in, rekaman)
                    st.session_state[reset_up] += 1
                    set_toast(
                        f"Import selesai: {baru} baris baru, "
                        f"{ubah} baris diperbarui."
                    )
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal mengimpor data: {e}")


    def bersihkan_state_indikator(ind_id):
        """Buang sisa pilihan di session_state yang menunjuk ke indikator yang dihapus."""
        pola = re.compile(
            rf"_{re.escape(PREFIX)}_{re.escape(str(ind_id))}(_|$)"
        )

        for k in list(st.session_state.keys()):
            if pola.search(str(k)):
                st.session_state.pop(k, None)

        for k in [
            f"indikator_{PREFIX}",
            f"edit_pilih_{PREFIX}",
            f"input_pilih_{PREFIX}",
            f"editdata_pilih_{PREFIX}",
            f"hapus_pilih_{PREFIX}_nilai",
            f"hapus_pilih_{PREFIX}_tahun",
            f"hapus_pilih_{PREFIX}_semua",
            f"hapus_pilih_{PREFIX}_indikator",
        ]:
            if st.session_state.get(k) == ind_id:
                st.session_state.pop(k, None)

        final = st.session_state.get(f"final_{PREFIX}")
        if final and final.get("ind_id") == ind_id:
            st.session_state.pop(f"final_{PREFIX}", None)


    def blok_hapus(supabase_admin, indikator_list, indikator_baru):
        """Hapus 1 nilai, 1 tahun penuh, seluruh data indikator, atau indikatornya."""

        if not indikator_list:
            st.info("Belum ada indikator.")
            return

        MODE = {
            "nilai": "Hapus 1 nilai",
            "tahun": "Hapus data 1 tahun (semua kabupaten/kota)",
            "semua": "Hapus seluruh data indikator",
            "indikator": "Hapus indikator (beserta seluruh datanya)",
        }

        mode = st.radio(
            "Yang mau dihapus",
            list(MODE),
            format_func=MODE.get,
            key=f"hapus_mode_{PREFIX}"
        )

        pilihan = indikator_baru if mode == "indikator" else indikator_list

        if mode == "indikator" and any(i.get("bawaan") for i in indikator_list):
            st.caption(
                "Indikator bawaan tidak dapat dihapus. Hanya indikator yang "
                "ditambahkan lewat panel ini yang bisa dihapus."
            )

        if not pilihan:
            st.info("Belum ada indikator yang datanya dapat dihapus.")
            return

        peta = {i["kunci"]: i for i in pilihan}

        h_id = st.selectbox(
            "Indikator",
            list(peta),
            format_func=lambda i: peta[i]["nama_indikator"],
            key=f"hapus_pilih_{PREFIX}_{mode}"
        )

        ind = peta[h_id]
        nama = ind["nama_indikator"]
        legacy = di_tabel_lama(ind)

        try:
            baris = ambil_data(ind)
        except Exception as e:
            st.error(f"Gagal mengambil data: {e}")
            return

        extra = None
        jumlah = 0
        uraian = ""
        label_tombol = "🗑 Hapus"

        # ---------------- 1 nilai ----------------
        if mode == "nilai":
            if not baris:
                st.info("Belum ada data untuk indikator ini.")
                return

            baris.sort(key=lambda r: (
                URUTAN_KABKO.get(r["kabupaten_kota"], 9999),
                -int(r["tahun"]),
                str(r.get("kategori") or ""),
            ))
            peta_baris = {r["uid"]: r for r in baris}

            def label_baris(i):
                r = peta_baris[i]
                kat = f" - {r['kategori']}" if r.get("kategori") else ""
                return f"{r['kabupaten_kota']} - {int(r['tahun'])}{kat}: {r['nilai']}"

            extra = st.selectbox(
                "Pilih data yang mau dihapus",
                list(peta_baris),
                format_func=label_baris,
                key=f"hapus_baris_{PREFIX}"
            )

            jumlah = 1
            uraian = f"data **{label_baris(extra)}** pada indikator **{nama}**"
            label_tombol = "🗑 Hapus Data Ini"

        # ---------------- 1 tahun ----------------
        elif mode == "tahun":
            tahun_ada = sorted({int(r["tahun"]) for r in baris}, reverse=True)

            if not tahun_ada:
                st.info("Belum ada data untuk indikator ini.")
                return

            tahun_pilih = st.selectbox(
                "Pilih tahun yang mau dihapus",
                tahun_ada,
                key=f"hapus_tahun_{PREFIX}"
            )

            baris_tahun = [r for r in baris if int(r["tahun"]) == tahun_pilih]

            # Pilihan kategori (hanya jika indikatornya punya kategori)
            kategori_pilih = None
            kategori_ada = {r["kategori"] for r in baris_tahun if r.get("kategori")}

            if kategori_ada:
                urutan = daftar_kategori_dari(ind)
                kategori_opsi = (
                    [k for k in urutan if k in kategori_ada]
                    + sorted(kategori_ada - set(urutan))
                )

                SEMUA_KATEGORI = "Semua kategori"

                pilih = st.selectbox(
                    "Kategori yang mau dihapus",
                    [SEMUA_KATEGORI] + kategori_opsi,
                    key=f"hapus_kategori_{PREFIX}"
                )

                if pilih != SEMUA_KATEGORI:
                    kategori_pilih = pilih

            target = [
                r for r in baris_tahun
                if kategori_pilih is None or r.get("kategori") == kategori_pilih
            ]

            extra = (tahun_pilih, kategori_pilih)
            jumlah = len(target)
            n_wil = len({r["kabupaten_kota"] for r in target})

            cakupan = (
                f"kategori {kategori_pilih}" if kategori_pilih else "semua kategori"
            ) if kategori_ada else None

            st.caption(
                f"Akan menghapus {jumlah} nilai dari {n_wil} kabupaten/kota "
                f"pada tahun {tahun_pilih}"
                + (f" ({cakupan})." if cakupan else ".")
            )

            uraian = (
                f"**seluruh data tahun {tahun_pilih}"
                + (f" kategori {kategori_pilih}" if kategori_pilih else "")
                + f"** pada indikator **{nama}** "
                f"({jumlah} nilai dari {n_wil} kabupaten/kota)"
            )
            label_tombol = (
                f"🗑 Hapus Tahun {tahun_pilih}"
                + (f" - {kategori_pilih}" if kategori_pilih else "")
            )

        # ---------------- seluruh data ----------------
        elif mode == "semua":
            if not baris:
                st.info("Belum ada data untuk indikator ini.")
                return

            jumlah = len(baris)
            n_thn = len({int(r["tahun"]) for r in baris})

            st.caption(f"Akan menghapus {jumlah} nilai dari {n_thn} tahun.")

            uraian = (
                f"**seluruh data** indikator **{nama}** "
                f"({jumlah} nilai dari {n_thn} tahun). Indikatornya sendiri tetap ada"
            )
            label_tombol = "🗑 Hapus Seluruh Data"

        # ---------------- indikator ----------------
        else:
            jumlah = len(baris)

            if legacy:
                st.caption(
                    f"Angka indikator ini ada di tabel `{ind['nama_tabel_lama']}` "
                    "dan tidak ikut dihapus. Hanya pendaftarannya yang dihapus."
                )
            else:
                st.caption(f"Indikator ini memiliki {jumlah} nilai data.")

            uraian = (
                f"**indikator {nama}** beserta seluruh datanya ({jumlah} nilai)"
                if not legacy
                else f"**indikator {nama}** (angka di tabel lamanya tidak dihapus)"
            )
            label_tombol = "🗑 Hapus Indikator"

        # ---------------- konfirmasi ----------------
        tanda = (mode, h_id, extra)
        kunci = f"konfirmasi_hapus_{PREFIX}"

        if st.button(label_tombol, key=f"hapus_btn_{PREFIX}"):
            st.session_state[kunci] = tanda

        if st.session_state.get(kunci) != tanda:
            st.session_state.pop(kunci, None)
            return

        st.warning(
            f"Yakin ingin menghapus {uraian}? Tindakan ini tidak bisa dibatalkan."
        )

        sah = True

        if mode in ("semua", "indikator"):
            ketik = st.text_input(
                f"Ketik nama indikator persis seperti ini untuk mengonfirmasi: {nama}",
                key=f"hapus_ketik_{PREFIX}_{mode}_{h_id}"
            )
            sah = ketik.strip() == nama.strip()

        col_ya, col_batal = st.columns(2)

        with col_ya:
            ya = st.button(
                "✅ Ya, Hapus Permanen",
                key=f"ya_hapus_{PREFIX}",
                disabled=not sah
            )

        with col_batal:
            if st.button("❌ Batal", key=f"batal_hapus_{PREFIX}"):
                st.session_state.pop(kunci, None)
                st.rerun()

        if ya:
            try:
                if mode == "nilai":
                    hapus_baris(supabase_admin, ind, peta_baris[extra])
                    pesan = "Data berhasil dihapus."

                elif mode == "tahun":
                    tahun_hapus, kategori_hapus = extra
                    hapus_data(
                        supabase_admin, ind,
                        tahun=tahun_hapus, kategori=kategori_hapus
                    )
                    pesan = (
                        f"Data tahun {tahun_hapus}"
                        + (f" kategori {kategori_hapus}" if kategori_hapus else "")
                        + f" berhasil dihapus ({jumlah} nilai)."
                    )

                elif mode == "semua":
                    hapus_data(supabase_admin, ind)
                    pesan = f"Seluruh data indikator berhasil dihapus ({jumlah} nilai)."

                else:
                    if not legacy:
                        # tabel lama tidak pernah dihapus lewat menghapus indikator
                        hapus_data(supabase_admin, ind, hanya_stat=True)
                    supabase_admin.table(TABEL_INDIKATOR).delete().eq(
                        "id", ind["id"]
                    ).execute()
                    bersihkan_state_indikator(h_id)
                    pesan = "Indikator berhasil dihapus."

                st.session_state.pop(kunci, None)
                set_toast(pesan)
                st.rerun()

            except Exception as e:
                st.error(f"Gagal menghapus: {e}")


    def blok_edit_indikator(supabase_admin, indikator_list):
        """Ubah sumber, metadata, dan kategori sebuah indikator."""

        if not indikator_list:
            st.info("Belum ada indikator yang dapat diedit.")
        else:
            peta = {i["kunci"]: i for i in indikator_list}

            edit_id = st.selectbox(
                "Pilih indikator yang mau diedit",
                list(peta),
                format_func=lambda i: peta[i]["nama_indikator"],
                key=f"edit_pilih_{PREFIX}"
            )
            ind_edit = peta[edit_id]

            t_edit = tipe_lama(ind_edit)
            kategori_wajib = t_edit in ("lebar", "kategori")

            awal = dict(ind_edit)
            if t_edit == "kategori":
                awal["daftar_kategori"] = kategori_efektif(ind_edit)

            payload, kategori = isian_indikator(
                f"edit_{edit_id}", awal, kategori_wajib=kategori_wajib
            )

            tabel_lama = ind_edit.get("nama_tabel_lama")

            if t_edit == "lebar":
                st.info(
                    "Kategori bawaan ("
                    + ", ".join(ind_edit["kolom_kategori"])
                    + f") tersimpan sebagai kolom di tabel `{tabel_lama}` "
                    "dan tidak bisa dihapus. Kategori tambahan disimpan di "
                    "tabel statistik_data."
                )
            elif t_edit == "kategori":
                st.caption(
                    f"Kategori yang sudah ada tersimpan di tabel `{tabel_lama}`. "
                    "Kategori baru dapat ditambahkan di sini."
                )
            elif tabel_lama and payload["memiliki_kategori"]:
                st.info(
                    f"Kategori **{TOTAL}** otomatis ada dan berisi angka yang "
                    f"sudah tersimpan di tabel `{tabel_lama}`. Kategori lain "
                    "disimpan terpisah di tabel statistik_data. Tabel lama "
                    "tidak diubah strukturnya."
                )
            elif tabel_lama:
                st.caption(
                    f"Angka indikator ini disimpan di tabel `{tabel_lama}`. "
                    "Jika Anda mengaktifkan kategori, angka yang sudah ada "
                    f"menjadi kategori {TOTAL}."
                )

            if st.button(
                "💾 Simpan Perubahan",
                type="primary",
                use_container_width=True,
                key=f"simpan_edit_{PREFIX}"
            ):
                nama_lain = [
                    i["nama_indikator"].strip().lower()
                    for i in indikator_list if i["kunci"] != edit_id
                ]

                galat = None

                # Kategori bawaan struktur tabel lama selalu ada dan paling depan
                if t_edit == "lebar":
                    asli = list(ind_edit["kolom_kategori"])
                elif t_edit == "nilai" and payload["memiliki_kategori"]:
                    asli = [TOTAL]
                else:
                    asli = []

                if asli:
                    kecil = {a.lower() for a in asli}
                    kategori = asli + [
                        k for k in kategori if k.strip().lower() not in kecil
                    ]
                    payload["daftar_kategori"] = kategori

                if not payload["nama_indikator"]:
                    galat = "Nama indikator wajib diisi."
                elif payload["nama_indikator"].lower() in nama_lain:
                    galat = "Nama indikator sudah dipakai indikator lain."
                elif payload["memiliki_kategori"] and not kategori:
                    galat = (
                        "Isi minimal satu kategori, atau pilih "
                        "'Tidak' pada pertanyaan kategori."
                    )
                elif (
                    t_edit == "nilai"
                    and payload["memiliki_kategori"]
                    and len(kategori) < 2
                ):
                    galat = (
                        f"Isi minimal satu kategori selain {TOTAL}, atau "
                        "pilih 'Tidak' pada pertanyaan kategori."
                    )
                elif not di_tabel_lama(ind_edit):
                    # Jaga konsistensi dengan data yang sudah tersimpan
                    try:
                        baris = ambil_data(ind_edit)
                    except Exception as e:
                        baris = []
                        galat = f"Gagal memeriksa data yang ada: {e}"

                    dipakai = {r["kategori"] for r in baris if r.get("kategori")}
                    ada_tanpa_kategori = any(not r.get("kategori") for r in baris)

                    if tabel_lama and not payload["memiliki_kategori"]:
                        # Total (tabel lama) boleh tetap ada saat kategori
                        # dimatikan: angkanya kembali menjadi data biasa.
                        dipakai.discard(TOTAL)

                    if galat is None:
                        if not payload["memiliki_kategori"] and dipakai:
                            galat = (
                                "Indikator ini sudah punya data berkategori "
                                f"({', '.join(sorted(dipakai))}). Hapus data "
                                "tersebut dulu sebelum menghapus kategori."
                            )
                        elif payload["memiliki_kategori"]:
                            hilang = dipakai - set(kategori)
                            if hilang:
                                galat = (
                                    "Kategori berikut masih dipakai data dan "
                                    "tidak boleh dihapus/diganti nama: "
                                    f"{', '.join(sorted(hilang))}."
                                )
                            elif ada_tanpa_kategori and not kategori_wajib:
                                galat = (
                                    "Indikator ini sudah punya data tanpa "
                                    "kategori. Hapus data tersebut dulu "
                                    "sebelum mengaktifkan kategori."
                                )

                if galat:
                    st.error(galat)
                else:
                    try:
                        if ind_edit.get("id") is None:
                            # Indikator bawaan yang baru pertama kali diedit:
                            # daftarkan metadatanya ke tabel indikator.
                            payload["nama_tabel_lama"] = ind_edit["nama_tabel_lama"]
                            supabase_admin.table(TABEL_INDIKATOR).insert(
                                payload
                            ).execute()
                        else:
                            payload.pop("menu_variabel")
                            payload["diperbarui_pada"] = (
                                datetime.now(timezone.utc).isoformat()
                            )
                            supabase_admin.table(TABEL_INDIKATOR).update(
                                payload
                            ).eq("id", ind_edit["id"]).execute()
                        set_toast("Indikator berhasil diperbarui.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal memperbarui indikator: {e}")


    def blok_edit_data(supabase_admin, indikator_baru):
        """Ubah angka (nilai) pada data yang sudah ada."""

        if not indikator_baru:
            st.info("Belum ada indikator yang datanya dapat diedit.")
            return

        peta = {i["kunci"]: i for i in indikator_baru}

        e_id = st.selectbox(
            "Indikator",
            list(peta),
            format_func=lambda i: peta[i]["nama_indikator"],
            key=f"editdata_pilih_{PREFIX}"
        )

        try:
            baris = ambil_data(peta[e_id])
        except Exception as e:
            st.error(f"Gagal mengambil data: {e}")
            return

        if not baris:
            st.info("Belum ada data untuk indikator ini.")
            return

        baris.sort(key=lambda r: (
            URUTAN_KABKO.get(r["kabupaten_kota"], 9999),
            -int(r["tahun"]),
            str(r.get("kategori") or ""),
        ))
        peta_baris = {r["uid"]: r for r in baris}

        def label_baris(i):
            r = peta_baris[i]
            kat = f" - {r['kategori']}" if r.get("kategori") else ""
            return f"{r['kabupaten_kota']} - {int(r['tahun'])}{kat}: {r['nilai']}"

        pilih = st.selectbox(
            "Pilih data yang mau diedit",
            list(peta_baris),
            format_func=label_baris,
            key=f"editdata_baris_{PREFIX}_{e_id}"
        )

        r = peta_baris[pilih]
        ada_kategori = bool(r.get("kategori"))
        nilai_lama = float(r["nilai"]) if r.get("nilai") is not None else 0.0

        with st.container(border=True):
            st.markdown("**Data yang dipilih**")

            kolom = st.columns(4 if ada_kategori else 3)

            with kolom[0]:
                st.text_input(
                    "Kabupaten/Kota", value=r["kabupaten_kota"],
                    disabled=True, key=f"ed_wil_{PREFIX}_{pilih}"
                )
            with kolom[1]:
                st.text_input(
                    "Tahun", value=str(int(r["tahun"])),
                    disabled=True, key=f"ed_thn_{PREFIX}_{pilih}"
                )
            if ada_kategori:
                with kolom[2]:
                    st.text_input(
                        "Kategori", value=r["kategori"],
                        disabled=True, key=f"ed_kat_{PREFIX}_{pilih}"
                    )
            with kolom[-1]:
                nilai_baru = st.number_input(
                    "Nilai", value=nilai_lama, format=f"%.{DESIMAL}f",
                    key=f"ed_nilai_{PREFIX}_{pilih}"
                )

            st.caption(
                "Kabupaten/Kota, Tahun, dan Kategori tidak dapat diubah. "
                "Hanya nilainya yang dapat diedit. Kalau wilayah, tahun, atau "
                "kategorinya yang salah, hapus datanya lalu input ulang."
            )

            if st.button(
                "💾 Simpan Perubahan",
                key=f"simpan_editdata_{PREFIX}"
            ):
                if round(float(nilai_baru), DESIMAL) == round(nilai_lama, DESIMAL):
                    st.info("Tidak ada perubahan nilai.")
                else:
                    try:
                        ubah_nilai(
                            supabase_admin, peta[e_id], r, float(nilai_baru)
                        )
                        set_toast("Nilai berhasil diperbarui.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal memperbarui data: {e}")


    def tampilkan_panel_admin():

        if not (is_admin and st.session_state.get("show_admin_panel", False)):
            return

        st.markdown("---")

        st.subheader(f"⚙️ Panel Admin — Kelola Indikator {NAMA_MENU}")

        tab_tambah, tab_edit, tab_input, tab_hapus = st.tabs([
            "➕ Tambah Indikator",
            "✏️ Edit Data/Indikator",
            "🧮 Input Data",
            "🗑 Hapus Data/Indikator"
        ])

        indikator_baru = [i for i in indikator_list if not i.get("bawaan")]
        nama_ada = [i["nama_indikator"].strip().lower() for i in indikator_list]

        # ========================================================
        # TAMBAH INDIKATOR
        # ========================================================
        with tab_tambah:
            reset_key = f"reset_tambah_{PREFIX}"
            st.session_state.setdefault(reset_key, 0)

            payload, kategori = isian_indikator(
                f"tambah_{st.session_state[reset_key]}", {}
            )

            if st.button(
                "💾 Simpan Indikator",
                type="primary",
                use_container_width=True,
                key=f"simpan_tambah_{PREFIX}"
            ):
                if not payload["nama_indikator"]:
                    st.error("Nama indikator wajib diisi.")
                elif payload["nama_indikator"].lower() in nama_ada:
                    st.error("Nama indikator sudah ada pada variabel ini.")
                elif payload["memiliki_kategori"] and not kategori:
                    st.error(
                        "Isi minimal satu kategori, atau pilih "
                        "'Tidak' pada pertanyaan kategori."
                    )
                else:
                    try:
                        supabase_admin.table(TABEL_INDIKATOR).insert(payload).execute()
                        st.session_state[reset_key] += 1
                        set_toast("Indikator baru berhasil ditambahkan.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menyimpan indikator: {e}")

        # ========================================================
        # EDIT INDIKATOR
        # ========================================================
        with tab_edit:
            mode_edit = st.radio(
                "Yang mau diedit",
                ["data", "indikator"],
                format_func={
                    "data": "Edit Data (ubah angka)",
                    "indikator": "Edit Indikator (sumber, metadata, kategori)",
                }.get,
                horizontal=True,
                key=f"edit_mode_{PREFIX}"
            )

            st.markdown("---")

            if mode_edit == "data":
                blok_edit_data(supabase_admin, indikator_list)
            else:
                blok_edit_indikator(supabase_admin, indikator_list)

        # ========================================================
        # INPUT DATA
        # ========================================================
        with tab_input:
            if not indikator_list:
                st.info("Tambahkan indikator terlebih dahulu sebelum mengisi data.")
            else:
                peta = {i["kunci"]: i for i in indikator_list}

                in_id = st.selectbox(
                    "Indikator",
                    list(peta),
                    format_func=lambda i: peta[i]["nama_indikator"],
                    key=f"input_pilih_{PREFIX}"
                )
                ind_in = peta[in_id]
                daftar_kat_in = kategori_efektif(ind_in)
                kat_in = bool(daftar_kat_in)

                st.caption(
                    "Jika kombinasi wilayah, tahun, dan kategori sudah ada, "
                    "nilainya akan diperbarui."
                )

                metode = st.radio(
                    "Metode Input",
                    ["Input Manual", "Import Excel/CSV"],
                    horizontal=True,
                    key=f"metode_{PREFIX}"
                )

                st.markdown("---")

                # ---------------- manual ----------------
                if metode == "Input Manual":
                    with st.form(f"form_input_{PREFIX}", clear_on_submit=True):
                        cols = st.columns(4 if kat_in else 3)

                        with cols[0]:
                            wilayah = st.selectbox("Kabupaten/Kota", DAFTAR_KABKO)
                        with cols[1]:
                            tahun = st.number_input(
                                "Tahun", min_value=2000, max_value=2100,
                                value=2025, step=1
                            )

                        kategori_in = None
                        if kat_in:
                            with cols[2]:
                                kategori_in = st.selectbox("Kategori", daftar_kat_in)

                        with cols[-1]:
                            nilai = st.number_input(
                                "Nilai", value=0.0, format=f"%.{DESIMAL}f"
                            )

                        kirim = st.form_submit_button(
                            "💾 Simpan Data", use_container_width=True
                        )

                    if kirim:
                        try:
                            baru, ubah = simpan_nilai(supabase_admin, ind_in, [{
                                "kabupaten_kota": wilayah,
                                "tahun": int(tahun),
                                "kategori": kategori_in,
                                "nilai": float(nilai),
                            }])
                            set_toast(
                                "Data berhasil diperbarui." if ubah
                                else "Data baru berhasil ditambahkan."
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal menyimpan data: {e}")

                # ---------------- import ----------------
                else:
                    blok_import(supabase_admin, ind_in, kat_in, daftar_kat_in, in_id)

        # ========================================================
        # HAPUS
        # ========================================================
        with tab_hapus:
            blok_hapus(supabase_admin, indikator_list, indikator_baru)

    # ------------------------------------------------------------
    # JALANKAN
    # ------------------------------------------------------------
    try:
        indikator_list = bangun_indikator()
    except Exception as e:
        pesan = str(e)
        masalah_jaringan = (
            isinstance(e, (ConnectionError, TimeoutError, OSError))
            or type(e).__name__ in (
                "ConnectError", "ConnectTimeout", "ReadTimeout",
                "TimeoutException", "NetworkError", "TransportError",
            )
            or any(t in pesan for t in (
                "getaddrinfo", "11001", "Name or service not known",
                "Temporary failure in name resolution", "timed out",
                "Connection refused", "No route to host", "Max retries",
            ))
        )

        if masalah_jaringan:
            st.error(
                "Tidak dapat terhubung ke Supabase. Ini masalah jaringan "
                "(bukan masalah tabel atau RLS): alamat server Supabase tidak "
                "dapat ditemukan oleh komputer yang menjalankan aplikasi. "
                "Periksa koneksi internet, DNS, VPN atau proxy, dan pastikan "
                "`SUPABASE_URL` di secrets.toml benar, lalu muat ulang halaman."
            )
        else:
            st.error(
                "Tabel indikator belum dapat dibaca. Pastikan tabel "
                f"`{TABEL_INDIKATOR}` dan `{TABEL_DATA}` sudah dibuat di "
                "Supabase dan kebijakan baca (RLS) untuk anon sudah aktif."
            )
        with st.expander("Detail teknis"):
            st.code(pesan)
        st.stop()

    tampilkan_halaman()
    tampilkan_panel_admin()