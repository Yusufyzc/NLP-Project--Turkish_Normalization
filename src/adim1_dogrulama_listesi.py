"""
Adım 1 manuel doğrulama: term'e göre dağılmış 30 rastgele oturum listeler.
Her oturum için: document_id, tarih, date_source, ilk 300 karakter.
"""

import json, random, csv
from pathlib import Path

random.seed(42)

oturumlar = []
with open("data/raw/oturumlar.jsonl", encoding="utf-8") as f:
    for satir in f:
        oturumlar.append(json.loads(satir))

# Term'e göre grupla
term_gruplari: dict[int, list] = {3: [], 4: [], 5: [], 6: []}
for k in oturumlar:
    term_gruplari[k["term"]].append(k)

# Her term'den ~7-8 tane seç (toplam 30)
dagilim = {3: 8, 4: 8, 5: 7, 6: 7}
secilen = []
for term, adet in dagilim.items():
    secilen += random.sample(term_gruplari[term], adet)

random.shuffle(secilen)

# CSV kaydet
csv_yolu = Path("guide/dogrulama_adim1.csv")
with open(csv_yolu, "w", newline="", encoding="utf-8") as f:
    yazar = csv.DictWriter(f, fieldnames=[
        "no", "document_id", "term", "session",
        "tarih", "date_source", "ilk_300_karakter"
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
            "ilk_300_karakter": (k["text"] or "")[:300].replace("\n", " "),
        })

print(f"Kaydedildi: {csv_yolu}\n")
print(f"{'No':<3} {'Belge ID':<28} {'T':>2} {'Oturum':>6}  {'Tarih':<12} {'Kaynak'}")
print("-" * 72)
for i, k in enumerate(secilen, 1):
    gun  = k["takvim_gun"]
    ay   = k["takvim_ay"]
    yil  = k["takvim_yil"]
    tarih = f"{gun:02d}.{ay:02d}.{yil}" if gun and ay else f"~{yil}"
    print(f"{i:<3} {k['document_id']:<28} {k['term']:>2} {k['session']:>6}  {tarih:<12} {k['date_source']}")
