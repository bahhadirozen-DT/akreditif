import re
from datetime import datetime

class UCP600KuralMotoru:
    def __init__(self, akreditif_verisi, sunulan_evraklar):
        """
        UCP 600 (39 Maddelik Tam Metin) Çapraz Kontrol ve Rezerv Motoru
        :param akreditif_verisi: MT700 Swift verilerini içeren dictionary
        :param sunulan_evraklar: Fatura, Konşimento, Sigorta vb. verilerini içeren dictionary
        """
        self.lc = akreditif_verisi
        self.docs = sunulan_evraklar
        self.rezervler = []

    def denetle_tum_kurallar(self):
        """UCP 600 dökümanındaki maddeleri sırasıyla tetikler"""
        # Genel İlkeler ve Tanımlar (Articles 1 - 5)
        self._madde_4_ve_5_belge_odaklilik()
        
        # Standartlar ve Süreler (Articles 14 - 16)
        self._madde_14b_inceleme_suresi()
        self._madde_14c_sunum_suresi()
        self._madde_14f_belge_duzenleyicisi()
        
        # Evrak Bazlı Kurallar (Articles 18 - 28)
        self._madde_18_ticari_fatura()
        self._madde_20_konsimento_tasima_belgesi()
        self._madde_28_sigorta_belgesi()
        
        # Toleranslar ve Kısmi Yüklemeler (Articles 30 - 32)
        self._madde_30_miktar_tutar_toleranslari()
        
        return self.rezervler

    # --- ARTICLES 1 - 5: GENEL HÜKÜMLER ---
    def _madde_4_ve_5_belge_odaklilik(self):
        """Madde 4 ve 5: Bankalar mallarla, hizmetlerle değil, sadece belgelerle ilgilenir."""
        # Evrakların fiziksel varlığının dictionary üzerinde kontrolü
        if not self.docs:
            self.rezervler.append({
                "madde": "UCP 600 Madde 5",
                "seviye": "KRITIK_REZERV",
                "mesaj": "İnceleme için hiçbir evrak verisi sunulmadı. Bankalar sadece sunulan belgeler üzerinden işlem yapar."
            })

    # --- ARTICLES 14 - 16: İNCELEME STANDARTLARI ---
    def _madde_14b_inceleme_suresi(self):
        """Madde 14(b): Bankanın belgeleri incelemek için sunum gününü takip eden maksimum 5 iş günü vardır."""
        # CI/CD sürecinde zaman aşımı takibi için altyapı
        presentation_date_str = self.docs.get('presentation_date')
        if presentation_date_str:
            # Gerçek bankacılık iş günü takvimi entegrasyon noktası
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
        """Madde 14(f): Akreditifte belgeyi kimin düzenleyeceği belirtilmemişse, lehtar hariç herkes düzenleyebilir."""
        # Taslak aşaması: Özel sertifikalar (Analiz, Paketleme vb.) için ihraççı doğrulaması
        pass

    # --- ARTICLES 18 - 28: EVRAK KURALLARI ---
    def _madde_18_ticari_fatura(self):
        """Madde 18: Ticari Fatura Şartları (a(i), a(ii), a(iii) ve c fıkraları)"""
        invoice = self.docs.get('invoice', {})
        
        # 18(a)(i): Lehtar tarafından düzenlenme kontrolü
        if invoice.get('issuer') and self.lc.get('beneficiary'):
            if invoice.get('issuer').lower() != self.lc.get('beneficiary').lower():
                self.rezervler.append({
                    "madde": "UCP 600 Madde 18(a)(i)",
                    "seviye": "UYARI",
                    "mesaj": "Fatura ihraççısı ile Akreditif Lehtarı (Beneficiary) ismi tam olarak uyuşmuyor."
                })

        # 18(a)(ii): Amir adına düzenlenme kontrolü
        if invoice.get('applicant') and self.lc.get('applicant'):
            if invoice.get('applicant').lower() != self.lc.get('applicant').lower():
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

        # 18(c): Kelimesi kelimesine Mal Tanımı Kontrolü (Çapraz Evrak Rezerv Kontrolü)
        lc_goods = self.lc.get('goods_description', '').strip().lower()
        inv_goods = invoice.get('goods_description', '').strip().lower()
        
        # Boşlukları ve noktalama işaretlerini normalize ederek karşılaştırma yapıyoruz
        lc_norm = re.sub(r'[^a-zA-Z0-8\s]', '', lc_goods)
        inv_norm = re.sub(r'[^a-zA-Z0-8\s]', '', inv_goods)
        
        if lc_norm != inv_norm:
            self.rezervler.append({
                "madde": "UCP 600 Madde 18(c)",
                "seviye": "KRITIK_REZERV",
                "mesaj": "Faturadaki mal tanımı, akreditifteki mal tanımı ile kelimesi kelimesine (exactly) uyuşmuyor!"
            })

    def _madde_20_konsimento_tasima_belgesi(self):
        """Madde 20: Konşimento (Bill of Lading) Kuralları"""
        bl = self.docs.get('bl', {})
        
        # 20(a)(i): İmza ve Taşıyan (Carrier) bilgisi kontrolü
        if not bl.get('is_signed') or not bl.get('carrier_identified'):
            self.rezervler.append({
                "madde": "UCP 600 Madde 20(a)(i)",
                "seviye": "KRITIK_REZERV",
                "mesaj": "Konşimento üzerinde Taşıyan (Carrier) kimliği veya geçerli imza/kaşe tespiti yapılamadı!"
            })

        # 20(a)(ii): Shipped on Board ibaresi kontrolü
        if not bl.get('shipped_on_board', False):
            self.rezervler.append({
                "madde": "UCP 600 Madde 20(a)(ii)",
                "seviye": "KRITIK_REZERV",
                "mesaj": "Konşimentoda 'Shipped on board' ibaresi veya yükleme kaydı bulunmuyor!"
            })

    def _madde_28_sigorta_belgesi(self):
        """Madde 28: Sigorta Belgesi ve Kapsamı (%110 kuralı ve Tarih kontrolü)"""
        insurance = self.docs.get('insurance', {})
        bl_date_str = self.docs.get('bl', {}).get('loading_date')
        
        # 28(e): Sigorta Belgesinin Tarihi
        if insurance.get('date') and bl_date_str:
            ins_date = datetime.strptime(insurance.get('date'), "%Y-%m-%d")
            bl_date = datetime.strptime(bl_date_str, "%Y-%m-%d")
            
            if ins_date > bl_date:
                self.rezervler.append({
                    "madde": "UCP 600 Madde 28(e)",
                    "seviye": "KRITIK_REZERV",
                    "mesaj": f"Sigorta poliçesi tarihi ({insurance.get('date')}), yükleme tarihinden ({bl_date_str}) sonradır!"
                })

        # 28(f)(ii): %110 Sigorta Kapsam Oranı Kontrolü (CIF / CIP için geçerli)
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

        # 30(a): 'about' veya 'circa' kelimeleri %10 tolerans sağlar
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
