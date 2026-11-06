from statistik_menu import jalankan_menu

SUMBER = "Badan Pusat Statistik (BPS)."

jalankan_menu({
    "menu": "Pengeluaran Makanan",
    "prefix": "pengeluaran",
    "judul": "🍚 Pengeluaran Perkapita untuk Makanan",
    "breadcrumb": "Statistik Sosial - Pengeluaran Makanan",
    "nama_menu": "Pengeluaran Makanan",
    "tahun_menurun": True,
    "desimal": 2,
    "sumber_default": SUMBER,

    # Indikator bawaan: angkanya tetap di tabel masing-masing.
    # Konsep, definisi, rumus, dan seterusnya dapat diisi admin lewat
    # Edit Data/Indikator (tersimpan di tabel statistik_variabel).
    # Kategori disimpan sebagai kolom di tabel (kolom_kategori: nama -> kolom).
    "indikator_bawaan": [
        {
            "tabel": "pengeluaran_makanan",
            "nama": "Pengeluaran Perkapita untuk Makanan",
            "satuan": "Persen (%)",
            "sumber_data": SUMBER,
            "kolom_kategori": {
                "Miskin": "miskin",
                "Tidak Miskin": "tidak_miskin",
                "Miskin dan Tidak Miskin": "miskin_dan_tidak_miskin",
            },
        },
    ],
})