from statistik_menu import jalankan_menu

SUMBER = "Badan Pusat Statistik (BPS)."

jalankan_menu({
    "menu": "Perumahan",
    "prefix": "perumahan",
    "judul": "🏠 Fasilitas Perumahan",
    "breadcrumb": "Statistik Sosial - Perumahan",
    "nama_menu": "Perumahan",
    "tahun_menurun": True,
    "desimal": 2,
    "sumber_default": SUMBER,

    # Indikator bawaan: angkanya tetap di tabel masing-masing.
    # Konsep, definisi, rumus, dan seterusnya dapat diisi admin lewat
    # Edit Data/Indikator (tersimpan di tabel statistik_variabel).
    # Kategori disimpan sebagai kolom di tabel (kolom_kategori: nama -> kolom).
    "indikator_bawaan": [
        {
            "tabel": "fasilitas_perumahan",
            "nama": "Fasilitas Perumahan",
            "satuan": "Persen (%)",
            "sumber_data": SUMBER,
            "kolom_kategori": {
                "Air Layak": "air_layak",
                "Jamban Sendiri/Bersama": "jamban_sendiri_bersama",
            },
        },
    ],
})