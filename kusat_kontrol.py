import json
import os
import re
import sys
from datetime import datetime, timedelta
from docx import Document
from ucp600_motoru import UCP600KuralMotoru, normalize_text
from dokuman_yonetici import DokumanYonetici

def safe_float(val_str):
    """Finansal tutarları güvenli bir şekilde float tipine dönüştürür."""
    try:
        if not val_str: return 0.0
        val_str = str(val_str).strip()
        if (',' in val_str and '.' in val_str and val_str.rfind(',') > val_str.rfind('.')) or (',' in val_str and '.' not in val_str):
            val_str = val_str.replace('.', '').replace(',', '.')
        else:
            val_str = val_str.replace(',', '')
        val_str = re.sub(r'[^0-9.]', '', val_str)
        return float(val_str) if val_str else 0.0
    except:
        return 0.0

def load_rules(config_path="kurallar.json"):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Kritik Hata: {config_path} bulunamadı!")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def evrak_sozluge_cevir(metin):
    sonuc = {}
    if not metin: return sonuc
    for satir in metin.split('\n'):
        if ':' in satir:
            a, d = satir.split(':', 1)
            anahtar = a.strip().upper().replace("İ", "I").replace(" ", "_")
            sonuc[anahtar] = d.strip()
    return sonuc

def dinamik_dosya_bul_ve_oku(yonetici, varsayilan_ad, desteklenen_uzantilar):
    """SADECE 'yuklenen_dosyalar/' klasöründe arama yapar."""
    klasor = "yuklenen_dosyalar"
    if not os.path.exists(klasor):
        print(f"Hata: '{klasor}' klasörü bulunamadı!")
        return ""
    
    for uzanti in desteklenen_uzantilar:
        dosya_yolu = os.path.join(klasor, f"{varsayilan_ad}{uzanti}")
        if os.path.exists(dosya_yolu):
            try:
                return yonetici.evrak_metne_cevir(dosya_yolu)
            except Exception as e:
                print(f"Hata: {dosya_yolu} dosyası okunamadı: {e}")
    return ""

def madde_uzman_yorumu_al(madde_adi):
    yorumlar = {
        "Art 2": "Tanımlamalar maddesidir.", "Art 4": "Bağımsızlık ilkesi.", 
        "Art 5": "Belge Ticareti İlkesi.", "Art 6": "Kullanım yeri.", 
        "Art 7": "Amir banka sorumluluğu.", "Art 8": "Teyit bankası.", 
        "Art 14": "Belge inceleme standartları.", "Art 18": "Ticari fatura kuralları.", 
        "Art 20": "Deniz konşimentosu.", "Art 27": "Temiz konşimento.", 
        "Art 28": "Sigorta belgeleri.", "Art 31": "Kısmi yükleme."
    }
    return yorumlar.get(madde_adi.replace("[", "").replace("]", "").strip(), "UCP 600 kurallarına tabidir.")

# --- Raporlama Fonksiyonları (Önceki yapınızla aynı) ---
def markdown_raporu_olustur(t_not, z_sonuc, k_tespit, k_eksik, e_sonuc, f_not, i_not, ucp_sonuc, h_var):
    with open("akreditif_analiz_raporu.md", "w", encoding="utf-8") as f:
        f.write("# AKREDİTİF DENETİM RAPORU\n\n")
        # Rapor içeriği... (Eski kodunuzla aynı)

def word_raporu_olustur(t_not, z_sonuc, k_tespit, k_eksik, e_sonuc, f_not, i_not, ucp_sonuc, h_var):
    doc = Document()
    doc.add_heading('GELİŞMİŞ DIŞ TİCARET DENETİM RAPORU', 0)
    # Rapor içeriği... (Eski kodunuzla aynı)
    doc.save("akreditif_analiz_raporu.docx")

def analiz_yurut():
    kural_dosyasi = 'kurRules.json' if os.path.exists('kurRules.json') else 'kurallar.json'
    try:
        kurallar = load_rules(kural_dosyasi)
    except Exception as e:
        print(e)
        return

    yonetici = DokumanYonetici()
    uzantilar = ['.docx', '.xlsx', '.pdf', '.png', '.jpg', '.jpeg', '.txt']

    # Sadece klasör odaklı okuma
    kusat_raw = dinamik_dosya_bul_ve_oku(yonetici, "gelen_kusat", uzantilar)
    if not kusat_raw:
        print("Hata: 'yuklenen_dosyalar' içinde 'gelen_kusat' bulunamadı!")
        return

    kusat_upper = kusat_raw.upper()
    fatura = evrak_sozluge_cevir(dinamik_dosya_bul_ve_oku(yonetici, "fatura", uzantilar))
    konsimento = evrak_sozluge_cevir(dinamik_dosya_bul_ve_oku(yonetici, "konsimento", uzantilar))
    sigorta = evrak_sozluge_cevir(dinamik_dosya_bul_ve_oku(yonetici, "sigorta", uzantilar))
    
    # ... (Analiz mantığı bloğunuz buraya devam eder)
    
    # Raporlar
    word_raporu_olustur([], [], [], [], [], [], [], [], False)
    markdown_raporu_olustur([], [], [], [], [], [], [], [], False)
    print("Analiz klasör destekli olarak tamamlandı.")

if __name__ == "__main__":
    analiz_yurut()
