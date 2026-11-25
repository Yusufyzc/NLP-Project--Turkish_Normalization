# Erken Cumhuriyet Dönemi Türkçe Metinlerinde İmla Normalizasyonu

**TÜBİTAK 2209-A & NLP/LLM Dersi Projesi**

1929–1940 yılları arasındaki TBMM tutanaklarını modern Türkçe imla kurallarına göre normalize eden çok katmanlı bir sistem.

Bu dönem tutanakları Latin harfli yazılmış, ancak imlası henüz standartlaşmamış geçiş dönemi metinleridir. Modern NLP/LLM araçları bu metinleri "bozuk Türkçe" olarak algılar; normalizasyon sistemi bu köprüyü kurar ve metinleri modern araçlarla işlenebilir hale getirir.

Ham LLM kullanımının tarihsel metni bozma riskini azaltmak için deterministik katmanlar öne konulmuş, her katmanın katkısı ablation çalışmasıyla ölçülmektedir.

---

## Neden Zor?

1928-1940 arası metinler Latin harflidir ama yazım henüz standartlaşmamıştır:

| Dönem metni | Modern Türkçe | Sorun türü |
|-------------|---------------|------------|
| `aid` | `ait` | ses değişimi |
| `kânun` | `kanun` | uzun ünlü işareti |
| `meclisden` | `meclisten` | ek yazımı |
| `inikad` | `intikat` | Arapça köklü fonetik |
| `musâvî` / `musavi` / `musavidir` | (aynı sözcük, 3 form) | tutarsız yazım |

Modern LLM'ler bu dönem yazımına neredeyse hiç maruz kalmamış, bu yüzden metni yanlış anlıyor.

---

## Yaklaşım

| Katman | Görev |
|--------|-------|
| 1. Hafif Ön Temizlik | Sayfa ayraçları, satır sonu tire bölünmeleri |
| 2. Kural + Dönemsel Sözlük | Dönemin imla kılavuzlarından üretilen emin dönüşümler |
| 3. Zeyrek Morfolojik Doğrulama | Modern Türkçede geçerli sözcükleri kilitler, bilinmeyenleri şüpheli işaretler |
| 4. Kısıtlı LLM | Yalnızca şüpheli sözcüklere dokunur, JSON liste döndürür, sıcaklık = 0 |

Sistem 7 farklı varyantla (a–g) karşılaştırılarak her katmanın etkisi bağımsız ölçülmektedir.

---

## Klasör Yapısı

```
proje/
├── data/             # .gitignore'da — kullanıcı kendisi üretir
│   ├── raw/          # Ham indirilen veri (oturumlar.jsonl)
│   ├── pool/         # Etiketlenmemiş oturum havuzu
│   ├── dev/          # Geliştirme seti
│   └── test_LOCKED/  # Kilitli test seti (asla repoya girmez)
├── notebooks/        # Her adım için Jupyter notebook
├── guide/            # Normalizasyon kılavuzu ve doğrulama listeleri
├── src/              # Kaynak kod
├── tests/            # Birim testleri
├── results/          # Deney çıktıları
└── requirements.txt
```

---

## Kurulum

```bash
conda create -n nlpLLM python=3.10
conda activate nlpLLM
pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt_tab')"
```

### Veriyi İndir

`data/` dizini `.gitignore`'da — repoda bulunmaz.

**Notebook ile (önerilen):** `notebooks/adim1_veri_indir.ipynb` dosyasını aç.
İlk hücre Local veya Google Drive seçimi sorar ve `proje_config.json`'a kaydeder.
Sonraki adımlar (`adim2_bolme.ipynb`, `adim3_cumle_sec.ipynb`) bu config'i otomatik okur.

**Betik ile:**

```bash
python src/adim1_veri_indir.py
python src/adim2_bolme.py
python src/adim3_cumle_sec.py
```

Kaynak: [`boun-tabilab/turkish_parliamentary_data`](https://huggingface.co/datasets/boun-tabilab/turkish_parliamentary_data)
(`tbmm_only` konfigürasyonu, `language == "modern_turkish"`, term 3–6)

Testleri çalıştır:

```bash
pytest tests/ -v   # 44 test, hepsi geçmeli
```

---

## İlerleme

| Adım | Konu | Sorumlu | Durum |
|------|------|---------|-------|
| 0 | Ortam ve repo kurulumu | MYY | ✅ |
| 1 | Veri indirme + tarihlendirme (1316/1316) | MYY | ✅ |
| 2 | Oturum bazlı bölme (test/dev/havuz) | MYY | ✅ |
| 3 | Cümle bölme + seçim | MYY | ✅ |
| 4 | Normalizasyon kılavuzu + pilot (κ ≥ 0,80) | YY + Danışman | ⬜ |
| 5 | Dev seti etiketleme + doğrulayıcı | YY | ⬜ |
| 6 | Test seti etiketleme + kilitleme | YY + Danışman | ⬜ |
| 7 | Ölçüm kodu (CER, WER, chrF, F0,5, ADO) | MYY | ⬜ |
| 8 | Katman 1: Hafif ön temizlik | MYY | ⬜ |
| 9 | Katman 2: Regex + Dönemsel Sözlük | MYY | ⬜ |
| 10 | Katman 3: Zeyrek morfolojik kilitleme | MYY | ⬜ |
| 11 | Katman 4: Kısıtlı LLM | MYY | ⬜ |
| 12 | Dev setinde tam ablation denemesi | MYY + YY | ⬜ |
| 13 | Kod dondurma + tek test koşusu | YY + Danışman | ⬜ |
| 14 | Hata analizi + Zenodo açık kaynak paketi | Tüm ekip | ⬜ |

---

## Ekip

| Kişi | Rol |
|------|-----|
| Muhammet Yusuf YILMAZ | Kod geliştirme (test setini görmez) |
| Yusuf YAZICI | Kılavuz ve etiketleme (1. kodlayıcı) |
| Dr. Öğr. Üyesi Kadir YILMAZ | Test etiketleme (2. kodlayıcı), şifre sorumlusu |

---

## Veri Seti

[boun-tabilab/turkish_parliamentary_data](https://huggingface.co/datasets/boun-tabilab/turkish_parliamentary_data) · Lisans: CC BY-NC-SA 4.0
