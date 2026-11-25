# Normalizasyon Kılavuzu — Şablon (Adım 4)

**Doldurulacak:** Yusuf YAZICI + Danışman  
**Hedef:** İki kodlayıcı bu kılavuzu okuyarak aynı 30 cümleyi bağımsız normalize ettiğinde Cohen κ ≥ 0.80 çıkmalı.

---

## Temel İlke

> Yalnızca **imla** normalize edilir. Sözcük değiştirilmez, cümle yeniden yazılmaz.  
> Şüpheli durumlarda değiştirme — orijinal forma sadık kal.

---

## Kural 1: Uzun ünlü işaretleri (şapka/düzeltme işareti)

**Kural:** `â → a`, `î → i`, `û → u` — genel sözcüklerde şapka kaldırılır.

| Girdi | Çıktı | Not |
|-------|-------|-----|
| kânun | kanun | ✓ |
| Meclîs | Meclis | ✓ |
| resmî | resmî | ✗ dokunma — özel kullanım |
| kâtip | kâtip | ✗ dokunma — TODO: dönem kılavuzunda doğrula |

---

## Kural 2: Sözcük sonu ünsüz değişimi (d/t, b/p, c/ç, g/k)

**Kural:** Türkçe ses uyumuna aykırı sözcük sonu ünsüzlerini düzelt.

| Girdi | Çıktı | Not |
|-------|-------|-----|
| aid | ait | ✓ |
| inikad | inikat | ✓ |
| had | hat | ✓ |
| ad | ad | ✗ dokunma — zaten doğru |

---

## Kural 3: Özel isim sonları

**Kural:** Özel isimlerde Osmanlı imlası → Türkçe fonetik yazım.

| Girdi | Çıktı | Not |
|-------|-------|-----|
| Ahmed | Ahmet | ✓ |
| Mehmed | Mehmet | ✓ |
| Mahmud | Mahmut | ✓ |
| Hamid | Hamit | ✓ |

---

## Kural 4: OCR gürültüsü

**Kural:** OCR kaynaklı karakter bozulmalarını düzelt.

| Girdi | Çıktı | Not |
|-------|-------|-----|
| Cumhu- riyet | Cumhuriyet | ✓ satır sonu tire |
| ı/i karışması | bağlama göre | dikkatli ol |

---

## Kural 5: Dokunulmaması gerekenler

Aşağıdaki durumlarda **asla değiştirme:**

- Sözcük modern Türkçede zaten geçerliyse (`kitap`, `ev`, `bütçe`)
- Özel terim ve unvanlar (`Reis`, `mebus`, `encümen`)
- Belirsiz durumlarda (iki kural çakışıyorsa orijinali bırak)

---

## Pilot Prosedür

1. Bu kılavuzu oku.
2. `data/dev/dev_cumleler.jsonl`'den **betikle seçilen 30 cümleyi** al.
3. Her cümleyi bağımsız normalize et — diğer kodlayıcıyla konuşma.
4. Sonuçları karşılaştır → Cohen κ hesapla.
5. Anlaşmazlık olan maddeleri tartış, kılavuzu güncelle.
6. κ ≥ 0.80 → Adım 5'e geç.  κ < 0.80 → kılavuzu güncelle, pilotu tekrarla.

---

## Doldurulacak Alanlar

- [ ] Her kural için gerçek metinden 2-3 örnek daha ekle
- [ ] Şüpheli sözcük listesi (pilot sırasında çıkan anlaşmazlıklar)
- [ ] κ sonucu ve tarihi buraya yaz
