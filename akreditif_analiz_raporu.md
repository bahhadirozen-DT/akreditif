# 📋 AKREDİTİF (KÜŞAT) GELİŞMİŞ DENETİM RAPORU

**Rapor Tarihi:** 07.06.2026 17:42
---

## 1. Kritik Süreler ve Vade Analizi
* En Geç Yükleme Tarihi (44C): 15.08.2026
* Bankaya Son Evrak İbraz Tarihi: 05.09.2026

## 2. Finansal Vade ve Ödeme Takvimi
* Akreditif Tipi: Vadeli Ödeme (Deferred Payment)
* Vade Süresi: Konşimento tarihinden itibaren 90 gün.
* Tahmini Ödeme Günü: 13.11.2026

## 3. Çapraz Evrak Uyumluluk Kontrolü (Rezerv Önleme)
* 🚨 **[REZERV RİSKİ]** Faturadaki mal tanımı küşattakiyle tam eşleşmiyor! (UCP 600 Madde 18).
* 🚨 **[REZERV RİSKİ]** Fatura tarihi (25.08.2026), yükleme tarihinden (15.08.2026) sonra olamaz! Banka reddeder.

## 4. Zorunlu UCP 600 Parametreleri
* ✅ **[UYUMLU]** [Art 1] 'UCP 600' doğrulandı.
* ✅ **[UYUMLU]** [Art 3] 'IRREVOCABLE' doğrulandı.

## 5. UCP 600 Maddeleri ve SWIFT Kontrolleri
* ⚠️ **[KONTROL ET]** [Art 2] 'ADVISING BANK' doğrudan geçmiyor. (İhbar bankası tanımı eksiksiz olmalıdır.)
* ⚠️ **[KONTROL ET]** [Art 4] 'CONTRACT' doğrudan geçmiyor. (Akreditif satış sözleşmesinden bağımsız bir işlemdir.)
* 🔍 **[TESPİT EDİLDİ]** [Art 5] DOCUMENTS -> Bankalar mallarla değil, sadece belgelerle ilgilenir.
* 🔍 **[TESPİT EDİLDİ]** [Art 6] :41A: -> Akreditifin geçerli olduğu banka ve ödeme/iştira şekli.
* 🔍 **[TESPİT EDİLDİ]** [Art 7] ISSUING BANK -> Amir bankanın kesin ödeme yükümlülüğü.
* ⚠️ **[KONTROL ET]** [Art 8] 'CONFIRMING BANK' doğrudan geçmiyor. (Teyit bankasının sorumlulukları ve teyit talimatı (:49:).)
* ⚠️ **[KONTROL ET]** [Art 9] 'AMENDMENT' doğrudan geçmiyor. (Değişikliklerin lehtar onayı olmadan yürürlüğe girememe kuralı.)
* ⚠️ **[KONTROL ET]** [Art 10] 'ADVISING AMENDMENTS' doğrudan geçmiyor. (Değişikliklerin ihbar edilme usulleri.)
* ⚠️ **[KONTROL ET]** [Art 11] 'TELETRANSMITTED' doğrudan geçmiyor. (Teleks/SWIFT mesajlarının ön talimat ve asıl metin ilişkisi.)
* ⚠️ **[KONTROL ET]** [Art 12] 'NOMINATED BANK' doğrudan geçmiyor. (Görevlendirilen bankanın yetki sınırları.)
* ⚠️ **[KONTROL ET]** [Art 13] 'REIMBURSEMENT' doğrudan geçmiyor. (Bankalar arası rücu ve ramisment anlaşmaları.)
* 🔍 **[TESPİT EDİLDİ]** [Art 14] :48: -> Belge inceleme standardı. İbraz süresi belirtilmemişse en fazla 21 gündür.
* ⚠️ **[KONTROL ET]** [Art 15] 'COMPLYING PRESENTATION' doğrudan geçmiyor. (Uygun ibraz durumunda ödeme yapılması zorunluluğu.)
* ⚠️ **[KONTROL ET]** [Art 16] 'DISCREPANT DOCUMENTS' doğrudan geçmiyor. (Rezervli belgelerin reddedilme bildirimi kuralları (en geç 5 iş günü).)
* ⚠️ **[KONTROL ET]** [Art 17] 'ORIGINAL' doğrudan geçmiyor. (Orijinal ve kopya belge ayrımı ve imza kriterleri.)
* 🔍 **[TESPİT EDİLDİ]** [Art 18] COMMERCIAL INVOICE -> Ticari fatura lehtar adına düzenlenmeli ve akreditif döviz cinsinden olmalıdır.
* ⚠️ **[KONTROL ET]** [Art 19] 'MULTIMODAL' doğrudan geçmiyor. (En az iki farklı taşıma modunu kapsayan taşıma belgesi kuralları.)
* 🔍 **[TESPİT EDİLDİ]** [Art 20] BILL OF LADING -> Deniz konşimentosu (Kaptan/Acente imzası, On Board notu).
* ⚠️ **[KONTROL ET]** [Art 21] 'NON-NEGOTIABLE SEA WAYBILL' doğrudan geçmiyor. (Ciro edilemez deniz yolu taşıma senedi kuralları.)
* ⚠️ **[KONTROL ET]** [Art 22] 'CHARTER PARTY' doğrudan geçmiyor. (Kiralık gemi konşimentosu kabul şartları.)
* ⚠️ **[KONTROL ET]** [Art 23] 'AIR TRANSPORT' doğrudan geçmiyor. (Hava yolu taşıma senedi (Air Waybill) imza ve asıl nüsha kuralları.)
* ⚠️ **[KONTROL ET]** [Art 24] 'ROAD RAIL INLAND' doğrudan geçmiyor. (Karayolu (CMR), demiryolu veya iç su yolu taşıma belgeleri.)
* ⚠️ **[KONTROL ET]** [Art 25] 'COURIER POST' doğrudan geçmiyor. (Kurye ve posta alındıları, makbuz tarihleri.)
* ⚠️ **[KONTROL ET]** [Art 26] 'DECK' doğrudan geçmiyor. (Gemi güvertesine yükleme (On Deck) ve 'Shipper's load and count' ibareleri.)
* 🔍 **[TESPİT EDİLDİ]** [Art 27] CLEAN -> Temiz taşıma belgesi (Clean Bill of Lading) şartı. Malda hasar ibaresi olmamalı.
* 🔍 **[TESPİT EDİLDİ]** [Art 28] INSURANCE -> Sigorta belgesi ve kapsamı (Kural olarak en az CIF/CIP değerinin %110'u).
* ⚠️ **[KONTROL ET]** [Art 29] 'EXPIRY DATE' doğrudan geçmiyor. (Kapanış tarihinin resmi tatile gelmesi durumunda uzama kuralları.)
* ⚠️ **[KONTROL ET]** [Art 30] 'TOLERANCE' doğrudan geçmiyor. (Miktar, tutar ve birim fiyattaki +/- %5 ve %10 tolerans kuralları (:39A:).)
* ⚠️ **[KONTROL ET]** [Art 31] 'PARTIAL' doğrudan geçmiyor. (Kısmi yükleme ve aktarma (Partial Shipments / Transshipments) kuralları.)
* ⚠️ **[KONTROL ET]** [Art 32] 'INSTALMENT' doğrudan geçmiyor. (Dönemsel/parti parti yüklemelerde bir dönemin kaçırılması durumunda akreditifin hükümsüz kalması.)
* ⚠️ **[KONTROL ET]** [Art 33] 'HOURS' doğrudan geçmiyor. (Bankaların çalışma saatleri dışında belge kabul etmeme hakkı.)
* ⚠️ **[KONTROL ET]** [Art 34] 'DISCLAIMER DOCUMENTS' doğrudan geçmiyor. (Belgelerin doğruluğu ve hukuki geçerliliği konusunda bankaların sorumsuzluğu.)
* ⚠️ **[KONTROL ET]** [Art 35] 'TRANSMISSION' doğrudan geçmiyor. (Belgelerin postada kaybolması veya gecikmesi durumunda bankaların sorumsuzluğu.)
* ⚠️ **[KONTROL ET]** [Art 36] 'FORCE MAJEURE' doğrudan geçmiyor. (Mücbir sebep (grev, afet, savaş) durumunda bankaların sorumluluktan muafiyeti.)
* ⚠️ **[KONTROL ET]** [Art 37] 'USER CHARGES' doğrudan geçmiyor. (Masrafların kime ait olduğu (:71D:) ve yabancı banka masrafları sorumluluğu.)
* ⚠️ **[KONTROL ET]** [Art 38] 'TRANSFERABLE' doğrudan geçmiyor. (Devredilebilir akreditifler (Transferable L/C) ve birinci/ikinci lehtar ilişkileri.)
* ⚠️ **[KONTROL ET]** [Art 39] 'ASSIGNMENT' doğrudan geçmiyor. (Akreditif alacağının temliki (hukuki devri) hakları.)

---
### 🚨 SONUÇ: Evraklarda veya küşatta riskli uyumsuzluklar (rezerv) tespit edildi! Kontrol etmeden bankaya vermeyin.
