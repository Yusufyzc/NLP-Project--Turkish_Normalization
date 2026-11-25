"""
Adım 1 manuel doğrulama: 30 oturum seçer.
  - Tüm 'komşu' oturumlar (9 adet) zorunlu dahil
  - Tüm 'regex_sayisal' oturumlar (5 adet) zorunlu dahil
  - Kalan 16 slot: term'e göre dağılmış, diğer kaynaklardan
Çıktı: guide/dogrulama_adim1.csv
"""

import json, random, csv
from pathlib import Path

random.seed(42)
HEDEF = 30

oturumlar = []
with open("data/raw/oturumlar.jsonl", encoding="utf-8") as f:
    for satir in f:
        oturumlar.append(json.loads(satir))

# Zorunlu: tüm komşu + tüm regex_sayisal
zorunlu = [k for k in oturumlar if k["date_source"] in ("komşu", "regex_sayisal")]
zorunlu_idler = {k["document_id"] for k in zorunlu}

# Kalan havuz: zorunlu dışındakiler, term'e göre grupla
havuz = [k for k in oturumlar if k["document_id"] not in zorunlu_idler]
term_gruplari: dict[int, list] = {3: [], 4: [], 5: [], 6: []}
for k in havuz:
    term_gruplari[k["term"]].append(k)

# Kalan slotları term'e orantılı dağıt
kalan = HEDEF - len(zorunlu)
term_toplam = sum(len(v) for v in term_gruplari.values())
dagilim = {}
kalan_kalan = kalan
for i, (term, grup) in enumerate(term_gruplari.items()):
    if i < len(term_gruplari) - 1:
        adet = round(kalan * len(grup) / term_toplam)
    else:
        adet = kalan_kalan  # son termin geri kalanı al
    adet = min(adet, len(grup))
    dagilim[term] = adet
    kalan_kalan -= adet

ek_secilen = []
for term, adet in dagilim.items():
    ek_secilen += random.sample(term_gruplari[term], adet)

secilen = zorunlu + ek_secilen
random.shuffle(secilen)

# CSV kaydet
csv_yolu = Path("guide/dogrulama_adim1.csv")
with open(csv_yolu, "w", newline="", encoding="utf-8") as f:
    yazar = csv.DictWriter(f, fieldnames=[
        "no", "document_id", "term", "session",
        "tarih", "date_source", "kapsam", "ilk_300_karakter"
    ])
    yazar.writeheader()
    for i, k in enumerate(secilen, 1):
        gun  = k["takvim_gun"]
        ay   = k["takvim_ay"]
        yil  = k["takvim_yil"]
        tarih = f"{gun:02d}.{ay:02d}.{yil}" if gun and ay else f"~{yil}"
        yazar.writerow({
            "no": i,
            "document_id": k["document_id"],
            "term": k["term"],
            "session": k["session"],
            "tarih": tarih,
            "date_source": k["date_source"],
            "kapsam": k.get("kapsam", "?"),
            "ilk_300_karakter": (k["text"] or "")[:300].replace("\n", " "),
        })

print(f"Kaydedildi: {csv_yolu}  ({len(secilen)} oturum)\n")
kaynak_dagilim: dict[str, int] = {}
for k in secilen:
    kaynak_dagilim[k["date_source"]] = kaynak_dagilim.get(k["date_source"], 0) + 1
print("date_source dağılımı:", kaynak_dagilim)
print()
print(f"{'No':<3} {'Belge ID':<28} {'T':>2} {'Oturum':>6}  {'Tarih':<12} {'Kaynak':<15} {'Kapsam'}")
print("-" * 80)
for i, k in enumerate(secilen, 1):
    gun  = k["takvim_gun"]
    ay   = k["takvim_ay"]
    yil  = k["takvim_yil"]
    tarih = f"{gun:02d}.{ay:02d}.{yil}" if gun and ay else f"~{yil}"
    print(f"{i:<3} {k['document_id']:<28} {k['term']:>2} {k['session']:>6}  {tarih:<12} {k['date_source']:<15} {k.get('kapsam','?')}")
