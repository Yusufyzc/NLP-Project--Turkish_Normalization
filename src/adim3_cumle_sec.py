"""
Adım 3: Cümle bölme ve seçim

Cümle bölücü: kısaltmalara duyarlı, tablo/içindekiler/sahne notu satırlarını eler.
Oturum başına en fazla MAX_CUMLE_PER_OTURUM cümle alır (çeşitlilik).

Seçim:
  Dev  : 150 rastgele cümle (dev oturumlarından)
  Test : 200 rastgele + 100 "zor" cümle (test oturumlarından)
         Zor kriter: şapkalı harf yoğunluğu — sistemden bağımsız

Çıktı:
  data/dev/dev_cumleler.jsonl
  data/test_LOCKED/test_cumleler_ham.jsonl  (henüz etiketlenmemiş)
  data/pool/pool_cumleler.jsonl
"""

import re
import json
import random
from pathlib import Path

SEED = 42
MAX_CUMLE_PER_OTURUM = 5   # aynı oturumdan en fazla bu kadar cümle

DEV_HEDEF   = 150
TEST_RASTG  = 200
TEST_ZOR    = 100

MIN_SOZCUK  = 5
MAX_SOZCUK  = 80

# ---------------------------------------------------------------------------
# Bilinen kısaltmalar — nokta bu listede varsa cümle bitmez
# ---------------------------------------------------------------------------
_KISALTMALAR = {
    "muh", "no", "nr", "sf", "s", "m", "dr", "prof", "mah", "mh",
    "b", "m.m", "b.m", "b.m.m", "i.t", "hz", "bk", "vb", "vs",
    "müz", "mec", "bşk", "mdm", "ord", "gen", "kol", "alb", "bnb",
}

_KISALTMA_DESENI = re.compile(
    r"\b(" + "|".join(re.escape(k) for k in sorted(_KISALTMALAR, key=len, reverse=True)) + r")\.$",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Cümle bölücü
# ---------------------------------------------------------------------------
def _cumlelere_bol(metin: str) -> list[str]:
    metin = metin.strip()
    if not metin:
        return []

    parcalar = re.split(r"(?<=[.!?])\s+", metin)

    cumleler: list[str] = []
    birikim = ""

    for parca in parcalar:
        if birikim:
            birikim = birikim.rstrip() + " " + parca.lstrip()
        else:
            birikim = parca

        # Önceki token kısaltma mı? → birleştir
        son_token = birikim.rsplit(None, 1)[-1] if birikim.split() else ""
        if _KISALTMA_DESENI.search(son_token):
            continue

        # Rakamla biten nokta → liste maddesi, birleştir
        if re.search(r"\b\d+\.$", birikim.rstrip()):
            continue

        cumleler.append(birikim.strip())
        birikim = ""

    if birikim.strip():
        cumleler.append(birikim.strip())

    return cumleler


# ---------------------------------------------------------------------------
# Filtreler
# ---------------------------------------------------------------------------
_SAHNE_NOTU = re.compile(r"^\s*\(.*?\)\s*$")
_TABLO_SATIR = re.compile(r"\|.*\|")
_SAYFA_AYRAC = re.compile(r"=====\s*PAGE\s*\d+\s*=====")

def _gecerli_mi(cumle: str) -> bool:
    kelimeler = cumle.split()
    if len(kelimeler) < MIN_SOZCUK or len(kelimeler) > MAX_SOZCUK:
        return False
    if _SAHNE_NOTU.match(cumle):
        return False
    if _TABLO_SATIR.search(cumle):
        return False
    if _SAYFA_AYRAC.search(cumle):
        return False
    # Çoğunlukla rakam/noktalama → içindekiler satırı
    harf_sayisi = sum(1 for c in cumle if c.isalpha())
    if harf_sayisi < len(cumle) * 0.5:
        return False
    return True


# ---------------------------------------------------------------------------
# Zor cümle skoru (sistemden bağımsız): şapkalı harf yoğunluğu
# ---------------------------------------------------------------------------
_SAPKALI = re.compile(r"[âîûêÂÎÛÊ]")

def _zor_skor(cumle: str) -> float:
    kelimeler = cumle.split()
    if not kelimeler:
        return 0.0
    sapkali = sum(1 for k in kelimeler if _SAPKALI.search(k))
    return sapkali / len(kelimeler)


# ---------------------------------------------------------------------------
# Oturum metinlerinden cümle havuzu üret
# ---------------------------------------------------------------------------
def _oturum_cumlelerini_cek(
    oturum: dict,
    max_per_oturum: int = MAX_CUMLE_PER_OTURUM,
) -> list[dict]:
    metin = oturum.get("text") or ""
    paragraflar = metin.split("\n")

    adaylar = []
    for paragraf in paragraflar:
        for cumle in _cumlelere_bol(paragraf):
            if _gecerli_mi(cumle):
                adaylar.append({
                    "oturum_id": oturum["document_id"],
                    "alt_donem": oturum["alt_donem"],
                    "takvim_yil": oturum["takvim_yil"],
                    "girdi": cumle,
                    "zor_skor": _zor_skor(cumle),
                })

    if len(adaylar) > max_per_oturum:
        random.shuffle(adaylar)
        adaylar = adaylar[:max_per_oturum]

    return adaylar


# ---------------------------------------------------------------------------
# ID listesi yükle
# ---------------------------------------------------------------------------
def _id_listesi_yukle(dosya: str) -> set[str]:
    yol = Path(dosya)
    if not yol.exists():
        raise FileNotFoundError(f"{dosya} bulunamadı — önce adim2_bolme.py çalıştır")
    with open(yol, encoding="utf-8") as f:
        return {satir.strip() for satir in f if satir.strip()}


# ---------------------------------------------------------------------------
# JSONL kaydet
# ---------------------------------------------------------------------------
def _jsonl_kaydet(dosya: str, kayitlar: list[dict]) -> None:
    Path(dosya).parent.mkdir(parents=True, exist_ok=True)
    with open(dosya, "w", encoding="utf-8") as f:
        for i, k in enumerate(kayitlar, 1):
            k["id"] = f"{Path(dosya).stem}_{i:04d}"
            f.write(json.dumps(k, ensure_ascii=False) + "\n")
    print(f"Kaydedildi: {dosya}  ({len(kayitlar)} cümle)")


# ---------------------------------------------------------------------------
# Ana fonksiyon
# ---------------------------------------------------------------------------
def cumle_sec(
    jsonl_yolu: str = "data/raw/oturumlar.jsonl",
    split_dizin: str = "data/split",
) -> None:
    random.seed(SEED)

    # Oturumları yükle
    oturumlar: dict[str, dict] = {}
    with open(jsonl_yolu, encoding="utf-8") as f:
        for satir in f:
            k = json.loads(satir)
            oturumlar[k["document_id"]] = k

    test_ids = _id_listesi_yukle(f"{split_dizin}/test_ids.txt")
    dev_ids  = _id_listesi_yukle(f"{split_dizin}/dev_ids.txt")
    pool_ids = _id_listesi_yukle(f"{split_dizin}/pool_ids.txt")

    # Her küme için cümle havuzu oluştur
    def havuz_olustur(id_seti: set[str]) -> list[dict]:
        havuz = []
        for doc_id in id_seti:
            if doc_id in oturumlar:
                havuz.extend(_oturum_cumlelerini_cek(oturumlar[doc_id]))
        return havuz

    print("Cümle havuzları oluşturuluyor...")
    test_havuz = havuz_olustur(test_ids)
    dev_havuz  = havuz_olustur(dev_ids)
    pool_havuz = havuz_olustur(pool_ids)
    print(f"  Test havuzu : {len(test_havuz)} cümle")
    print(f"  Dev havuzu  : {len(dev_havuz)} cümle")
    print(f"  Pool havuzu : {len(pool_havuz)} cümle")

    # Dev: rastgele 150
    random.shuffle(dev_havuz)
    dev_secilen = dev_havuz[:DEV_HEDEF]

    # Test: rastgele 200
    random.shuffle(test_havuz)
    test_rastgele = test_havuz[:TEST_RASTG]
    test_rastgele_set = {c["girdi"] for c in test_rastgele}

    # Test: zor 100 (şapkalı yoğunluğu, rastgele seçilmemişlerden)
    kalan = [c for c in test_havuz[TEST_RASTG:] if c["girdi"] not in test_rastgele_set]
    kalan.sort(key=lambda c: c["zor_skor"], reverse=True)
    test_zor = kalan[:TEST_ZOR]

    test_secilen = test_rastgele + test_zor
    print(f"\nSeçilen:")
    print(f"  Dev             : {len(dev_secilen)}")
    print(f"  Test (rastgele) : {len(test_rastgele)}")
    print(f"  Test (zor)      : {len(test_zor)}")

    # Kaydet
    _jsonl_kaydet("data/dev/dev_cumleler.jsonl",              dev_secilen)
    _jsonl_kaydet("data/test_LOCKED/test_cumleler_ham.jsonl", test_secilen)
    _jsonl_kaydet("data/pool/pool_cumleler.jsonl",             pool_havuz)


if __name__ == "__main__":
    cumle_sec()
