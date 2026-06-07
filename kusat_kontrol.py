import json
import os
import re
from datetime import datetime, timedelta
from docx import Document
from docx.shared import Pt, RGBColor

def word_raporu_olustur(tarih_notlari, zorunlu_sonuclar, kritik_sonuclar, hata_var_mi):
    doc = Document()
    
    # Başlık Stili
    title = doc.add_heading('AKREDİTİF (KÜŞAT) DENETİM RAPORU', level=1)
    title.runs[0].font.name = 'Arial'
    title.runs[0].font.size = Pt(18)
    title.runs[0].font.bold = True
    
    # Tarih ekle
    doc.add_paragraph(f"Rapor Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    doc.add_paragraph("-" * 40)
    
    # 1. Bölüm: Tarih Analizi
    doc.add_heading('1. Tarih ve Vade Analizi', level=2)
    for not_metni in tarih_notlari:
        doc.add_paragraph(not_metni)
        
    # 2. Bölüm: Zorunlu Kurallar
    doc.add_heading('2. Zorunlu UCP 600 Parametreleri', level=2)
    for durum, metin in zorunlu_sonuclar:
        p = doc.add_paragraph()
        run = p.add_run(f"[{durum}] {metin}")
        if durum == "UYUMLU":
            run.font.color.rgb = RGBColor(0, 128, 0) # Yeşil
        else:
            run.font.color.rgb = RGBColor(255, 0, 0) # Kırmızı
            
    # 3. Bölüm: Operasyonel Kontroller
    doc.add_heading('3. UCP 600 Maddeleri ve SWIFT Kontrolleri', level=2)
    for durum, metin in kritik_sonuclar:
        p = doc.add_paragraph()
        run = p.add_run(f"[{durum}] {metin}")
        if durum == "TESPİT EDİLDİ":
            run.font.color.rgb = RGBColor(0, 51, 102) # Koyu Mavi
        else:
            run.font.color.rgb = RGBColor(204, 102, 0) # Turuncu

    # Sonuç Özeti
    doc.add_paragraph("-" * 40)
    p_sonuc = doc.add_paragraph()
    if hata_var_mi:
        run_s = p_sonuc.add_run("🚨 SONUÇ: Kritik UCP 600 eksiklikleri var! Bu küşatı onaylamayın.")
        run_s.font.bold = True
        run_s.font.color.rgb = RGBColor(255, 0, 0)
    else:
        run_s = p_sonuc.add_run("🎉 SONUÇ: Tüm 39 madde ve SWIFT blokları kontrol edildi. Altyapı tam uyumlu.")
        run_s.font.bold = True
        run_s.font.color.rgb = RGBColor(0, 128, 0)
        
    # Dosyayı kaydet
    doc.save("akreditif_analiz_raporu.docx")
    print("📝 Word raporu 'akreditif_analiz_raporu.docx' adıyla başarıyla oluşturuldu.")

def tarih_bul_ve_hesapla(metin, tarih_notlari):
    yukleme_tarihi_match = re.search(r':44C:.*?(\b\d{6}\b)', metin)
    ibraz_suresi_match = re.search(r':48:.*?(\d+)\b', metin)
    
    if yukleme_tarihi_match:
        try:
            y_str = yukleme_tarihi_match.group(1)
            y_date = datetime.strptime(y_str, "%y%m%d")
            tarih_notlari.append(f"📅 En Geç Yükleme Tarihi (44C): {y_date.strftime('%d.%m.%Y')}")
            
            gun_sayisi = 21
            if ibraz_suresi_match:
                gun_sayisi = int(ibraz_suresi_match.group(1))
                tarih_notlari.append(f"ℹ️ Özel İbraz Süresi Tespit Edildi (:48:): {gun_sayisi} Gün")
            else:
                tarih_notlari.append("ℹ️ Özel ibraz süresi bulunamadı. UCP 600 Madde 14 gereği standart 21 gün uygulandı.")
                
            son_ibraz = y_date + timedelta(days=gun_sayisi)
            tarih_notlari.append(f"🚨 Bankaya Son Belge Teslim Tarihi: {son_ibraz.strftime('%d.%m.%Y')} (Kritik Vade!)")
        except Exception:
            tarih_notlari.append("⚠️ Tarih formatı çözümlenirken bir sorun oluştu, manuel kontrol edin.")
    else:
        tarih_notlari.append("⚠️ Metinde net bir ':44C:' en geç yükleme tarihi kodu bulunamadı.")

def kusat_analiz_et(kusat_dosya_yolu):
    if not os.path.exists(kusat_dosya_yolu):
        print(f"❌ HATA: '{kusat_dosya_yolu}' dosyası bulunamadı.")
        return

    with open('kurallar.json', 'r', encoding='utf-8') as f:
        kurallar = json.load(f)
        
    with open(kusat_dosya_yolu, 'r', encoding='utf-8') as f:
        kusat_metni_upper = f.read().upper()
        
    tarih_notlari = []
    tarih_bul_ve_hesapla(kusat_metni_upper, tarih_notlari)
    
    zorunlu_sonuclar = []
    kritik_sonuclar = []
    hata_var_mi = False

    # Zorunlu Kurallar
    for kural in kurallar['zorunlu_kurallar']:
        if kural['anahtar'].upper() in kusat_metni_upper:
            zorunlu_sonuclar.append(("UYUMLU", f"[{kural['madde']}] '{kural['anahtar']}' metinde doğrulandı."))
        else:
            zorunlu_sonuclar.append(("RİSK", f"[{kural['madde']}] '{kural['anahtar']}' BULUNAMADI! -> {kural['aciklama']}"))
            hata_var_mi = True
            
    # Kritik Kontroller
    for kural in kurallar['kritik_kontroller']:
        if kural['anahtar'].upper() in kusat_metni_upper:
            kritik_sonuclar.append(("TESPİT EDİLDİ", f"[{kural['madde']}] {kural['anahtar']} -> {kural['aciklama']}"))
        else:
            kritik_sonuclar.append(("KONTROL ET", f"[{kural['madde']}] '{kural['anahtar']}' doğrudan geçmiyor. ({kural['aciklama']})"))

    # Word Dokümanını Oluştur
    word_raporu_olustur(tarih_notlari, zorunlu_sonuclar, kritik_sonuclar, hata_var_mi)

    if hata_var_mi:
        exit(1)
    else:
        exit(0)

if __name__ == "__main__":
    kusat_analiz_et("gelen_kusat.txt")
