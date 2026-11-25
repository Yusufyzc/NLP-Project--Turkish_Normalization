"""
Adım 2: Oturum bazlı bölme — test / dev / havuz

Yalnızca kapsam=="ana" (1929-1940) oturumlar kullanılır.
Alt döneme göre katmanlı örnekleme: seed=42.

Çıktı:
  data/split/test_ids.txt
  data/split/dev_ids.txt
  data/split/pool_ids.txt
"""

import json
import random
from pathlib import Path

SEED = 42
TEST_ORAN = 0.10   # her alt_dönem grubunun %10'u
DEV_ORAN  = 0.10   # her alt_dönem grubunun %10'u


def bolme_yap(jsonl_yolu: str = "data/raw/oturumlar.jsonl") -> dict[str, list[str]]:
    random.seed(SEED)

    oturumlar = []
    with open(jsonl_yolu, encoding="utf-8") as f:
        for satir in f:
            oturumlar.append(json.loads(satir))

    # Yalnızca "ana" kapsam
    ana = [k for k in oturumlar if k.get("kapsam") == "ana"]
    if not ana:
        raise ValueError(
            "oturumlar.jsonl'de 'kapsam' alanı bulunamadı. "
            "Önce 'python src/adim1_veri_indir.py' çalıştır."
        )

    # Alt döneme göre grupla
    gruplar: dict[str, list[str]] = {}
    for k in ana:
        ad = k["alt_donem"]
        gruplar.setdefault(ad, []).append(k["document_id"])

    test_ids, dev_ids, pool_ids = [], [], []

    for alt_donem in sorted(gruplar):
        idler = gruplar[alt_donem][:]
        random.shuffle(idler)
        n = len(idler)
        n_test = max(1, round(n * TEST_ORAN))
        n_dev  = max(1, round(n * DEV_ORAN))

        test_ids += idler[:n_test]
        dev_ids  += idler[n_test : n_test + n_dev]
        pool_ids += idler[n_test + n_dev :]

        print(f"  {alt_donem}: toplam={n}  test={n_test}  dev={n_dev}  havuz={n - n_test - n_dev}")

    return {"test": test_ids, "dev": dev_ids, "pool": pool_ids}


def kaydet(bolme: dict[str, list[str]], cikti_dizin: str = "data/split") -> None:
    Path(cikti_dizin).mkdir(parents=True, exist_ok=True)
    for ad, idler in bolme.items():
        yol = Path(cikti_dizin) / f"{ad}_ids.txt"
        with open(yol, "w", encoding="utf-8") as f:
            for doc_id in sorted(idler):
                f.write(doc_id + "\n")
        print(f"Kaydedildi: {yol}  ({len(idler)} oturum)")


if __name__ == "__main__":
    print("Oturum bazlı bölme başlıyor...\n")
    bolme = bolme_yap()
    print()

    # Kesişim kontrolü
    t, d, p = set(bolme["test"]), set(bolme["dev"]), set(bolme["pool"])
    assert not (t & d), "HATA: test ve dev kesişiyor!"
    assert not (t & p), "HATA: test ve pool kesişiyor!"
    assert not (d & p), "HATA: dev ve pool kesişiyor!"
    print(f"Toplam ana oturum : {len(t) + len(d) + len(p)}")
    print(f"  Test             : {len(t)}")
    print(f"  Dev              : {len(d)}")
    print(f"  Havuz            : {len(p)}")
    print("Kesişim kontrolü  : ✓")

    kaydet(bolme)
