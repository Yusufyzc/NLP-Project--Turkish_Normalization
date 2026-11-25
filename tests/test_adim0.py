import zeyrek

analyzer = zeyrek.MorphAnalyzer()


def _is_oov(word: str) -> bool:
    """analyze() çıktısında tüm parse'lar 'Unk' lemma dönüyorsa OOV."""
    sonuclar = analyzer.analyze(word)
    all_parses = [p for parses in sonuclar for p in parses]
    if not all_parses:
        return True
    return all(p.lemma == "Unk" for p in all_parses)


def test_zeyrek_bilinen_cekimli():
    # Çekimli bilinen sözcük OOV değil
    assert not _is_oov("mekteplerinde")


def test_zeyrek_bilinen_cekimsiz():
    # Çekimsiz (yalın) bilinen sözcükler lemma==girdi olsa da OOV değil
    assert not _is_oov("kitap")
    assert not _is_oov("ev")
    assert not _is_oov("okul")


def test_zeyrek_oov():
    # Gerçek OOV: analyze() 'Unk' döndürür
    assert _is_oov("mekteblerinde")
    assert _is_oov("uydurmasözcük")
