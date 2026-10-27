import re
def mask_sensitive_data(text):
 stats={"TC":0,"IBAN":0,"Telefon":0,"E-posta":0}
 def replace(pattern,fn,key,s):
  def wrapped(m): stats[key]+=1; return fn(m)
  return re.sub(pattern,wrapped,s)
 text=replace(r"\b([1-9][0-9]{2})[0-9]{5}([0-9]{3})\b",lambda m:m.group(1)+"*****"+m.group(2),"TC",text)
 text=replace(r"\b(TR[0-9]{2})[\s0-9]{18,22}([0-9]{4})\b",lambda m:m.group(1)+" **** **** **** "+m.group(2),"IBAN",text)
 text=replace(r"(?:\+?90|0)?5[0-9]{2}[\s-]?[0-9]{3}[\s-]?[0-9]{2}[\s-]?[0-9]{2}",lambda m:"+90 5** *** ** **","Telefon",text)
 text=replace(r"([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",lambda m:m.group(1)[:2]+"***@"+m.group(2),"E-posta",text)
 return {"masked_text":text,"stats":stats}
def calculate_severance_indemnity(start_date,end_date,gross_salary):
 days=(end_date-start_date).days; years=days/365.25; cap=46900.0; eligible=years>=1; base=min(gross_salary,cap); gross=base*years if eligible else 0
 weeks=2 if days<180 else 4 if days<=540 else 6 if days<=1080 else 8; ihbar=gross_salary/30*weeks*7
 return {"eligible":eligible,"years_worked":round(years,2),"gross_kidem":round(gross,2),"net_kidem":round(gross*(1-.00759),2),"notice_weeks":weeks,"gross_ihbar":round(ihbar,2),"net_ihbar":round(ihbar*(1-.15-.00759),2),"total_net":round(gross*(1-.00759)+ihbar*(1-.15-.00759),2),"kidem_tavani":cap}
def get_contract_diff_samples():
 return [{"clause":"Fesih ve cezai şart","before":"Taraflar 30 gün önceden bildirimle feshedebilir.","after":"Müşteri dilediği an feshedebilir; yüklenici 6 aylık ceza öder.","risk":"YÜKSEK","impact":"Tek taraflı ve orantısız yükümlülük. Karşılıklı fesih hakkı ve eşit bildirim süresi önerilir."},{"clause":"Yetkili mahkeme","before":"Antalya mahkemeleri yetkilidir.","after":"Londra tahkimi; tüm masraflar yükleniciye aittir.","risk":"KRİTİK","impact":"Yabancı tahkim maliyet ve uygulanabilirlik riski doğurabilir. Yerel yargı veya dengeli tahkim şartı talep edin."},{"clause":"Fikri mülkiyet","before":"Önceden mevcut fikri mülkiyet yüklenicide kalır.","after":"Tüm kod, model ve know-how devredilir.","risk":"KRİTİK","impact":"Arka plan fikri mülkiyet korunmuyor. Önceden var olan teknoloji için açık istisna eklenmeli."}]
