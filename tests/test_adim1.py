import sys
sys.path.insert(0, "src")

import pytest
from adim1_veri_indir import metinden_tarih_cek, _ocr_normalize


def _tarih(metin):
    """Sadece tarih dict'ini döner (kaynak bilgisini görmezden gel)."""
    return metinden_tarih_cek(metin)[0]


# ---------------------------------------------------------------------------
# Yazılı ay ismi
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("metin,beklenen", [
    ("Ankara 17 Şubat 1930 Pazartesi\nMeclis açıldı.",
     {"gun": 17, "ay": 2, "yil": 1930}),
    ("3 Teşrinievvel 1931 tarihinde toplantı yapıldı.",
     {"gun": 3, "ay": 10, "yil": 1931}),
    ("1 Kânunusani 1929",
     {"gun": 1, "ay": 1, "yil": 1929}),
    ("15 Kânunuevvel 1933",
     {"gun": 15, "ay": 12, "yil": 1933}),
    ("12 Ekim 1936 Salı",
     {"gun": 12, "ay": 10, "yil": 1936}),
    ("5 Ocak 1938",
     {"gun": 5, "ay": 1, "yil": 1938}),
])
def test_tarih_cek_dogru(metin, beklenen):
    assert _tarih(metin) == beklenen


@pytest.mark.parametrize("metin", [
    "Herhangi bir tarih içermeyen metin.",
    "1930 yılında bazı olaylar yaşandı.",
    "17 Şubat 1920",   # kapsam dışı yıl
    "17 Şubat 1945",   # kapsam dışı yıl
])
def test_tarih_cek_none(metin):
    assert _tarih(metin) is None


def test_tarih_tam_metinde_bulunur():
    metin = "x" * 5000 + "17 Şubat 1930"
    assert _tarih(metin) == {"gun": 17, "ay": 2, "yil": 1930}


def test_ocr_bozuklugu_teşrinisani():
    assert _tarih("3 Teģrinisāni 1927 Perģembe") == {"gun": 3, "ay": 11, "yil": 1927}


def test_sampkali_teşrinisani():
    assert _tarih("7 Teşrinisâni 1927 Pazartesi") == {"gun": 7, "ay": 11, "yil": 1927}


# ---------------------------------------------------------------------------
# Sayısal format
# ---------------------------------------------------------------------------
def test_sayisal_format_nokta():
    metin = "CİLT: 7\n\nYirmi Birinci İnikat\n\n5.1.1929 Cumartesi"
    assert _tarih(metin) == {"gun": 5, "ay": 1, "yil": 1929}


def test_sayisal_format_bosluklu():
    assert _tarih("31 . 12 . 1928 Pazartesi") == {"gun": 31, "ay": 12, "yil": 1928}


# ---------------------------------------------------------------------------
# Romen rakamlı format (veri setindeki asıl desen)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("metin,beklenen", [
    ("15 - XI - 1937 Pazartesi",  {"gun": 15, "ay": 11, "yil": 1937}),
    ("7. VIII. 1942 Cuma",        {"gun": 7,  "ay": 8,  "yil": 1942}),
    ("18-V-1931 Pazartesi",       {"gun": 18, "ay": 5,  "yil": 1931}),
    ("12 - V - 1932 Perşembe",    {"gun": 12, "ay": 5,  "yil": 1932}),
    ("20 - II - 1932 Cumartesi",  {"gun": 20, "ay": 2,  "yil": 1932}),
    ("2 - VII - 1931 Perşembe",   {"gun": 2,  "ay": 7,  "yil": 1931}),
    ("20 - 1 - 1937 Çarşamba",    {"gun": 20, "ay": 1,  "yil": 1937}),  # OCR I→1
])
def test_romen_format(metin, beklenen):
    tarih, kaynak = metinden_tarih_cek(metin)
    assert tarih == beklenen
    assert kaynak == "regex_romen"


# ---------------------------------------------------------------------------
# Öncelik: ilk tarih alınır
# ---------------------------------------------------------------------------
def test_ilk_tarih_alinir():
    metin = (
        "===== PAGE 1 =====\nBeşinci İnikat\n7 Kasım 1927\n"
        "===== PAGE 2 =====\nDördüncü İnikat\n5 Kasım 1927\n"
    )
    tarih, _ = metinden_tarih_cek(metin)
    assert tarih == {"gun": 7, "ay": 11, "yil": 1927}


# ---------------------------------------------------------------------------
# OCR normalizasyonu
# ---------------------------------------------------------------------------
def test_ocr_normalize():
    assert _ocr_normalize("Teģrinisāni") == "Teşrinisani"
    assert _ocr_normalize("Teşrinisâni") == "Teşrinisani"
