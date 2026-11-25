# CLAUDE.md — Proje Bağlamı

Bu dosya her oturumda sıfırdan okumayı önlemek için tutulur.
Projeyi tanımak için önce bu dosyayı oku, sonra `PROJE_PLANI.md`'ye bak.

---

## Proje Nedir?

1929–1940 TBMM tutanaklarını modern Türkçe imla kurallarına normalize eden çok katmanlı bir sistem.
TÜBİTAK 2209-A & NLP/LLM dersi kapsamında.

**Veri:** `boun-tabilab/turkish_parliamentary_data` (Hugging Face), `tbmm_only` konfigürasyonu,
`language == "modern_turkish"`, `term 3–6` → 1316 oturum (kapsam filtresi sonrası: 943 "ana").

**Sistem:** 4 katman (hafif temizlik → regex+sözlük → Zeyrek → kısıtlı LLM).
7 ablation varyantı (a–g) ile her katmanın katkısı ölçülüyor.

**Rol ayrımı (kritik):**
- Yusuf YAZICI → kılavuz + etiketleme, test setini görebilir
- Muhammet Yusuf YILMAZ → kod, **test setini asla görmemeli**
- Dr. Kadir YILMAZ → 2. kodlayıcı + şifre sorumlusu

---

## Ortam

```
conda activate nlpLLM   # Python 3.10, D:\anaconda3\envs\nlpLLM
cd "C:\Users\Yusuf Yazici\Desktop\NLP-Project--Turkish_Normalization"
pytest tests/ -v        # tüm testleri çalıştır (44 passed)
```

**Kurulum notu:** Zeyrek için `python -c "import nltk; nltk.download('punkt_tab')"` gerekli.

**Notebook ortam yönetimi:** `src/ortam.py`
- `ortam_sec()` — Adım 1 notebook'unda çağrılır, Local/Drive seçimi sorar, `proje_config.json`'a kaydeder
- `ortam_yukle()` — Adım 2+ notebook'larında çağrılır, config'i okur, `os.chdir` yapar
- Colab'da Drive seçilirse `/content/drive/MyDrive/NLP-Project--Turkish_Normalization` kullanılır

**Zeyrek OOV tespiti — DOĞRU YÖNTEM:**
`analyzer.analyze(word)` kullan, `lemma == 'Unk'` kontrolü yap.
`lemma == girdi` YANLIŞ — çekimsiz bilinen sözcükler (kitap, ev, okul) de lemma==girdi döndürür.
```python
def _is_oov(word):
    sonuclar = analyzer.analyze(word)
    all_parses = [p for parses in sonuclar for p in parses]
    if not all_parses:
        return True
    return all(p.lemma == "Unk" for p in all_parses)
```

---

## Tamamlanan Adımlar

### ✅ Adım 0 — Ortam ve Repo Kurulumu

- Klasör yapısı kuruldu (`data/raw`, `pool`, `dev`, `test_LOCKED`, `src`, `tests`, `guide`, `results`)
- `data/` tamamen `.gitignore`'da — repoya girmez
- `requirements.txt` yazıldı
- `src/ortam.py` — Local/Drive ortam yöneticisi eklendi
- Zeyrek OOV testleri: `tests/test_adim0.py` (3 test, `analyze()` + `Unk` yöntemi)

### ✅ Adım 1 — Veri İndirme ve Tarihlendirme

**Çıktı:** `data/raw/oturumlar.jsonl`, `data/raw/tarih_raporu.csv`

**Her kayıt şu alanları içeriyor:**
```json
{
  "document_id": "tbmm03001001_eht",
  "term": 3, "year": 1, "session": 1, "volume": 1,
  "takvim_gun": 1, "takvim_ay": 11, "takvim_yil": 1927,
  "date_source": "regex_yazi",
  "kapsam": "erken",
  "alt_donem": "1927-1928",
  "text": "..."
}
```

**Kapsam dağılımı (gerçek veri):**
- `"erken"` → 248 oturum (1927-1928)
- `"ana"`   → 943 oturum (1929-1940) ← asıl deney verisi
- `"gec"`   → 125 oturum (1941-1943)

**Alt dönem (yıl tabanlı):** `"1927-1928"`, `"1929-1934"`, `"1935-1940"`, `"1941-1943"`

**Tarih çıkarma:** regex_yazi: 997 · regex_romen: 305 · regex_sayisal: 5 · komşu: 9

**Testler:** `tests/test_adim1.py` — 24 test geçiyor.

**Manuel doğrulama:** `guide/dogrulama_adim1.csv` — 30 oturum (tüm 9 komşu + tüm 5 regex_sayisal zorunlu dahil).

### ✅ Adım 2 — Oturum Bazlı Bölme

**Girdi:** `oturumlar.jsonl` → yalnızca `kapsam=="ana"` (943 oturum)
**Yöntem:** alt_donem'e göre katmanlı, seed=42, %10 test / %10 dev / %80 havuz
**Çıktı:** `data/split/test_ids.txt`, `data/split/dev_ids.txt`, `data/split/pool_ids.txt`
**Testler:** `tests/test_adim2.py` — 4 test geçiyor (kesişim, bütünlük, determinizm, alt dönem).

### ✅ Adım 3 — Cümle Bölme ve Seçim

**Cümle bölücü:** kısaltma duyarlı (Muh., No., M.M. vb.), tablo/sahne notu/ayraç filtresi.
**Seçim:**
- Dev: 150 rastgele cümle → `data/dev/dev_cumleler.jsonl`
- Test: 200 rastgele + 100 zor (şapkalı harf yoğunluğu) → `data/test_LOCKED/test_cumleler_ham.jsonl`
- Pool: tümü → `data/pool/pool_cumleler.jsonl`

**Zor kriter:** şapkalı harf yoğunluğu (â, î, û) — sistemden bağımsız, deterministik.
**Testler:** `tests/test_adim3.py` — 13 test geçiyor.

---

## Yapılacak Adımlar

### ⬜ Adım 4 — Kılavuz ve Pilot (YY + Danışman)

Şablon: `guide/kilavuz_adim4_sablonu.md`
Normalizasyon karar ağacını yazılı kurallara çevir.
İki kodlayıcı `data/dev/dev_cumleler.jsonl`'den 30 cümleyi bağımsız normalize etsin.
**Hedef: Cohen κ ≥ 0.80** (sözcük düzeyinde, güven aralığıyla raporla)

### ⬜ Adım 5 — Dev Seti Etiketleme (YY)

JSONL formatı:
```json
{"id": "dev_0001", "oturum": "...", "alt_donem": "1935-1940", "girdi": "...", "referans": "..."}
```
Doğrulayıcı betik: her değişiklik izinli kategorilerden biri olmalı.

### ⬜ Adım 6 — Test Seti Kilitleme (YY + Dr. Kadir YILMAZ)

Kural yazmayan kişiler etiketlesin. 50 cümlede çift kodlayıcı κ.
SHA-256 özeti kaydet, şifreli zip'e koy, **proje klasörü dışında** sakla, şifre danışmanda kalsın.
Test betikleri çıktıyı yalnızca şifreli dosyaya yazsın, terminale/log'a basmasın.

### ⬜ Adım 7 — Ölçüm Kodu (sistemden ÖNCE)

Metrikler: CER, WER (`jiwer`), chrF (`sacrebleu`), P/R/F0.5, ADO.

**ADO — sözcük düzeyinde:**
```
ADO = N_sozcuk(girdi==ref AND çıktı!=ref) / N_sozcuk(girdi==ref) × 100
```
Sözcük hizalaması: `difflib`. Birim testleri elle hesaplanmış örneklerle.

### ⬜ Adım 8 — Katman 1: Hafif Ön Temizlik → Varyant (b)

`===== PAGE n =====` ayraçları, markdown tablo kalıntıları, satır sonu tireler.

### ⬜ Adım 9 — Katman 2: Regex + Dönemsel Sözlük → Varyant (c)

Beyaz listeyi **bölmeden sonra** yalnızca `data/pool/` havuzundan üret.
**Kritik testler:** `aid→ait`, `Ahmed→Ahmet`, `kânun→kanun` ✓; `ad→ad`, `kitabı→kitabı` ✗

### ⬜ Adım 10 — Katman 3: Zeyrek Kilitleme

OOV tespiti: `analyzer.analyze()` + `lemma == "Unk"` (çekimsiz sözcük tuzağına dikkat).

### ⬜ Adım 11 — Katman 4: Kısıtlı LLM → Varyantlar (d)–(g)

LLM JSON liste döndürsün. Sıcaklık=0, önbellek, kilitli sözcük koruması.

### ⬜ Adım 12 — Dev'de Tam Ablation

7 varyant (a–g), bootstrap %95 GA, Holm-Wilcoxon, alt dönem kırılımı.

### ⬜ Adım 13 — Dondurma ve Tek Test Koşusu

`git tag v1.0-final` → şifre açılır → **bir kez** çalıştırılır.

### ⬜ Adım 14 — Hata Analizi + Zenodo

Nitel hata taksonomisi. CC BY-NC-SA 4.0 ile Zenodo'ya yükle.

---

## Dosya Yapısı

```
src/
  ortam.py               — Local/Drive ortam yöneticisi
  adim1_veri_indir.py    — veri indirme + tarihlendirme
  adim1_dogrulama_listesi.py
  adim2_bolme.py         — oturum bazlı bölme (seed=42)
  adim3_cumle_sec.py     — cümle bölücü + seçici
tests/
  test_adim0.py          — Zeyrek OOV (3 test)
  test_adim1.py          — tarih çıkarma (24 test)
  test_adim2.py          — bölme doğruluğu (4 test)
  test_adim3.py          — cümle bölücü (13 test)
notebooks/
  adim1_veri_indir.ipynb
  adim2_bolme.ipynb
  adim3_cumle_sec.ipynb
data/raw/
  oturumlar.jsonl        — 1316 oturum (erken:248, ana:943, gec:125)
  tarih_raporu.csv
data/split/              — test/dev/pool ID listeleri
data/dev/                — dev_cumleler.jsonl (150 cümle)
data/pool/               — pool_cumleler.jsonl
data/test_LOCKED/        — test_cumleler_ham.jsonl (300 cümle, henüz etiketlenmedi)
guide/
  dogrulama_adim1.csv
  kilavuz_adim4_sablonu.md
proje_config.json        — ortam.py tarafından üretilir (Local/Drive yolu)
```
