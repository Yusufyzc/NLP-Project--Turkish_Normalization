# Erken Cumhuriyet Dönemi Türkçe Metinlerinde İmla Normalizasyonu

**TÜBİTAK 2209-A & NLP/LLM Dersi Projesi**

1928–1940 yılları arasındaki TBMM tutanaklarını modern Türkçe imla kurallarına göre normalize eden çok katmanlı bir sistem. Ham LLM kullanımının tarihsel metni bozma riskini ortadan kaldırmak için deterministik katmanlar öne konulmuş, her katmanın katkısı ablation çalışmasıyla ölçülmektedir.

---

## Yaklaşım

| Katman | Görev |
|--------|-------|
| 1. Hafif Ön Temizlik | Sayfa ayraçları, satır sonu tire bölünmeleri |
| 2. Kural + Dönemsel Sözlük | Emin olunan dönüşümler (*aid → ait*, *kânun → kanun*) |
| 3. Zeyrek Morfolojik Doğrulama | Doğru sözcükleri kilitler, tanınmayanları şüpheli işaretler |
| 4. Kısıtlı LLM | Yalnızca şüpheli yerlere dokunur, sıcaklık = 0 |

Sistem 7 farklı varyantla (a–g) karşılaştırılarak her katmanın etkisi bağımsız olarak ölçülmektedir.

---

## Klasör Yapısı

```
proje/
├── data/
│   ├── raw/          # Ham indirilen veri
│   ├── pool/         # Etiketlenmemiş havuz
│   ├── dev/          # Geliştirme seti
│   └── test_LOCKED/  # Kilitli test seti (.gitignore'da)
├── guide/            # Normalizasyon kılavuzu
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

Testleri çalıştır:

```bash
pytest tests/ -v
```

---

## İlerleme

| Adım | Konu | Sorumlu | Durum |
|------|------|---------|-------|
| 0 | Ortam ve repo kurulumu | MYY | ✅ |
| 1 | Veri indirme + tarihlendirme | MYY | ⬜ |
| 2 | Oturum bazlı bölme (test/dev/havuz) | MYY | ⬜ |
| 3 | Cümle bölme + seçim | MYY | ⬜ |
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

[GNACT — boun-tabilab/turkish_parliamentary_data](https://huggingface.co/datasets/boun-tabilab/turkish_parliamentary_data) · Lisans: CC BY-NC-SA 4.0
