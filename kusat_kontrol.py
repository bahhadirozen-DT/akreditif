import json
import os
import re
from datetime import datetime, timedelta
from docx import Document

def basitleştir_metin(m):
    return re.sub(r'[^A-Z0-9]', '', m.upper()) if m else ""

def dosya_oku_ve_sozluk_yap(dosya_yolu):
    sonuc = {}
    if os.path.exists(dosya_yolu):
        with open(dosya_yolu, 'r', encoding='utf-8') as f:
            for satir in f:
                if ':' in satir:
                    a, d = satir.split(':', 1)
                    sonuc[a.strip().upper()] = d.strip()
    return sonuc

def markdown_raporu_olustur(t_not, z_sonuc, k_sonuc, e_sonuc, f_not, i_not, ucp_sonuc, h_var):
    with open("akreditif_analiz_raporu.md", "w", encoding="utf-8") as f:
        f.write("# 📋 AKREDİTİF GELİŞMİŞ DENETİM RAPORU\n\n")
        f.write(f"**Rapor Tarihi:** {datetime.now().strftime('%d.%m.%Y %H:%M')}\n---\n\n")
        
        f.write("## 1. Kritik Süreler ve Vade Analizi\n")
        for n in t_not: f.write(f"* {n}\n")
        
        f.write("\n## 2. Finansal Vade ve Ödeme Takvimi\n")
        if f_not:
            for n in f_not: f.write(f"* {n}\n")
        else:
            f.write("* ℹ Finansal takvim hesaplanamadı.\n")
            
        f.write("\n## 3. Incoterms ve Sigorta Denetimi\n")
        for d, m in i_not:
            e = "✅" if "UYUMLU" in d or "BİLGİ" in d else "🚨"
            f.write(f"* {e} **[{d}]** {m}\n")
            
        f.write("\n## 4. Çapraz Evrak Uyumluluk Kontrolü\n")
        for d, m in e_sonuc:
            e = "✅" if "UYUMLU" in d else "🚨"
            f.write(f"* {e} **[{d}]** {m}\n")
            
        f.write("\n## 5. Zorunlu UCP 600 Parametreleri\n")
        for d, m in z_sonuc:
            e = "✅" if d == "UYUMLU" else "❌"
            f.write(f"* {e} **[{d}]** {m}\n")
            
        f.write("\n## 6. UCP 600 Maddeleri ve SWIFT Kontrolleri\n")
        for d, m in k_sonuc:
            e = "🔍" if d == "TESPİT EDİLDİ" else "⚠"
            f.write(f"* {e} **[{d}]** {m}\n")

        f.write("\n## 7. UCP 600 (39 Madde) Resmi Kural Motoru Çıktıları\n")
        for d, m in ucp_sonuc:
            e = "✅" if "UYUMLU" in d or "BİLGİ" in d else "🚨"
            f.write(f"* {e} **[{d}]** {m}\n")
            
        f.write("\n---\n")
        if h_var: 
            f.write("### 🚨 SONUÇ: Rezerv riskleri tespit edildi! Kontrol etmeden bankaya vermeyin.\n")
        else: 
            f.write("### 🎉 SONUÇ: Tüm kontroller başarıyla tamamlandı. Altyapı tam uyumlu.\n")

def word_raporu_olustur(t_not, z_sonuc, k_sonuc, e_sonuc, f_not, i_not, ucp_sonuc, h_var):
    doc = Document()
    doc.add_heading('GELİŞMİŞ DIŞ TİCARET DENETİM RAPORU', level=1)
    doc.add_paragraph(f"Rapor Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
    
    doc.add_heading('1. Kritik Süreler ve Vade Analizi', level=2)
    for n in t_not: doc.add_paragraph(str(n))
    
    doc.add_heading('2. Finansal Vade ve Ödeme Takvimi', level=2)
    if f_not:
        for n in f_not: doc.add_paragraph(str(n))
    else:
        doc.add_paragraph("Finansal takvim hesaplanamadı.")
        
    doc.add_heading('3. Incoterms ve Sigorta Denetimi', level=2)
    for d, m in i_not: doc.add_paragraph(f"[{str(d)}] {str(m)}")
    
    doc.add_heading('4. Çapraz Evrak Uyumluluk Kontrolü', level=2)
    for d, m in e_sonuc: doc.add_paragraph(f"[{str(d)}] {str(m)}")
    
    doc.add_heading('5. Zorunlu UCP 600 Parametreleri', level=2)
    for d, m in z_sonuc: doc.add_paragraph(f"[{str(d)}] {str(m)}")
    
    doc.add_heading('6. UCP 600 Maddeleri ve SWIFT Kontrolleri', level=2)
    for d, m in k_sonuc: doc.add_paragraph(f"[{str(d)}] {str(m)}")

    doc.add_heading('7. UCP 600 (39 Madde) Resmi Kural Motoru Çıktıları', level=2)
    for d, m in ucp_sonuc: doc.add_paragraph(f"[{str(d)}] {str(m)}")
    
    doc.add_paragraph("\n" + "="*40)
    if h_var: 
        doc.add_paragraph("SONUÇ: Rezerv riskleri tespit edildi!")
    else: 
        doc.add_paragraph("SONUÇ: Altyapı tam uyumlu.")
    doc.save("akreditif_analiz_raporu.docx")

def analiz_yurut():
    with open('kurRules.json' if os.path.exists('kurRules.json') else 'kurallar.json', 'r', encoding='utf-8') as f: 
        kurallar = json.load(f)
    with open("gelen_kusat.txt", 'r', encoding='utf-8') as f: 
        kusat_upper = f.read().upper()
        
    fatura = dosya_oku_ve_sozluk_yap("fatura.txt")
    konsimento = dosya_oku_ve_sozluk_yap("konsimento.txt")
    sigorta = dosya_oku_ve_sozluk_yap("sigorta.txt")
    
    t_not, f_not, e_sonuc, z_sonuc, k_sonuc, i_not, ucp_sonuc = [], [], [], [], [], [], []
    h_var = False

    # 1. TARİH VE VADE SÜRE ANALİZLERİ
    y_match = re.search(r':44C:.*?(\b\d{6}\b)', kusat_upper)
    i_match = re.search(r':48:.*?(\d+)\b', kusat_upper)
    v_match = re.search(r'(\d+)\s*DAYS', kusat_upper)
    
    bl_tarih_nesnesi = None
    if "YUKLEME_TARIHI" in konsimento:
        try:
            bl_tarih_nesnesi = datetime.strptime(konsimento["YUKLEME_TARIHI"].strip(), "%d.%m.%Y")
        except Exception: 
            pass

    if y_match:
        y_date = datetime.strptime(y_match.group(1), "%y%m%d")
        t_not.append(f"En Geç Yükleme Tarihi (44C): {y_date.strftime('%d.%m.%Y')}")
        gun = int(i_match.group(1)) if i_match else 21
        son_ibraz = y_date + timedelta(days=gun)
        t_not.append(f"Bankaya Son Evrak İbraz Tarihi: {son_ibraz.strftime('%d.%m.%Y')}")
        
        # UCP 600 Madde 14(c) Sunum Süresi Çapraz Kontrolü
        if bl_tarih_nesnesi:
            ibraz_farki = (datetime.now() - bl_tarih_nesnesi).days 
            if ibraz_farki > gun:
                ucp_sonuc.append(("REZERV RİSKİ", f"Madde 14(c): Evrak sunum süresi yüklemeden sonra {ibraz_farki} gün olmuş. {gun} günlük yasal limit aşılmış!"))
                h_var = True
            else:
                ucp_sonuc.append(("UYUMLU", f"Madde 14(c): Sunum süresi yasal limit ({gun} gün) dahilinde."))

    if v_match and bl_tarih_nesnesi:
        try:
            v_gun = int(v_match.group(1))
            o_t = bl_tarih_nesnesi + timedelta(days=v_gun)
            f_not.append(f"Vade: Konşimentodan {v_gun} gün sonra.")
            f_not.append(f"Tahmini Ödeme Günü: {o_t.strftime('%d.%m.%Y')}")
        except Exception: 
            pass

    # 2. INCOTERMS & UCP 600 MADDE 28 SİGORTA DENETİMİ
    incoterms = ["EXW", "FCA", "FAS", "FOB", "CFR", "CIF", "CPT", "CIP", "DAP", "DDP"]
    b_in = next((i for i in incoterms if i in kusat_upper), None)
    if b_in:
        i_not.append(("BILGI", f"Saptanan teslim sekli: {b_in}"))
        if b_in in ["CIF", "CIP"]:
            if "INSURANCE" in kusat_upper or "110%" in kusat_upper:
                i_not.append(("UYUMLU", "Sigorta sartlari eksiksiz saptandi."))
                
                # UCP 600 Madde 28(f)(ii) %110 Teminat Kontrolü
                if "TUTAR" in fatura and "SIGORTA_TUTARI" in sigorta:
                    try:
                        f_tutar = float(fatura["TUTAR"].replace(",", ".").strip())
                        s_tutar = float(sigorta["SIGORTA_TUTARI"].replace(",", ".").strip())
                        if s_tutar < (f_tutar * 1.10):
                            ucp_sonuc.append(("REZERV RİSKİ", f"Madde 28(f)(ii): Sigorta tutarı ({s_tutar}), fatura CIF değerinin %110'undan ({(f_tutar*1.10)}) az!"))
                            h_var = True
                        else:
                            ucp_sonuc.append(("UYUMLU", "Madde 28(f)(ii): Sigorta kapsamı %110 şartını sağlıyor."))
                    except Exception: 
                        pass
            else:
                i_not.append(("REZERV RISKI", "Sigorta policesi sartı eksik!"))
                h_var = True

    # 3. UCP 600 MADDE 18 - FATURA VE MAL TANIMI ÇAPRAZ KONTROLLERİ
    m_match = re.search(r':46A:.*?COMMERCIAL INVOICE.*?\n(.*?)\n', kusat_upper)
    if m_match and "MAL_TANIMI" in fatura:
        k_mal, f_mal = basitleştir_metin(m_match.group(1)), basitleştir_metin(fatura["MAL_TANIMI"])
        if f_mal in k_mal or k_mal in f_mal:
            e_sonuc.append(("UYUMLU", "Mal tanimi fatura ile uyusuyor."))
            ucp_sonuc.append(("UYUMLU", "Madde 18(c): Ticari faturadaki mal tanımı akreditifle tam olarak uyuşuyor."))
        else:
            e_sonuc.append(("REZERV RISKI", "Faturadaki mal tanimi kusatla uyusmuyor!"))
            ucp_sonuc.append(("REZERV RİSKİ", "Madde 18(c): Faturadaki mal tanımı akreditifle kelimesi kelimesine (exactly) uyuşmuyor!"))
            h_var = True

    if "TARİH" in fatura and bl_tarih_nesnesi:
        try:
            f_d = datetime.strptime(fatura["TARİH"].strip(), "%d.%m.%Y")
            if f_d <= bl_tarih_nesnesi:
                e_sonuc.append(("UYUMLU", "Fatura tarihi gumruk yuklemesinden once."))
            else:
                e_sonuc.append(("REZERV RISKI", "Fatura tarihi yuklemeden sonra olamaz!"))
                h_var = True
        except Exception: 
            pass

    # UCP 600 Madde 28(e) Sigorta Tarihi Kontrolü
    if "TARİH" in sigorta and bl_tarih_nesnesi:
        try:
            s_d = datetime.strptime(sigorta["TARİH"].strip(), "%d.%m.%Y")
            if s_d > bl_tarih_nesnesi:
                ucp_sonuc.append(("REZERV RİSKİ", "Madde 28(e): Sigorta poliçesi tarihi yükleme tarihinden sonra olamaz!"))
                h_var = True
            else:
                ucp_sonuc.append(("UYUMLU", "Madde 28(e): Sigorta poliçesi yükleme günü veya öncesinde düzenlenmiş."))
        except Exception: 
            pass

    # 4. UCP 600 MADDE 30 - QUANTITY/AMOUNT TOLERANCE KONTROLÜ
    if "TUTAR" in fatura:
        try:
            f_tutar = float(fatura["TUTAR"].replace(",", ".").strip())
            akreditif_tutari_match = re.search(r':32B:[A-Z]{3}\s*([\d,.]+)', kusat_upper)
            if akreditif_tutari_match:
                a_tutar = float(akreditif_tutari_match.group(1).replace(",", ".").strip())
                tolerans_var = "ABOUT" in kusat_upper or "CIRCA" in kusat_upper
                limit = 0.10 if tolerans_var else 0.00
                
                ust_limit = a_tutar * (1 + limit)
                alt_limit = a_tutar * (1 - limit)
                
                if f_tutar > ust_limit or f_tutar < alt_limit:
                    ucp_sonuc.append(("REZERV RİSKİ", f"Madde 30(a): Fatura tutarı ({f_tutar}) tolerans sınırları ({alt_limit} - {ust_limit}) dışında!"))
                    h_var = True
                else:
                    ucp_sonuc.append(("UYUMLU", "Madde 30(a): Fatura tutarı kabul edilebilir tolerans limitleri içinde."))
        except Exception:
            pass

    # 5 & 6. ESKİ JSON TABANLI UCP KONTROLLERİ
    for k in kurallar['zorunlu_kurallar']:
        if k['anahtar'].upper() in kusat_upper:
            z_sonuc.append(("UYUMLU", f"'{k['anahtar']}' dogrulandi."))
        else:
            z_sonuc.append(("RISK", f"'{k['anahtar']}' BULUNAMADI!"))
            h_var = True

    for k in kurallar['kritik_kontroller']:
        if k['anahtar'].upper() in kusat_upper:
            k_sonuc.append(("TESPIT EDILDI", f"[{k['madde']}] {k['anahtar']} saptandi."))
        else:
            k_sonuc.append(("KONTROL ET", f"[{k['madde']}] {k['anahtar']} dogrudan gecmiyor."))

    # RAPORLARI DOSYALARA YAZ
    word_raporu_olustur(t_not, z_sonuc, k_sonuc, e_sonuc, f_not, i_not, ucp_sonuc, h_var)
    markdown_raporu_olustur(t_not, z_sonuc, k_sonuc, e_sonuc, f_not, i_not, ucp_sonuc, h_var)
    exit(0)

if __name__ == "__main__":
    analiz_yurut()
