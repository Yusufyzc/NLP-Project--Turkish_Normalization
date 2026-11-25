"""
Adim 1: GNACT veri setini indir, tarihlendirme yap ve kaydet.

Çıktı:
  data/raw/oturumlar.jsonl  — her satır bir oturum kaydı
  data/raw/tarih_raporu.csv — yıl bazında oturum sayıları
"""

import re
import json
import csv
from pathlib import Path
from datasets import load_dataset

# ---------------------------------------------------------------------------
# OCR normalizasyonu
# ---------------------------------------------------------------------------
_OCR_TABLO = str.maketrans(
    "ģāīūŗļķņĢĀĪŪâîûÂÎÛéÉ",
    "şaiurıknŞAİUaiuAIUeE",
)

def _ocr_normalize(metin: str) -> str:
    return metin.translate(_OCR_TABLO)


# ---------------------------------------------------------------------------
# Format 1 — Yazılı ay ismi: "17 Şubat 1930"
# ---------------------------------------------------------------------------
_AY_HAM = {
    "kanunusani": 1, "kanunısani": 1, "kanunasını": 1,
    "ocak": 1,
    "şubat": 2,
    "mart": 3,
    "nisan": 4,
    "mayıs": 5,
    "haziran": 6,
    "temmuz": 7,
    "agustos": 8, "ağustos": 8,
    "eylul": 9,   "eylül": 9,
    "teşrinievvel": 10,
    "ekim": 10,
    "teşrinisani": 11,
    "kasım": 11, "kasim": 11,
    "kanunuevvel": 12,
    "aralık": 12,
}

AY_ESLESTIRME: dict[str, int] = {
    _ocr_normalize(k): v for k, v in _AY_HAM.items()
}
AY_REGEX = "|".join(re.escape(k) for k in AY_ESLESTIRME)

TARIH_YAZI = re.compile(
    rf"(\d{{1,2}})\s+({AY_REGEX})\s+(1[89]\d\d)",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Format 2 — Romen rakamlı ay: "15 - XI - 1937" / "7. VIII. 1942"
# OCR hatası: I → 1 (tek basamak "1" Ocak olarak yorumlanır)
# ---------------------------------------------------------------------------
_ROMEN_AYLAR = {
    "xii": 12, "xi": 11, "x": 10,
    "ix": 9, "viii": 8, "vii": 7, "vi": 6,
    "v": 5, "iv": 4, "iii": 3, "ii": 2, "i": 1,
    "1": 1,   # OCR: I (Ocak) → 1
}
_ROMEN_REGEX = "xii|xi|x|ix|viii|vii|vi|v|iv|iii|ii|i|1"

TARIH_ROMEN = re.compile(
    rf"(\d{{1,2}})\s*[-\.]\s*({_ROMEN_REGEX})\s*[-\.]\s*(1[89]\d\d)",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Format 3 — Sayısal: "5.1.1929" veya "31 . 12 . 1928"
# ---------------------------------------------------------------------------
TARIH_SAYISAL = re.compile(
    r"\b(\d{1,2})\s*\.\s*(\d{1,2})\s*\.\s*(1[89]\d\d)\b"
)

# ---------------------------------------------------------------------------
# Alt dönem: term 3-4 → "1927-1934",  term 5-6 → "1935-1943"
# ---------------------------------------------------------------------------
def _alt_donem(term: int) -> str:
    return "1927-1934" if term in (3, 4) else "1935-1943"


# ---------------------------------------------------------------------------
# Ana tarih çıkarıcı
# ---------------------------------------------------------------------------
def metinden_tarih_cek(metin: str) -> tuple[dict | None, str]:
    """
    Metinde ilk eşleşen tarihi döner: (tarih_dict, kaynak).
    tarih_dict: {'gun', 'ay', 'yil'} veya None
    kaynak: 'regex_yazi' | 'regex_romen' | 'regex_sayisal' | None
    """
    norm = _ocr_normalize(metin)

    # 1) Yazılı ay
    m = TARIH_YAZI.search(norm)
    if m:
        gun, yil = int(m.group(1)), int(m.group(3))
        ay = AY_ESLESTIRME.get(_ocr_normalize(m.group(2).lower()))
        if ay and (1927 <= yil <= 1943):
            return {"gun": gun, "ay": ay, "yil": yil}, "regex_yazi"

    # 2) Romen rakamlı ay
    m = TARIH_ROMEN.search(norm)
    if m:
        gun, yil = int(m.group(1)), int(m.group(3))
        ay = _ROMEN_AYLAR.get(m.group(2).lower())
        if ay and (1927 <= yil <= 1943):
            return {"gun": gun, "ay": ay, "yil": yil}, "regex_romen"

    # 3) Sayısal
    m = TARIH_SAYISAL.search(norm)
    if m:
        gun, ay, yil = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 1 <= gun <= 31 and 1 <= ay <= 12 and (1927 <= yil <= 1943):
            return {"gun": gun, "ay": ay, "yil": yil}, "regex_sayisal"

    return None, "yok"


# ---------------------------------------------------------------------------
# Komşu oturum fallback (aynı cilt, bitişik oturum numarası)
# ---------------------------------------------------------------------------
def _komsu_tarih_ekle(kayitlar: list[dict]) -> None:
    """Tarihi olmayan kayıtlara aynı ciltteki komşu oturumun yılını yazar."""
    cilt_gruplari: dict[tuple, list[int]] = {}
    for idx, k in enumerate(kayitlar):
        anahtar = (k["term"], k["volume"])
        cilt_gruplari.setdefault(anahtar, []).append(idx)

    for indeksler in cilt_gruplari.values():
        # Oturum numarasına göre sırala
        indeksler.sort(key=lambda i: kayitlar[i]["session"])
        for sira, idx in enumerate(indeksler):
            if kayitlar[idx]["takvim_yil"] is not None:
                continue
            # Önceki komşu
            for j in range(sira - 1, -1, -1):
                k2 = kayitlar[indeksler[j]]
                if k2["takvim_yil"] is not None:
                    kayitlar[idx]["takvim_yil"] = k2["takvim_yil"]
                    kayitlar[idx]["takvim_ay"] = k2["takvim_ay"]
                    kayitlar[idx]["takvim_gun"] = k2["takvim_gun"]
                    kayitlar[idx]["date_source"] = "komşu"
                    break
            if kayitlar[idx]["takvim_yil"] is not None:
                continue
            # Sonraki komşu
            for j in range(sira + 1, len(indeksler)):
                k2 = kayitlar[indeksler[j]]
                if k2["takvim_yil"] is not None:
                    kayitlar[idx]["takvim_yil"] = k2["takvim_yil"]
                    kayitlar[idx]["takvim_ay"] = k2["takvim_ay"]
                    kayitlar[idx]["takvim_gun"] = k2["takvim_gun"]
                    kayitlar[idx]["date_source"] = "komşu"
                    break


# ---------------------------------------------------------------------------
# İndirme ve kaydetme
# ---------------------------------------------------------------------------
def veri_indir_ve_isle():
    cikti_dizin = Path("data/raw")
    cikti_dizin.mkdir(parents=True, exist_ok=True)

    print("Veri seti indiriliyor (tbmm_only)...")
    ds = load_dataset(
        "boun-tabilab/turkish_parliamentary_data",
        "tbmm_only",
        split="train",
    )
    print(f"Toplam kayit: {len(ds)}")

    filtrelenmis = ds.filter(
        lambda r: r["language"] == "modern_turkish" and 3 <= r["term"] <= 6
    )
    print(f"Filtre sonrasi (donem 3-6, modern_turkish): {len(filtrelenmis)}")

    kayitlar = []
    for kayit in filtrelenmis:
        tarih, kaynak = metinden_tarih_cek(kayit["text"] or "")
        kayitlar.append({
            "document_id": kayit["document_id"],
            "term": kayit["term"],
            "year": kayit["year"],
            "session": kayit["session"],
            "volume": kayit["volume"],
            "page_num": kayit["page_num"],
            "takvim_gun": tarih["gun"] if tarih else None,
            "takvim_ay":  tarih["ay"]  if tarih else None,
            "takvim_yil": tarih["yil"] if tarih else None,
            "date_source": kaynak if tarih else "yok",
            "alt_donem":  _alt_donem(kayit["term"]),
            "text": kayit["text"],
        })

    # Komşu fallback
    _komsu_tarih_ekle(kayitlar)

    # Dönem fallback (hâlâ tarihi olmayanlara)
    _TERM_YIL = {3: 1929, 4: 1933, 5: 1937, 6: 1941}
    for k in kayitlar:
        if k["takvim_yil"] is None:
            k["takvim_yil"] = _TERM_YIL[k["term"]]
            k["takvim_ay"]  = None
            k["takvim_gun"] = None
            k["date_source"] = "dönem"

    # Kapsama raporu
    toplam = len(kayitlar)
    kaynak_sayac: dict[str, int] = {}
    for k in kayitlar:
        kaynak_sayac[k["date_source"]] = kaynak_sayac.get(k["date_source"], 0) + 1

    print(f"\nToplam oturum       : {toplam}")
    for kaynak, sayi in sorted(kaynak_sayac.items()):
        print(f"  {kaynak:<18}: {sayi:>4}  ({sayi/toplam*100:.1f}%)")

    # JSONL kaydet
    jsonl_yolu = cikti_dizin / "oturumlar.jsonl"
    with open(jsonl_yolu, "w", encoding="utf-8") as f:
        for k in kayitlar:
            f.write(json.dumps(k, ensure_ascii=False) + "\n")
    print(f"\nKaydedildi: {jsonl_yolu}")

    # Yıl tablosu
    yil_sayac: dict[int, int] = {}
    for k in kayitlar:
        yil = k["takvim_yil"]
        if yil:
            yil_sayac[yil] = yil_sayac.get(yil, 0) + 1

    csv_yolu = cikti_dizin / "tarih_raporu.csv"
    with open(csv_yolu, "w", newline="", encoding="utf-8") as f:
        yazar = csv.writer(f)
        yazar.writerow(["yil", "oturum_sayisi"])
        for yil in sorted(yil_sayac):
            yazar.writerow([yil, yil_sayac[yil]])
    print(f"Kaydedildi: {csv_yolu}")

    print("\nYil bazinda oturum sayilari:")
    for yil in sorted(yil_sayac):
        print(f"  {yil}: {yil_sayac[yil]}")

    return kayitlar


if __name__ == "__main__":
    veri_indir_ve_isle()
