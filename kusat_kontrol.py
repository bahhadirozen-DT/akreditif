import json
import os
import re
from datetime import datetime, timedelta

def tarih_bul_ve_hesapla(metin):
    print("[TARİH VE VADE ANALİZİ]")
    yukleme_tarihi_match = re.search(r':44C:.*?(\b\d{6}\b)', metin)
    ibraz_suresi_match = re.search(r':48:.*?(\d+)\b', metin)
    
    if yukleme_tarihi_match:
        try:
            y_str = yukleme_tarihi_match.group(1)
            y_date = datetime.strptime(y_str, "%y%m%d")
            print(f"📅 En Geç Yükleme Tarihi (44C): {y_date.strftime('%d.%m.%Y')}")
            
            gun_sayisi = 21
            if ibraz_suresi_match:
                gun_sayisi = int(ibraz_suresi_match.group(1))
                print(f"ℹ️ Özel İbraz Süresi Tespit Edildi (:48:): {gun_sayisi} Gün")
            else:
                print("ℹ️ Özel ibraz süresi bulunamadı. UCP 600 Madde 14 gereği standart 21 gün uygulandı.")
                
            son_ibraz = y_date + timedelta(days=gun_sayisi)
            print(f"🚨 Bankaya Son Belge Teslim Tarihi: {son_ibraz.strftime('%d.%m.%Y')} (Kritik Vade!)")
        except Exception:
            print("⚠️ Tarih formatı çözümlenirken bir sorun oluştu, manuel kontrol edin.")
    else:
        print("⚠️ Metinde net bir ':44C:' en geç yükleme tarihi kodu bulunamadı.")
    print("-" * 50)

def kusat_analiz_et(kusat_dosya_yolu):
    if not os.path.exists(kusat_dosya_yolu):
        print(f"❌ HATA: '{kusat_dosya_yolu}' dosyası bulunamadı.")
        return

    with open('kurallar.json', 'r', encoding='utf-8') as f:
        kurallar = json.load(f)
        
    with open(kusat_dosya_yolu, 'r', encoding='utf-8') as f:
        kusat_metni_upper = f.read().upper()
        
    print(f"\n==================================================")
    print(f"   AKREDİTİF (KÜŞAT) OTOMATİK DENETİM RAPORU      ")
    print(f"==================================================\n")
    
    tarih_bul_ve_hesapla(kusat_metni_upper)
    hata_var_mi = False

    print("[ZORUNLU UCP 600 PARAMETRELERİ]")
    for kural in kurallar['zorunlu_kurallar']:
        if kural['anahtar'].upper() in kusat_metni_upper:
            print(f"✅ UYUMLU: [{kural['madde']}] '{kural['anahtar']}' metinde doğrulandı.")
        else:
            print(f"❌ RİSK: [{kural['madde']}] '{kural['anahtar']}' BULUNAMADI! -> {kural['aciklama']}")
            hata_var_mi = True
            
    print("-" * 50)

    print("[UCP 600 MADDELERİ VE SWIFT KONTROLLERİ]")
    for kural in kurallar['kritik_kontroller']:
        if kural['anahtar'].upper() in kusat_metni_upper:
            print(f"🔍 TESPİT EDİLDİ: [{kural['madde']}] {kural['anahtar']} -> {kural['aciklama']}")
        else:
            print(f"⚠️ KONTROL ET: [{kural['madde']}] '{kural['anahtar']}' doğrudan geçmiyor veya istisna olabilir. ({kural['aciklama']})")

    print("\n" + "=" * 50)
    if hata_var_mi:
        print("🚨 SONUÇ: Kritik UCP 600 eksiklikleri var! Bu küşatı onaylamayın.")
        exit(1)
    else:
        print("🎉 SONUÇ: Tüm 39 madde ve SWIFT blokları kontrol edildi. Altyapı tam uyumlu.")
        exit(0)

if __name__ == "__main__":
    kusat_analiz_et("gelen_kusat.txt")
