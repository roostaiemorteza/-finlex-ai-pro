import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import math

from core.tax_engine import get_sample_invoices, calculate_fx_variance, calculate_payroll, analyze_competitor_pricing
from core.legal_engine import mask_sensitive_data, calculate_severance

st.set_page_config(page_title="FinLex AI Pro", layout="wide", initial_sidebar_state="expanded")

# --- UI Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Manrope', sans-serif;
    }
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #e0e0e0;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background: rgba(30, 30, 40, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
    }
    .metric-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# --- Language Selection (Only TR and EN now) ---
lang = st.sidebar.radio("Dil / Language / زبان", ["🇹🇷 Türkçe", "🇬🇧 English", "🇮🇷 فارسی"])
is_fa = "فارسی" in lang
is_tr = "Türkçe" in lang

if is_tr:
    st.sidebar.markdown("### FinLex AI Pro\n*Akıllı Muhasebe, İK ve Finans Platformu*")
    menu = ["Yönetici Özeti (CFO)", "Akıllı Muhasebe & KKEG", "Bordro ve İK (SGK)", "Gelir Tablosu & Karlılık", "Bilanço", "Rakip Analizi & Fiyatlandırma", "Hukuk & KVKK"]
elif is_fa:
    st.sidebar.markdown("### FinLex AI Pro\n*حسابداری، منابع انسانی و امور مالی*")
    menu = ["خلاصه مدیریتی (CFO)", "حسابداری هوشمند و مالیات", "حقوق و دستمزد (SGK)", "صورت سود و زیان", "ترازنامه", "تحلیل رقبا و قیمت‌گذاری", "حقوقی و حریم خصوصی"]
else:
    st.sidebar.markdown("### FinLex AI Pro\n*Smart Accounting, HR & Finance Platform*")
    menu = ["Executive Dashboard", "Smart Accounting & Tax", "Payroll & HR (SGK)", "P&L & Profitability", "Balance Sheet", "Competitor Pricing AI", "Legal & Privacy"]

choice = st.sidebar.selectbox("ماژول را انتخاب کنید" if is_fa else ("Modül Seçimi / Select Module" if is_tr else "Select Module"), menu)

st.markdown(f"<div class='main-header'>{choice}</div>", unsafe_allow_html=True)
st.markdown("---")

df_invoices = get_sample_invoices()

if choice in ["Yönetici Özeti (CFO)", "Executive Dashboard", "خلاصه مدیریتی (CFO)"]:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""<div class='metric-card'>Top. Nakit / Total Cash<br><span class='metric-val'>₺1,245,000</span></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class='metric-card'>Aylık Gider / Burn Rate<br><span class='metric-val' style='color:#f44336;'>₺340,000</span></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class='metric-card'>Nakit Ömrü / Runway<br><span class='metric-val' style='color:#FFC107;'>3.6 Ay/Mo</span></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown("""<div class='metric-card'>Vergi Riski / Tax Risk<br><span class='metric-val' style='color:#4CAF50;'>Düşük/Low</span></div>""", unsafe_allow_html=True)

    st.subheader("Nakit Akışı Tahmini / Cash Flow Forecast" if is_tr else "Cash Flow Forecast")
    dates = pd.date_range(start="2026-10-01", periods=90)
    cash = [1245000]
    for i in range(1, 90):
        cash.append(cash[-1] + np.random.randint(-15000, 18000))
    fig = px.line(x=dates, y=cash, template="plotly_dark")
    fig.update_layout(xaxis_title="Tarih" if is_tr else "Date", yaxis_title="Nakit (₺)" if is_tr else "Cash (₺)", margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)

elif choice in ["Akıllı Muhasebe & KKEG", "Smart Accounting & Tax", "حسابداری هوشمند و مالیات"]:
    st.subheader("Fatura İşlemleri (Tek Düzen Hesap Planı)" if is_tr else "Invoice Processing (Chart of Accounts)")
    st.dataframe(df_invoices, use_container_width=True)

    st.subheader("Kur Farkı Hesaplama" if is_tr else "FX Variance Calculation")
    c1, c2, c3 = st.columns(3)
    amt = c1.number_input("Tutar (USD)" if is_tr else "Amount (USD)", value=10000)
    inv_r = c2.number_input("Fatura Kuru (₺)" if is_tr else "Invoice Rate (₺)", value=32.50)
    pay_r = c3.number_input("Ödeme Kuru (₺)" if is_tr else "Payment Rate (₺)", value=34.20)

    if st.button("Hesapla / Calculate"):
        res = calculate_fx_variance(amt, inv_r, pay_r)
        st.json(res)

elif choice in ["Bordro ve İK (SGK)", "Payroll & HR (SGK)", "حقوق و دستمزد (SGK)"]:
    st.subheader("Otomatik Bordro Hesaplayıcı" if is_tr else "Automated Payroll Calculator")
    st.info("2026 SGK ve Vergi dilimlerine göre hesaplama (Tahmini)" if is_tr else "Calculation based on 2026 SGK and Tax brackets (Est.)")

    brut = st.number_input("Brüt Maaş (₺) / Gross Salary (₺)", min_value=17002.0, value=35000.0, step=1000.0)

    if st.button("Bordro Oluştur / Generate Payroll"):
        payroll = calculate_payroll(brut)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Çalışan Kesintileri / Employee Deductions")
            st.write(f"**SGK İşçi Payı:** ₺{payroll['SGK İşçi Payı (%14)']:,.2f}")
            st.write(f"**İşsizlik İşçi Payı:** ₺{payroll['İşsizlik İşçi Payı (%1)']:,.2f}")
            st.write(f"**Gelir Vergisi:** ₺{payroll['Gelir Vergisi (%15)']:,.2f}")
            st.write(f"**Damga Vergisi:** ₺{payroll['Damga Vergisi (‰7.59)']:,.2f}")
            st.markdown(f"<h3 style='color:#4CAF50;'>Net Maaş: ₺{payroll['Net Maaş']:,.2f}</h3>", unsafe_allow_html=True)

        with col2:
            st.markdown("### İşveren Maliyeti / Employer Cost")
            st.write(f"**Brüt Maaş:** ₺{payroll['Brüt Maaş']:,.2f}")
            st.write(f"**SGK İşveren Payı:** ₺{payroll['SGK İşveren Payı (%20.5)']:,.2f}")
            st.write(f"**İşsizlik İşveren Payı:** ₺{payroll['İşsizlik İşveren Payı (%2)']:,.2f}")
            st.markdown(f"<h3 style='color:#f44336;'>Toplam İşveren Maliyeti: ₺{payroll['İşverene Toplam Maliyet']:,.2f}</h3>", unsafe_allow_html=True)

elif choice in ["Gelir Tablosu & Karlılık", "P&L & Profitability", "صورت سود و زیان"]:
    st.subheader("Aylık Gelir Tablosu (P&L)" if is_tr else "Monthly Profit & Loss Statement (P&L)")

    # Calculate from invoices
    sales = df_invoices[df_invoices["Türü"] == "Satış"]["Matrah"].sum()
    cogs = df_invoices[df_invoices["Hesap Kodu"] == "153"]["Matrah"].sum()
    opex = df_invoices[df_invoices["Hesap Kodu"] == "770"]["Matrah"].sum()

    # Payroll is an editable estimate rather than an invisible fixed assumption.
    employee_count = st.number_input("Çalışan sayısı / Employees", min_value=0, value=5, step=1)
    gross_salary = st.number_input("Kişi başı brüt maaş (₺) / Gross salary per employee", min_value=0.0, value=35000.0, step=1000.0)
    payroll_cost = employee_count * calculate_payroll(gross_salary)["İşverene Toplam Maliyet"]
    total_expenses = cogs + opex + payroll_cost
    net_profit = sales - total_expenses

    metrics = {
        "600 - Yurtiçi Satışlar (Brüt Satışlar)": sales,
        "153 - Ticari Mallar (Satışların Maliyeti)": -cogs,
        "BRÜT KAR (Gross Profit)": sales - cogs,
        "770 - Genel Yönetim Giderleri (Kira, Elektrik vb)": -opex,
        "770 - Personel Giderleri (İşveren Maliyeti)": -payroll_cost,
        "NET FAALİYET KARI (Net Operating Profit)": net_profit
    }

    df_pl = pd.DataFrame(list(metrics.items()), columns=["Hesap / Kalem" if is_tr else "Account / Line Item", "Tutar (₺)" if is_tr else "Amount (₺)"])

    def color_negative_red(val):
        color = 'red' if isinstance(val, (int, float)) and val < 0 else 'green' if isinstance(val, (int, float)) and val > 0 else 'white'
        return f'color: {color}'

    st.dataframe(df_pl.style.applymap(color_negative_red, subset=["Tutar (₺)" if is_tr else "Amount (₺)"]), use_container_width=True)

    fig = go.Figure(go.Waterfall(
        name="20", orientation="v",
        measure=["relative", "relative", "total", "relative", "relative", "total"],
        x=["Brüt Satışlar", "Maliyetler (SMM)", "Brüt Kar", "Yönetim Giderleri", "Personel Giderleri", "Net Kar"],
        y=[sales, -cogs, 0, -opex, -payroll_cost, 0],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    fig.update_layout(title="Karlılık Şelale Grafiği" if is_tr else "Profitability Waterfall Chart", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

elif choice in ["Bilanço", "Balance Sheet", "ترازنامه"]:
    st.subheader("Bilanço / Balance Sheet / ترازنامه")
    st.info("Rakamları dönem sonu muhasebe kayıtlarınıza göre girin. / Enter period-end balances from your accounting records.")
    c1, c2, c3 = st.columns(3)
    cash_assets = c1.number_input("Nakit ve Bankalar (₺) / Cash & Banks", min_value=0.0, value=1245000.0)
    receivables = c2.number_input("Ticari Alacaklar (₺) / Receivables", min_value=0.0, value=0.0)
    inventory = c3.number_input("Stoklar (₺) / Inventory", min_value=0.0, value=0.0)
    c4, c5, c6 = st.columns(3)
    fixed_assets = c4.number_input("Duran Varlıklar (₺) / Fixed Assets", min_value=0.0, value=0.0)
    liabilities = c5.number_input("Yükümlülükler (₺) / Liabilities", min_value=0.0, value=0.0)
    equity_input = c6.number_input("Özkaynaklar (₺) / Equity", value=0.0)
    assets = cash_assets + receivables + inventory + fixed_assets
    total_liab_equity = liabilities + equity_input
    balance_gap = assets - total_liab_equity
    st.metric("Toplam Varlıklar / Total Assets", f"₺{assets:,.2f}")
    st.metric("Yükümlülükler + Özkaynaklar / Liabilities + Equity", f"₺{total_liab_equity:,.2f}")
    if abs(balance_gap) < 0.01:
        st.success("Bilanço dengede / Balance sheet balances")
    else:
        st.warning(f"Denge farkı / Balance difference: ₺{balance_gap:,.2f}")

elif choice in ["Rakip Analizi & Fiyatlandırma", "Competitor Pricing AI", "تحلیل رقبا و قیمت‌گذاری"]:
    st.subheader("Yapay Zeka Destekli Fiyatlandırma Motoru" if is_tr else "AI-Powered Pricing Engine")
    st.write("Rakiplerin fiyatlarını analiz ederek optimum satış fiyatınızı belirleyin." if is_tr else "Analyze competitor pricing to determine your optimal selling price.")

    col1, col2, col3 = st.columns(3)
    my_cost = col1.number_input("Ürün Maliyeti (₺) / Product Cost", value=150.0)
    comp_a = col2.number_input("Rakip A Fiyatı (₺) / Competitor A Price", value=220.0)
    comp_b = col3.number_input("Rakip B Fiyatı (₺) / Competitor B Price", value=245.0)

    if st.button("Analiz Et / Analyze Pricing"):
        res = analyze_competitor_pricing(my_cost, comp_a, comp_b)
        st.success(f"**Öneri / Suggestion:** {res['Yapay Zeka Önerisi']}")
        st.write(f"**Durum / Status:** {res['Durum Analizi']}")

        # Chart
        labels = ["Benim Maliyetim", "Rakip A", "Rakip B", "Piyasa Ortalaması", "AI Önerisi"]
        vals = [my_cost, comp_a, comp_b, res["Ortalama Piyasa Fiyatı"], res["30% Marjlı Önerilen Fiyat"]]
        fig = px.bar(x=labels, y=vals, color=labels, title="Fiyat Karşılaştırması", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

elif choice in ["Hukuk & KVKK", "Legal & Privacy", "حقوقی و حریم خصوصی"]:
    st.subheader("KVKK Veri Maskeleme" if is_tr else "GDPR/KVKK Data Masking")
    text_input = st.text_area("Metin Girin / Enter Text", "Ahmet Yılmaz'ın TC'si 12345678901, IBAN: TR120000000000000000000000")
    if st.button("Maskele / Mask"):
        st.info(mask_sensitive_data(text_input))
