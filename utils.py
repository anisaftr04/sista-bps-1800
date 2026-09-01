import streamlit as st
import pandas as pd 
import textwrap
from io import BytesIO


def load_css():
    with open("style.css", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )


# ============================================================
# NOTIFIKASI TOAST DI TENGAH (pengganti success_popup)
# ============================================================
def set_toast(pesan, jenis="sukses"):
    """Panggil ini di mana saja (boleh sebelum st.rerun())."""
    ikon = "✅" if jenis == "sukses" else ("❌" if jenis == "error" else "ℹ️")
    st.toast(pesan, icon=ikon)


# ============================================================
# POPUP LOGIN ADMIN
# ============================================================

@st.dialog("🔐 Login Admin")
def login_dialog():

    st.write("Silakan masukkan username dan password admin.")

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
            and password == st.secrets["ADMIN_PASSWORD"]
        ):

            st.session_state["is_admin"] = True
            st.session_state["show_admin_panel"] = False

            st.success("Login berhasil.")
            st.rerun()

        else:
            st.error("❌ Username atau password salah.")


# ============================================================
# POPUP KETIKA KLIK EDIT TAPI BELUM LOGIN
# ============================================================

@st.dialog("🔒 Akses Admin")
def edit_login_dialog():

    konten = textwrap.dedent("""
        <div style="text-align:center;">
            <div style="font-size:45px;">🔐</div>
            <h3>Login Admin Diperlukan</h3>
            <p style="font-size:16px;">
                Untuk mengedit data, Anda perlu
                login sebagai admin terlebih dahulu.
            </p>
        </div>
    """).strip()

    st.markdown(konten, unsafe_allow_html=True)

    if st.button(
        "Login sebagai Admin",
        key="popup_login_button",
        use_container_width=True,
        type="primary"
    ):
        st.session_state["trigger_login_dialog"] = True
        st.rerun()


def show_login_dialog_if_requested():
    """
    Dipanggil di bps.py (di luar dialog manapun) supaya login_dialog()
    bisa terbuka setelah edit_login_dialog() ditutup.
    """
    if st.session_state.get("trigger_login_dialog"):
        st.session_state["trigger_login_dialog"] = False
        login_dialog()


# ============================================================
# LOGIN ADMIN DI KANAN ATAS (samping Deploy)
# ============================================================

def admin_login():

    if "is_admin" not in st.session_state:
        st.session_state["is_admin"] = False

    if st.session_state["is_admin"]:

        col1, col2 = st.columns([1, 1])

        with col1:
            st.button("Admin", key="admin_label_btn", disabled=True)

        with col2:
            if st.button("Logout", key="logout_admin"):
                st.session_state["is_admin"] = False
                st.session_state["show_admin_panel"] = False
                st.rerun()

    else:

        if st.button("Login Admin", key="open_login_admin"):
            login_dialog()

    return st.session_state["is_admin"]


# ============================================================
# TOMBOL EDIT DI HALAMAN
# ============================================================

def admin_edit_button():

    if "show_admin_panel" not in st.session_state:
        st.session_state["show_admin_panel"] = False

    if st.button(
        "✏️ Edit",
        key="edit_data_button"
    ):

        if st.session_state.get("is_admin", False):

            st.session_state["show_admin_panel"] = True
            st.rerun()

        else:

            edit_login_dialog()

def buat_template_excel(kolom_list, nama_sheet="Data"):
    df_kosong = pd.DataFrame(columns=kolom_list)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_kosong.to_excel(writer, index=False, sheet_name=nama_sheet)
    output.seek(0)
    return output

def admin_import_data(supabase_admin, table_name, kolom_wajib, key_prefix, kolom_teks=None, nama_sheet="Data", on_success=None):

    kolom_teks = kolom_teks or []

    reset_key = f"reset_counter_{key_prefix}"
    if reset_key not in st.session_state:
        st.session_state[reset_key] = 0

    st.caption(f"Kolom yang dibutuhkan: `{', '.join(kolom_wajib)}`")

    template = buat_template_excel(kolom_wajib, nama_sheet)
    st.download_button(
        "📄 Download Template Excel",
        data=template,
        file_name=f"template_{table_name}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"template_{key_prefix}"
    )

    uploader_key = f"upload_{key_prefix}_{st.session_state[reset_key]}"

    file_upload = st.file_uploader(
        "Pilih file Excel (.xlsx) atau CSV (.csv)",
        type=["xlsx", "csv"],
        key=uploader_key
    )

    if file_upload is None:
        return

    try:
        if file_upload.name.lower().endswith(".csv"):
            df_upload = pd.read_csv(file_upload)
        else:
            df_upload = pd.read_excel(file_upload)
    except Exception as e:
        st.error(f"Gagal membaca file: {e}")
        return

    kolom_hilang = [k for k in kolom_wajib if k not in df_upload.columns]
    if kolom_hilang:
        st.error(f"Kolom berikut tidak ditemukan di file: {', '.join(kolom_hilang)}. Pastikan nama kolom persis sama dengan template.")
        return

    df_upload = df_upload[kolom_wajib].copy()
    df_upload = df_upload.dropna(how="all")

    for kol in kolom_wajib:
        if kol in kolom_teks:
            df_upload[kol] = df_upload[kol].astype(str).str.strip()
        else:
            df_upload[kol] = pd.to_numeric(df_upload[kol], errors="coerce")

    kolom_angka = [k for k in kolom_wajib if k not in kolom_teks]
    baris_error = df_upload[df_upload[kolom_angka].isna().any(axis=1)]

    if not baris_error.empty:
        st.error(f"Ditemukan {len(baris_error)} baris dengan data tidak valid (kosong/bukan angka). Perbaiki dulu file-nya:")
        st.dataframe(baris_error, use_container_width=True, hide_index=True)
        return

    st.write(f"Ditemukan **{len(df_upload)} baris** data. Pratinjau sebelum diimpor:")
    st.dataframe(df_upload, use_container_width=True, hide_index=True)

    if st.button("📥 Import Semua Data Ini", key=f"import_btn_{key_prefix}", type="primary"):
        records = df_upload.to_dict(orient="records")

        for r in records:
            if "tahun" in r and pd.notna(r["tahun"]):
                r["tahun"] = int(r["tahun"])

        try:
            supabase_admin.table(table_name).insert(records).execute()
            st.session_state[reset_key] += 1
            if on_success:
                on_success()
            set_toast(f"{len(records)} baris data berhasil diimpor.")
            st.rerun()
        except Exception as e:
            st.error(f"Gagal mengimpor data: {e}")