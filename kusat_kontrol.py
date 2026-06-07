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

def markdown_raporu_olustur(t_not, z_sonuc, k_sonuc, e_sonuc, f_not, i_not, h_var):
    with open("akreditif_analiz_raporu.md", "w", encoding="utf-8") as f:
        f.write("# 📋 AKREDİTİF GELİŞMİŞ DENETİM RAPORU\n\n")
        f.write(f"**Rapor Tarihi:** {datetime.now().strftime('%d.%m.%Y %H:%M')}\n---\n\n")
        
        f.write("## 1. Kritik Süreler ve Vade Analizi\n")
        for n in t_not: f.write(f"* {n}\n")
        
        f.write("\n## 2. Finansal Vade ve Ödeme Takvimi\n")
        if f_not:
            for n in f_not: f.write(f"* {n}\n")
        else: f.write("* ℹ️ Finansal takvim hesaplanamadı.\n")
            
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
            e = "🔍" if d == "TESPİT EDİLDİ" else "⚠️"
            f.write(f"* {e} **[{d}]** {m}\n")
            
        f.write("\n---\n")
        if h_var: f.write("### 🚨 SONUÇ: Rezerv riskleri tespit edildi! Kontrol etmeden bankaya vermeyin.\n")
        else: f.write("### 🎉 SONUÇ: Tüm kontroller başarıyla tamamlandı. Altyapı tam uyumlu.\n")

def word_raporu_olustur(t_not, z_sonuc, k_sonuc, e_sonuc, f_not, i_not, h_var):
    doc = Document()
    doc.add_heading('GELİŞMİŞ DIŞ TİCARET DENETİM RAPORU', level=1)
    doc.add_paragraph(f"Rapor Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    doc.add_paragraph("=" * 50)
    
    doc.add_heading('1. Kritik Süreler ve Vade Analizi', level=2)
    for n in t_not: doc.add_paragraph(n)
        
    doc.add_heading('2. Finansal Vade ve Ödeme Takvimi', level=2)
    if f_not:
        for n in f_not: doc.add_paragraph(n)
    else: doc.add_paragraph("ℹ️ Finansal takvim hesaplanamadı.")

    doc.add_heading('3. Incoterms ve Sigorta Denetimi', level=2)
    for d, m in i_not: doc.add_paragraph(f"[{d}] {m}")

    doc.add_heading('4. Çapraz Evrak Uyumluluk Kontrolü', level=2)
    for d, m in e_sonuc: doc.add_paragraph(f"[{d}] {m}")

    doc.add_heading('5. Zorunlu UCP 600 Parametreleri', level=2)
    for d, m in z_sonuc: doc.add_paragraph(f"[{d}] {m}")
            
    doc.add_heading('6. UCP 600 Maddeleri ve SWIFT Kontrolleri', level=2)
    for d, m in k_sonuc: doc.add_paragraph(f"[{d}] {m}")

    doc.add_paragraph("=" * 50)
    if h_var: doc.add_paragraph("🚨 SONUÇ: Rezerv riskleri tespit edildi!")
    else: doc.add_paragraph("🎉 SONUÇ: Altyapı tam uyumlu.")

    doc.save("akreditif_analiz_raporu.docx")

def analiz_yurut():
    with open('kurallar.json', 'r', encoding='utf-8') as f: kurallar = json.load(f)
    with open("gelen_kusat.txt", 'r', encoding='utf-8') as f: kusat_upper = f.read().upper()
    fatura = dosya_oku_ve_sozluk_yap("fatura.txt")
    konsimento = dosya_oku_ve_sozluk_yap("konsimento.txt")
    
    t_not, f_not, e_sonuc, z_sonuc, k_sonuc, i_not = [], [], [], [], [], []
    h_var = False

    # 1. TARİH
    y_match = re.search(r':44C:.*?(\b\d{6}\b)', kusat_upper)
    i_match = re.search(r':48:.*?(\d+)\b', kusat_upper)
    if y_match:
        y_date = datetime.strptime(y_match.group(1), "%y%m%d")
        t_not.append(f"En Geç Yükleme Tarihi (44C): {y_date.strftime('%d.%m.%Y')}")
        gun = int(i_match.group(1)) if i_match else 21
        son_ibraz = y_date + timedelta(days=gun)
        t_not.append(f"Bankaya Son Evrak İbraz Tarihi: {son_ibraz.strftime('%d.%m.%Y')}")

    # 2. VADE
    v_match = re.search(r'(\d+)\s*DAYS', kusat_upper)
    if v_match and "YUKLEME_TARIHI" in konsimento:
        try:
            v_gun = int(v_match.group(1))
            bl_t = datetime.strptime(konsimento["YUKLEME_TARIHI"].strip(), "%d.%m.%Y")
            o_t = bl_t + timedelta(days=v_gun)
            f_not.append(f"Vade: Konşimentodan {v_gun} gün sonra.")
            f_not.append(f"Tahmini Ödeme Günü: {o_t.strftime('%d.%m.%Y')}")
        except Exception: pass

    # 3. INCOTERMS
    incoterms = ["EXW", "FCA", "FAS", "FOB", "CFR", "CIF", "CPT", "CIP", "DAP", "DDP"]
    b_in = next((i for i in incoterms if i in kusat_upper), None)
    if b_in:
        i_not.append(("BİLGİ", f"Saptanan teslim şekli: {b_in}"))
        if b_in in ["CIF", "CIP"]:
            if "INSURANCE" in kusat_upper or "110%" in kusat_upper:
                i_not.append(("UYUMLU", "Sigorta şartları eksiksiz saptandı."))
            else:
                i_not.append(("REZERV RİSKİ", "Sigorta poliçesi şartı eksik!"))
                h_var = True

    # 4. EVRAK KONTROL
    m_match = re.search(r':46A:.*?COMMERCIAL INVOICE.*?\n(.*?)\n', kusat_upper)
    if m_match and "MAL_TANIMI" in fatura:
        k_mal, f_mal = basitleştir_metin(m_match.group(1)), basitleştir_metin(fatura["MAL_TANIMI"])
        if f_mal in k_mal or k_mal in f_mal:
            e_sonuc.append(("UYUMLU", "Mal tanımı fatura ile uyuşuyor."))
        else:
            e_sonuc.append(("REZERV RİSKİ", "Faturadaki mal tanımı küşatla uyuşmuyor!"))
            h_var = True

    if "TARİH" in fatura and "YUKLEME_TARIHI" in konsimento:
        try:
            f_d = datetime.strptime(fatura["TARİH"].strip(), "%d.%m.%Y")
            bl_d = datetime.strptime(konsimento["YUKLEME_TARIHI"].strip(), "%d.%m.%Y")
            if f_d <= bl_d: e_sonuc.append(("UYUMLU", "Fatura tarihi gümrük yüklemesinden önce."))
            else:
                e_sonuc.append(("REZERV RİSKİ", "Fatura tarihi yüklemeden sonra olamaz!"))
                h_var = True
        except Exception: pass

    # 5 & 6. UCP
    for k in kurallar['zorunlu_kurallar']:
        if k['anahtar'].upper() in kusat_upper: z_sonuc.append(("UYUMLU", f"'{k['anahtar']}' doğrulandı."))
        else:
            z_sonuc.append(("RİSK", f"'{k['anahtar']}' BULUNAMADI!"))
            h_var = True
            
    for k in kurallar['kritik_kontroller']:
        if k['anahtar'].upper() in kusat_upper:
            k_sonuc.append(("TESPİT EDİLDİ", f"[{k['madde']}] {k['anahtar']} saptandı."))
        else:
            k_sonuc.append(("KONTROL ET", f"[{k['madde']}] {k['anahtar']} doğrudan geçmiyor."))

    word_raporu_olustur(t_not, z_sonuc, k_sonuc, e_sonuc, f_not, i_not, h_var)
    markdown_raporu_olustur(t_not, z_sonuc, k_sonuc, e_sonuc, f_not, i_not, h_var)
    exit(0)

if __name__ == "__main__":
    analiz_yurut()
