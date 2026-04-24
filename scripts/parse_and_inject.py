import csv, json, re
from datetime import datetime
from dateutil import parser as dp

def parse_float(v):
    try: return round(float(str(v).replace(',','').strip()), 6)
    except: return None

def find_header(all_rows):
    for i, row in enumerate(all_rows):
        for cell in row:
            if str(cell).strip() == 'Ticker':
                return i
    for i, row in enumerate(all_rows):
        if any(str(c).strip() for c in row):
            return i
    return 0

def parse_dr(filepath):
    rows = []
    with open(filepath, encoding='utf-8-sig', errors='ignore') as f:
        all_rows = list(csv.reader(f))
    hi = find_header(all_rows)
    print(f"DR: found header at row {hi}: {all_rows[hi][:6]}")
    col = {}
    for i, h in enumerate(all_rows[hi]):
        h = str(h).strip()
        if h: col[h] = i
    print(f"DR columns: {list(col.keys())}")
    date_str = ''
    if hi > 0:
        for cell in all_rows[0]:
            if cell.strip() and cell.strip() != '0':
                date_str = cell.strip()
                break
    for row in all_rows[hi+1:]:
        if not row or len(row) <= 1: continue
        ticker_idx = col.get('Ticker', 1)
        if ticker_idx >= len(row): continue
        ticker = row[ticker_idx].strip()
        if not ticker or ticker in ['nan','NaN','0','']: continue
        def g(key, default=''):
            idx = col.get(key, -1)
            if idx < 0 or idx >= len(row): return default
            return str(row[idx]).strip()
        name    = g('Name')
        country = g('Country')
        theme   = g('Theme 1')
        sub     = g('Sub Theme')
        sec1    = g('Sector 1')
        sec2    = g('Sector 2')
        inc = ''
        try:
            inc_val = g('Inception date')
            if inc_val and inc_val not in ['0','']:
                inc = dp.parse(inc_val).strftime('%d %b %Y')
        except: pass
        ytd   = parse_float(g('YTD'))
        m1    = parse_float(g('1M'))
        m3    = parse_float(g('3M'))
        m6    = parse_float(g('6M'))
        y1    = parse_float(g('1Y'))
        div   = parse_float(g('Dividend yield (%)'))
        wk52h = parse_float(g('52-wk high'))
        tv    = parse_float(g('Trading value'))
        rsi   = parse_float(g('RSI'))
        rows.append([ticker,name,country,theme,sec1,ytd,m1,m3,m6,y1,wk52h,tv,rsi,div,sub,inc,sec2])
    return rows, date_str

def parse_ul(filepath):
    rows = []
    with open(filepath, encoding='utf-8-sig', errors='ignore') as f:
        all_rows = list(csv.reader(f))
    hi = find_header(all_rows)
    print(f"UL: found header at row {hi}: {all_rows[hi][:6]}")
    col = {}
    for i, h in enumerate(all_rows[hi]):
        h = str(h).strip()
        if h: col[h] = i
    for row in all_rows[hi+1:]:
        if not row or len(row) <= 1: continue
        ticker_idx = col.get('Ticker', 1)
        if ticker_idx >= len(row): continue
        ticker = row[ticker_idx].strip()
        if not ticker or ticker in ['nan','NaN','0','']: continue
        def g(key, default=''):
            idx = col.get(key, -1)
            if idx < 0 or idx >= len(row): return default
            return str(row[idx]).strip()
        name    = g('Name')
        country = g('Country')
        theme   = g('Theme 1')
        sub     = g('Sub Theme')
        sec1    = g('Sector 1')
        sec2    = g('Sector 2')
        ytd = parse_float(g('YTD'))
        m1  = parse_float(g('1M'))
        m3  = parse_float(g('3M'))
        m6  = parse_float(g('6M'))
        y1  = parse_float(g('1Y'))
        rows.append([ticker,name,country,theme,sec1,ytd,m1,m3,m6,y1,None,None,None,None,sub,'',sec2])
    return rows

dr, date_str = parse_dr('data/Current_DR80.csv')
ul = parse_ul('data/Current_DR80_UL.csv')

boeing = next((r[:] for r in dr if 'BOEING' in r[1].upper()), None)
if boeing:
    bc = boeing[:]; bc[3] = 'Spacetech'; dr.append(bc)

print(f"DR: {len(dr)} rows, UL: {len(ul)} rows")

today = datetime.now()
thai_months = ['มกราคม','กุมภาพันธ์','มีนาคม','เมษายน','พฤษภาคม','มิถุนายน',
               'กรกฎาคม','สิงหาคม','กันยายน','ตุลาคม','พฤศจิกายน','ธันวาคม']
try:
    if date_str:
        d = dp.parse(date_str)
        thai_date = f"{d.day} {thai_months[d.month-1]} {d.year+543}"
        eng_date  = d.strftime('%d %B %Y')
    else:
        raise ValueError("no date")
except:
    thai_date = f"{today.day} {thai_months[today.month-1]} {today.year+543}"
    eng_date  = today.strftime('%d %B %Y')

print(f"Date: {thai_date} / {eng_date}")

with open('index.html','r',encoding='utf-8') as f:
    html = f.read()

html = re.sub(r'const DR_RAW = \[.*?\];', f'const DR_RAW = {json.dumps(dr, ensure_ascii=False)};', html, flags=re.DOTALL)
html = re.sub(r'const UL_RAW = \[.*?\];', f'const UL_RAW = {json.dumps(ul, ensure_ascii=False)};', html, flags=re.DOTALL)
html = re.sub(r'\d+ [ก-๙]+ \d{4}', thai_date, html)
html = re.sub(r'\d+ \w+ 202\d', eng_date, html)

with open('index.html','w',encoding='utf-8') as f:
    f.write(html)

print(f"✅ index.html updated — {thai_date}")
