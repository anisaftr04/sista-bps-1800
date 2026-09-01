import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from io import BytesIO

from utils import load_css, admin_edit_button, set_toast, admin_import_data

load_css()

is_admin = st.session_state.get("is_admin", False)

DAFTAR_KABKOTA = [
    "Bandar Lampung", "Metro", "Lampung Barat", "Lampung Selatan",
    "Lampung Tengah", "Lampung Timur", "Lampung Utara", "Mesuji",
    "Pesawaran", "Pesisir Barat", "Pringsewu", "Tanggamus",
    "Tulang Bawang", "Tulang Bawang Barat", "Way Kanan"
]

col_judul, col_edit = st.columns([8, 1])
with col_judul:
    st.title("🏠 Fasilitas Perumahan")
with col_edit:
    st.write("")
    admin_edit_button()


# =============================
# KONEKSI SUPABASE
# =============================

url = st.secrets["SUPABASE_URL"] 
key = st.secrets["SUPABASE_KEY"] 
service_key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"] 

supabase: Client = create_client(url, key) 
supabase_admin: Client = create_client(url, service_key)


# =============================
# AMBIL DATA
# =============================

response = supabase.table("fasilitas_perumahan").select("*").execute()
data = response.data

if not data:
    st.warning("Data Fasilitas Perumahan belum tersedia.")
    st.stop()

df = pd.DataFrame(data)
df["tahun"] = pd.to_numeric(df["tahun"], errors="coerce")


# =============================
# PILIH KABUPATEN/KOTA
# =============================

daftar_wilayah = sorted(df["kabupaten_kota"].dropna().unique())
wilayah = st.selectbox("📍 Pilih Kabupaten/Kota", daftar_wilayah)

df_wilayah = df[df["kabupaten_kota"] == wilayah].copy()
df_wilayah = df_wilayah.sort_values("tahun")


# =============================
# JUDUL
# =============================

st.subheader(f"🏠 Fasilitas Perumahan - {wilayah}")
st.write(f"Data tahun {df_wilayah['tahun'].min()}–{df_wilayah['tahun'].max()}.")


# =============================
# TABEL
# =============================

df_tabel = df_wilayah[
    ["tahun", "air_layak", "jamban_sendiri_bersama"]
].copy()

df_tabel = df_tabel.rename(columns={
    "tahun": "Tahun",
    "air_layak": "Air Layak",
    "jamban_sendiri_bersama": "Jamban Sendiri/Bersama"
})

st.dataframe(
    df_tabel,
    use_container_width=True,
    hide_index=True
)


# =============================
# DOWNLOAD EXCEL
# =============================

output = BytesIO()

with pd.ExcelWriter(output, engine="openpyxl") as writer:
    df_tabel.to_excel(
        writer,
        index=False,
        sheet_name="Fasilitas Perumahan"
    )

output.seek(0)

st.download_button(
    label="📥 Download Excel Fasilitas Perumahan",
    data=output,
    file_name=f"Fasilitas_Perumahan_{wilayah}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


# =============================
# GRAFIK
# =============================

df_grafik = df_wilayah[
    ["tahun", "air_layak", "jamban_sendiri_bersama"]
].copy()

df_grafik = df_grafik.rename(columns={
    "air_layak": "Air Layak",
    "jamban_sendiri_bersama": "Jamban Sendiri/Bersama"
})

df_long = df_grafik.melt(
    id_vars="tahun",
    var_name="Kategori",
    value_name="Persentase"
)

fig = px.line(
    df_long,
    x="tahun",
    y="Persentase",
    color="Kategori",
    markers=True,
    title=f"Fasilitas Perumahan - {wilayah}"
)

fig.update_layout(
    xaxis_title="Tahun",
    yaxis_title="Persentase (%)",
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False)
)

st.plotly_chart(fig, use_container_width=True)


# =========================================================
# INFORMASI
# =========================================================

st.caption("Sumber data: Badan Pusat Statistik (BPS).")


# =============================
# PANEL ADMIN
# =============================

if is_admin and st.session_state.get("show_admin_panel", False):

    st.markdown("---")
    st.subheader("⚙️ Panel Admin — Fasilitas Perumahan")

    tab_tambah, tab_edit, tab_hapus = st.tabs([
        "➕ Tambah Data",
        "✏️ Edit Data",
        "🗑 Hapus Data"
    ])


    # =====================================================
    # TAMBAH DATA
    # =====================================================

    with tab_tambah:

        metode = st.radio(
            "Metode Input",
            ["Input Manual", "Import Excel/CSV"],
            horizontal=True,
            key="metode_tambah_perumahan"
        )


        # =================================================
        # INPUT MANUAL
        # =================================================

        if metode == "Input Manual":

            with st.form(
                "form_tambah_perumahan",
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
                    kabkota_baru = st.selectbox(
                        "Kabupaten/Kota",
                        DAFTAR_KABKOTA,
                        key="tambah_kabkota_rmh"
                    )

                col_c, col_d = st.columns(2)

                with col_c:
                    air_baru = st.number_input(
                        "Air Layak (%)",
                        value=0.0
                    )

                with col_d:
                    jamban_baru = st.number_input(
                        "Jamban Sendiri/Bersama (%)",
                        value=0.0
                    )

                if st.form_submit_button("💾 Simpan Data Baru"):

                    data_baru = {
                        "tahun": int(tahun_baru),
                        "kabupaten_kota": kabkota_baru,
                        "air_layak": air_baru,
                        "jamban_sendiri_bersama": jamban_baru
                    }

                    try:

                        supabase_admin.table(
                            "fasilitas_perumahan"
                        ).insert(data_baru).execute()

                        set_toast(
                            "✅ Data baru berhasil ditambahkan."
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
                table_name="fasilitas_perumahan",
                kolom_wajib=kolom_wajib,
                key_prefix="fasilitas_perumahan",
                kolom_teks=kolom_teks
            )


    # =====================================================
    # EDIT DATA
    # =====================================================

    with tab_edit:

        opsi_baris = [
            f"{row['tahun']} - {row['kabupaten_kota']}"
            for _, row in df.iterrows()
        ]

        pilih_baris = st.selectbox(
            "Pilih data yang mau diedit",
            opsi_baris,
            key="pilih_edit_rmh"
        )

        if pilih_baris:

            tahun_pilih, kabkota_pilih = pilih_baris.split(
                " - ",
                1
            )

            tahun_pilih = int(tahun_pilih)

            baris = df[
                (df["tahun"] == tahun_pilih) &
                (df["kabupaten_kota"] == kabkota_pilih)
            ].iloc[0]

            with st.form("form_edit_perumahan"):

                st.write(
                    f"Mengedit data: **{pilih_baris}**"
                )

                col_c, col_d = st.columns(2)

                with col_c:
                    air_edit = st.number_input(
                        "Air Layak (%)",
                        value=float(baris["air_layak"])
                    )

                with col_d:
                    jamban_edit = st.number_input(
                        "Jamban Sendiri/Bersama (%)",
                        value=float(
                            baris["jamban_sendiri_bersama"]
                        )
                    )

                if st.form_submit_button(
                    "💾 Simpan Perubahan"
                ):

                    try:

                        supabase_admin.table(
                            "fasilitas_perumahan"
                        ).update({
                            "air_layak": air_edit,
                            "jamban_sendiri_bersama": jamban_edit
                        }).eq(
                            "tahun",
                            tahun_pilih
                        ).eq(
                            "kabupaten_kota",
                            kabkota_pilih
                        ).execute()

                        set_toast(
                            "✅ Data berhasil diperbarui."
                        )

                        st.rerun()

                    except Exception as e:
                        st.error(
                            f"Gagal memperbarui data: {e}"
                        )


    # =====================================================
    # HAPUS DATA
    # =====================================================

    with tab_hapus:

        opsi_hapus = [
            f"{row['tahun']} - {row['kabupaten_kota']}"
            for _, row in df.iterrows()
        ]

        pilih_hapus = st.selectbox(
            "Pilih data yang mau dihapus",
            opsi_hapus,
            key="pilih_hapus_rmh"
        )

        if st.button(
            "🗑 Hapus Data Ini",
            key="tombol_hapus_rmh"
        ):

            st.session_state[
                "konfirmasi_hapus_rmh"
            ] = pilih_hapus

        if st.session_state.get(
            "konfirmasi_hapus_rmh"
        ):

            target = st.session_state[
                "konfirmasi_hapus_rmh"
            ]

            st.warning(
                f"Yakin ingin menghapus data **{target}**? "
                "Tindakan ini tidak bisa dibatalkan."
            )

            col_ya, col_batal = st.columns(2)

            with col_ya:

                if st.button(
                    "✅ Ya, Hapus Permanen",
                    key="ya_hapus_rmh"
                ):

                    tahun_hapus, kabkota_hapus = target.split(
                        " - ",
                        1
                    )

                    try:

                        supabase_admin.table(
                            "fasilitas_perumahan"
                        ).delete().eq(
                            "tahun",
                            int(tahun_hapus)
                        ).eq(
                            "kabupaten_kota",
                            kabkota_hapus
                        ).execute()

                        del st.session_state[
                            "konfirmasi_hapus_rmh"
                        ]

                        set_toast(
                            "✅ Data berhasil dihapus."
                        )

                        st.rerun()

                    except Exception as e:
                        st.error(
                            f"Gagal menghapus data: {e}"
                        )

            with col_batal:

                if st.button(
                    "❌ Batal",
                    key="batal_hapus_rmh"
                ):

                    del st.session_state[
                        "konfirmasi_hapus_rmh"
                    ]

                    st.rerun()