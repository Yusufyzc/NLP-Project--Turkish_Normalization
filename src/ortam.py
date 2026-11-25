"""
Ortam yönetimi: Local veya Google Drive.

Adım 1'de ortam_sec() çağrılır, seçim proje_config.json'a kaydedilir.
Diğer adımlarda ortam_yukle() çağrılır, config okunur ve çalışma dizini ayarlanır.
"""

import os
import json
import sys
from pathlib import Path

CONFIG_ADI = "proje_config.json"
PROJE_ADI  = "NLP-Project--Turkish_Normalization"


def _in_colab() -> bool:
    try:
        import google.colab  # noqa: F401
        return True
    except ImportError:
        return False


def _proje_koku() -> str:
    """Çalışma dizinini proje köküne ayarla, yolunu döndür."""
    for aday in [Path("."), Path("..")]:
        if (aday / "src").exists() and (aday / "requirements.txt").exists():
            kok = str(aday.resolve())
            os.chdir(kok)
            return kok
    # Bulamazsa mevcut dizini kullan
    return str(Path(".").resolve())


# ---------------------------------------------------------------------------
# Adım 1'de çağrılır
# ---------------------------------------------------------------------------
def ortam_sec() -> str:
    """
    Kullanıcıya Local / Google Drive seçimi sorar.
    Seçimi proje_config.json'a kaydeder.
    Çalışma dizinini proje köküne ayarlar.
    Proje kök yolunu döndürür.
    """
    print("╔══════════════════════════════════════╗")
    print("║         DEPOLAMA SEÇİMİ              ║")
    print("╠══════════════════════════════════════╣")
    print("║  1 → Local  (bilgisayarımda çalışır) ║")
    print("║  2 → Google Drive  (Colab için)      ║")
    print("╚══════════════════════════════════════╝")

    while True:
        s = input("\nSeçiminiz (1/2): ").strip()
        if s in ("1", "2"):
            break
        print("Lütfen 1 veya 2 girin.")

    if s == "2":
        from google.colab import drive as _drive
        print("\nGoogle Drive bağlanıyor...")
        _drive.mount("/content/drive")
        base = f"/content/drive/MyDrive/{PROJE_ADI}"
        Path(base).mkdir(parents=True, exist_ok=True)
        os.chdir(base)
        sys.path.insert(0, f"{base}/src")
        mod = "drive"
        print(f"\n✓ Google Drive bağlandı.")
        print(f"📁 Klasör: https://drive.google.com (Drive'ı açıp '{PROJE_ADI}' klasörünü bulun)")
    else:
        base = _proje_koku()
        sys.path.insert(0, f"{base}/src")
        mod = "local"
        print(f"\n✓ Local çalışma dizini: {base}")

    # Config kaydet
    config = {"mod": mod, "base": base}
    with open(Path(base) / CONFIG_ADI, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False)

    return base


# ---------------------------------------------------------------------------
# Adım 2+ notebook'larında çağrılır
# ---------------------------------------------------------------------------
def ortam_yukle() -> str:
    """
    Kaydedilmiş config'i bulur, çalışma dizinini ayarlar.
    Config yoksa önce adim1 çalıştır hatası verir.
    """
    # Önce local dizinlerde ara
    for aday in [Path("."), Path("..")]:
        yol = aday / CONFIG_ADI
        if yol.exists():
            config = json.loads(yol.read_text(encoding="utf-8"))
            base = config["base"]
            os.chdir(base)
            sys.path.insert(0, f"{base}/src")
            print(f"✓ {config['mod'].upper()} — {base}")
            return base

    # Colab'da Drive'da ara
    if _in_colab():
        drive_yol = Path(f"/content/drive/MyDrive/{PROJE_ADI}/{CONFIG_ADI}")
        if not drive_yol.exists():
            # Drive bağlı değilse bağla
            from google.colab import drive as _drive
            _drive.mount("/content/drive")
        if drive_yol.exists():
            config = json.loads(drive_yol.read_text(encoding="utf-8"))
            base = config["base"]
            os.chdir(base)
            sys.path.insert(0, f"{base}/src")
            print(f"✓ DRIVE — {base}")
            return base

    raise FileNotFoundError(
        f"'{CONFIG_ADI}' bulunamadı.\n"
        "Lütfen önce adim1_veri_indir.ipynb notebook'unu çalıştırın."
    )
