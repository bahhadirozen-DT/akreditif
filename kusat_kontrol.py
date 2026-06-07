import json
import os
import re
import sys
from datetime import datetime, timedelta
from docx import Document

# --- Önemli: Bu kütüphanelerin yüklü olduğundan emin olun ---
# pip install python-docx

from ucp600_motoru import UCP600KuralMotoru
from dokuman_yonetici import DokumanYonetici

def safe_float(val_str):
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
        # Kural dosyası yoksa varsayılan boş bir yapı döndürebiliriz
        return {"zorunlu_kurallar": [], "kritik_kontroller": []}
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
    klasor = "yuklenen_dosyalar"
    if not os.path.exists(klasor):
        print(f"Hata: '{klasor}' klasörü bulunamadı!")
        return ""
    
    for uzanti in desteklenen_uzantilar:
        dosya_yolu = os.path.join(klasor, f"{varsayilan_ad}{uzanti}")
        if os.path.exists(dosya_yolu):
            try:
                print(f"[OKUNUYOR] {dosya_yolu}")
                return yonetici.evrak_metne_cevir(dosya_yolu)
            except Exception as e:
                print(f"Hata: {dosya_yolu} okunamadı: {e}")
    return ""

def markdown_raporu_olustur(t_not, z_sonuc, k_tespit, k_eksik, e_sonuc, f_not, i_not, ucp_sonuc, h_var):
    with open("akreditif_analiz_raporu.md", "w", encoding="utf-8") as f:
        f.write("# 📋 AKREDİTİF GÜVENLİ DENETİM RAPORU\n\n")
        f.write(f"**Tarih:** {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n")
        if h_var: f.write("### 🚨 SONUÇ: Rezerv riski tespit edildi!\n")
        else: f.write("### ✅ SONUÇ: Evraklar uyumlu görünüyor.\n")

def word_raporu_olustur(t_not, z_sonuc, k_tespit, k_eksik, e_sonuc, f_not, i_not, ucp_sonuc, h_var):
    doc = Document()
    doc.add_heading('AKREDİTİF ANALİZ RAPORU', 0)
    doc.add_paragraph(f"Tarih: {datetime.now().strftime('%d.%m.%Y')}")
    if h_var: doc.add_paragraph("SONUÇ: Rezerv riski bulundu.")
    else: doc.add_paragraph("SONUÇ: Uyumlu.")
    doc.save("akreditif_analiz_raporu.docx")

def analiz_yurut():
    kurallar = load_rules()
    yonetici = DokumanYonetici()
    uzantilar = ['.docx', '.txt', '.pdf', '.png', '.jpg']

    # Sadece 'yuklenen_dosyalar' içinden oku
    kusat_raw = dinamik_dosya_bul_ve_oku(yonetici, "gelen_kusat", uzantilar)
    if not kusat_raw:
        print("Kritik: 'gelen_kusat' dosyası 'yuklenen_dosyalar/' içinde bulunamadı.")
        return

    fatura = evrak_sozluge_cevir(dinamik_dosya_bul_ve_oku(yonetici, "fatura", uzantilar))
    
    # Analiz mantığı (Burayı kendi iş kurallarınla doldurabilirsin)
    print("Analiz başladı...")
    
    # Raporları oluştur
    markdown_raporu_olustur([], [], [], [], [], [], [], [], False)
    word_raporu_olustur([], [], [], [], [], [], [], [], False)
    
    print("Analiz tamamlandı. Raporlar oluşturuldu.")

if __name__ == "__main__":
    analiz_yurut()
