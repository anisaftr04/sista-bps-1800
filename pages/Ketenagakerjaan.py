from statistik_menu import jalankan_menu

SUMBER = "Badan Pusat Statistik (BPS)."

jalankan_menu({
    "menu": "Ketenagakerjaan",
    "prefix": "ketenagakerjaan",
    "judul": "💼 Ketenagakerjaan",
    "breadcrumb": "Statistik Sosial - Ketenagakerjaan",
    "nama_menu": "Ketenagakerjaan",
    "tahun_menurun": False,
    "desimal": 3,
    "sumber_default": SUMBER,

    # Indikator bawaan: angkanya tetap di tabel masing-masing.
    # Konsep, definisi, rumus, dan seterusnya dapat diisi admin lewat
    # Edit Data/Indikator (tersimpan di tabel statistik_variabel).
    # Tabel yang punya kolom `kategori` dikenali otomatis.
    "indikator_bawaan": [
        {
            "tabel": "angkatan_kerja",
            "nama": "Angkatan Kerja",
            "satuan": "-",
            "sumber_data": SUMBER,
        },
        {
            "tabel": "tpak",
            "nama": "TPAK",
            "satuan": "Persen (%)",
            "sumber_data": SUMBER,
        },
        {
            "tabel": "tpt",
            "nama": "TPT",
            "satuan": "Persen (%)",
            "sumber_data": SUMBER,
        },
        {
            "tabel": "penduduk_bekerja",
            "nama": "Penduduk Bekerja",
            "satuan": "-",
            "sumber_data": SUMBER,
        },
        {
            "tabel": "lapangan_usaha",
            "nama": "Lapangan Usaha",
            "satuan": "-",
            "sumber_data": SUMBER,
        },
        {
            "tabel": "status_pekerjaan",
            "nama": "Status Pekerjaan",
            "satuan": "-",
            "sumber_data": SUMBER,
        },
        {
            "tabel": "pendidikan_pekerja",
            "nama": "Pendidikan Pekerja",
            "satuan": "-",
            "sumber_data": SUMBER,
        },
        {
            "tabel": "jam_kerja",
            "nama": "Jam Kerja",
            "satuan": "-",
            "sumber_data": SUMBER,
        },
        {
            "tabel": "upah",
            "nama": "Upah/Gaji",
            "satuan": "-",
            "sumber_data": SUMBER,
        },
        {
            "tabel": "setengah_penganggur",
            "nama": "Setengah Penganggur",
            "satuan": "-",
            "sumber_data": SUMBER,
        },
        {
            "tabel": "pekerja_informal",
            "nama": "Pekerja Informal",
            "satuan": "-",
            "sumber_data": SUMBER,
        },
    ],
})