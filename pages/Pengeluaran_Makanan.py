import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client
from io import BytesIO

from utils import load_css, admin_edit_button, set_toast, admin_import_data


# =========================================================
# LOAD CSS
# =========================================================

load_css()


# =========================================================
# CUSTOM CSS
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
    </style>

    <div class="breadcrumb-container">
        <a href="/" target="_self">Beranda</a>
        &gt; Statistik Sosial - Pengeluaran Makanan
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# STATUS ADMIN
# =========================================================

is_admin = st.session_state.get("is_admin", False)


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
# JUDUL
# =========================================================

col_judul, col_edit = st.columns([8, 1])

with col_judul:
    st.title("🍚 Pengeluaran Perkapita untuk Makanan")

with col_edit:
    st.write("")
    admin_edit_button()


# =========================================================
# KONEKSI SUPABASE
# =========================================================

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
service_key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]

supabase: Client = create_client(url, key)
supabase_admin: Client = create_client(url, service_key)


# =========================================================
# DAFTAR DATA
# =========================================================

daftar_data = {
    "Pengeluaran Perkapita untuk Makanan": "pengeluaran_makanan"
}


# =========================================================
# FILTER DATA
# =========================================================

st.subheader("⚙️ Filter Data")

col_f1, col_f2, col_f3 = st.columns(3)


# =========================================================
# PILIH INDIKATOR
# =========================================================

with col_f1:

    st.markdown("📊 **Pilih Indikator**")

    indikator_input = st.selectbox(
        "📊 Pilih Data Pengeluaran Makanan",
        list(daftar_data.keys()),
        label_visibility="collapsed"
    )


nama_tabel_input = daftar_data[indikator_input]


# =========================================================
# AMBIL DAFTAR TAHUN
# =========================================================

try:

    response_tahun = (
        supabase
        .table(nama_tabel_input)
        .select("tahun")
        .execute()
    )

    df_tahun = pd.DataFrame(response_tahun.data)

    if not df_tahun.empty and "tahun" in df_tahun.columns:

        df_tahun["tahun"] = pd.to_numeric(
            df_tahun["tahun"],
            errors="coerce"
        )

        daftar_tahun = sorted(
            df_tahun["tahun"]
            .dropna()
            .unique()
            .astype(int),
            reverse=True
        )

    else:

        daftar_tahun = []


except Exception:

    daftar_tahun = []


# =========================================================
# PILIH TAHUN
# =========================================================

with col_f2:

    st.markdown("📅 **Tahun**")

    semua_tahun = st.checkbox(
        "Pilih Semua",
        value=True,
        key="chk_semua_tahun_pm"
    )

    prev_key_tahun = "_prev_chk_semua_tahun_pm"

    if prev_key_tahun not in st.session_state:

        st.session_state[prev_key_tahun] = semua_tahun

    elif st.session_state[prev_key_tahun] != semua_tahun:

        for thn in daftar_tahun:

            st.session_state[
                f"thn_{thn}_pm"
            ] = semua_tahun

        st.session_state[prev_key_tahun] = semua_tahun


    with st.container(height=160):

        tahun_terpilih_input = []

        if daftar_tahun:

            for thn in daftar_tahun:

                cek = st.checkbox(
                    str(thn),
                    value=semua_tahun,
                    key=f"thn_{thn}_pm"
                )

                if cek:
                    tahun_terpilih_input.append(int(thn))

        else:

            st.warning("Tidak ada data tahun.")


# =========================================================
# AMBIL DAFTAR WILAYAH
# =========================================================

try:

    response_wilayah = (
        supabase
        .table(nama_tabel_input)
        .select("kabupaten_kota")
        .execute()
    )

    df_wilayah_opt = pd.DataFrame(
        response_wilayah.data
    )

    if (
        not df_wilayah_opt.empty
        and "kabupaten_kota" in df_wilayah_opt.columns
    ):

        daftar_wilayah = sorted(
            df_wilayah_opt[
                "kabupaten_kota"
            ]
            .dropna()
            .unique()
        )

    else:

        daftar_wilayah = []


except Exception:

    daftar_wilayah = []


# =========================================================
# PILIH KABUPATEN / KOTA
# =========================================================

with col_f3:

    st.markdown("📍 **Kabupaten/Kota**")

    semua_wilayah = st.checkbox(
        "Pilih Semua",
        value=True,
        key="chk_semua_wilayah_pm"
    )

    prev_key_wilayah = "_prev_chk_semua_wilayah_pm"

    if prev_key_wilayah not in st.session_state:

        st.session_state[
            prev_key_wilayah
        ] = semua_wilayah

    elif st.session_state[
        prev_key_wilayah
    ] != semua_wilayah:

        for wil in daftar_wilayah:

            st.session_state[
                f"wil_{wil}_pm"
            ] = semua_wilayah

        st.session_state[
            prev_key_wilayah
        ] = semua_wilayah


    with st.container(height=160):

        wilayah_terpilih_input = []

        if daftar_wilayah:

            for wil in daftar_wilayah:

                cek_wil = st.checkbox(
                    wil,
                    value=semua_wilayah,
                    key=f"wil_{wil}_pm"
                )

                if cek_wil:
                    wilayah_terpilih_input.append(wil)

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
        "submitted_pm"
    ] = True

    st.session_state[
        "indikator_final_pm"
    ] = indikator_input

    st.session_state[
        "tahun_final_pm"
    ] = tahun_terpilih_input

    st.session_state[
        "wilayah_final_pm"
    ] = wilayah_terpilih_input


# =========================================================
# JIKA BELUM SUBMIT
# =========================================================

if not st.session_state.get(
    "submitted_pm",
    False
):

    st.info(
        "👆 Silakan sesuaikan pilihan tahun dan "
        "wilayah di atas, lalu klik tombol "
        "**Tampilkan Data**."
    )

    st.stop()


# =========================================================
# AMBIL FILTER DARI SESSION STATE
# =========================================================

indikator = st.session_state.get(
    "indikator_final_pm",
    list(daftar_data.keys())[0]
)

nama_tabel = daftar_data[indikator]

tahun_terpilih = st.session_state.get(
    "tahun_final_pm",
    []
)

wilayah_terpilih = st.session_state.get(
    "wilayah_final_pm",
    [])


# =========================================================
# VALIDASI FILTER
# =========================================================

if (
    not tahun_terpilih
    or not wilayah_terpilih
):

    st.warning(
        "⚠️ Tahun atau Kabupaten/Kota belum "
        "ada yang dicentang. Silakan centang "
        "minimal satu lalu klik "
        "**Tampilkan Data**."
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
        "Data Pengeluaran Perkapita untuk "
        "Makanan belum tersedia."
    )

    st.stop()


df = pd.DataFrame(data)


# =========================================================
# VALIDASI KOLOM
# =========================================================

kolom_wajib_data = [
    "tahun",
    "kabupaten_kota",
    "miskin",
    "tidak_miskin",
    "miskin_dan_tidak_miskin"
]

kolom_tidak_ada = [
    kolom
    for kolom in kolom_wajib_data
    if kolom not in df.columns
]

if kolom_tidak_ada:

    st.error(
        "Kolom berikut tidak ditemukan di tabel "
        f"`{nama_tabel}`: {', '.join(kolom_tidak_ada)}"
    )

    st.stop()


# =========================================================
# KONVERSI DATA NUMERIK
# =========================================================

df["tahun"] = pd.to_numeric(
    df["tahun"],
    errors="coerce"
)

for kolom in [
    "miskin",
    "tidak_miskin",
    "miskin_dan_tidak_miskin"
]:

    df[kolom] = pd.to_numeric(
        df[kolom],
        errors="coerce"
    )


df = df.dropna(
    subset=[
        "tahun",
        "kabupaten_kota"
    ]
)

df["tahun"] = df["tahun"].astype(int)


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
# JUDUL
# =========================================================

st.markdown("---")

st.subheader(
    ":material/rice_bowl: "
    "Pengeluaran Perkapita untuk Makanan"
)

st.write(
    f"Menampilkan data untuk "
    f"{len(wilayah_terpilih)} wilayah dan "
    f"{len(tahun_terpilih)} tahun."
)


# =========================================================
# DATA TIDAK DITEMUKAN
# =========================================================

if df_filtered.empty:

    st.warning(
        "Tidak ada data yang sesuai dengan "
        "filter yang dipilih."
    )

else:

    # =====================================================
    # TABEL PIVOT
    # =====================================================

    df_long = df_filtered.melt(
        id_vars=[
            "tahun",
            "kabupaten_kota"
        ],
        value_vars=[
            "miskin",
            "tidak_miskin",
            "miskin_dan_tidak_miskin"
        ],
        var_name="kategori",
        value_name="nilai"
    )


    nama_kategori = {
        "miskin": "Miskin",
        "tidak_miskin": "Tidak Miskin",
        "miskin_dan_tidak_miskin":
            "Miskin dan Tidak Miskin"
    }

    df_long["kategori"] = (
        df_long["kategori"]
        .map(nama_kategori)
    )


    # =====================================================
    # TABEL
    # =====================================================

    st.subheader(":material/list_alt: Data")


    df_tampilkan = df_long.pivot_table(
        index=[
            "kabupaten_kota",
            "kategori"
        ],
        columns="tahun",
        values="nilai",
        aggfunc="first"
    ).reset_index()


    df_tampilkan = df_tampilkan.rename(
        columns={
            "kabupaten_kota":
                "Kabupaten/Kota",
            "kategori":
                "Kategori"
        }
    )


    kolom_tahun = sorted(
        [
            col
            for col in df_tampilkan.columns
            if isinstance(col, int)
        ]
    )


    # Format angka
    df_tabel_display = df_tampilkan.copy()

    for col in kolom_tahun:

        df_tabel_display[col] = (
            df_tabel_display[col]
            .apply(
                lambda x:
                f"{x:,.2f}".replace(",", ".")
                if pd.notnull(x)
                else "-"
            )
        )


    st.dataframe(
        df_tabel_display,
        use_container_width=True,
        hide_index=True
    )


    # =====================================================
    # DOWNLOAD EXCEL
    # =====================================================

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df_tabel_display.to_excel(
            writer,
            index=False,
            sheet_name="Pengeluaran Makanan"
        )

    output.seek(0)


    st.download_button(
        label="📥 Download Excel",
        data=output,
        file_name=(
            "Pengeluaran_Makanan_"
            f"{len(wilayah_terpilih)}Wilayah.xlsx"
        ),
        mime=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )


    # =====================================================
    # GRAFIK
    # =====================================================

    st.subheader(
        "📈 Perkembangan Pengeluaran Perkapita "
        "untuk Makanan"
    )


    fig = px.line(
        df_long,
        x="tahun",
        y="nilai",
        color="kabupaten_kota",
        line_dash="kategori",
        markers=True,
        title=(
            "Perkembangan Pengeluaran Perkapita "
            "untuk Makanan Berdasarkan Wilayah"
        )
    )


    fig.update_layout(
        xaxis_title="Tahun",
        yaxis_title="Persentase (%)",
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
        "⚙️ Panel Admin — Pengeluaran Makanan"
    )

    st.caption(
        f"Mengelola tabel: `{nama_tabel}`"
    )


    # =====================================================
    # TABS
    # =====================================================

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
            key="metode_tambah_pengeluaran_makanan"
        )


        st.markdown("---")


        # =================================================
        # INPUT MANUAL
        # =================================================

        if metode == "Input Manual":

            with st.form(
                "form_tambah_pengeluaran",
                clear_on_submit=True
            ):

                col_a, col_b = st.columns(2)


                with col_a:

                    tahun_baru = st.number_input(
                        "Tahun",
                        min_value=2000,
                        max_value=2100,
                        step=1,
                        value=2024
                    )


                with col_b:

                    kabkota_baru = st.selectbox(
                        "Kabupaten/Kota",
                        DAFTAR_KABKOTA,
                        key="tambah_kabkota_pm"
                    )


                st.markdown(
                    "**Isi nilai berdasarkan kategori:**"
                )


                col_c, col_d, col_e = st.columns(3)


                with col_c:

                    miskin_baru = st.number_input(
                        "Miskin (%)",
                        value=0.0,
                        step=0.01,
                        format="%.2f"
                    )


                with col_d:

                    tidak_miskin_baru = st.number_input(
                        "Tidak Miskin (%)",
                        value=0.0,
                        step=0.01,
                        format="%.2f"
                    )


                with col_e:

                    gabungan_baru = st.number_input(
                        "Miskin dan Tidak Miskin (%)",
                        value=0.0,
                        step=0.01,
                        format="%.2f"
                    )


                if st.form_submit_button(
                    "💾 Simpan Data Baru"
                ):

                    data_baru = {

                        "tahun":
                            int(tahun_baru),

                        "kabupaten_kota":
                            kabkota_baru,

                        "miskin":
                            miskin_baru,

                        "tidak_miskin":
                            tidak_miskin_baru,

                        "miskin_dan_tidak_miskin":
                            gabungan_baru
                    }


                    try:

                        (
                            supabase_admin
                            .table(nama_tabel)
                            .insert(data_baru)
                            .execute()
                        )


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
                "miskin",
                "tidak_miskin",
                "miskin_dan_tidak_miskin"
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

    with tab_edit:

        if df.empty:

            st.info(
                "Belum ada data yang dapat diedit."
            )

        else:

            opsi_baris = [

                f"{row['tahun']} - "
                f"{row['kabupaten_kota']}"

                for _, row in df.iterrows()

            ]


            pilih_baris = st.selectbox(
                "Pilih data yang mau diedit",
                opsi_baris,
                key="pilih_edit_pm"
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


                baris_df = df[
                    (df["tahun"] == tahun_pilih)
                    &
                    (
                        df["kabupaten_kota"]
                        == kabkota_pilih
                    )
                ]


                if not baris_df.empty:

                    baris = baris_df.iloc[0]


                    with st.form(
                        "form_edit_pengeluaran"
                    ):

                        st.write(
                            f"Mengedit data: "
                            f"**{pilih_baris}**"
                        )


                        col_c, col_d, col_e = (
                            st.columns(3)
                        )


                        with col_c:

                            miskin_edit = st.number_input(
                                "Miskin (%)",
                                value=float(
                                    baris["miskin"]
                                ),
                                step=0.01,
                                format="%.2f"
                            )


                        with col_d:

                            tidak_miskin_edit = (
                                st.number_input(
                                    "Tidak Miskin (%)",
                                    value=float(
                                        baris[
                                            "tidak_miskin"
                                        ]
                                    ),
                                    step=0.01,
                                    format="%.2f"
                                )
                            )


                        with col_e:

                            gabungan_edit = (
                                st.number_input(
                                    "Miskin dan Tidak Miskin (%)",
                                    value=float(
                                        baris[
                                            "miskin_dan_tidak_miskin"
                                        ]
                                    ),
                                    step=0.01,
                                    format="%.2f"
                                )
                            )


                        if st.form_submit_button(
                            "💾 Simpan Perubahan"
                        ):

                            try:

                                (
                                    supabase_admin
                                    .table(nama_tabel)
                                    .update({
                                        "miskin":
                                            miskin_edit,
                                        "tidak_miskin":
                                            tidak_miskin_edit,
                                        "miskin_dan_tidak_miskin":
                                            gabungan_edit
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

        if df.empty:

            st.info(
                "Belum ada data yang dapat dihapus."
            )

        else:

            opsi_hapus = [

                f"{row['tahun']} - "
                f"{row['kabupaten_kota']}"

                for _, row in df.iterrows()

            ]


            pilih_hapus = st.selectbox(
                "Pilih data yang mau dihapus",
                opsi_hapus,
                key="pilih_hapus_pm"
            )


            if st.button(
                "🗑 Hapus Data Ini",
                key="tombol_hapus_pm"
            ):

                st.session_state[
                    "konfirmasi_hapus_pm"
                ] = pilih_hapus


            if st.session_state.get(
                "konfirmasi_hapus_pm"
            ):

                target = st.session_state[
                    "konfirmasi_hapus_pm"
                ]


                st.warning(
                    f"Yakin ingin menghapus data "
                    f"**{target}**? "
                    "Tindakan ini tidak bisa dibatalkan."
                )


                col_ya, col_batal = (
                    st.columns(2)
                )


                # =================================================
                # KONFIRMASI HAPUS
                # =================================================

                with col_ya:

                    if st.button(
                        "✅ Ya, Hapus Permanen",
                        key="ya_hapus_pm"
                    ):

                        tahun_hapus, kabkota_hapus = (
                            target.split(
                                " - ",
                                1
                            )
                        )


                        try:

                            (
                                supabase_admin
                                .table(nama_tabel)
                                .delete()
                                .eq(
                                    "tahun",
                                    int(tahun_hapus)
                                )
                                .eq(
                                    "kabupaten_kota",
                                    kabkota_hapus
                                )
                                .execute()
                            )


                            del st.session_state[
                                "konfirmasi_hapus_pm"
                            ]


                            set_toast(
                                "✅ Data berhasil dihapus."
                            )


                            st.rerun()


                        except Exception as e:

                            st.error(
                                f"Gagal menghapus data: {e}"
                            )


                # =================================================
                # BATAL
                # =================================================

                with col_batal:

                    if st.button(
                        "❌ Batal",
                        key="batal_hapus_pm"
                    ):

                        del st.session_state[
                            "konfirmasi_hapus_pm"
                        ]

                        st.rerun()
