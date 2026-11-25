import sys
sys.path.insert(0, "src")

from adim2_bolme import bolme_yap

JSONL = "data/raw/oturumlar.jsonl"


def _yukle():
    try:
        return bolme_yap(JSONL)
    except FileNotFoundError:
        import pytest
        pytest.skip("oturumlar.jsonl bulunamadı — önce adim1_veri_indir.py çalıştır")
    except ValueError as e:
        import pytest
        pytest.skip(str(e))


def test_kesisim_bos():
    bolme = _yukle()
    t = set(bolme["test"])
    d = set(bolme["dev"])
    p = set(bolme["pool"])
    assert not (t & d), "test ve dev kesişiyor"
    assert not (t & p), "test ve pool kesişiyor"
    assert not (d & p), "dev ve pool kesişiyor"


def test_tum_ana_oturumlar_dahil():
    import json
    bolme = _yukle()
    tum_ids = set(bolme["test"]) | set(bolme["dev"]) | set(bolme["pool"])
    with open(JSONL, encoding="utf-8") as f:
        ana_ids = {json.loads(s)["document_id"]
                   for s in f if json.loads(s).get("kapsam") == "ana"}
    assert tum_ids == ana_ids


def test_ayni_seed_ayni_bolme():
    b1 = _yukle()
    b2 = _yukle()
    assert sorted(b1["test"]) == sorted(b2["test"])
    assert sorted(b1["dev"])  == sorted(b2["dev"])
    assert sorted(b1["pool"]) == sorted(b2["pool"])


def test_her_alt_donemde_yeterli_oturum():
    import json
    bolme = _yukle()
    for kume_adi, idler in bolme.items():
        id_set = set(idler)
        with open(JSONL, encoding="utf-8") as f:
            alt_donemler = {json.loads(s)["alt_donem"]
                            for s in f
                            if json.loads(s)["document_id"] in id_set}
        assert len(alt_donemler) >= 2, f"{kume_adi} kümesinde her iki alt dönem yok: {alt_donemler}"
