import streamlit as st
import pandas as pd
import textwrap
from io import BytesIO


# ============================================================
# LOAD CSS
# ============================================================

def load_css():

    with open("style.css", encoding="utf-8") as f:

        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )


# ============================================================
# TOAST
# ============================================================

def set_toast(pesan, jenis="sukses"):

    ikon = (
        "✅"
        if jenis == "sukses"
        else
        "❌"
        if jenis == "error"
        else
        "ℹ️"
    )

    st.toast(
        pesan,
        icon=ikon
    )


# ============================================================
# LOGIN ADMIN
# ============================================================

@st.dialog("🔐 Login Admin")
def login_dialog():

    st.write(
        "Silakan masukkan username dan password admin."
    )

    username = st.text_input(
        "Username",
        key="admin_username_input"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="admin_password_input"
    )

    if st.button(
        "🔐 Login",
        key="admin_login_submit",
        use_container_width=True,
        type="primary"
    ):

        if (
            username == st.secrets["ADMIN_USERNAME"]
            and
            password == st.secrets["ADMIN_PASSWORD"]
        ):

            st.session_state["is_admin"] = True

            st.session_state["show_admin_panel"] = False

            st.success(
                "Login berhasil."
            )

            st.rerun()

        else:

            st.error(
                "❌ Username atau password salah."
            )


# ============================================================
# POPUP AKSES ADMIN
# ============================================================
@st.dialog("🔒 Akses Admin")
def edit_login_dialog():

    konten = textwrap.dedent(
        """
        <div style="text-align:center;">

            <div style="font-size:45px;">
                🔐
            </div>

            <h3>
                Login Admin Diperlukan
            </h3>

            <p style="font-size:16px;">
                Untuk mengedit data, Anda perlu
                login sebagai admin terlebih dahulu.
            </p>

        </div>
        """
    ).strip()

    st.html(konten)   # <-- ganti baris ini, tidak perlu unsafe_allow_html lagi

    if st.button(
        "Login sebagai Admin",
        key="popup_login_button",
        use_container_width=True,
        type="primary"
    ):
        st.session_state["trigger_login_dialog"] = True
        st.rerun()

# ============================================================
# REQUEST LOGIN DARI HALAMAN
# ============================================================

def show_login_dialog_if_requested():

    if st.session_state.get(
        "trigger_login_dialog",
        False
    ):

        st.session_state[
            "trigger_login_dialog"
        ] = False

        login_dialog()


# ============================================================
# GULIR OTOMATIS KE PANEL ADMIN
# ============================================================

def scroll_ke_panel_admin():
    """Menggulir halaman ke judul 'Panel Admin' sekali, setelah klik Edit.

    Judul panel dicari berdasarkan teksnya, jadi berlaku untuk semua
    halaman yang memakai judul '⚙️ Panel Admin ...'. Pencarian diulang
    sebentar karena panel baru muncul setelah data selesai dimuat.
    """

    kode = """
        <script>
        (function () {
            var doc = window.parent.document;

            // Jarak judul dari tepi atas layar (px).
            // Makin kecil = halaman tergulir makin ke bawah.
            // Tinggi header biru sekitar 100 px, jadi jangan di bawah itu.
            var JARAK = 120;

            var percobaan = 0;

            function cari() {
                var judul = doc.querySelectorAll("h1, h2, h3, h4");
                for (var i = 0; i < judul.length; i++) {
                    if (judul[i].textContent.indexOf("Panel Admin") !== -1) {
                        return judul[i];
                    }
                }
                return null;
            }

            var timer = setInterval(function () {
                var judul = cari();

                if (judul) {
                    clearInterval(timer);

                    judul.style.scrollMarginTop = JARAK + "px";
                    judul.scrollIntoView({behavior: "smooth", block: "start"});

                    // Isi panel masih dimuat setelah judul muncul, jadi
                    // halaman belum cukup panjang. Ulangi beberapa kali
                    // sampai judul benar-benar berada di posisi atas.
                    [600, 1400, 2400].forEach(function (ms) {
                        setTimeout(function () {
                            if (judul.getBoundingClientRect().top > JARAK + 8) {
                                judul.scrollIntoView({
                                    behavior: "smooth",
                                    block: "start"
                                });
                            }
                        }, ms);
                    });

                    return;
                }

                percobaan += 1;
                if (percobaan > 50) {
                    clearInterval(timer);
                }
            }, 200);
        })();
        </script>
        """

    if hasattr(st, "iframe"):
        # Streamlit versi baru
        st.iframe(kode, height=1)
    else:
        # Streamlit versi lama (mis. 1.63)
        import streamlit.components.v1 as components
        components.html(kode, height=0)


# ============================================================
# TOMBOL EDIT
# ============================================================

def admin_edit_button():

    if "show_admin_panel" not in st.session_state:

        st.session_state[
            "show_admin_panel"
        ] = False


    # Sembunyikan tombol Edit saat admin sudah berada di mode edit.
    # Tombol muncul lagi setelah logout (atau panel ditutup).
    if (
        st.session_state.get("is_admin", False)
        and st.session_state.get("show_admin_panel", False)
    ):

        # Baru saja klik Edit: gulir ke panel (hanya sekali)
        if st.session_state.pop("scroll_ke_panel_admin", False):
            scroll_ke_panel_admin()

        return


    if st.button(
        "✏️ Edit",
        key="edit_data_button"
    ):

        if st.session_state.get(
            "is_admin",
            False
        ):

            st.session_state[
                "show_admin_panel"
            ] = True

            st.session_state[
                "scroll_ke_panel_admin"
            ] = True

            st.rerun()

        else:

            edit_login_dialog()


# ============================================================
# TEMPLATE EXCEL
# ============================================================

def buat_template_excel(
    kolom_list,
    nama_sheet="Data"
):

    df_kosong = pd.DataFrame(
        columns=kolom_list
    )

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df_kosong.to_excel(
            writer,
            index=False,
            sheet_name=nama_sheet
        )

    output.seek(0)

    return output


# ============================================================
# IMPORT DATA ADMIN
# ============================================================

def admin_import_data(
    supabase_admin,
    table_name,
    kolom_wajib,
    key_prefix,
    kolom_teks=None,
    nama_sheet="Data",
    on_success=None
):

    kolom_teks = kolom_teks or []


    # --------------------------------------------------------
    # RESET UPLOADER
    # --------------------------------------------------------

    reset_key = (
        f"reset_counter_{key_prefix}"
    )

    if reset_key not in st.session_state:

        st.session_state[
            reset_key
        ] = 0


    # --------------------------------------------------------
    # INFO KOLOM
    # --------------------------------------------------------

    st.caption(
        "Kolom yang dibutuhkan: "
        f"`{', '.join(kolom_wajib)}`"
    )


    # --------------------------------------------------------
    # TEMPLATE
    # --------------------------------------------------------

    template = buat_template_excel(
        kolom_wajib,
        nama_sheet
    )

    st.download_button(
        "📄 Download Template Excel",

        data=template,

        file_name=(
            f"template_{table_name}.xlsx"
        ),

        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),

        key=(
            f"template_{key_prefix}"
        )
    )


    # --------------------------------------------------------
    # UPLOADER
    # --------------------------------------------------------

    uploader_key = (
        f"upload_{key_prefix}_"
        f"{st.session_state[reset_key]}"
    )

    file_upload = st.file_uploader(
        "Pilih file Excel (.xlsx) atau CSV (.csv)",

        type=[
            "xlsx",
            "csv"
        ],

        key=uploader_key
    )


    if file_upload is None:

        return


    # --------------------------------------------------------
    # BACA FILE
    # --------------------------------------------------------

    try:

        if file_upload.name.lower().endswith(
            ".csv"
        ):

            df_upload = pd.read_csv(
                file_upload
            )

        else:

            df_upload = pd.read_excel(
                file_upload
            )

    except Exception as e:

        st.error(
            f"Gagal membaca file: {e}"
        )

        return


    # --------------------------------------------------------
    # CEK KOLOM
    # --------------------------------------------------------

    kolom_hilang = [
        k
        for k in kolom_wajib
        if k not in df_upload.columns
    ]

    if kolom_hilang:

        st.error(
            "Kolom berikut tidak ditemukan "
            f"di file: {', '.join(kolom_hilang)}. "
            "Pastikan nama kolom persis sama "
            "dengan template."
        )

        return


    # --------------------------------------------------------
    # PILIH KOLOM
    # --------------------------------------------------------

    df_upload = df_upload[
        kolom_wajib
    ].copy()

    df_upload = df_upload.dropna(
        how="all"
    )


    # --------------------------------------------------------
    # KONVERSI DATA
    # --------------------------------------------------------

    for kol in kolom_wajib:

        if kol in kolom_teks:

            df_upload[kol] = (
                df_upload[kol]
                .astype(str)
                .str.strip()
            )

        else:

            df_upload[kol] = pd.to_numeric(
                df_upload[kol],
                errors="coerce"
            )


    # --------------------------------------------------------
    # VALIDASI ANGKA
    # --------------------------------------------------------

    kolom_angka = [
        k
        for k in kolom_wajib
        if k not in kolom_teks
    ]

    baris_error = df_upload[
        df_upload[kolom_angka]
        .isna()
        .any(axis=1)
    ]


    if not baris_error.empty:

        st.error(
            f"Ditemukan {len(baris_error)} "
            "baris dengan data tidak valid "
            "(kosong/bukan angka). "
            "Perbaiki dulu file-nya:"
        )

        st.dataframe(
            baris_error,
            use_container_width=True,
            hide_index=True
        )

        return


    # --------------------------------------------------------
    # PREVIEW
    # --------------------------------------------------------

    st.write(
        f"Ditemukan **{len(df_upload)} baris** "
        "data. Pratinjau sebelum diimpor:"
    )

    st.dataframe(
        df_upload,
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # IMPORT
    # --------------------------------------------------------

    if st.button(
        "📥 Import Semua Data Ini",

        key=f"import_btn_{key_prefix}",

        type="primary"
    ):

        records = df_upload.to_dict(
            orient="records"
        )


        # ----------------------------------------------------
        # TAHUN JADI INTEGER
        # ----------------------------------------------------

        for r in records:

            if (
                "tahun" in r
                and pd.notna(r["tahun"])
            ):

                r["tahun"] = int(
                    r["tahun"]
                )


        # ----------------------------------------------------
        # INSERT SUPABASE
        # ----------------------------------------------------

        try:

            (
                supabase_admin
                .table(table_name)
                .insert(records)
                .execute()
            )


            st.session_state[
                reset_key
            ] += 1


            if on_success:

                on_success()


            set_toast(
                f"{len(records)} baris data "
                "berhasil diimpor."
            )

            st.rerun()


        except Exception as e:

            st.error(
                f"Gagal mengimpor data: {e}"
            )