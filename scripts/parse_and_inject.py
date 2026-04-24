import csv, json, re, os
from datetime import datetime
from dateutil import parser as dp

def parse_float(v):
    try: return round(float(str(v).replace(',','').strip()), 6)
    except: return None

def parse_dr(filepath):
    rows = []
    with open(filepath, encoding='utf-8-sig') as f:
        all_rows = list(csv.reader(f))
    hi = next((i for i,r in enumerate(all_rows) if any('Ticker' in str(c) for c in r)), None)
    if hi is None: raise ValueError("No header row found in DR CSV")
    col = {h.strip():i for i,h in enumerate(all_rows[hi]) if h.strip()}
    print(f"DR columns: {list(col.keys())}")
    for row in all_rows[hi+1:]:
        if len(row) <= 1: continue
        ticker = row[col.get('Ticker',0)].strip()
        if not ticker or ticker in ['nan','NaN']: continue
        name    = row[col['Name']].strip() if 'Name' in col else ''
        country = row[col['Country']].strip() if 'Country' in col else ''
        theme   = row[col['Theme 1']].strip() if 'Theme 1' in col else ''
        sub     = row[col['Sub Theme']].strip() if 'Sub Theme' in col else ''
        sec1    = row[col['Sector 1']].strip() if 'Sector 1' in col else ''
        sec2    = row[col['Sector 2']].strip() if 'Sector 2' in col else ''
        inc = ''
        if 'Inception date' in col:
            try: inc = dp.parse(row[col['Inception date']]).strftime('%d %b %Y')
            except: pass
        ytd = parse_float(row[col['YTD']]) if 'YTD' in col else None
        m1  = parse_float(row[col['1M']]) if '1M' in col else None
        m3  = parse_float(row[col['3M']]) if '3M' in col else None
        m6  = parse_float(row[col['6M']]) if '6M' in col else None
        y1  = parse_float(row[col['1Y']]) if '1Y' in col else None
        div   = parse_float(row[col['Dividend yield (%)']]) if 'Dividend yield (%)' in col else None
        wk52h = parse_float(row[col['52-wk high']]) if '52-wk high' in col else None
        tv    = parse_float(row[col['Trading value']]) if 'Trading value' in col else None
        rsi   = parse_float(row[col['RSI']]) if 'RSI' in col else None
        rows.append([ticker,name,country,theme,sec1,ytd,m1,m3,m6,y1,wk52h,tv,rsi,div,sub,inc,sec2])
    return rows

def parse_ul(filepath):
    rows = []
    with open(filepath, encoding='utf-8-sig') as f:
        all_rows = list(csv.reader(f))
    hi = next((i for i,r in enumerate(all_rows) if any('Ticker' in str(c) for c in r)), None)
    if hi is None: raise ValueError("No header row found in UL CSV")
    col = {h.strip():i for i,h in enumerate(all_rows[hi]) if h.strip()}
    for row in all_rows[hi+1:]:
        if len(row) <= 1: continue
        ticker = row[col.get('Ticker',0)].strip()
        if not ticker or ticker in ['nan','NaN']: continue
        name    = row[col['Name']].strip() if 'Name' in col else ''
        country = row[col['Country']].strip() if 'Country' in col else ''
        theme   = row[col['Theme 1']].strip() if 'Theme 1' in col else ''
        sub     = row[col['Sub Theme']].strip() if 'Sub Theme' in col else ''
        sec1    = row[col['Sector 1']].strip() if 'Sector 1' in col else ''
        sec2    = row[col['Sector 2']].strip() if 'Sector 2' in col else ''
        ytd = parse_float(row[col['YTD']]) if 'YTD' in col else None
        m1  = parse_float(row[col['1M']]) if '1M' in col else None
        m3  = parse_float(row[col['3M']]) if '3M' in col else None
        m6  = parse_float(row[col['6M']]) if '6M' in col else None
        y1  = parse_float(row[col['1Y']]) if '1Y' in col else None
        rows.append([ticker,name,country,theme,sec1,ytd,m1,m3,m6,y1,None,None,None,None,sub,'',sec2])
    return rows

dr = parse_dr('data/Current_DR80.csv')
ul = parse_ul('data/Current_DR80_UL.csv')

boeing = next((r[:] for r in dr if 'BOEING' in r[1].upper()), None)
if boeing:
    bc = boeing[:]; bc[3] = 'Spacetech'; dr.append(bc)

print(f"DR: {len(dr)} rows, UL: {len(ul)} rows")

today = datetime.now()
thai_months = ['มกราคม','กุมภาพันธ์','มีนาคม','เมษายน','พฤษภาคม','มิถุนายน',
               'กรกฎาคม','สิงหาคม','กันยายน','ตุลาคม','พฤศจิกายน','ธันวาคม']
thai_date = f"{today.day} {thai_months[today.month-1]} {today.year+543}"
eng_date  = today.strftime('%d %B %Y')

with open('index.html','r',encoding='utf-8') as f:
    html = f.read()

html = re.sub(r'const DR_RAW = \[.*?\];', f'const DR_RAW = {json.dumps(dr, ensure_ascii=False)};', html, flags=re.DOTALL)
html = re.sub(r'const UL_RAW = \[.*?\];', f'const UL_RAW = {json.dumps(ul, ensure_ascii=False)};', html, flags=re.DOTALL)
html = re.sub(r'\d+ [ก-๙]+ \d{4}', thai_date, html)
html = re.sub(r'\d+ \w+ 202\d', eng_date, html)

with open('index.html','w',encoding='utf-8') as f:
    f.write(html)

print(f"✅ index.html updated — {thai_date}")
