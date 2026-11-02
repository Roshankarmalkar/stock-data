import json, time, datetime, sys
import yfinance as yf

def cagr(a, b, n):
    try:
        if a and b and a > 0 and b > 0 and n > 0:
            return (b / a) ** (1 / n) - 1
    except Exception:
        pass
    return None

def row(df, names):
    try:
        for n in names:
            if df is not None and n in df.index:
                return df.loc[n].dropna().sort_index()
    except Exception:
        pass
    return None

def series_cagr(s):
    if s is None or len(s) < 3:
        return None
    return cagr(float(s.iloc[0]), float(s.iloc[-1]), len(s) - 1)

syms = [l.strip().upper() for l in open('symbols.txt') if l.strip() and not l.startswith('#')]
out = {}
for s in syms:
    try:
        t = yf.Ticker(s + '.NS')
        i = t.info or {}
        price = i.get('currentPrice') or i.get('regularMarketPrice')
        if not price:
            print('skip', s); continue
        fin = t.financials
        de = i.get('debtToEquity')
        out[s] = {
            'name': i.get('shortName') or s,
            'sector': i.get('sector'),
            'price': price,
            'pe': i.get('trailingPE'),
            'peg': i.get('pegRatio') or i.get('trailingPegRatio'),
            'roe': i.get('returnOnEquity'),
            'de': de / 100 if de is not None else None,
            'margin': i.get('profitMargins'),
            'earng': i.get('earningsGrowth'),
            'rev_cagr': series_cagr(row(fin, ['Total Revenue', 'Operating Revenue'])),
            'np_cagr': series_cagr(row(fin, ['Net Income', 'Net Income Common Stockholders'])),
            'target': i.get('targetMeanPrice'),
            'ma200': i.get('twoHundredDayAverage'),
        }
        print('ok', s)
    except Exception as e:
        print('fail', s, str(e)[:80])
    time.sleep(0.5)

if not out:
    sys.exit('No data fetched, keeping the old file')
json.dump({'updated': datetime.datetime.utcnow().isoformat(), 'data': out}, open('fundamentals.json', 'w'))
print('saved', len(out))
