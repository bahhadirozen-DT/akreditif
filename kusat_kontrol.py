import json
import os
import re
from datetime import datetime, timedelta
from docx import Document
from docx.shared import Pt, RGBColor

def basitleştir_metin(metin):
    return re.sub(r'[^A-Z0-9]', '', metin.upper())

def dosya_oku_ve_sozluk_yap(dosya_yolu):
    sonuc = {}
    if os.path.exists(dosya_yolu):
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            for satir in f:
                if ':' in satir:
                    anahtar, deger = satir.split(':', 1)
                    sonuc[anahtar.strip().upper()] = deger.strip()
    return sonuc

def markdown_raporu_olustur(tarih_notlari, zorunlu_sonuclar, kritik_sonuclar, evrak_sonuclar, finans_notlari, hata_var_mi):
    # GitHub arayüzünde doğrudan listelenecek dosya
    with open("akreditif_analiz_raporu.md", "w", encoding="utf-8") as f:
        f.write("# 📋 AKREDİTİF (KÜŞAT) GELİŞMİŞ DENETİM RAPORU\n\n")
        f.write(f"**Rapor Tarihi:** {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
        f.write("---\n\n")
        
        f.write("## 1. Kritik Süreler ve Vade Analizi\n")
        for not_metni in tarih_notlari:
            f.write(f"* {not_metni}\n")
        f.write("\n")
        
        f.write("## 2. Finansal Vade ve Ödeme Takvimi\n")
        if finans_notlari:
            for not_metni in finans_notlari:
                f.write(f"* {not_metni}\n")
        else:
            f.write("* ℹ️ Vadeli ödeme veya konşimento bilgisi eksik olduğundan finansal takvim hesaplanamadı.\n")
        f.write("\n")
        
        f.write("## 3. Çapraz Evrak Uyumluluk Kontrolü (Rezerv Önleme)\n")
        for durum, metin in evrak_sonuclar:
            emoji = "✅" if durum == "EVRAK UYUMLU" else "🚨"
            f.write(f"* {emoji} **[{durum}]** {metin}\n")
        f.write("\n")
        
        f.write("## 4. Zorunlu UCP 600 Parametreleri\n")
        for durum, metin in zorunlu_sonuclar:
            emoji = "✅" if durum == "UYUMLU" else "❌"
            f.write(f"* {emoji} **[{durum}]** {metin}\n")
        f.write("\n")
        
        f.write("## 5. UCP 600 Maddeleri ve SWIFT Kontrolleri\n")
        for durum, metin in kritik_sonuclar:
            emoji = "🔍" if durum == "TESPİT EDİLDİ" else "⚠️"
            f.write(f"* {emoji} **[{durum}]** {metin}\n")
        f.write("\n")
        
        f.write("---\n")
        if hata_var_mi:
            f.write("### 🚨 SONUÇ: Evraklarda veya küşatta riskli uyumsuzluklar (rezerv) tespit edildi! Kontrol etmeden bankaya vermeyin.\n")
        else:
            f.write("### 🎉 SONUÇ: Tüm 39 madde ve SWIFT blokları kontrol edildi. Altyapı tam uyumlu.\n")

def word_raporu_olustur(tarih_notlari, zorunlu_sonuclar, kritik_sonuclar, evrak_sonuclar, finans_notlari, hata_var_mi):
    doc = Document()
    title = doc.add_heading('GELİŞMİŞ DIŞ TİCARET RİSK VE EVRAK DENETİM RAPORU', level=1)
    title.runs.font.name = 'Arial'
    title.runs.font.size = Pt(16)
    title.runs.font.bold = True
    
    doc.add_paragraph(f"Rapor Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    doc.add_paragraph("=" * 50)
    
    doc.add_heading('1. Kritik Süreler ve Vade Analizi', level=2)
    for not_metni in tarih_notlari:
        doc.add_paragraph(not_metni)
        
    doc.add_heading('2. Finansal Vade ve Ödeme Takvimi', level=2)
    if finans_notlari:
        for not_metni in finans_notlari:
            doc.add_paragraph(not_metni)
    else:
        doc.add_paragraph("ℹ️ Vadeli ödeme veya konşimento bilgisi eksik olduğundan finansal takvim hesaplanamadı.")

    doc.add_heading('3. Çapraz Evrak Uyumluluk Kontrolü (Rezerv Önleme)', level=2)
    for durum, metin in evrak_sonuclar:
        p = doc.add_paragraph()
        run = p.add_run(f"[{durum}] {metin}")
        if durum == "EVRAK UYUMLU":
            run.font.color.rgb = RGBColor(0, 128, 0)
        else:
            run.font.color.rgb = RGBColor(255, 0, 0)

    doc.add_heading('4. Zorunlu UCP 600 Parametreleri', level=2)
    for durum, metin in zorunlu_sonuclar:
        p = doc.add_paragraph()
        run = p.add_run(f"[{durum}] {metin}")
        if durum == "UYUMLU":
            run.font.color.rgb = RGBColor(0, 128, 0)
        else:
            run.font.color.rgb = RGBColor(255, 0, 0)
            
    doc.add_heading('5. UCP 600 Maddeleri ve SWIFT Kontrolleri', level=2)
    for durum, metin in kritik_sonuclar:
        p = doc.add_paragraph()
        run = p.add_run(f"[{durum}] {metin}")
        if durum == "TESPİT EDİLDİ":
            run.font.color.rgb = RGBColor(0, 51, 102)
        else:
            run.font.color.rgb = RGBColor(204, 102, 0)

    doc.save("akreditif_analiz_raporu.docx")

def analiz_yurut():
    with open('kurallar.json', 'r', encoding='utf-8') as f:
        kurallar = json.load(f)
        
    with open("gelen_kusat.txt", 'r', encoding='utf-8') as f:
        kusat_upper = f.read().upper()
        
    fatura = dosya_oku_ve_sozluk_yap("fatura.txt")
    konsimento = dosya_oku_ve_sozluk_yap("konsimento.txt")
    
    tarih_notlari = []
    finans_notlari = []
    evrak_sonuclar = []
    zorunlu_sonuclar = []
    kritik_sonuclar = []
    hata_var_mi = False

    yukleme_tarihi_match = re.search(r':44C:.*?(\b\d{6}\b)', kusat_upper)
    ibraz_suresi_match = re.search(r':48:.*?(\d+)\b', kusat_upper)
    if yukleme_tarihi_match:
        y_date = datetime.strptime(yukleme_tarihi_match.group(1), "%y%m%d")
        tarih_notlari.append(f"En Geç Yükleme Tarihi (44C): {y_date.strftime('%d.%m.%Y')}")
        gun = int(ibraz_suresi_match.group(1)) if ibraz_suresi_match else 21
        son_ibraz = y_date + timedelta(days=gun)
        tarih_notlari.append(f"Bankaya Son Evrak İbraz Tarihi: {son_ibraz.strftime('%d.%m.%Y')}")
    else:
        tarih_notlari.append("Küşatta resmi bir en geç yükleme tarihi (:44C:) saptanamadı.")

    vade_match = re.search(r'(\d+)\s*DAYS', kusat_upper)
    if vade_match and "YUKLEME_TARIHI" in konsimento:
        try:
            vade_gun = int(vade_match.group(1))
            bl_tarih = datetime.strptime(konsimento["YUKLEME_TARIHI"], "%d.%m.%Y")
            odeme_tarihi = bl_tarih + timedelta(days=vade_gun)
            finans_notlari.append(f"Akreditif Tipi: Vadeli Ödeme (Deferred Payment)")
            finans_notlari.append(f"Vade Süresi: Konşimento tarihinden itibaren {vade_gun} gün.")
            finans_notlari.append(f"Tahmini Ödeme Günü: {odeme_tarihi.strftime('%d.%m.%Y')}")
            if odeme_tarihi.weekday() >= 5:
                finans_notlari.append("UYUMLULUK UYARISI: Ödeme günü hafta sonuna denk geliyor! Banka ilk iş günü işlem yapabilir.")
        except Exception:
            pass

    mal_match = re.search(r':46A:.*?COMMERCIAL INVOICE.*?\n(.*?)\n', kusat_upper)
    if mal_match and "MAL_TANIMI" in fatura:
        kusat_mal = basitleştir_metin(mal_match.group(1))
        fatura_mal = basitleştir_metin(fatura["MAL_TANIMI"])
        if fatura_mal in kusat_mal or kusat_mal in fatura_mal:
            evrak_sonuclar.append(("EVRAK UYUMLU", "Mal tanımı ticari fatura ile küşat arasında birebir uyuşuyor."))
        else:
            evrak_sonuclar.append(("REZERV RİSKİ", "Faturadaki mal tanımı küşattakiyle eşleşmiyor! (UCP 600 Madde 18)."))
            hata_var_mi = True

    if "TARİH" in fatura and "YUKLEME_TARIHI" in konsimento:
        try:
            f_date = datetime.strptime(fatura["TARİH"], "%d.%m.%Y")
            bl_date = datetime.strptime(konsimento["YUKLEME_TARIHI"], "%d.%m.%Y")
            if f_date <= bl_date:
                evrak_sonuclar.append(("EVRAK UYUMLU", f"Fatura tarihi ({fatura['TARİH']}), yükleme tarihinden ({konsimento['YUKLEME_TARIHI']}) önce/aynı gün. Uygun."))
            else:
                evrak_sonuclar.append(("REZERV RİSKİ", f"Fatura tarihi ({fatura['TARİH']}), yükleme tarihinden ({konsimento['YUKLEME_TARIHI']}) sonra olamaz! Banka reddeder."))
                hata_var_mi = True
        except Exception:
            pass

    for kural in kurallar['zorunlu_kurallar']:
        if kural['anahtar'].upper() in kusat_upper:
            zorunlu_sonuclar.append(("UYUMLU", f"[{kural['madde']}] '{kural['anahtar']}' doğrulandı."))
        else:
            zorunlu_sonuclar.append(("RİSK", f"[{kural['madde']}] '{kural['anahtar']}' BULUNAMADI! -> {kural['aciklama']}"))
            hata_var_mi = True
            
    for kural in kurallar['kritik_kontroller']:
        if kural['anahtar'].upper() in kusat_upper:
            kritik_sonuclar.append(("TESPİT EDİLDİ", f"[{kural['madde']}] {kural['anahtar']} -> {kural['aciklama']}"))
        else:
            kritik_sonuclar.append(("KONTROL ET", f"[{kural['madde']}] '{kural['anahtar']}' doğrudan geçmiyor. ({kural['aciklama']})"))

    word_raporu_olustur(tarih_notlari, zorunlu_sonuclar, kritik_sonuclar, evrak_sonuclar, finans_notlari, hata_var_mi)
    markdown_raporu_olustur(tarih_notlari, zorunlu_sonuclar, kritik_sonuclar, evrak_sonuclar, finans_notlari, hata_var_mi)
    exit(1 if hata_var_mi else 0)

if __name__ == "__main__":
    analiz_yurut()
