import zeyrek

analyzer = zeyrek.MorphAnalyzer()


def test_zeyrek_bilinen_sozcuk():
    sonuclar = analyzer.lemmatize("mekteplerinde")
    assert len(sonuclar) > 0, "Zeyrek bilinen sözcüğü çözümleyemedi"


def test_zeyrek_oov():
    # OOV durumunda Zeyrek lemma olarak sözcüğün kendisini döndürür: lemma == girdi
    sonuclar = analyzer.lemmatize("mekteblerinde")
    token, lemmalar = sonuclar[0]
    assert token == "mekteblerinde"
    assert lemmalar == ["mekteblerinde"], (
        f"OOV beklentisi: lemma == girdi, gelen: {sonuclar}"
    )


def test_zeyrek_oov_formati():
    """OOV durumunun tam çıktısını görmek için — Adım 10'da buna dayanacağız."""
    bilinen = analyzer.lemmatize("mekteplerinde")
    oov = analyzer.lemmatize("mekteblerinde")
    print(f"\nbilinen → {bilinen}")
    print(f"oov     → {oov}")
