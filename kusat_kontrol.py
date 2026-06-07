import json
import os
import re
from datetime import datetime, timedelta
from docx import Document
from docx.shared import Pt, RGBColor

def basitleştir_metin(metin):
    # Karşılaştırmaları kolaylaştırmak için boşlukları ve noktalama işaretlerini temizler
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

def word_raporu_olustur(tarih_notlari, zorunlu_sonuclar, kritik_sonuclar, evrak_sonuclar, finans_notlari, hata_var_mi):
    doc = Document()
    
    title = doc.add_heading('GELİŞMİŞ DIŞ TİCARET RİSK VE EVRAK DENETİM RAPORU', level=1)
    title.runs.font.name = 'Arial'
    title.runs.font.size = Pt(16)
    title.runs.font.bold = True
    
    doc.add_paragraph(f"Rapor Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    doc.add_paragraph("=" * 50)
    
    # 1. Bölüm: Tarih Analizi
    doc.add_heading('1. Kritik Süreler ve Vade Analizi', level=2)
    for not_metni in tarih_notlari:
        doc.add_paragraph(not_metni)
        
    # 2. Bölüm: Finansal Hesaplamalar
    doc.add_heading('2. Finansal Vade ve Ödeme Takvimi', level=2)
    if finans_notlari:
        for not_metni in finans_notlari:
            doc.add_paragraph(not_metni)
    else:
        doc.add_paragraph("ℹ️ Vadeli ödeme veya konşimento bilgisi eksik olduğundan finansal takvim hesaplanamadı.")

    # 3. Bölüm: Çapraz Evrak Uyumluluk Kontrolü
    doc.add_heading('3. Çapraz Evrak Uyumluluk Kontrolü (Rezerv Önleme)', level=2)
    for durum, metin in evrak_sonuclar:
        p = doc.add_paragraph()
        run = p.add_run(f"[{durum}] {metin}")
        if durum == "EVRAK UYUMLU":
            run.font.color.rgb = RGBColor(0, 128, 0)
        else:
            run.font.color.rgb = RGBColor(255, 0, 0)
            hata_var_mi = True

    # 4. Bölüm: Zorunlu Kurallar
    doc.add_heading('4. Zorunlu UCP 600 Parametreleri', level=2)
    for durum, metin in zorunlu_sonuclar:
        p = doc.add_paragraph()
        run = p.add_run(f"[{durum}] {metin}")
        if durum == "UYUMLU":
            run.font.color.rgb = RGBColor(0, 128, 0)
        else:
            run.font.color.rgb = RGBColor(255, 0, 0)
            hata_var_mi = True
            
    # 5. Bölüm: Operasyonel Kontroller
    doc.add_heading('5. UCP 600 Maddeleri ve SWIFT Kontrolleri', level=2)
    for durum, metin in kritik_sonuclar:
        p = doc.add_paragraph()
        run = p.add_run(f"[{durum}] {metin}")
        if durum == "TESPİT EDİLDİ":
            run.font.color.rgb = RGBColor(0, 51, 102)
        else:
            run.font.color.rgb = RGBColor(204, 102, 0)

    doc.add_paragraph("-" * 50)
    p_sonuc = doc.add_paragraph()
    if hata_var_mi:
        run_s = p_sonuc.add_run("🚨 DIKKAT: Evraklarda veya küşatta riskli uyumsuzluklar (rezerv) tespit edildi! Kontrol etmeden bankaya vermeyin.")
        run_s.font.bold = True
        run_s.font.color.rgb = RGBColor(255, 0, 0)
    else:
        run_s = p_sonuc.add_run("🎉 TEBRİKLER: Küşat kuralları tam, yüklenen evraklar akreditif şartlarıyla %100 uyumlu görünüyor.")
        run_s.font.bold = True
        run_s.font.color.rgb = RGBColor(0, 128, 0)
        
    doc.save("akreditif_analiz_raporu.docx")

def analiz_yurut():
    with open('kurallar.json', 'r', encoding='utf-8') as f:
        kurallar = json.load(f)
        
    with open("gelen_kusat.txt", 'r', encoding='utf-8') as f:
        kusat_metni = f.read()
        kusat_upper = kusat_metni.upper()
        
    fatura = dosya_oku_ve_sozluk_yap("fatura.txt")
    konsimento = dosya_oku_ve_sozluk_yap("konsimento.txt")
    
    tarih_notlari = []
    finans_notlari = []
    evrak_sonuclar = []
    zorunlu_sonuclar = []
    kritik_sonuclar = []
    hata_var_mi = False

    # 1. TARİH ANALİZİ
    yukleme_tarihi_match = re.search(r':44C:.*?(\b\d{6}\b)', kusat_upper)
    ibraz_suresi_match = re.search(r':48:.*?(\d+)\b', kusat_upper)
    if yukleme_tarihi_match:
        y_date = datetime.strptime(yukleme_tarihi_match.group(1), "%y%m%d")
        tarih_notlari.append(f"📅 En Geç Yükleme Tarihi (44C): {y_date.strftime('%d.%m.%Y')}")
        gun = int(ibraz_suresi_match.group(1)) if ibraz_suresi_match else 21
        son_ibraz = y_date + timedelta(days=gun)
        tarih_notlari.append(f"🚨 Bankaya Son Evrak İbraz Tarihi: {son_ibraz.strftime('%d.%m.%Y')}")
    else:
        tarih_notlari.append("⚠️ Küşatta resmi bir en geç yükleme tarihi (:44C:) saptanamadı.")

    # 2. FİNANSAL VADE HESAPLAYICI (Yeni Bölüm)
    # Küşat metninde ":42C: BY SIGHT" yerine vadeli bir ibare veya "90 DAYS" gibi yazılar arar
    vade_match = re.search(r'(\d+)\s*DAYS', kusat_upper)
    if vade_match and "YUKLEME_TARIHI" in konsimento:
        try:
            vade_gun = int(vade_match.group(1))
            bl_tarih = datetime.strptime(konsimento["YUKLEME_TARIHI"], "%d.%m.%Y")
            odeme_tarihi = bl_tarih + timedelta(days=vade_gun)
            
            finans_notlari.append(f"💰 Akreditif Tipi: Vadeli Ödeme (Deferred Payment)")
            finans_notlari.append(f"⏱️ Vade Süresi: Konşimento tarihinden itibaren {vade_gun} gün.")
            finans_notlari.append(f"🗓️ Tahmini Hak Ediş ve Ödeme Günü: {odeme_tarihi.strftime('%d.%m.%Y')}")
            if odeme_tarihi.weekday() >= 5: # Cumartesi=5, Pazar=6
                finans_notlari.append("⚠️ UYARI: Ödeme günü hafta sonuna denk geliyor! Banka ilk iş günü işlem yapabilir.")
        except Exception:
            pass

    # 3. ÇAPRAZ EVRAK KONTROLÜ (Yeni Bölüm)
    # Küşattaki mal tanımı ile fatura ve konşimentodaki mal tanımını karşılaştırır (UCP 600 Art 18)
    mal_match = re.search(r':46A:.*?COMMERCIAL INVOICE.*?\n(.*?)\n', kusat_upper)
    if mal_match and "MAL_TANIMI" in fatura:
        kusat_mal = basitleştir_metin(mal_match.group(1))
        fatura_mal = basitleştir_metin(fatura["MAL_TANIMI"])
        if fatura_mal in kusat_mal or kusat_mal in fatura_mal:
            evrak_sonuclar.append(("EVRAK UYUMLU", "Mal tanımı ticari fatura ile küşat arasında birebir uyuşuyor."))
        else:
            evrak_sonuclar.append(("REZERV RİSKİ", "Faturadaki mal tanımı küşattakiyle eşleşmiyor! (UCP 600 Madde 18 ihlali)."))
            hata_var_mi = True

    # Fatura tarihinin yükleme tarihinden önce olup olmadığını denetler
    if "TARİH" in fatura and "YUKLEME_TARIHI" in konsimento:
        try:
            f_date = datetime.strptime(fatura["TARİH"], "%d.%m.%Y")
            bl_date = datetime.strptime(konsimento["YUKLEME_TARIHI"], "%d.%m.%Y")
            if f_date <= bl_date:
                evrak_sonuclar.append(("EVRAK UYUMLU", f"Fatura tarihi ({fatura['TARİH']}), konşimento yükleme tarihinden ({konsimento['YUKLEME_TARIHI']}) önce/aynı gün. Kurallara uygun."))
            else:
                evrak_sonuclar.append(("REZERV RİSKİ", f"HATA: Fatura tarihi ({fatura['TARİH']}), yükleme tarihinden ({konsimento['YUKLEME_TARIHI']}) sonra olamaz! Banka reddeder."))
                hata_var_mi = True
        except Exception:
            pass

    # 4 & 5. UCP STANDART KONTROLLERİ
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
    exit(1 if hata_var_mi else 0)

if __name__ == "__main__":
    analiz_yurut()
