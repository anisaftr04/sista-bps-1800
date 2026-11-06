from statistik_menu import jalankan_menu

SUMBER = (
    "Badan Pusat Statistik (BPS), "
    "Survei Sosial Ekonomi Nasional (Susenas)."
)

jalankan_menu({
    "menu": "Kemiskinan",
    "prefix": "kemiskinan",
    "judul": "📉 Kemiskinan",
    "breadcrumb": "Statistik Sosial - Kemiskinan",
    "nama_menu": "Kemiskinan",
    "tahun_menurun": False,
    "sumber_default": SUMBER,

    # Indikator bawaan: angkanya tetap di tabel masing-masing.
    # Metadata di bawah adalah nilai awal; admin dapat mengubahnya
    # lewat Edit Data/Indikator (tersimpan di tabel statistik_variabel).
    "indikator_bawaan": [
        {
            "tabel": "p0_persen_pend_miskin",
            "nama": "P0 - Persentase Penduduk Miskin",
            "satuan": "Persen (%)",
            "sumber_data": SUMBER,
            "konsep": "Kemiskinan, Penduduk Miskin",
            "definisi": "Persentase penduduk miskin yang berada di bawah garis kemiskinan.",
            "interpretasi": "Angka P0 menunjukkan proporsi penduduk miskin di suatu wilayah. Persentase penduduk miskin yang tinggi menunjukkan bahwa tingkat kemiskinan di suatu wilayah juga tinggi.",
            "mekanisme": "Menghitung proporsi penduduk miskin terhadap seluruh penduduk.",
            "rumus": "P0 = (Jumlah Penduduk Miskin / Jumlah Penduduk) × 100%",
            "ukuran": "Persentase",
        },
        {
            "tabel": "garis_kemiskinan",
            "nama": "Garis Kemiskinan",
            "satuan": "Rp/kapita/bulan",
            "sumber_data": SUMBER,
            "konsep": "Garis Kemiskinan",
            "definisi": "Garis Kemiskinan merupakan representasi dari jumlah rupiah minimum yang dibutuhkan untuk memenuhi kebutuhan pokok minimum makanan yang setara dengan 2100 kilokalori per kapita per hari dan kebutuhan pokok bukan makanan.",
            "interpretasi": "Penduduk yang memiliki rata-rata pengeluaran konsumsi per kapita per bulan di bawah garis kemiskinan dikategorikan sebagai penduduk miskin.",
            "mekanisme": "Garis Kemiskinan terdiri dari Garis Kemiskinan Makanan dan Garis Kemiskinan Bukan Makanan.",
            "rumus": "GK = GKM + GKBM",
            "ukuran": "Jumlah",
        },
        {
            "tabel": "jumlah_penduduk_miskin",
            "nama": "Jumlah Penduduk Miskin",
            "satuan": "Ribu jiwa",
            "sumber_data": SUMBER,
            "konsep": "Kemiskinan, Penduduk Miskin",
            "definisi": "Jumlah penduduk miskin yang memiliki rata-rata pengeluaran per kapita per bulan di bawah garis kemiskinan.",
            "interpretasi": "Menunjukkan banyaknya penduduk yang berada di bawah garis kemiskinan.",
            "mekanisme": "Menghitung jumlah penduduk yang memiliki rata-rata pengeluaran per kapita per bulan di bawah garis kemiskinan.",
            "rumus": "-",
            "ukuran": "Jumlah",
        },
        {
            "tabel": "p1_indeks_kedalaman",
            "nama": "P1 - Indeks Kedalaman Kemiskinan",
            "satuan": "Indeks",
            "sumber_data": SUMBER,
            "konsep": "Kemiskinan, Penduduk Miskin",
            "definisi": "Ukuran rata-rata kesenjangan pengeluaran masing-masing penduduk miskin terhadap garis kemiskinan. Indeks ini menunjukkan sejauh mana penduduk miskin berada di bawah garis kemiskinan.",
            "interpretasi": "Penurunan nilai indeks Kedalaman Kemiskinan mengindikasikan bahwa rata-rata pengeluaran penduduk miskin cenderung makin mendekati garis kemiskinan dan ketimpangan pengeluaran penduduk miskin juga semakin menyempit.",
            "mekanisme": "Menghitung rata-rata kesenjangan pengeluaran penduduk miskin terhadap garis kemiskinan.",
            "rumus": "P1 = 1/n Σ[(z − yᵢ) / z]",
            "ukuran": "Indeks",
        },
        {
            "tabel": "p2_indeks_keparahan",
            "nama": "P2 - Indeks Keparahan Kemiskinan",
            "satuan": "Indeks",
            "sumber_data": SUMBER,
            "konsep": "Kemiskinan, Penduduk Miskin",
            "definisi": "Gambaran mengenai penyebaran pengeluaran di antara penduduk miskin yang mengindikasikan besarnya ketimpangan yang terjadi antarpenduduk miskin.",
            "interpretasi": "Semakin tinggi nilai indeks, semakin tinggi ketimpangan pengeluaran di antara penduduk miskin.",
            "mekanisme": "Mengukur sebaran pengeluaran penduduk di bawah garis kemiskinan.",
            "rumus": "P2 = 1/n Σ[(z − yᵢ) / z]²",
            "ukuran": "Indeks",
        },
        {
            "tabel": "gini_ratio",
            "nama": "Gini Ratio",
            "satuan": "Indeks",
            "sumber_data": SUMBER,
            "konsep": "Ketimpangan Pengeluaran",
            "definisi": "Salah satu ukuran ketimpangan pengeluaran penduduk.",
            "interpretasi": "Semakin tinggi nilai Gini Ratio, semakin tinggi ketimpangan pengeluaran.",
            "mekanisme": "Mengukur tingkat ketimpangan distribusi pengeluaran penduduk.",
            "rumus": "-",
            "ukuran": "Indeks",
        },
    ],
})