import pandas as pd
import numpy as np

def get_sample_invoices():
    return pd.DataFrame([
        {"Tarih": "2026-10-01", "Fatura No": "INV-001", "Cari Hesap": "Marmara Tedarik", "Matrah": 50000, "KDV %": 20, "KDV Tutarı": 10000, "Hesap Kodu": "153", "Açıklama": "Ticari Mallar", "KKEG": "Hayır", "Türü": "Alış"},
        {"Tarih": "2026-10-05", "Fatura No": "INV-002", "Cari Hesap": "Ofis Market", "Matrah": 4500, "KDV %": 20, "KDV Tutarı": 900, "Hesap Kodu": "770", "Açıklama": "Kırtasiye Gideri", "KKEG": "Hayır", "Türü": "Alış"},
        {"Tarih": "2026-10-10", "Fatura No": "INV-003", "Cari Hesap": "Lüks Restoran", "Matrah": 12000, "KDV %": 10, "KDV Tutarı": 1200, "Hesap Kodu": "770", "Açıklama": "Temsil Ağırlama", "KKEG": "Evet (%50)", "Türü": "Alış"},
        {"Tarih": "2026-10-15", "Fatura No": "INV-004", "Cari Hesap": "Vatan Elektrik", "Matrah": 8500, "KDV %": 20, "KDV Tutarı": 1700, "Hesap Kodu": "770", "Açıklama": "Elektrik Faturası", "KKEG": "Hayır", "Türü": "Gider"},
        {"Tarih": "2026-10-20", "Fatura No": "INV-005", "Cari Hesap": "Su İdaresi", "Matrah": 2200, "KDV %": 1, "KDV Tutarı": 22, "Hesap Kodu": "770", "Açıklama": "Su Faturası", "KKEG": "Hayır", "Türü": "Gider"},
        {"Tarih": "2026-10-25", "Fatura No": "INV-006", "Cari Hesap": "Emlak A.Ş.", "Matrah": 30000, "KDV %": 20, "KDV Tutarı": 6000, "Hesap Kodu": "770", "Açıklama": "Aylık Kira", "KKEG": "Hayır", "Türü": "Gider"},
        {"Tarih": "2026-10-08", "Fatura No": "SAL-001", "Cari Hesap": "Demir A.Ş.", "Matrah": 150000, "KDV %": 20, "KDV Tutarı": 30000, "Hesap Kodu": "600", "Açıklama": "Yurtiçi Satış", "KKEG": "Hayır", "Türü": "Satış"},
        {"Tarih": "2026-10-18", "Fatura No": "SAL-002", "Cari Hesap": "Çelik Ltd.", "Matrah": 85000, "KDV %": 20, "KDV Tutarı": 17000, "Hesap Kodu": "600", "Açıklama": "Yurtiçi Satış", "KKEG": "Hayır", "Türü": "Satış"}
    ])

def calculate_fx_variance(amount, invoice_rate, payment_rate):
    variance = amount * (payment_rate - invoice_rate)
    is_gain = variance > 0
    account_code = "646 (Kambiyo Karları)" if is_gain else "656 (Kambiyo Zararları)"
    vat = abs(variance) * 0.20
    return {
        "Fark Tutarı (TL)": abs(variance),
        "Durum": "Kur Karı" if is_gain else "Kur Zararı",
        "Hesap Kodu": account_code,
        "Hesaplanması Gereken KDV (TL)": vat,
        "Fatura Toplamı (TL)": abs(variance) + vat
    }

def calculate_payroll(brut_maas):
    # 2026 Estimated SGK & Tax Rates
    sgk_isci_primi = brut_maas * 0.14
    issizlik_isci_primi = brut_maas * 0.01
    kesintiler_toplami_sgk = sgk_isci_primi + issizlik_isci_primi
    gelir_vergisi_matrahi = brut_maas - kesintiler_toplami_sgk
    gelir_vergisi = gelir_vergisi_matrahi * 0.15  # Tier 1 simple approx
    damga_vergisi = brut_maas * 0.00759
    kesintiler_toplami = kesintiler_toplami_sgk + gelir_vergisi + damga_vergisi
    net_maas = brut_maas - kesintiler_toplami

    sgk_isveren_primi = brut_maas * 0.205
    issizlik_isveren_primi = brut_maas * 0.02
    isverene_maliyet = brut_maas + sgk_isveren_primi + issizlik_isveren_primi

    return {
        "Brüt Maaş": brut_maas,
        "SGK İşçi Payı (%14)": sgk_isci_primi,
        "İşsizlik İşçi Payı (%1)": issizlik_isci_primi,
        "Gelir Vergisi Matrahı": gelir_vergisi_matrahi,
        "Gelir Vergisi (%15)": gelir_vergisi,
        "Damga Vergisi (‰7.59)": damga_vergisi,
        "Net Maaş": net_maas,
        "SGK İşveren Payı (%20.5)": sgk_isveren_primi,
        "İşsizlik İşveren Payı (%2)": issizlik_isveren_primi,
        "İşverene Toplam Maliyet": isverene_maliyet
    }

def analyze_competitor_pricing(my_cost, comp_price_a, comp_price_b):
    avg_market_price = (comp_price_a + comp_price_b) / 2
    suggested_price = my_cost * 1.30  # Target 30% margin
    if suggested_price > avg_market_price:
        status = "Rekabetçi Değil (Maliyet Yüksek)"
        action = "Maliyetleri Düşür veya Hedef Kitleyi Değiştir"
    else:
        status = "Rekabetçi (Avantajlı Konum)"
        action = f"Satış Fiyatını {avg_market_price * 0.95:,.2f} TL olarak belirle (Pazarı Sürklase Et)"

    return {
        "Ortalama Piyasa Fiyatı": avg_market_price,
        "30% Marjlı Önerilen Fiyat": suggested_price,
        "Durum Analizi": status,
        "Yapay Zeka Önerisi": action
    }
