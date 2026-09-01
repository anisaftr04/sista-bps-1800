import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from io import BytesIO

from utils import load_css, admin_edit_button, set_toast, admin_import_data

load_css()

is_admin = st.session_state.get("is_admin", False)

# ============================================================
# JUDUL + TOMBOL EDIT
# ============================================================

col_judul, col_edit = st.columns([8, 1])

with col_judul:
    st.title("📉 Kemiskinan")

with col_edit:
    st.write("")
    admin_edit_button()

# ============================================================
# KONEKSI SUPABASE
# ============================================================

url = st.secrets["SUPABASE_URL"] 
key = st.secrets["SUPABASE_KEY"] 
service_key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"] 
supabase: Client = create_client(url, key) 
supabase_admin: Client = create_client(url, service_key)

# ============================================================
# AMBIL DATA
# ============================================================

response = supabase.table("kemiskinan").select("*").execute()
data = response.data

if not data:
    st.warning("Data Kemiskinan belum tersedia.")
    st.stop()

df = pd.DataFrame(data)
df["tahun"] = pd.to_numeric(df["tahun"], errors="coerce")
df = df.sort_values("tahun")

# ============================================================
# PILIH INDIKATOR
# ============================================================

daftar_indikator = {
    "P0 - Persentase Penduduk Miskin": {
        "kota": "p0_kota",
        "desa": "p0_desa",
        "kota_desa": "p0_kota_desa"
    },

    "Garis Kemiskinan": {
        "kota": "garis_kemiskinan_kota",
        "desa": "garis_kemiskinan_desa",
        "kota_desa": "garis_kemiskinan_kota_desa"
    },

    "Jumlah Penduduk Miskin": {
        "kota": "jumlah_miskin_kota",
        "desa": "jumlah_miskin_desa",
        "kota_desa": "jumlah_miskin_kota_desa"
    },

    "P1 - Indeks Kedalaman Kemiskinan": {
        "kota": "p1_kota",
        "desa": "p1_desa",
        "kota_desa": "p1_kota_desa"
    },

    "P2 - Indeks Keparahan Kemiskinan": {
        "kota": "p2_kota",
        "desa": "p2_desa",
        "kota_desa": "p2_kota_desa"
    },

    "Gini Ratio": {
        "kota": "gini_kota",
        "desa": "gini_desa",
        "kota_desa": "gini_kota_desa"
    }
}

indikator = st.selectbox(
    "📊 Pilih Indikator",
    list(daftar_indikator.keys())
)

wilayah_pilihan = {
    "Kota": "kota",
    "Desa": "desa",
    "Kota + Desa": "kota_desa"
}

wilayah = st.selectbox(
    "📍 Pilih Wilayah",
    list(wilayah_pilihan.keys())
)

kolom_data = daftar_indikator[
    indikator
][
    wilayah_pilihan[wilayah]
]

df_tampil = df[
    [
        "tahun",
        "periode",
        kolom_data
    ]
].copy()

df_tampil = df_tampil.rename(
    columns={
        "tahun": "Tahun",
        "periode": "Periode",
        kolom_data: "Nilai"
    }
)

df_tampil = df_tampil.sort_values("Tahun")

st.subheader(
    f"📉 {indikator} - {wilayah}"
)

st.write(
    f"Data tahun "
    f"{df_tampil['Tahun'].min()}–"
    f"{df_tampil['Tahun'].max()}."
)

st.dataframe(
    df_tampil,
    use_container_width=True,
    hide_index=True
)
# ============================================================
# DOWNLOAD EXCEL
# ============================================================

output = BytesIO()

with pd.ExcelWriter(
    output,
    engine="openpyxl"
) as writer:

    df_tampil.to_excel(
        writer,
        index=False,
        sheet_name="Kemiskinan"
    )

output.seek(0)

st.download_button(
    label="📥 Download Excel Kemiskinan",
    data=output,
    file_name=f"Kemiskinan_{indikator}_{wilayah}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ============================================================
# GRAFIK
# ============================================================

fig = px.line(
    df_tampil,
    x="Tahun",
    y="Nilai",
    markers=True,
    title=f"{indikator} - {wilayah}"
)

fig.update_layout(
    xaxis_title="Tahun",
    yaxis_title="Nilai",
    hovermode="x unified",
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
st.caption("Sumber data: Badan Pusat Statistik (BPS).")

# ============================================================
# PANEL ADMIN
# ============================================================

if is_admin and st.session_state.get(
    "show_admin_panel",
    False
):

    st.markdown("---")

    st.subheader(
        "⚙️ Panel Admin — Kelola Data Kemiskinan"
    )

    semua_kolom_nilai = []

    for ind in daftar_indikator.values():
        semua_kolom_nilai.extend(
            ind.values()
        )

    semua_kolom_nilai = sorted(
        set(semua_kolom_nilai)
    )

    tab_tambah, tab_edit, tab_hapus = st.tabs(
        [
            "➕ Tambah Data",
            "✏️ Edit Data",
            "🗑 Hapus Data"
        ]
    )

    # ========================================================
    # TAMBAH DATA
    # ========================================================

    with tab_tambah:

        metode = st.radio(
            "Metode Input",
            ["Input Manual", "Import Excel/CSV"],
            horizontal=True,
            key="metode_tambah_kemiskinan"
        )

        st.markdown("---")

        if metode == "Input Manual":

            with st.form("form_tambah_kemiskinan", clear_on_submit=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    tahun_baru = st.number_input("Tahun", min_value=2000, max_value=2100, step=1)
                with col_b:
                    periode_baru = st.text_input("Periode", placeholder="Misal: Maret / September")

                st.markdown("**Isi nilai per indikator:**")
                nilai_input = {}
                cols = st.columns(3)
                for i, kolom in enumerate(semua_kolom_nilai):
                    with cols[i % 3]:
                        nilai_input[kolom] = st.number_input(kolom.replace("_", " ").title(), value=0.0, key=f"tambah_{kolom}")

                if st.form_submit_button("💾 Simpan Data Baru"):
                    data_baru = {"tahun": int(tahun_baru), "periode": periode_baru}
                    data_baru.update(nilai_input)
                    try:
                        supabase_admin.table("kemiskinan").insert(data_baru).execute()
                        set_toast("Data baru berhasil ditambahkan.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menyimpan data: {e}")

        else:

            kolom_wajib = ["tahun", "periode"] + semua_kolom_nilai
            admin_import_data(
                supabase_admin=supabase_admin,
                table_name="kemiskinan",
                kolom_wajib=kolom_wajib,
                key_prefix="kemiskinan",
                kolom_teks=["periode"]
            )

    # ========================================================
    # EDIT DATA
    # ========================================================

    with tab_edit:

        opsi_baris = [
            f"{row['tahun']} - {row['periode']}"
            for _, row in df.iterrows()
        ]

        pilih_baris = st.selectbox(
            "Pilih data yang mau diedit",
            opsi_baris,
            key="pilih_edit"
        )

        if pilih_baris:

            tahun_pilih, periode_pilih = (
                pilih_baris.split(
                    " - ",
                    1
                )
            )

            baris = df[
                (
                    df["tahun"]
                    == int(tahun_pilih)
                )
                &
                (
                    df["periode"]
                    == periode_pilih
                )
            ].iloc[0]

            with st.form(
                "form_edit_kemiskinan"
            ):

                st.write(
                    f"Mengedit data: **{pilih_baris}**"
                )

                nilai_edit = {}

                cols = st.columns(3)

                for i, kolom in enumerate(
                    semua_kolom_nilai
                ):

                    with cols[i % 3]:

                        nilai_edit[kolom] = st.number_input(
                            kolom.replace(
                                "_",
                                " "
                            ).title(),

                            value=(
                                float(baris[kolom])
                                if pd.notna(
                                    baris[kolom]
                                )
                                else 0.0
                            ),

                            key=f"edit_{kolom}"
                        )

                if st.form_submit_button(
                    "💾 Simpan Perubahan"
                ):

                    try:

                        (
                            supabase_admin
                            .table("kemiskinan")
                            .update(nilai_edit)
                            .eq(
                                "tahun",
                                int(tahun_pilih)
                            )
                            .eq(
                                "periode",
                                periode_pilih
                            )
                            .execute()
                        )

                        # POPUP BERHASIL
                        set_toast(
                            "Data berhasil diperbarui."
                        )

                    except Exception as e:

                        st.error(
                            f"Gagal memperbarui data: {e}"
                        )

    # ========================================================
    # HAPUS DATA
    # ========================================================

    with tab_hapus:

        opsi_hapus = [
            f"{row['tahun']} - {row['periode']}"
            for _, row in df.iterrows()
        ]

        pilih_hapus = st.selectbox(
            "Pilih data yang mau dihapus",
            opsi_hapus,
            key="pilih_hapus"
        )

        if st.button(
            "🗑 Hapus Data Ini",
            key="tombol_hapus"
        ):

            st.session_state[
                "konfirmasi_hapus_kemiskinan"
            ] = pilih_hapus

        if st.session_state.get(
            "konfirmasi_hapus_kemiskinan"
        ):

            target = st.session_state[
                "konfirmasi_hapus_kemiskinan"
            ]

            st.warning(
                f"Yakin ingin menghapus data "
                f"**{target}**? "
                f"Tindakan ini tidak bisa dibatalkan."
            )

            col_ya, col_batal = st.columns(2)

            with col_ya:

                if st.button(
                    "✅ Ya, Hapus Permanen",
                    key="ya_hapus_kemiskinan"
                ):

                    tahun_hapus, periode_hapus = (
                        target.split(
                            " - ",
                            1
                        )
                    )

                    try:

                        (
                            supabase_admin
                            .table("kemiskinan")
                            .delete()
                            .eq(
                                "tahun",
                                int(tahun_hapus)
                            )
                            .eq(
                                "periode",
                                periode_hapus
                            )
                            .execute()
                        )

                        del st.session_state[
                            "konfirmasi_hapus_kemiskinan"
                        ]

                        # POPUP BERHASIL
                        set_toast(
                            "Data berhasil dihapus."
                        )
                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Gagal menghapus data: {e}"
                        )

            with col_batal:

                if st.button(
                    "❌ Batal",
                    key="batal_hapus_kemiskinan"
                ):

                    del st.session_state[
                        "konfirmasi_hapus_kemiskinan"
                    ]

                    st.rerun()