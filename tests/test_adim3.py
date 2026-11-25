import sys
sys.path.insert(0, "src")

import pytest
from adim3_cumle_sec import _cumlelere_bol, _gecerli_mi, _zor_skor


# ---------------------------------------------------------------------------
# Cümle bölücü — TBMM metnine özgü örnekler
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("metin,beklenen_sayi", [
    # Normal iki cümle
    ("Meclis açıldı. Oturum başladı.", 2),
    # Kısaltma nokta → bölme yapılmamalı
    ("Muh. Ahmed Bey söz aldı.", 1),
    # No. kısaltması
    ("No. 42 sayılı kanun okundu. Müzakere başladı.", 2),
    # Sadece bir cümle
    ("Bütçe müzakeresi tamamlandı.", 1),
    # Madde numarası → bölme yapılmamalı
    ("1. Madde kabul edildi. 2. Madde okundu.", 2),
    # Çok cümle
    ("Reis Bey konuştu. Muhalefet itiraz etti. Oylama yapıldı.", 3),
])
def test_cumle_bolme(metin, beklenen_sayi):
    sonuc = _cumlelere_bol(metin)
    assert len(sonuc) == beklenen_sayi, f"Beklenen {beklenen_sayi}, gelen {len(sonuc)}: {sonuc}"


# ---------------------------------------------------------------------------
# Geçerlilik filtresi
# ---------------------------------------------------------------------------
def test_cok_kisa_cumle_elenir():
    assert not _gecerli_mi("Tamam.")               # 1 sözcük
    assert not _gecerli_mi("Oturum açıldı.")       # 2 sözcük


def test_sahne_notu_elenir():
    assert not _gecerli_mi("(Alkışlar)")
    assert not _gecerli_mi("(Gürültü)")


def test_tablo_satiri_elenir():
    assert not _gecerli_mi("| Yıl | Miktar | Toplam |")


def test_sayfa_ayrac_elenir():
    assert not _gecerli_mi("===== PAGE 3 =====")


def test_gecerli_cumle_kabul_edilir():
    cumle = "Meclisin bu oturumunda bütçe müzakeresi tamamlanmış ve oya konulmuştur."
    assert _gecerli_mi(cumle)


# ---------------------------------------------------------------------------
# Zor skor
# ---------------------------------------------------------------------------
def test_zor_skor_sapkali_yuksek():
    cumle_sapkali = "Kânun mûcibince verilen karâr ittihâz edilmiştir."
    cumle_normal  = "Kanun gereğince verilen karar alınmıştır."
    assert _zor_skor(cumle_sapkali) > _zor_skor(cumle_normal)


def test_zor_skor_sifir_sapkasiz():
    cumle = "Bu kanun maddesine göre oylama yapılacaktır."
    assert _zor_skor(cumle) == 0.0
