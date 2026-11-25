# CLAUDE.md — Proje Bağlamı

Bu dosya her oturumda sıfırdan okumayı önlemek için tutulur.
Projeyi tanımak için önce bu dosyayı oku, sonra `PROJE_PLANI.md`'ye bak.

---

## Proje Nedir?

1929–1940 TBMM tutanaklarını modern Türkçe imla kurallarına normalize eden çok katmanlı bir sistem.
TÜBİTAK 2209-A & NLP/LLM dersi kapsamında.

**Veri:** `boun-tabilab/turkish_parliamentary_data` (Hugging Face), `tbmm_only` konfigürasyonu,
`language == "modern_turkish"`, `term 3–6` → 1316 oturum (kapsam filtresi sonrası: 1929-1940).

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
pytest tests/ -v        # tüm testleri çalıştır
```

**Kurulum notu:** Zeyrek için `python -c "import nltk; nltk.download('punkt_tab')"` gerekli.

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
- `data/test_LOCKED/` `.gitignore`'da — repoya girmez
- `requirements.txt` yazıldı
- Zeyrek OOV testleri güncellendi: `tests/test_adim0.py` (3 test, `analyze()` + `Unk` yöntemi)

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

**Kapsam alanı (yıl tabanlı):**
- `"erken"` → 1927-1928 (harf kanunu öncesi, stres testi katmanı)
- `"ana"`   → 1929-1940 (asıl deney verisi, Adım 2'de bu kullanılır)
- `"gec"`   → 1941-1943 (geç dönem yazım değişimi, stres testi katmanı)

**Alt dönem (yıl tabanlı, term'e göre DEĞİL):**
- `"1927-1928"`, `"1929-1934"`, `"1935-1940"`, `"1941-1943"`

**Tarih çıkarma:** 3 format, öncelik sırasıyla:
1. `regex_yazi` — "17 Şubat 1930", "3 Teşrinievvel 1931" → 997 oturum (%75.8)
2. `regex_romen` — "15 - XI - 1937", "7. VIII. 1942" → 305 oturum (%23.2)
3. `regex_sayisal` — "5.1.1929", "31 . 12 . 1928" → 5 oturum (%0.4)
4. `komşu` — aynı ciltte komşu oturumdan → 9 oturum (%0.7)

**Kapsama: 1316/1316 (%100). Dönem fallback hiç kullanılmadı.**

**Testler:** `tests/test_adim1.py` — 24 test, hepsi geçiyor.

**Manuel doğrulama:** `guide/dogrulama_adim1.csv` — 30 oturum:
- Tüm 9 `komşu` + tüm 5 `regex_sayisal` zorunlu dahil
- Kalan 16 slot: term'e göre dağılmış

**Önemli notlar:**
- `language` değeri `"modern_turkish"` (`"tr"` değil)
- Term 3 Kasım 1927'de başlıyor; 1927-1928 kayıtlar `kapsam="erken"`
- Beyaz liste (Adım 9) yalnızca bölmeden SONRA ham havuzdan üretilmeli
- Pilot sayımlar keşif amaçlı, kural kaynağı değil ("bölmeden önce keşif" etiketli)

---

## Yapılacak Adımlar

### ⬜ Adım 2 — Oturum Bazlı Bölme

`oturumlar.jsonl`'deki oturumları `seed=42` ile **test / dev / ham havuz**'a böl.
**Yalnızca `kapsam == "ana"` (1929-1940) kayıtları** kullan.
Alt döneme (`"1929-1934"` / `"1935-1940"`) göre katmanlı örnekleme yap.
Çıktı: 3 ayrı ID listesi dosyası.

**Test:** Üç kümenin kesişimi boş, aynı seed ile aynı bölme çıkıyor.

### ⬜ Adım 3 — Cümle Bölme ve Seçim

Kısaltmalara dikkat eden cümle bölücü yaz ("Muh.", "No." vb.).
Tablo satırlarını, içindekiler satırlarını, "(Alkışlar)" gibi sahne notlarını ele.
Oturum başına en fazla N cümle al (çeşitlilik için).
- **Test:** 200 rastgele + 100 zor cümle (sistemden bağımsız ölçütle — Zeyrek OOV değil)
- **Dev:** 150 cümle
Seçimi betik yapsın, kimse okumasın.

### ⬜ Adım 4 — Kılavuz ve Pilot

Normalizasyon karar ağacını yazılı kurallara çevir.
İki kodlayıcı dev'den 30 cümleyi bağımsız normalize etsin.
**Hedef: Cohen κ ≥ 0.80** (sözcük düzeyinde "değişti/değişmedi", güven aralığıyla raporla)

### ⬜ Adım 5 — Dev Seti Etiketleme

JSONL formatı:
```json
{"id": "dev_0001", "oturum": "...", "alt_donem": "1935-1940", "girdi": "...", "referans": "..."}
```
Doğrulayıcı betik: her değişiklik izinli kategorilerden biri olmalı.

### ⬜ Adım 6 — Test Seti Kilitleme

Kural yazmayan kişiler etiketlesin. 50 cümlede çift kodlayıcı κ.
SHA-256 özeti kaydet, şifreli zip'e koy, **proje klasörü dışında** sakla, şifre danışmanda kalsın.
Test cümlelerini üreten betik çıktıyı yalnızca şifreli dosyaya yazsın, terminale/log'a basmasın.

### ⬜ Adım 7 — Ölçüm Kodu (sistemden ÖNCE)

Metrikler: CER, WER (`jiwer`), chrF (`sacrebleu`), P/R/F0.5, ADO.

**ADO — sözcük düzeyinde tanım:**
```
ADO = (zaten_dogru_sozcuklerden_degistirilen) / (zaten_dogru_sozcuk_sayisi) × 100
    = N_sozcuk(girdi==ref AND çıktı!=ref) / N_sozcuk(girdi==ref) × 100
```
Sözcük hizalaması gerekiyor (`difflib`). Birim testleri elle hesaplanmış örneklerle.

### ⬜ Adım 8 — Katman 1: Hafif Ön Temizlik → Varyant (b)

`===== PAGE n =====` ayraçları, markdown tablo kalıntıları, satır sonu tireler.
**Test:** `Cumhu-\nriyet` → `Cumhuriyet`, gerçek tireli bileşikler korunuyor.

### ⬜ Adım 9 — Katman 2: Regex + Dönemsel Sözlük → Varyant (c)

Beyaz listeyi **bölmeden sonra** yalnızca ham havuzdan üret (imla kılavuzlarından da).
Alt dönem ve sözcük türü parametre olsun.
**Kritik testler:** `aid→ait`, `Ahmed→Ahmet`, `kânun→kanun` ✓; `ad→ad`, `kitabı→kitabı` ✗ (dokunulmamalı).

### ⬜ Adım 10 — Katman 3: Zeyrek Kilitleme

Her sözcük: **kilitli** (Zeyrek tanıyor) veya **şüpheli** (OOV).
OOV tespiti: `analyzer.analyze()` + `lemma == "Unk"` (çekimsiz sözcük tuzağına dikkat — CLAUDE.md ortam bölümüne bak).

### ⬜ Adım 11 — Katman 4: Kısıtlı LLM → Varyantlar (d)–(g)

LLM düzeltilmiş metin değil **JSON liste** döndürsün:
```json
{"duzeltmeler": [{"index": 4, "eski": "inikad", "yeni": "inikat"}]}
```
Sıcaklık=0, sabit model sürümü. Tüm yanıtlar diske önbelleğe alınsın.
Kilitli sözcüklere yapılan değişiklikler kodla otomatik geri alınsın.

### ⬜ Adım 12 — Dev'de Tam Ablation

7 varyant (a–g), bootstrap %95 GA, Holm-Wilcoxon, alt dönem kırılımı.

### ⬜ Adım 13 — Dondurma ve Tek Test Koşusu

`git tag v1.0-final` → test setinin şifresi açılır → **bir kez** çalıştırılır.

### ⬜ Adım 14 — Hata Analizi + Zenodo

Nitel hata taksonomisi. CC BY-NC-SA 4.0 ile Zenodo'ya yükle (DOI al).

---

## Dosya Yapısı

```
src/
  adim1_veri_indir.py        — veri indirme + tarihlendirme (Adım 1)
  adim1_dogrulama_listesi.py — 30 oturumluk PDF doğrulama listesi
tests/
  test_adim0.py              — Zeyrek OOV testleri (3 test, analyze()+Unk yöntemi)
  test_adim1.py              — Tarih çıkarma testleri (24 test)
data/raw/
  oturumlar.jsonl            — 1316 oturum, kapsam + alt_donem bilgisiyle
  tarih_raporu.csv           — yıl bazında oturum sayıları
guide/
  dogrulama_adim1.csv        — 30 oturumun PDF doğrulama listesi
```
