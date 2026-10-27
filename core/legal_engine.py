import re

def mask_sensitive_pii(text):
    stats = {"TC": 0, "IBAN": 0, "Telefon": 0, "E-posta": 0}
    def replace(pattern, fn, key, s):
        def wrapped(m):
            stats[key] += 1
            return fn(m)
        return re.sub(pattern, wrapped, s)
    text = replace(r"\b([1-9][0-9]{2})[0-9]{5}([0-9]{3})\b", lambda m: m.group(1) + "*****" + m.group(2), "TC", text)
    text = replace(r"\b(TR[0-9]{2})[\s0-9]{18,22}([0-9]{4})\b", lambda m: m.group(1) + " **** **** **** " + m.group(2), "IBAN", text)
    text = replace(r"(?:\+?90|0)?5[0-9]{2}[\s-]?[0-9]{3}[\s-]?[0-9]{2}[\s-]?[0-9]{2}", lambda m: "+90 5** *** ** **", "Telefon", text)
    text = replace(r"([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", lambda m: m.group(1)[:2] + "***@" + m.group(2), "E-posta", text)
    return {"masked_text": text, "stats": stats}

# Alias جهت سازگاری با سایر ماژول‌ها
mask_sensitive_data = mask_sensitive_pii


def calculate_severance_indemnity(start_date, end_date, gross_salary):
    days = (end_date - start_date).days
    years = days / 365.25
    cap = 46900.0
    eligible = years >= 1
    base = min(gross_salary, cap)
    gross = base * years if eligible else 0.0
    weeks = 2 if days < 180 else 4 if days <= 540 else 6 if days <= 1080 else 8
    ihbar = gross_salary / 30 * weeks * 7
    return {
        "eligible": eligible,
        "years_worked": round(years, 2),
        "gross_kidem": round(gross, 2),
        "net_kidem": round(gross * (1 - 0.00759), 2),
        "notice_weeks": weeks,
        "gross_ihbar": round(ihbar, 2),
        "net_ihbar": round(ihbar * (1 - 0.15 - 0.00759), 2),
        "total_net": round(gross * (1 - 0.00759) + ihbar * (1 - 0.15 - 0.00759), 2),
        "kidem_tavani": cap,
    }

# Alias جهت سازگاری با ایمپورت‌هایی که نام کوتاه calculate_severance دارند
calculate_severance = calculate_severance_indemnity


def get_contract_diff_samples():
    return [
        {
            "clause": "Fesih ve cezai şart",
            "old_text": "Taraflar 30 gün önceden bildirmek şartıyla sözleşmeyi feshedebilir.",
            "new_text": "Şirket derhal ve tazminatsız fesih hakkına sahiptir; çalışan feshederse 6 aylık brüt ücret cezai şart öder.",
            "risk_level": "KRİTİK",
            "risk_score": 92,
            "explanation": "Tek taraflı ağır cezai şart ve orantısız fesih hakkı Borçlar Kanunu madde 27 ve 420 kapsamında geçersiz sayılabilir.",
        },
        {
            "clause": "Rekabet yasağı",
            "old_text": "Çalışan ayrıldıktan sonra 6 ay boyunca aynı il sınırları içinde rakip firmada çalışamaz.",
            "new_text": "Çalışan ayrıldıktan sonra 2 yıl boyunca Türkiye genelinde hiçbir rakip veya ilişkili şirkette görev alamaz.",
            "risk_level": "YÜKSEK",
            "risk_score": 78,
            "explanation": "Coğrafi sınırın tüm Türkiye'ye yayılması ve 2 yıllık süre Türk Ticaret Kanunu ve İş Kanunu dengelerine aykırılık oluşturabilir.",
        },
        {
            "clause": "Çalışma saatleri ve fazla mesai",
            "old_text": "Haftalık çalışma süresi 45 saattir. Fazla mesai %50 zamlı ödenir.",
            "new_text": "Aylık 270 saate kadar fazla çalışma ücrete dahildir; ilave mesai talep edilemez.",
            "risk_level": "YÜKSEK",
            "risk_score": 75,
            "explanation": "Yargıtay içtihatlarına göre yıllık 270 saatlik sınır aylık olarak dayatılamaz; aşan kısımlar ücrete dahil sayılamaz.",
        },
    ]
