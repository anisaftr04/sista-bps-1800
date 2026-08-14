import streamlit as st
from supabase import create_client, Client

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(url, key)

st.title("📂 Manajemen Dokumen")

cari = st.text_input("🔍 Cari Dokumen")

response = (
    supabase.table("dokumen")
    .select("*")
    .order("created_at", desc=True)
    .execute()
)

data = response.data

if not data:
    st.info("Belum ada dokumen.")

else:

    if cari:
        data = [
            d for d in data
            if cari.lower() in (d["nama_dokumen"] or "").lower()
        ]

    for dok in data:

        with st.container(border=True):

            st.subheader(f"📄 {dok['nama_dokumen']}")

            st.write(f"**Kabupaten :** {dok['kabupaten']}")
            st.write(f"**Kategori :** {dok['kategori']}")
            st.write(f"**Keterangan :** {dok['keterangan']}")

            col1, col2 = st.columns(2)

            with col1:

                url = supabase.storage.from_("dokumen").get_public_url(
                    dok["path_file"]
                )

                st.link_button(
                    "📥 Download",
                    url
                )

            with col2:

                if st.button(
                    "🗑️ Hapus",
                    key=dok["id"]
                ):

                    supabase.storage.from_("dokumen").remove(
                        [dok["path_file"]]
                    )

                    supabase.table("dokumen").delete().eq(
                        "id",
                        dok["id"]
                    ).execute()

                    st.success("Dokumen berhasil dihapus.")
\
                    st.rerun()