import re
from datetime import datetime

def normalize_text(text):
    """
    Çapraz evrak kontrolünde mal tanımlarını ve unvanları normalize eder.
    Ölçü ve oran bildiren %, /, . gibi kritik karakterleri korur.
    """
    if not text:
        return ""
    tablo = str.maketrans("ÇĞİÖŞÜ", "CGIOSU")
    text = text.upper().translate(tablo)
    cleaned = re.sub(r'[^A-Z0-9\s%/\.]', '', text)
    return " ".join(cleaned.strip().split())

class UCP600KuralMotoru:
    def __init__(self, akreditif_verisi, sunulan_evraklar, kurallar_sozlugu=None):
        """
        UCP 600 Çapraz Kontrol ve Rezerv Motoru
        :param akreditif_verisi: MT700 Swift verilerini içeren dictionary
        :param sunulan_evraklar: Fatura, Konşimento, Sigorta vb. verilerini içeren dictionary
        :param kurallar_sozlugu: kurallar.json dosyasından okunan ISBP sözlüğü
        """
        self.lc = akreditif_verisi
        self.docs = sunulan_evraklar
        self.kurallar = kurallar_sozlugu if kurallar_sozlugu else {}
        self.rezervler = []
        self.isbp_sozlugu = self._isbp_haritasi_olustur()

    def _isbp_haritasi_olustur(self):
        """ISBP kurallarındaki kısaltmaları hızlı arama için düz bir sözlüğe dönüştürür."""
        harita = {}
        if "isbp_kurallari" in self.kurallar:
            for kural in self.kurallar["isbp_kurallari"]:
                orj = normalize_text(kural["orijinal"])
                for karsilik in kural["karsiliklar"]:
                    harita[normalize_text(karsilik)] = orj
        return harita

    def metin_isbp_normalize(self, metin):
        """Metin içindeki kısaltmaları (Ltd, Co vb.) resmi uzun hallerine dönüştürür."""
        normalize_metin = normalize_text(metin)
        kelimeler = normalize_metin.split()
        donusturulmus = [self.isbp_sozlugu.get(kelime, kelime) for kelime in kelimeler]
        return " ".join(donusturulmus)

    def denetle_tum_kurallar(self):
        """UCP 600 dökümanındaki maddeleri sırasıyla tetikler"""
        self._madde_4_ve_5_belge_odaklilik()
        self._madde_14b_inceleme_suresi()
        self._madde_14c_sunum_suresi()
        self._madde_14f_belge_duzenleyicisi()
        self._madde_18_ticari_fatura()
        self._madde_20_konsimento_tasima_belgesi()
        self._madde_28_sigorta_belgesi()
        self._madde_30_miktar_tutar_toleranslari()
        return self.rezervler

    # --- ARTICLES 1 - 5: GENEL HÜKÜMLER ---
    def _madde_4_ve_5_belge_odaklilik(self):
        """Madde 4 ve 5: Bankalar belgelerle ilgilenir."""
        if not self.docs:
            self.rezervler.append({
                "madde": "UCP 600 Madde 5",
                "seviye": "KRITIK_REZERV",
                "mesaj": "İnceleme için hiçbir evrak verisi sunulmadı. Bankalar sadece sunulan belgeler üzerinden işlem yapar."
            })

    # --- ARTICLES 14 - 16: İNCELEME STANDARTLARI ---
    def _madde_14b_inceleme_suresi(self):
        """Madde 14(b): Bankanın belgeleri incelemek için maksimum 5 iş günü vardır."""
        pass

    def _madde_14c_sunum_suresi(self):
        """Madde 14(c): Yükleme tarihinden itibaren en geç 21 gün içinde sunum yapılmalıdır."""
        bl_date_str = self.docs.get('bl', {}).get('loading_date')
        pres_date_str = self.docs.get('presentation_date')
        expiry_date_str = self.lc.get('expiry_date')

        if bl_date_str and pres_date_str:
            bl_date = datetime.strptime(bl_date_str, "%Y-%m-%d")
            pres_date = datetime.strptime(pres_date_str, "%Y-%m-%d")
            
            fark = (pres_date - bl_date).days
            if fark > 21:
                self.rezervler.append({
                    "madde": "UCP 600 Madde 14(c)",
                    "seviye": "KRITIK_REZERV",
                    "mesaj": f"Belgeler yükleme tarihinden {fark} gün sonra sunulmuş. 21 günlük yasal süre aşılmıştır!"
                })
            
            if expiry_date_str:
                exp_date = datetime.strptime(expiry_date_str, "%Y-%m-%d")
                if pres_date > exp_date:
                    self.rezervler.append({
                        "madde": "UCP 600 Madde 14(c)",
                        "seviye": "KRITIK_REZERV",
                        "mesaj": f"Sunum tarihi ({pres_date_str}), Akreditif vade tarihinden ({expiry_date_str}) sonradır!"
                    })

    def _madde_14f_belge_duzenleyicisi(self):
        """Madde 14(f): Belge düzenleyici kuralları."""
        pass

    # --- ARTICLES 18 - 28: EVRAK KURALLARI ---
    def _madde_18_ticari_fatura(self):
        """Madde 18: Ticari Fatura Şartları (ISBP Kısaltma ve Unvan desteğiyle geliştirildi)"""
        invoice = self.docs.get('invoice', {})
        
        # 18(a)(i): Lehtar adı kontrolü (ISBP Korumalı)
        if invoice.get('issuer') and self.lc.get('beneficiary'):
            inv_issuer_isbp = self.metin_isbp_normalize(invoice.get('issuer'))
            lc_benef_isbp = self.metin_isbp_normalize(self.lc.get('beneficiary'))
            if inv_issuer_isbp != lc_benef_isbp:
                self.rezervler.append({
                    "madde": "UCP 600 Madde 18(a)(i)",
                    "seviye": "UYARI",
                    "mesaj": "Fatura ihraççısı ile Akreditif Lehtarı (Beneficiary) unvanı uyuşmuyor."
                })

        # 18(a)(ii): Amir adı kontrolü (ISBP Korumalı)
        if invoice.get('applicant') and self.lc.get('applicant'):
            inv_app_isbp = self.metin_isbp_normalize(invoice.get('applicant'))
            lc_app_isbp = self.metin_isbp_normalize(self.lc.get('applicant'))
            if inv_app_isbp != lc_app_isbp:
                self.rezervler.append({
                    "madde": "UCP 600 Madde 18(a)(ii)",
                    "seviye": "KRITIK_REZERV",
                    "mesaj": f"Fatura, Akreditif Amiri ({self.lc.get('applicant')}) adına düzenlenmemiş!"
                })

        # 18(a)(iii): Para birimi uyumu
        if invoice.get('currency') and self.lc.get('currency'):
            if invoice.get('currency') != self.lc.get('currency'):
                self.rezervler.append({
                    "madde": "UCP 600 Madde 18(a)(iii)",
                    "seviye": "KRITIK_REZERV",
                    "mesaj": f"Fatura para birimi ({invoice.get('currency')}), Akreditif para birimi ({self.lc.get('currency')}) ile uyuşmuyor!"
                })

        # 18(c): Mal Tanımı Kontrolü (ISBP Korumalı)
        if "goods_description" in invoice and "goods_description" in self.lc:
            inv_goods_isbp = self.metin_isbp_normalize(invoice.get('goods_description'))
            lc_goods_isbp = self.metin_isbp_normalize(self.lc.get('goods_description'))
            
            if lc_goods_isbp not in inv_goods_isbp and inv_goods_isbp not in lc_goods_isbp:
                self.rezervler.append({
                    "madde": "UCP 600 Madde 18(c)",
                    "seviye": "KRITIK_REZERV",
                    "mesaj": "Faturadaki mal tanımı, akreditifteki mal tanımı ile uyuşmuyor!"
                })

    def _madde_20_konsimento_tasima_belgesi(self):
        """Madde 20: Konşimento (Bill of Lading) Kuralları"""
        bl = self.docs.get('bl', {})
        if not bl.get('is_signed') or not bl.get('carrier_identified'):
            self.rezervler.append({
                "madde": "UCP 600 Madde 20(a)(i)",
                "seviye": "KRITIK_REZERV",
                "mesaj": "Konşimento üzerinde Taşıyan (Carrier) kimliği veya geçerli imza/kaşe tespiti yapılamadı!"
            })

        if not bl.get('shipped_on_board', False):
            self.rezervler.append({
                "madde": "UCP 600 Madde 20(a)(ii)",
                "seviye": "KRITIK_REZERV",
                "mesaj": "Konşimentoda 'Shipped on board' ibaresi veya yükleme kaydı bulunmuyor!"
            })

    def _madde_28_sigorta_belgesi(self):
        """Madde 28: Sigorta Belgesi ve Kapsamı"""
        insurance = self.docs.get('insurance', {})
        bl_date_str = self.docs.get('bl', {}).get('loading_date')
        
        if insurance.get('date') and bl_date_str:
            ins_date = datetime.strptime(insurance.get('date'), "%Y-%m-%d")
            bl_date = datetime.strptime(bl_date_str, "%Y-%m-%d")
            if ins_date > bl_date:
                self.rezervler.append({
                    "madde": "UCP 600 Madde 28(e)",
                    "seviye": "KRITIK_REZERV",
                    "mesaj": f"Sigorta poliçesi tarihi ({insurance.get('date')}), yükleme tarihinden ({bl_date_str}) sonradır!"
                })

        incoterm = self.lc.get('incoterm', '').upper()
        if 'CIF' in incoterm or 'CIP' in incoterm:
            invoice_amount = self.docs.get('invoice', {}).get('amount', 0)
            insurance_coverage = insurance.get('coverage_amount', 0)
            gerekli_kapsam = invoice_amount * 1.10
            if insurance_coverage < gerekli_kapsam:
                self.rezervler.append({
                    "madde": "UCP 600 Madde 28(f)(ii)",
                    "seviye": "KRITIK_REZERV",
                    "mesaj": f"Sigorta kapsamı ({insurance_coverage}), fatura tutarının %110'undan ({gerekli_kapsam}) düşüktür!"
                })

    # --- ARTICLES 30 - 32: TOLERANSLAR ---
    def _madde_30_miktar_tutar_toleranslari(self):
        """Madde 30: Akreditif Tutarı, Miktar ve Birim Fiyatta Toleranslar"""
        lc_amount = self.lc.get('amount', 0)
        invoice_amount = self.docs.get('invoice', {}).get('amount', 0)
        lc_desc = self.lc.get('goods_description', '').lower()

        tolerans_kelimesi = 'about' in lc_desc or 'circa' in lc_desc
        limit = 0.10 if tolerans_kelimesi else 0.00

        ust_limit = lc_amount * (1 + limit)
        alt_limit = lc_amount * (1 - limit)

        if invoice_amount > ust_limit or invoice_amount < alt_limit:
            msg_tipi = "%10 tolerans dahilinde" if tolerans_kelimesi else "toleranssız (%0)"
            self.rezervler.append({
                "madde": "UCP 600 Madde 30(a)",
                "seviye": "UYARI",
                "mesaj": f"Fatura tutarı ({invoice_amount}), Akreditif sınırlarının dışında. Tanım: {msg_tipi} ({alt_limit} - {ust_limit})"
            })
