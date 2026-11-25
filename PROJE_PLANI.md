# Erken Cumhuriyet Dönemi Türkçe Metinlerinde Kural/Sözlük ve Morfoloji Destekli Yapay Zekâ İmla Normalizasyonu

**Proje Uygulama Planı** — TÜBİTAK 2209-A & NLP/LLM Dersi

> Temel ilke: Sona bırakıp her şeyi bir anda birleştirmek yerine **her adımı test ederek ilerle**. Bir adımın testi geçmeden sonrakine geçilmez.

---

## İçindekiler

1. [Projenin Mantığı](#1-projenin-mantığı)
2. [Ne Yapmamız Gerekiyor](#2-ne-yapmamız-gerekiyor)
3. [Adım Adım İş Planı](#3-adım-adım-iş-planı)
4. [İlerleme Takibi](#4-ilerleme-takibi)
5. [Kaynaklar](#5-kaynaklar)

---

## 1. Projenin Mantığı

### Problem
1928–1940 TBMM tutanakları Latin harfiyle basılmış, ama yazım bugünkü kurallardan farklı (*Ahmed, inikad, kânun*). Üstüne OCR gürültüsü eklenmiş (*Cumhu- riyet*, ı/i karışması). Bu yüzden aramada, indekslemede ve NLP araçlarında bu metinler kötü sonuç veriyor.

### Kolay çözüm ve sorunu
"Metni LLM'e verelim, düzeltsin." Literatür bunun riskli olduğunu gösteriyor:

- LLM cümleyi yeniden yazıyor,
- doğru sözcüğü "düzeltiyor" (*ad → at*),
- dönemin sözcüklerini modernleştiriyor (*mebus → milletvekili*).

Sonuçta metin daha "temiz" görünse de tarihsel olarak yanlış hale geliyor.

### Bizim yaklaşımımız
LLM'i tek başına bırakmak yerine önüne güvenli katmanlar koyuyoruz:

| Katman | Görev | Davranış |
|---|---|---|
| 1. Hafif Ön Temizlik | Sayfa ayraçları, satır sonu tire bölünmeleri | Mekanik, deterministik |
| 2. Kural + Dönemsel Sözlük | Emin olunan dönüşümler (*aid → ait*, *kânun → kanun*) | Deterministik, sözlük onaylı |
| 3. Zeyrek Morfolojik Doğrulama | Doğru sözcükleri **kilitler**, tanınmayanları **şüpheli** işaretler | Koruyucu süzgeç |
| 4. Kısıtlı LLM | Yalnızca şüpheli yerlere dokunabilir | Sıcaklık 0, sert kısıtlı |

### Nasıl kanıtlıyoruz
Katmanları tek tek ekleyip çıkararak (**ablation**) her katmanın katkısını, geliştirme sırasında **hiç görülmemiş, kilitli bir test setinde** ölçüyoruz. Proje "sistemimiz harika" demiyor. "Hangi katman ne kadar işe yarıyor, LLM ne zaman zarar veriyor" sorusunu cevaplıyor. Bilimsel değer burada.

### Başarı ne demek
İki şey **birlikte** sağlanmalı:

1. Hata azalır: CER / WER düşer, chrF ve F0,5 artar.
2. Doğru metin bozulmaz: **Aşırı Düzeltme Oranı** düşük kalır.

İkincisi en az birincisi kadar önemli.

### Sistem varyantları (ablation)

| Kod | Varyant |
|---|---|
| (a) | Taban çizgisi: işlemsiz ham metin |
| (b) | Yalnız hafif ön temizlik |
| (c) | Hafif temizlik + Regex + Dönemsel Sözlük (dil modelsiz) |
| (d) | Yalnız LLM (sıfır atışlı) |
| (e) | Yalnız LLM (kısıtlı istem, kural/sözlük yok) |
| (f) | Regex + Sözlük + Kısıtlı LLM (morfolojisiz) |
| (g) | Tam Sistem: Regex + Sözlük + Zeyrek + Kısıtlı LLM |

---

## 2. Ne Yapmamız Gerekiyor

Büyük resimde dört iş var. **Sıralama önemli.**

1. **Veriyi hazırlamak:** indirmek, tarihlendirmek, oturum bazında üçe bölmek (test / dev / ham havuz).
2. **Referansı (altın standardı) üretmek:** önce kılavuzu yazmak, sonra elle normalize etmek, test setini kilitlemek.
3. **Ölçüm kodunu yazmak, sistemden önce.** Ölçemediğimiz şeyi test edemeyiz. Her katmandan sonra dev setinde skorlara bakabilmek için ölçüm altyapısı ilk elde olmalı.
4. **Katmanları sırayla kurmak:** her katmanı birim testleriyle doğrulamak, dev setinde "bir önceki adımdan kötüleşti mi?" diye kontrol etmek, sonra bir sonrakine geçmek.

### ⚠️ Rol ayrımı (en baştan)

| Kişi | Rol | Test setini görebilir mi? |
|---|---|---|
| Muhammet Yusuf YILMAZ | Kural/Regex, Zeyrek ve LLM katmanlarının kodlanması | ❌ **Hayır** |
| Yusuf YAZICI | Kılavuz, dev ve test etiketlemesi (1. kodlayıcı) | ✅ Evet |
| Dr. Öğr. Üyesi Kadir YILMAZ (veya 3. kişi) | Test etiketlemesi (2. kodlayıcı), şifre sorumlusu | ✅ Evet |

> Kuralları yazan kişi test cümlelerini **hiç görmemeli**. Bu ayrım ilk hafta kesinleşmeli.

---

## 3. Adım Adım İş Planı

Her adımın sonunda bir **✅ Test** var. **Test geçmeden bir sonraki adıma geçilmez.**

---

### Adım 0: Ortam ve Repo Kurulumu

**Yapılacaklar**
- Git reposu aç. Klasör yapısı:
  ```
  proje/
  ├── data/
  │   ├── raw/
  │   ├── pool/
  │   ├── dev/
  │   └── test_LOCKED/      # .gitignore'da!
  ├── guide/                # normalizasyon kılavuzu
  ├── src/
  ├── tests/
  ├── results/
  └── requirements.txt
  ```
- Python sanal ortamı kur. Paketler:
  ```
  datasets
  zeyrek
  jiwer
  sacrebleu
  scipy
  pandas
  pytest
  ```
- `data/test_LOCKED/` klasörünü `.gitignore`'a ekle. Test verisi kod deposuna **girmez**.

**✅ Test**
- [ ] `pytest` boş bir testle çalışıyor.
- [ ] Zeyrek *mekteplerinde* sözcüğünü çözümlüyor.
- [ ] Zeyrek *mekteblerinde* sözcüğünü tanımıyor (OOV).
- [ ] Zeyrek'in OOV'yi **nasıl gösterdiği** not edildi. İlerideki adımlar buna dayanacak.

---

### Adım 1: Veriyi İndirme ve Tarihlendirme ⚠️

**Önemli bulgu**
GNACT (`boun-tabilab/turkish_parliamentary_data`) veri setinde **takvim tarihi içeren ayrı bir alan yok**. Zaman bilgisi yalnızca `term`, `year`, `session`, `volume` alanlarında. Buradaki `year` da takvim yılı değil, **yasama yılı**. Bu yüzden "1928–1940" filtresi doğrudan uygulanamaz.

Veri setinin özellikleri:
- Yapılandırmalar: `full_sessions`, `pages`, `tbmm_only`
- Sütunlar: `document_id`, `legislative_body`, `term`, `year`, `session`, `volume`, `page_num`, `text`, `is_full_session`, `language`
- `language`: `tr` (Modern Türkçe) veya `ota` (Osmanlı Türkçesi)
- Lisans: **CC BY-NC-SA 4.0**

**Yapılacaklar**
- `tbmm_only` yapılandırmasını yükle, `language == "tr"` olanları al, kabaca 3–6. yasama dönemlerini süz.
- Her tutanağın başındaki tarih satırını regex ile çekip **gerçek tarihi** üret.
- **Not:** 1934/35 yazım kırılması büyük olasılıkla **4. dönemden 5. döneme geçişle** çakışıyor. Kırılma yazım değişikliğinden değil kaynak veya dijitalleştirme farkından kaynaklanıyor olabilir. Taramalarla kontrol edildi, ama raporda bu açıkça not edilmeli.
- **Lisans notu:** Paylaşacağımız test seti de CC BY-NC-SA 4.0 ile çıkmalı.

**✅ Test**
- [ ] Oturumların en az %95'inde tarih çıkarılabiliyor.
- [ ] Rastgele 10 oturumun tarihi orijinal tutanak PDF'iyle elle karşılaştırıldı: **10/10**.
- [ ] Yıl başına oturum sayısı tablosu üretildi, **boş yıl yok**.

---

### Adım 2: Oturum Bazlı Bölme (betikle, metni okumadan)

**Yapılacaklar**
- Oturum kimliklerini alt döneme (**1928–1934** / **1935–1940**) göre katmanlandır.
- `seed=42` ile **test / dev / ham havuz** kümelerine dağıt.
- Her kümenin kimlik listesini dosyaya yaz.

**✅ Test**
- [ ] `pytest`: üç kümenin oturum kimlikleri kesişimi **boş**.
- [ ] Betik aynı seed ile tekrar çalıştığında **aynı** bölme çıkıyor.
- [ ] Her alt dönemde yeterli sayıda oturum var.

---

### Adım 3: Cümle Bölme ve Cümle Seçimi

**Yapılacaklar**
- Basit bir cümle bölücü yaz. Kısaltmalara dikkat et ("Muh.", "No." vb.).
- Seçimi **betik yapsın, kimse okumasın**:
  - **Test:** 200 rastgele (temsilî) + 100 zor cümle (ham Zeyrek OOV yoğunluğuna göre)
  - **Dev:** 150 cümle

**✅ Test**
- [ ] Elle bölünmüş 20 örnek paragrafta (**havuzdan** alınmış) bölücü en az **19/20** doğru.
- [ ] Çok kısa (3 sözcükten az) ya da aşırı uzun cümle yok.

---

### Adım 4: Kılavuzu Yazma ve Pilot Uygulama

**Yapılacaklar**
- Karar ağacını (Ek Görsel 2) yazılı kurallara çevir. Her kural için **doğru ve yanlış örnek** ver.
- İki kodlayıcı **dev setinden 30 cümleyi** bağımsız olarak normalize etsin.
- Anlaşmazlıkları tartışıp kılavuzu güncelle.

**✅ Test**
- [ ] Pilotta Cohen **κ ≥ 0,80**. Altında kalırsa kılavuzu düzelt, pilotu tekrarla.

---

### Adım 5: Dev Setini Etiketleme ve Format Doğrulayıcı

**Yapılacaklar**
- Etiketleme formatı JSONL:
  ```json
  {"id": "dev_0001", "oturum": "...", "alt_donem": "1935-1940", "girdi": "...", "referans": "..."}
  ```
- Bir **doğrulayıcı betik** yaz. Kontrol etsin:
  - girdi ile referans arasındaki her değişiklik **izinli bir kategoriye** giriyor (b/d→p/t, şapka, tire, OCR),
  - sözcük sayısı tutarlı.

**✅ Test**
- [ ] Doğrulayıcı 150 cümlenin **hepsinden** geçiyor.
- [ ] Kasten bozulmuş **5 örneği** yakalıyor.

---

### Adım 6: Test Setini Etiketleme ve Kilitleme

**Yapılacaklar**
- Etiketlemeyi **kural yazmayan kişiler** yapsın.
- 50 cümlelik alt kümede çift kodlayıcı κ hesapla.
- Dosyanın **SHA-256** özetini kaydet.
- Dosyayı şifreli bir zip'e koy. **Şifre danışmanda** kalsın.

**✅ Test**
- [ ] κ ≥ 0,80.
- [ ] SHA-256 özeti raporda ve repoda yazılı.

---

### Adım 7: Ölçüm Kodu (sistemden ÖNCE)

**Yapılacaklar**
Ölçülecek metrikler:
- **CER**, **WER** (`jiwer`)
- **chrF** (`sacrebleu`)
- Değişen belirteçlerde **P / R / F0,5**:

  $$F_{0,5} = \frac{1{,}25 \cdot P \cdot R}{0{,}25 \cdot P + R}$$

- **Aşırı Düzeltme Oranı (ADO)**:

  $$ADO = \frac{N(\text{Girdi} = \text{Referans} \land \text{Çıktı} \neq \text{Referans})}{N(\text{Girdi} = \text{Referans})} \times 100$$

- **Yeniden Yazma Oranı** (tanımı netleştirilecek)

Sözcük hizalaması gerekiyor (`difflib` veya Levenshtein hizalaması).

**✅ Test** (elle hesaplanmış küçük örneklerle birim testleri)
- [ ] Girdi = referans = çıktı → CER = 0, ADO = 0
- [ ] Tek doğru düzeltme → P = R = 1
- [ ] Doğru bir sözcüğü bozmak → ADO artıyor
- [ ] Dev setinde **(a) ham metin baseline'ı** hesaplandı. *Bu ilk gerçek sayımız.*

---

### Adım 8: Katman 1, Hafif Ön Temizlik → Varyant (b)

**Yapılacaklar**
- `===== PAGE n =====` ayraçlarını, markdown tablo kalıntılarını ve satır sonu tirelerini temizle.
- Orijinal sözcük sınırlarına müdahale etme.

**✅ Test**
- [ ] Birim testi: `Cumhu-\nriyet` → `Cumhuriyet`
- [ ] Birim testi: `===== PAGE 3 =====` siliniyor
- [ ] Birim testi: gerçek tireli bileşikler korunuyor
- [ ] Dev setinde (b)'nin CER'i (a)'dan **kötü değil**

---

### Adım 9: Katman 2, Regex ve Dönemsel Sözlük → Varyant (c)

**Yapılacaklar**
- Beyaz listeyi **yalnızca ham havuzdan** ve imla kılavuzlarından (1928 / 1935 / 1941) üret.
- Alt dönem (1928–1934 / 1935–1940) ve sözcük türü (özel ad / genel sözcük) **parametre** olarak verilsin.
- Kurallar yalnızca sözlük onaylı köklerde ve bağlamsal sınır koşullarında çalışsın.

**✅ Test** (en kritik birim testleri)
```python
import pytest
from src.katman2 import normalize_token

@pytest.mark.parametrize("girdi,beklenen", [
    # Düzeltilmesi gerekenler
    ("aid", "ait"),
    ("inikad", "inikat"),
    ("Ahmed", "Ahmet"),
    ("kânun", "kanun"),
    # Karşı örnekler: DOKUNULMAMALI
    ("ad", "ad"),
    ("kitabı", "kitabı"),
    ("maksadı", "maksadı"),
    ("nafia", "nafia"),
    ("kâtip", "kâtip"),
    ("resmî", "resmî"),
])
def test_katman2(girdi, beklenen):
    assert normalize_token(girdi, alt_donem="1935-1940") == beklenen
```
- [ ] Tüm birim testleri geçiyor.
- [ ] Dev setinde **ADO ≈ 0**.
- [ ] Dev setinde CER, (b)'ye göre **düşüyor**.
- [ ] Dev'de yakalanan **her hata yeni bir birim testine** dönüştürüldü.

---

### Adım 10: Katman 3, Zeyrek ile Kilitleme

**Yapılacaklar**
- Her sözcüğü etiketle:
  - **kilitli:** Zeyrek veya beyaz liste doğruluyor,
  - **şüpheli:** OOV veya kural adayı.

**✅ Test**
- [ ] Bilinen doğru sözcükler **kilitleniyor**.
- [ ] Bilinen bozuk sözcükler **şüpheli** olarak işaretleniyor.
- [ ] Dev setinde 2. katmandan önce ve sonra **OOV oranı** raporlandı (Hedef 2).

---

### Adım 11: Katman 4, Kısıtlı LLM → Varyantlar (d)–(g)

**Yapılacaklar**
- Sıcaklık = 0, sabit model sürümü.
- LLM düzeltilmiş metni değil, **JSON düzeltme listesi** döndürsün:
  ```json
  {"duzeltmeler": [{"index": 4, "eski": "inikad", "yeni": "inikat"}]}
  ```
- **Sert kısıt:** kilitli sözcüklere yapılan her değişiklik **kodla otomatik geri alınsın**.
- Tüm LLM yanıtlarını **diske önbellekle**. Bütçeyi korur, yeniden üretilebilirlik sağlar.
- İstemlerin SHA-256 özetlerini kaydet.

**✅ Test**
- [ ] **Sahte LLM** ile birim testi: kasten kilitli sözcüğü değiştiren sahte model → değişiklik **geri alınıyor**.
- [ ] Bozuk JSON gelirse sistem çökmüyor, girdiyi aynen döndürüyor.
- [ ] Önce yalnızca **20 dev cümlesiyle** gerçek API denemesi yapıldı, maliyet ölçüldü.

---

### Adım 12: Dev Setinde Tam Deneme

**Yapılacaklar**
- Yedi varyantı (a–g) ve istatistik betiklerini dev setinde **baştan sona** çalıştır:
  - Ortalama ± SS ve Medyan (IQR)
  - Oturum bazlı küme bootstrap (%95 GA, 10.000 yineleme, `seed=42`)
  - Holm düzeltmeli eşleştirilmiş Wilcoxon testi (**önceden belirlenmiş karşılaştırmalar**: c–a/b, e–d, g–e, g–f)
  - 1928–1934 / 1935–1940 alt dönem kırılımı, kutu grafikleri

**✅ Test**
- [ ] **Tek komutla** bütün tablo ve grafikler üretiliyor.
- [ ] Aynı seed ile güven aralıkları **birebir** aynı çıkıyor.

---

### Adım 13: Kodu Dondurma ve Tek Test Koşusu

**Yapılacaklar**
- `git tag v1.0-final`
- İstem özetlerini ve model sürümlerini kaydet.
- **Ancak bundan sonra** test setinin şifresi açılsın, **bir kez** koşulsun (her varyant 3 tekrar).

**✅ Test**
- [ ] Sonuç dosyası, tag'li koda ve test setinin SHA-256 özetine bağlı olarak kaydedildi.

---

### Adım 14: Hata Analizi ve Açık Kaynak Paketi

**Yapılacaklar**
- Aşırı düzeltme ve morfolojik sınır hatalarını **kategorilere ayır** (nitel hata taksonomisi).
- Repoyu, kılavuzu ve veriyi (CC BY-NC-SA 4.0'a uygun) **Zenodo**'ya koy (DOI).

**✅ Test**
- [ ] Repo temiz bir makineye klonlandı, **tek komutla aynı sayılar** çıktı.

---

## 4. İlerleme Takibi

| Adım | Konu | Sorumlu | Çalışma Takvimi İP | Durum |
|---|---|---|---|---|
| 0 | Ortam ve repo | MYY | İP1 | ✅ |
| 1 | Veri indirme + tarihlendirme | MYY | İP1 | ✅ |
| 2 | Oturum bazlı bölme | MYY (betikle) | İP1 | ✅ |
| 3 | Cümle bölme + seçim | MYY (betikle) | İP1 | ✅ |
| 4 | Kılavuz + pilot | YY + Danışman | İP2 | ⬜ |
| 5 | Dev etiketleme | YY | İP2 | ⬜ |
| 6 | Test etiketleme + kilit | YY + Danışman | İP2 | ⬜ |
| 7 | Ölçüm kodu | MYY | İP3 | ⬜ |
| 8 | Katman 1 | MYY | İP3 | ⬜ |
| 9 | Katman 2 | MYY | İP3 | ⬜ |
| 10 | Katman 3 (Zeyrek) | MYY | İP4 | ⬜ |
| 11 | Katman 4 (LLM) | MYY | İP4 | ⬜ |
| 12 | Dev'de tam deneme | MYY + YY | İP4 | ⬜ |
| 13 | Dondurma + test koşusu | YY + Danışman | İP5 | ⬜ |
| 14 | Hata analizi + paket | Tüm ekip | İP6 | ⬜ |

*MYY: Muhammet Yusuf YILMAZ · YY: Yusuf YAZICI · Durum: ⬜ başlanmadı / 🟨 sürüyor / ✅ tamam*

---

## 5. Kaynaklar

- GNACT veri seti: [boun-tabilab/turkish_parliamentary_data (Hugging Face)](https://huggingface.co/datasets/boun-tabilab/turkish_parliamentary_data)
- [TÜBİTAK 2209-A 2026 Yılı Çağrı Duyurusu](https://tubitak.gov.tr/sites/default/files/2026-10/2209-A_2026_Yili_Cagri_Duyurusu.pdf)
- Proje önerisi: *Erken Cumhuriyet Dönemi Türkçe Metinlerinde Kural/Sözlük ve Morfoloji Destekli Yapay Zekâ İmla Normalizasyonu* (TÜBİTAK 2209-A Araştırma Önerisi Formu, 2026)
