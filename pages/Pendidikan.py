from statistik_menu import jalankan_menu

SUMBER = "Badan Pusat Statistik (BPS)."

# Kode wilayah yang dipakai tabel-tabel Pendidikan
WILAYAH = {
    "1801": "Lampung Barat",
    "1802": "Tanggamus",
    "1803": "Lampung Selatan",
    "1804": "Lampung Timur",
    "1805": "Lampung Tengah",
    "1806": "Lampung Utara",
    "1807": "Way Kanan",
    "1808": "Tulang Bawang",
    "1809": "Pesawaran",
    "1810": "Pringsewu",
    "1811": "Mesuji",
    "1812": "Tulang Bawang Barat",
    "1813": "Pesisir Barat",
    "1871": "Bandar Lampung",
    "1872": "Metro",
}

jalankan_menu({
    "menu": "Pendidikan",
    "prefix": "pendidikan",
    "judul": "📚 Indikator Pendidikan",
    "breadcrumb": "Statistik Sosial - Pendidikan",
    "nama_menu": "Pendidikan",
    "tahun_menurun": True,
    "desimal": 2,
    "sumber_default": SUMBER,
    "peta_wilayah": WILAYAH,

    # Tabel lama memakai kolom `kode_wilayah` (bukan nama kabupaten/kota) dan
    # satu kolom untuk setiap kategori (kolom_kategori: nama -> kolom).
    "indikator_bawaan": [
        {
            "tabel": "aps",
            "nama": "APS Berdasarkan Kelompok Umur",
            "satuan": "Persen (%)",
            "sumber_data": SUMBER,
            "kolom_wilayah": "kode_wilayah",
            "kolom_kategori": {
                "7–12 Tahun": "usia_7_12",
                "13–15 Tahun": "usia_13_15",
            },
        },
        {
            "tabel": "aps_kabko_2025",
            "nama": "APS Kabupaten/Kota Tahun 2025",
            "satuan": "Persen (%)",
            "sumber_data": SUMBER,
            "kolom_wilayah": "kode_wilayah",
            "kolom_kategori": {
                "7–12 Tahun": "aps_7_12",
                "13–15 Tahun": "aps_13_15",
                "16–18 Tahun": "aps_16_18",
                "19–23 Tahun": "aps_19_23",
            },
        },
        {
            "tabel": "apm_kabko_2025",
            "nama": "APM",
            "satuan": "Persen (%)",
            "sumber_data": SUMBER,
            "kolom_wilayah": "kode_wilayah",
            "kolom_kategori": {
                "SD": "apm_sd",
                "SMP": "apm_smp",
                "SMA": "apm_sma",
                "Perguruan Tinggi": "apm_pt",
            },
        },
        {
            "tabel": "apk_kabko_2025",
            "nama": "APK",
            "satuan": "Persen (%)",
            "sumber_data": SUMBER,
            "kolom_wilayah": "kode_wilayah",
            "kolom_kategori": {
                "SD": "apk_sd",
                "SMP": "apk_smp",
                "SMA": "apk_sma",
                "Perguruan Tinggi": "apk_pt",
            },
        },
    ],
})