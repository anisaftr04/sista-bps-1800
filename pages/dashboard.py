import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================
# Koneksi Supabase
# ==========================
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(url, key)

st.title("🏠 Dashboard")
st.success("Selamat datang di Sistem Informasi Statistik Sosial (SISTA)")

# ==========================
# Ambil data dari Supabase
# ==========================
response = supabase.table("dokumen").select("*").execute()
data = response.data

if len(data) == 0:
    st.warning("Belum ada dokumen yang diupload.")
else:
    df = pd.DataFrame(data)

    total_dokumen = len(df)
    total_pdf = len(df[df["nama_file"].str.lower().str.endswith(".pdf", na=False)])
    total_word = len(df[df["nama_file"].str.lower().str.endswith(".docx", na=False)])
    total_excel = len(
    df[df["nama_file"].str.lower().str.endswith((".xlsx", ".xls"), na=False)]
)
    total_ppt = len(df[df["nama_file"].str.lower().str.endswith(".pptx", na=False)])

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("📄 Total Dokumen", total_dokumen)
    col2.metric("📕 PDF", total_pdf)
    col3.metric("📘 Word", total_word)
    col4.metric("📗 Excel", total_excel)
    col5.metric("📙 PPT", total_ppt)