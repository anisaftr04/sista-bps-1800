from statistik_menu import jalankan_menu

SUMBER = "Badan Pusat Statistik (BPS)."

jalankan_menu({
    "menu": "Kependudukan",
    "prefix": "kependudukan",
    "judul": "👥 Kependudukan",
    "breadcrumb": "Statistik Sosial - Kependudukan",
    "nama_menu": "Kependudukan",
    "tahun_menurun": False,
    "desimal": 3,
    "sumber_default": SUMBER,

    # Indikator bawaan: angkanya tetap di tabel masing-masing.
    # Konsep, definisi, rumus, dan seterusnya dapat diisi admin lewat
    # Edit Data/Indikator (tersimpan di tabel statistik_variabel).
    "indikator_bawaan": [
        {
            "tabel": "jumlah_penduduk",
            "nama": "Jumlah Penduduk",
            "satuan": "Jiwa",
            "sumber_data": SUMBER,
        },
        {
            "tabel": "kepadatan_penduduk",
            "nama": "Kepadatan Penduduk",
            "satuan": "Jiwa/km²",
            "sumber_data": SUMBER,
        },
        {
            "tabel": "laju_pertumbuhan_penduduk",
            "nama": "Laju Pertumbuhan Penduduk",
            "satuan": "Persen (%)",
            "sumber_data": SUMBER,
        },
        {
            "tabel": "rasio_jenis_kelamin",
            "nama": "Rasio Jenis Kelamin",
            "satuan": "-",
            "sumber_data": SUMBER,
        },
        {
            "tabel": "persentase_penduduk",
            "nama": "Persentase Penduduk",
            "satuan": "Persen (%)",
            "sumber_data": SUMBER,
        },
    ],
})