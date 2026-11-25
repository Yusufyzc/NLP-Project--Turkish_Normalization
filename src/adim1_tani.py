"""Veri setinin gerçek alan değerlerini görmek için tanı betiği."""

from datasets import load_dataset
import collections

ds = load_dataset(
    "boun-tabilab/turkish_parliamentary_data",
    "tbmm_only",
    split="train",
)

print("=== SUTUNLAR ===")
print(ds.column_names)

print("\n=== ILK KAYIT ===")
ilk = ds[0]
for k, v in ilk.items():
    if k == "text":
        print(f"  text (ilk 300 karakter): {str(v)[:300]}")
    else:
        print(f"  {k}: {v!r}  (tip: {type(v).__name__})")

print("\n=== TERM DEGERLERI (en sik 20) ===")
term_sayac = collections.Counter(ds["term"])
for deger, sayi in sorted(term_sayac.items())[:20]:
    print(f"  {deger!r}: {sayi}")

print("\n=== LANGUAGE DEGERLERI ===")
lang_sayac = collections.Counter(ds["language"])
for deger, sayi in lang_sayac.most_common():
    print(f"  {deger!r}: {sayi}")

print("\n=== TERM 3-6 MODERN_TURKISH: IS_FULL_SESSION DAGILIMI ===")
hedef = [r for r in ds if r["language"] == "modern_turkish" and 3 <= r["term"] <= 6]
full = [r for r in hedef if r["is_full_session"]]
page = [r for r in hedef if not r["is_full_session"]]
print(f"  is_full_session=True : {len(full)}")
print(f"  is_full_session=False: {len(page)}")
print(f"  page_num ornekleri   : {list({r['page_num'] for r in hedef})[:10]}")

print("\n=== TARIH KACINCI KARAKTERDE BULUNUYOR? ===")
import re, sys; sys.path.insert(0, "src")
from adim1_veri_indir import TARIH_DESENI, _ocr_normalize

konumlar = []
bulunamayan_ornekler = []
for r in hedef:
    metin = _ocr_normalize(r["text"] or "")
    m = TARIH_DESENI.search(metin)
    if m:
        konumlar.append(m.start())
    elif len(bulunamayan_ornekler) < 3:
        bulunamayan_ornekler.append(r)

if konumlar:
    print(f"  Bulunan: {len(konumlar)}/{len(hedef)}")
    print(f"  Min konum: {min(konumlar)}")
    print(f"  Max konum: {max(konumlar)}")
    print(f"  Medyan   : {sorted(konumlar)[len(konumlar)//2]}")
    esikler = [500, 1000, 2000, 5000, 10000]
    for e in esikler:
        kapsanan = sum(1 for k in konumlar if k < e)
        print(f"  {e} karakter içinde: {kapsanan}/{len(konumlar)} ({kapsanan/len(konumlar)*100:.1f}%)")

print("\n=== TARIH BULUNAMAYAN 3 ORNEK (ilk 600 karakter) ===")
for i, r in enumerate(bulunamayan_ornekler):
    print(f"\n--- term={r['term']} year={r['year']} session={r['session']} ---")
    print(str(r["text"])[:600])
