"""Tarihsiz oturumların ilk 300 karakterini göster; desen analizi için."""

import json, random
random.seed(99)

tarihsiz = []
with open("data/raw/oturumlar.jsonl", encoding="utf-8") as f:
    for satir in f:
        k = json.loads(satir)
        if k["takvim_yil"] is None:
            tarihsiz.append(k)

print(f"Toplam tarihsiz oturum: {len(tarihsiz)}")
print(f"Gösterilen: 20\n{'='*70}")

ornekler = random.sample(tarihsiz, min(20, len(tarihsiz)))
for i, k in enumerate(ornekler, 1):
    print(f"\n--- {i}. term={k['term']} year={k['year']} session={k['session']} vol={k['volume']} ---")
    print((k["text"] or "")[:300])
    print("-"*70)
