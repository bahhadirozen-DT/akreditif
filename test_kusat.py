import os
import json
import pytest
from kusat_kontrol import safe_float, normalize_text, analiz_yurut

# ==========================================
# 1. BİRİM TESTLERİ (UNIT TESTS - EDGE CASES)
# ==========================================

@pytest.mark.parametrize("input_val, expected", [
    ("1.500,00", 1500.0),
    ("1,500.00", 1500.0),
    ("  USD 250.75 ", 250.75),
    ("100.500.200,50", 100500200.50),
    ("0", 0.0),
    ("", 0.0),
    ("EUR 450", 450.0)
])
def test_safe_float_edge_cases(input_val, expected):
    """Farklı finansal formatların dönüşüm güvenliğini test eder."""
    assert safe_float(input_val) == expected


@pytest.mark.parametrize("input_text, expected", [
    ("COTTON 100%", "COTTON 100%"),
    ("PIECES / KG", "PIECES / KG"),
    ("Çelik Profil GMS.", "CELIK PROFIL GMS."),
    ("Multi \n  Line   Text", "MULTI LINE TEXT"),
    ("GEREKSİZ   BOŞLUKLAR", "GEREKSIZ BOSLUKLAR")
])
def test_normalize_text_banking_standards(input_text, expected):
    """Kritik dış ticaret karakterlerinin korunduğunu test eder."""
    assert normalize_text(input_text) == expected


# ==========================================
# 2. ENTEGRASYON TESTLERİ (MOCK ENVIRONMENTS)
# ==========================================

@pytest.fixture
def hazir_test_ortami():
    """Test öncesi sahte evrakları oluşturur, test sonrası temizler."""
    
    # Sahte Kurallar JSON
    kurallar_data = {
        "zorunlu_kurallar": [{"anahtar": "40A"}],
        "kritik_kontroller": [{"madde": "UCP 43", "anahtar": "PARTIAL SHIPMENTS DISALLOWED"}]
    }
    with open("kurallar.json", "w", encoding="utf-8") as f:
        json.dump(kurallar_data, f)

    # Sahte SWIFT MT700 (Gelen Akreditif)
    kusat_data = (
        ":40A:IRREVOCABLE\n"
        ":32B:USD 100000,00\n"
        ":44C:260330\n"  # En geç yükleme: 26 Mart 2030
        ":45A:COTTON 100% Woven Fabric\n"
        "PARTIAL SHIPMENTS DISALLOWED\n"
    )
    with open("gelen_kusat.txt", "w", encoding="utf-8") as f:
        f.write(kusat_data)

    # Sahte Ticari Fatura
    fatura_data = "TUTAR: 100.000,00\nMAL_TANIMI: COTTON 100% Woven Fabric\nTARIH: 20.03.2030\n"
    with open("fatura.txt", "w", encoding="utf-8") as f:
        f.write(fatura_data)

    # Sahte Konşimento (B/L)
    konsimento_data = "YUKLEME_TARIHI: 22.03.2030\n"
    with open("konsimento.txt", "w", encoding="utf-8") as f:
        f.write(konsimento_data)

    # Sahte Sigorta Poliçesi (%110 Tam Uyumlu)
    sigorta_data = "SIGORTA_TUTARI: 110.000,00\nTARIH: 21.03.2030\n"
    with open("sigorta.txt", "w", encoding="utf-8") as f:
        f.write(sigorta_data)

    yield  # Testin koştuğu an

    # Test bittikten sonra üretilen sahte girdi ve çıktı dosyalarını temizle temizle
    dosyalar = ["kurallar.json", "gelen_kusat.txt", "fatura.txt", "konsimento.txt", "sigorta.txt", 
                "akreditif_analiz_raporu.md", "akreditif_analiz_raporu.docx"]
    for d in dosyalar:
        if os.path.exists(d):
            os.remove(d)


def test_analiz_yurut_tam_uyum_senaryosu(hazir_test_ortami):
    """Tüm evraklar uyumlu olduğunda raporların hatasız üretildiğini doğrular."""
    
    # Ana fonksiyonu çalıştır
    analiz_yurut()
    
    # Raporlar başarıyla oluşturuldu mu?
    assert os.path.exists("akreditif_analiz_raporu.md")
    assert os.path.exists("akreditif_analiz_raporu.docx")
    
    # Rapor içeriğini oku ve rezerv riskinin OLMADIĞINI (Başarı durumunu) kontrol et
    with open("akreditif_analiz_raporu.md", "r", encoding="utf-8") as f:
        rapor_icerik = f.read()
        
    assert "Tüm kontroller başarıyla tamamlandı" in rapor_icerik
    assert "REZERV RİSKİ" not in rapor_icerik
