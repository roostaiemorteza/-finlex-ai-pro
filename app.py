import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import math

from core.tax_engine import get_sample_invoices, calculate_fx_variance, calculate_payroll, analyze_competitor_pricing
from core.legal_engine import mask_sensitive_pii, calculate_severance

st.set_page_config(page_title="FinLex AI Pro", layout="wide", initial_sidebar_state="expanded")

# --- UI Styling: Luxury FinTech ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root {
  --ink: #080E1B; --panel: #111C2F; --panel-hi: #17253B;
  --line: rgba(167,190,218,.14); --mint: #55E0C0; --gold: #D6B779;
  --text: #F2F5FA; --muted: #9BAAC0;
}
html, body, [class*="css"] { font-family: 'Manrope','DM Sans',sans-serif; }
.stApp { background: radial-gradient(ellipse at 15% 0%, rgba(42,94,112,.23), transparent 38%), var(--ink); color: var(--text); }
[data-testid="stHeader"] { background: rgba(8,14,27,.78); }
[data-testid="stSidebar"] { background: linear-gradient(180deg,#101A2B 0%,#0B1220 100%); border-right: 1px solid var(--line); }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 { color: var(--text); letter-spacing: -.03em; }
.main-header { font-size: clamp(1.8rem,3vw,2.65rem); font-weight: 800; letter-spacing: -.045em; color: var(--text); margin: .35rem 0 .7rem; }
.stCaption, [data-testid="stCaptionContainer"] { color: var(--muted); }
.stButton > button { border: 1px solid rgba(85,224,192,.5); border-radius: 12px; min-height: 2.8rem; padding: .55rem 1.2rem; color: #061510; font-weight: 700; background: linear-gradient(135deg,#70E9CA,#39BFA4); box-shadow: 0 8px 24px rgba(53,194,162,.18); transition: all .18s ease; }
.stButton > button:hover { transform: translateY(-2px); border-color: var(--gold); background: linear-gradient(135deg,#DCC58F,#B89555); box-shadow: 0 10px 28px rgba(214,183,121,.2); }
[data-testid="stMetric"] { background: linear-gradient(145deg,rgba(23,37,59,.96),rgba(14,24,40,.96)); border: 1px solid var(--line); border-radius: 16px; padding: 1rem 1.15rem; box-shadow: 0 12px 35px rgba(0,0,0,.15); }
[data-testid="stMetricLabel"] { color: var(--muted); }
[data-testid="stMetricValue"] { color: var(--mint); }
.metric-card { background: linear-gradient(145deg,rgba(23,37,59,.96),rgba(14,24,40,.96)); border: 1px solid var(--line); border-radius: 16px; padding: 1.35rem; box-shadow: 0 12px 35px rgba(0,0,0,.15); margin-bottom: 1rem; color: var(--muted); }
.metric-val { display: inline-block; margin-top: .35rem; font-size: 1.75rem; font-weight: 800; letter-spacing: -.035em; color: var(--mint); }
[data-testid="stDataFrame"], [data-testid="stTable"] { border: 1px solid var(--line); border-radius: 14px; overflow: hidden; }
[data-baseweb="select"] > div, [data-baseweb="input"] > div, [data-baseweb="textarea"] { background: #111C2F; border-color: var(--line); border-radius: 10px; }
[data-testid="stAlert"] { border-radius: 12px; }
hr { border-color: var(--line); margin: 1.1rem 0 1.5rem; }
.stApp { min-width: 320px; }
.block-container { max-width: 1500px; padding-top: 2.15rem; padding-bottom: 3rem; }
[data-testid="stSidebar"] { border-right: 1px solid var(--line); }
[data-testid="stSidebar"] [data-testid="stRadio"] label, [data-testid="stSidebar"] [data-testid="stSelectbox"] label { color: var(--muted); font-weight: 600; }
.stButton > button:focus-visible, [data-baseweb="select"]:focus-within, [data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within { outline: 2px solid var(--gold); outline-offset: 2px; }
[data-testid="stTabs"] button { font-weight: 700; }
[data-testid="stAlert"] { border: 1px solid var(--line); }
@media (max-width: 700px) {
  .block-container { padding: 1.2rem .9rem 2rem; }
  .main-header { font-size: 1.8rem; }
  [data-testid="stMetric"] { padding: .8rem; }
}
</style>
""", unsafe_allow_html=True)

# --- Language Selection (Only TR and EN now) ---
lang = st.sidebar.radio("Dil / Language", ["🇹🇷 Türkçe", "🇬🇧 English"])
is_tr = "Türkçe" in lang

if is_tr:
    st.sidebar.markdown("### FinLex AI Pro\n*Akıllı Muhasebe, İK ve Finans Platformu*")
    menu = ["Yönetici Özeti (CFO)", "Akıllı Muhasebe & KKEG", "Bordro ve İK (SGK)", "Gelir Tablosu & Karlılık", "Bilanço", "Rakip Analizi & Fiyatlandırma", "Hukuk & KVKK"]
else:
    st.sidebar.markdown("### FinLex AI Pro\n*Smart Accounting, HR & Finance Platform*")
    menu = ["Executive Dashboard", "Smart Accounting & Tax", "Payroll & HR (SGK)", "P&L & Profitability", "Balance Sheet", "Competitor Pricing AI", "Legal & Privacy"]

choice = st.sidebar.selectbox("Modül Seçimi" if is_tr else "Select Module", menu)

st.markdown(f"<div class='main-header'>{choice}</div>", unsafe_allow_html=True)
st.markdown("---")

df_invoices = get_sample_invoices()

if choice == menu[0]:
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
    rng = np.random.default_rng(42)
    for i in range(1, 90):
        cash.append(cash[-1] + rng.integers(-15000, 18000))
    fig = px.line(x=dates, y=cash, template="plotly_dark")
    fig.update_layout(xaxis_title="Tarih" if is_tr else "Date", yaxis_title="Nakit (₺)" if is_tr else "Cash (₺)", margin=dict(l=0, r=0, t=30, b=0), font=dict(family="Manrope, sans-serif", color="#EAF0F8"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", colorway=["#55E0C0", "#D6B779", "#7AA7FF"])
    st.plotly_chart(fig, use_container_width=True)

elif choice == menu[1]:
    st.subheader("Fatura İşlemleri (Tek Düzen Hesap Planı)" if is_tr else "Invoice Processing (Chart of Accounts)")
    st.dataframe(df_invoices, use_container_width=True)

    st.subheader("Kur Farkı Hesaplama" if is_tr else "FX Variance Calculation")
    c1, c2, c3 = st.columns(3)
    amt = c1.number_input("Tutar (USD)" if is_tr else "Amount (USD)", min_value=0.0, value=10000.0, step=500.0)
    inv_r = c2.number_input("Fatura Kuru (₺)" if is_tr else "Invoice Rate (₺)", min_value=0.0, value=32.50, step=0.10)
    pay_r = c3.number_input("Ödeme Kuru (₺)" if is_tr else "Payment Rate (₺)", min_value=0.0, value=34.20, step=0.10)

    if st.button("Hesapla / Calculate"):
        res = calculate_fx_variance(amt, inv_r, pay_r)
        st.json(res)

elif choice == menu[2]:
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

elif choice == menu[3]:
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
    fig.update_layout(title="Karlılık Şelale Grafiği" if is_tr else "Profitability Waterfall Chart", template="plotly_dark", font=dict(family="Manrope, sans-serif", color="#EAF0F8"), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

elif choice == menu[4]:
    st.subheader("Bilanço / Balance Sheet")
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

elif choice == menu[5]:
    st.subheader("Yapay Zeka Destekli Fiyatlandırma Motoru" if is_tr else "AI-Powered Pricing Engine")
    st.write("Rakiplerin fiyatlarını analiz ederek optimum satış fiyatınızı belirleyin." if is_tr else "Analyze competitor pricing to determine your optimal selling price.")

    col1, col2, col3 = st.columns(3)
    my_cost = col1.number_input("Ürün Maliyeti (₺) / Product Cost", min_value=0.0, value=150.0, step=10.0)
    comp_a = col2.number_input("Rakip A Fiyatı (₺) / Competitor A Price", min_value=0.0, value=220.0, step=10.0)
    comp_b = col3.number_input("Rakip B Fiyatı (₺) / Competitor B Price", min_value=0.0, value=245.0, step=10.0)

    if st.button("Analiz Et / Analyze Pricing"):
        res = analyze_competitor_pricing(my_cost, comp_a, comp_b)
        st.success(f"**Öneri / Suggestion:** {res['Yapay Zeka Önerisi']}")
        st.write(f"**Durum / Status:** {res['Durum Analizi']}")

        # Chart
        labels = ["Benim Maliyetim", "Rakip A", "Rakip B", "Piyasa Ortalaması", "AI Önerisi"]
        vals = [my_cost, comp_a, comp_b, res["Ortalama Piyasa Fiyatı"], res["30% Marjlı Önerilen Fiyat"]]
        fig = px.bar(x=labels, y=vals, color=labels, title="Fiyat Karşılaştırması", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

elif choice == menu[6]:
    st.subheader("KVKK Veri Maskeleme" if is_tr else "GDPR/KVKK Data Masking")
    text_input = st.text_area("Metin Girin / Enter Text", "Ahmet Yılmaz'ın TC'si 12345678901, IBAN: TR120000000000000000000000")
    if st.button("Maskele / Mask", type="primary"):
        result = mask_sensitive_pii(text_input)
        st.success(result["masked_text"])
        st.caption(("Maskelenen öğeler" if is_tr else "Items masked") + ": " + " · ".join(f"{key}: {count}" for key, count in result["stats"].items()))
