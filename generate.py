"""
Regime Monitor — Dual Model (MACRO + TACTICAL) — Daily
MACRO: 20d lookback, 130d vol, 15d smooth, min 15d duration, k=6
TACTICAL: 10d lookback, 65d vol, no smooth, min 5d duration, k=6
"""
import pandas as pd
import numpy as np
import yfinance as yf
import json
import warnings
import os
from datetime import datetime, timedelta
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
warnings.filterwarnings('ignore')

END = datetime.now().strftime('%Y-%m-%d')
START = '2019-01-01'

# ── Universe ──────────────────────────────────────────────────
UNIVERSE = {
    'Crypto': {'BTC-USD':'BTC','ETH-USD':'ETH','SOL-USD':'SOL'},
    'Metals': {'GC=F':'Gold','SI=F':'Silver','HG=F':'Copper','PA=F':'Palladium','PL=F':'Platinum','ALI=F':'Aluminum'},
    'Energy': {'CL=F':'WTI','BZ=F':'Brent','NG=F':'NatGas','RB=F':'Gasoline','HO=F':'HeatingOil'},
    'US Sectors': {
        'XLK':'Tech','XLF':'Financials','XLE':'Energy_Eq','XLV':'Healthcare',
        'XLI':'Industrials','XLP':'Staples','XLY':'Discretionary',
        'XLU':'Utilities','XLRE':'RealEstate','XLB':'Materials','XLC':'CommSvc',
    },
    'Global Equities': {
        '^GSPC':'US_SP500','^IXIC':'US_Nasdaq','^STOXX50E':'EU_Stoxx50',
        'EWJ':'Japan','EWY':'Korea','EWT':'Taiwan','FXI':'China',
        'EWG':'Germany','EWU':'UK','EWZ':'Brazil','INDA':'India',
        'EEM':'EM_Broad','EWA':'Australia','EWC':'Canada',
        'EWS':'Singapore','THD':'Thailand','EWW':'Mexico',
        'EIDO':'Indonesia','VNM':'Vietnam','EZA':'SouthAfrica',
        'QAT':'Qatar','KSA':'SaudiArabia','TUR':'Turkey',
    },
    'Rates': {'^IRX':'US_3M','^FVX':'US_5Y','^TNX':'US_10Y','^TYX':'US_30Y'},
    'Currencies': {
        'EURUSD=X':'EURUSD','JPYUSD=X':'JPYUSD','GBPUSD=X':'GBPUSD',
        'CNYUSD=X':'CNYUSD','AUDUSD=X':'AUDUSD','CHFUSD=X':'CHFUSD',
        'KRWUSD=X':'KRWUSD','SGDUSD=X':'SGDUSD',
    },
    'Credit': {'HYG':'HY_Bond','LQD':'IG_Bond','JNK':'HY_Junk','BKLN':'BankLoans','EMB':'EM_Bond'},
}
RATE_ASSETS = {'US_3M','US_5Y','US_10Y','US_30Y'}
CURVE_ASSETS = {'YC_10Y3M','YC_10Y5Y','YC_30Y10Y'}
SECTOR_TICKERS = ['Tech','Financials','Energy_Eq','Healthcare','Industrials','Staples','Discretionary','Utilities','RealEstate','Materials','CommSvc']
CYCLICAL = ['Discretionary','Industrials','Financials','Materials']
DEFENSIVE = ['Staples','Utilities','Healthcare','RealEstate']
CAT_ORDER = ["Crypto","Metals","Energy","US Sectors","Global Equities","Rates","Curves","Currencies","Credit"]

# ── 1. Data Collection (shared) ──────────────────────────────
print(f"Regime Monitor update: {START} → {END}")
all_tickers = {}
for cat, tickers in UNIVERSE.items():
    for ticker, name in tickers.items():
        all_tickers[ticker] = name

print(f"Downloading {len(all_tickers)} tickers...")
raw = yf.download(list(all_tickers.keys()), start=START, end=END, progress=False, group_by='ticker')
df = pd.DataFrame()
success = []
for ticker, name in all_tickers.items():
    try:
        if ticker in raw.columns.get_level_values(0):
            s = raw[ticker]['Close'].squeeze()
            if isinstance(s, pd.Series) and s.notna().sum() > 100:
                s.name = name; df = pd.concat([df, s], axis=1); success.append(name)
    except: pass

print(f"✅ {len(success)} assets")
df.index = pd.to_datetime(df.index).tz_localize(None)
df = df.sort_index().ffill()
# Daily data — no resampling, just drop weekends/holidays
daily = df[df.index.dayofweek < 5].dropna(how='all')

# Derived
for a, b, name in [('US_10Y','US_3M','YC_10Y3M'),('US_30Y','US_10Y','YC_30Y10Y'),('US_10Y','US_5Y','YC_10Y5Y')]:
    if a in daily.columns and b in daily.columns: daily[name] = daily[a] - daily[b]
if 'ETH' in daily.columns and 'BTC' in daily.columns: daily['ETH_BTC'] = daily['ETH'] / daily['BTC']
if 'IG_Bond' in daily.columns and 'HY_Bond' in daily.columns: daily['CreditSpread'] = daily['IG_Bond'] / daily['HY_Bond']

CAT_ASSETS = {}
for cat, tickers in UNIVERSE.items():
    assets = [n for n in tickers.values() if n in daily.columns]
    if cat == 'Crypto' and 'ETH_BTC' in daily.columns: assets.append('ETH_BTC')
    if assets: CAT_ASSETS[cat] = assets
curves = [c for c in ['YC_10Y3M','YC_10Y5Y','YC_30Y10Y'] if c in daily.columns]
if curves: CAT_ASSETS['Curves'] = curves
if 'Credit' in CAT_ASSETS and 'CreditSpread' in daily.columns: CAT_ASSETS['Credit'].append('CreditSpread')

# ── 2. Reusable pipeline functions ───────────────────────────

def compute_zscores(daily, lookback, vol_window):
    """Compute z-scores with given lookback and vol window"""
    zscores = pd.DataFrame(index=daily.index)
    for col in daily.columns:
        is_rate = col in RATE_ASSETS or col in CURVE_ASSETS
        if is_rate:
            zscores[col] = daily[col].diff(lookback) / (daily[col].diff(1).rolling(vol_window).std() * np.sqrt(lookback))
        else:
            zscores[col] = daily[col].pct_change(lookback) / (daily[col].pct_change(1).rolling(vol_window).std() * np.sqrt(lookback))
    return zscores

def build_features(zscores, daily):
    """Build 14-dim feature vector from z-scores"""
    scols = [c for c in SECTOR_TICKERS if c in zscores.columns]
    features = pd.DataFrame(index=daily.index)
    for cat in CAT_ORDER:
        fn = f"cat_{cat.replace(' ','_')}"
        if cat not in CAT_ASSETS: features[fn] = 0.0; continue
        cols = [a for a in CAT_ASSETS[cat] if a in zscores.columns]
        features[fn] = zscores[cols].mean(axis=1) if cols else 0.0
    cyc = [c for c in CYCLICAL if c in zscores.columns]
    dfc = [c for c in DEFENSIVE if c in zscores.columns]
    features['cyclical_vs_defensive'] = (zscores[cyc].mean(axis=1) - zscores[dfc].mean(axis=1)) if cyc and dfc else 0.0
    features['energy_vs_tech'] = (zscores['Energy_Eq'] - zscores['Tech']) if 'Energy_Eq' in zscores.columns and 'Tech' in zscores.columns else 0.0
    features['financials'] = zscores['Financials'] if 'Financials' in zscores.columns else 0.0
    features['sector_dispersion'] = zscores[scols].std(axis=1) if scols else 0.0
    def breadth(idx):
        return sum(1 for c in scols if pd.notna(zscores[c].iloc[idx]) and zscores[c].iloc[idx] > 0.8) / max(1,len(scols))
    features['sector_breadth'] = [breadth(i) for i in range(len(daily))]
    return features.dropna()

def score_regime(p):
    """Return scores dict for all regime labels"""
    eq=p.get('cat_Global_Equities',0); energy=p.get('cat_Energy',0)
    credit=p.get('cat_Credit',0); rates=p.get('cat_Rates',0)
    crypto=p.get('cat_Crypto',0); metals=p.get('cat_Metals',0)
    cyc_def=p.get('cyclical_vs_defensive',0); breadth=p.get('sector_breadth',0)
    e_vs_t=p.get('energy_vs_tech',0)
    risk=(eq+credit)/2; real=(energy+metals)/2
    s = {}
    s['REFLATION'] = max(0,eq)*1.5 + max(0,credit)*1.5 + max(0,real)*1 + max(0,crypto)*1.5 + breadth*3
    s['RECOVERY'] = max(0,eq)*1 + max(0,credit)*1.5 + max(0,crypto)*2 + max(0,0.35-breadth)*3 + max(0,metals)*1
    s['GOLDILOCKS'] = max(0,credit)*2.5 + max(0,-rates)*2 + max(0,-energy)*1 + max(0,eq)*0.5 + max(0,-cyc_def)*1
    s['OVERHEAT'] = max(0,eq)*1 + energy*2 + max(0,rates)*2 + e_vs_t*1
    s['SUPPLY SHOCK'] = energy*2 + max(0,-credit)*1.5 + max(0,rates)*1 + e_vs_t*1.5
    s['STAGFLATION'] = max(0,-eq)*2 + max(0,-credit)*2 + max(0,rates)*2 + max(0,energy)*0.5
    s['RECESSION'] = max(0,-eq)*2 + max(0,-credit)*2 + max(0,-energy)*1.5 + max(0,-rates)*1.5 + max(0,-cyc_def)*1
    s['CRISIS'] = max(0,-eq)*2 + max(0,-credit)*2 + max(0,-rates)*3 + max(0,-crypto)*1 + max(0,-real)*1
    s['DEFLATION'] = max(0,-eq)*1.5 + max(0,-real)*2 + max(0,-rates)*2.5 + max(0,-crypto)*1
    s['CONTRACTION'] = max(0,-cyc_def)*2 + max(0,0.3-breadth)*3 + max(0,-eq)*1
    return s

def label_regime(p):
    return max(score_regime(p), key=score_regime(p).get)

def stabilize_regimes(labels, probs, min_dur):
    """Absorb short regime segments into neighbors. Never touch the last segment."""
    if min_dur <= 1: return labels
    labels = labels.copy()
    changed = True
    while changed:
        changed = False
        runs = []
        i = 0
        while i < len(labels):
            j = i
            while j < len(labels) and labels[j] == labels[i]: j += 1
            runs.append((i, j, labels[i])); i = j
        for ri, (start, end, lbl) in enumerate(runs):
            if ri == len(runs) - 1: continue  # never touch last segment
            if end - start < min_dur and len(runs) > 1:
                if ri > 0 and ri < len(runs) - 1:
                    prev_lbl, next_lbl = runs[ri-1][2], runs[ri+1][2]
                    p_prev = np.mean([probs[k, prev_lbl] for k in range(start, end)])
                    p_next = np.mean([probs[k, next_lbl] for k in range(start, end)])
                    new_lbl = prev_lbl if p_prev >= p_next else next_lbl
                elif ri == 0: new_lbl = runs[ri+1][2]
                else: new_lbl = runs[ri-1][2]
                labels[start:end] = new_lbl; changed = True; break
    return labels

def run_pipeline(daily, lookback, vol_window, smooth_window, min_dur, k):
    """Full pipeline: z-scores → features → GMM → labels → output dict"""
    zscores = compute_zscores(daily, lookback, vol_window)
    features = build_features(zscores, daily)
    feat_names = list(features.columns)

    # Optional smoothing
    if smooth_window > 1:
        features_input = features.rolling(smooth_window, min_periods=1, center=True).mean()
    else:
        features_input = features

    scaler = StandardScaler()
    X = scaler.fit_transform(features_input.values)
    gmm = GaussianMixture(n_components=k, covariance_type='full', n_init=30, random_state=42, max_iter=500)
    gmm.fit(X)
    labels = gmm.predict(X)
    probs = gmm.predict_proba(X)

    # Stabilize
    labels = stabilize_regimes(labels, probs, min_dur)

    # Auto-label
    regime_profiles = {}
    labels_map = {}
    # First pass: assign labels
    for r in range(k):
        mask = labels == r
        if mask.sum() == 0: labels_map[r] = 'UNKNOWN'; continue
        profile = {fn: float(features[feat_names].iloc[np.where(mask)[0]].mean()[fn]) for fn in feat_names}
        labels_map[r] = label_regime(profile)

    # Dedup: if two clusters share a label, rename the smaller one to its 2nd best
    used = {}
    for r in sorted(range(k), key=lambda r: -np.sum(labels==r)):  # largest cluster first
        lbl = labels_map[r]
        if lbl not in used:
            used[lbl] = r
        else:
            # Find next best unused label
            mask = labels == r
            if mask.sum() == 0: continue
            profile = {fn: float(features[feat_names].iloc[np.where(mask)[0]].mean()[fn]) for fn in feat_names}
            scores = score_regime(profile)
            for alt_lbl, _ in sorted(scores.items(), key=lambda x:-x[1]):
                if alt_lbl not in used:
                    labels_map[r] = alt_lbl; used[alt_lbl] = r; break

    # Second pass: build profiles
    for r in range(k):
        mask = labels == r
        if mask.sum() == 0: continue
        profile = {fn: float(features[feat_names].iloc[np.where(mask)[0]].mean()[fn]) for fn in feat_names}
        dates = features.index[mask]
        periods = []
        if len(dates) > 0:
            sd = dates[0]
            for i in range(1, len(dates)):
                if (dates[i]-dates[i-1]).days > 5:
                    periods.append(f"{sd.strftime('%Y-%m')}->{dates[i-1].strftime('%Y-%m')}")
                    sd = dates[i]
            periods.append(f"{sd.strftime('%Y-%m')}->{dates[-1].strftime('%Y-%m')}")
        regime_profiles[r] = {'label':labels_map[r],'n_days':int(mask.sum()),'pct':round(mask.sum()/len(features)*100,1),
                              'profile':{k2:round(v,3) for k2,v in profile.items()},'periods':periods[:8]}

    # Timeline
    timeline = []
    prev_r = None
    for i in range(len(labels)):
        r = int(labels[i]); d = features.index[i].strftime('%Y-%m-%d')
        if r != prev_r:
            if timeline: timeline[-1]['end'] = features.index[i-1].strftime('%Y-%m-%d')
            timeline.append({'start':d,'end':d,'r':r,'l':labels_map[r]})
            prev_r = r
        else: timeline[-1]['end'] = d

    # Current — aggregate probability across all clusters with same label
    cur_r = int(labels[-1])
    cur_label = labels_map[cur_r]
    pl = probs[-1]
    conf = sum(pl[r] for r in range(k) if labels_map.get(r) == cur_label)
    # Runner-up: best label that isn't the current one
    label_probs = {}
    for r in range(k):
        lbl = labels_map.get(r, 'UNKNOWN')
        label_probs[lbl] = label_probs.get(lbl, 0) + pl[r]
    sorted_labels = sorted(label_probs.items(), key=lambda x:-x[1])
    runner = sorted_labels[1] if len(sorted_labels) > 1 else ('UNKNOWN', 0)

    # Assets with this model's z-scores
    current_assets = {}
    for cat in CAT_ORDER:
        if cat not in CAT_ASSETS: continue
        cd = {}
        for asset in CAT_ASSETS[cat]:
            if asset not in daily.columns: continue
            price = float(daily[asset].iloc[-1]) if pd.notna(daily[asset].iloc[-1]) else None
            z = float(zscores[asset].iloc[-1]) if asset in zscores.columns and pd.notna(zscores[asset].iloc[-1]) else None
            ir = asset in RATE_ASSETS; ic = asset in CURVE_ASSETS
            if z is not None:
                if ir: regime = 'rising' if z>0.8 else 'falling' if z<-0.8 else 'stable'
                elif ic: regime = 'steepening' if z>0.8 else 'flattening' if z<-0.8 else 'stable'
                else: regime = 'bull' if z>0.8 else 'bear' if z<-0.8 else 'sideways'
            else: regime = 'sideways'
            cd[asset] = {'regime':regime,'score':round(z,3) if z else None,'price':round(price,4) if price else None}
        if cd: current_assets[cat] = cd

    return {
        'date': features.index[-1].strftime('%Y-%m-%d'),
        'total_assets': len(success), 'days': len(features), 'n_regimes': k,
        'params': {'lookback': lookback, 'vol_window': vol_window, 'smooth': smooth_window, 'min_dur': min_dur},
        'current': {
            'regime_id':cur_r,'label':cur_label,'confidence':round(float(conf),3),
            'runner_up':{'label':runner[0],'confidence':round(float(runner[1]),3)},
            'features':{fn:round(float(features.iloc[-1][fn]),3) for fn in feat_names},
        },
        'regimes': {str(r):info for r,info in regime_profiles.items()},
        'timeline': timeline,
        'assets': current_assets,
        'cat_order': CAT_ORDER,
    }

# ── 3. Run both models ───────────────────────────────────────
print("Running MACRO model (20d/130d/smooth/k=6)...")
macro = run_pipeline(daily, lookback=20, vol_window=130, smooth_window=15, min_dur=15, k=6)
print(f"  → {macro['current']['label']} ({macro['current']['confidence']:.0%})")

print("Running TACTICAL model (10d/65d/raw/k=6)...")
tactical = run_pipeline(daily, lookback=10, vol_window=65, smooth_window=1, min_dur=5, k=6)
print(f"  → {tactical['current']['label']} ({tactical['current']['confidence']:.0%})")

output = {'macro': macro, 'tactical': tactical}

# ── 4. Generate HTML ──────────────────────────────────────────
data_str = json.dumps(output, separators=(',',':'))

FAVICON = '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'

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Regime Monitor</title>
<link rel="icon" href="data:image/png;base64,{FAVICON}">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{{--bg:#fafaf9;--s:#fff;--b:#e7e5e4;--bl:#f5f5f4;--t:#1c1917;--t2:#57534e;--t3:#a8a29e;--g:#16a34a;--gb:#f0fdf4;--gd:#bbf7d0;--r:#dc2626;--rb:#fef2f2;--rd:#fecaca;--x:#78716c;--xb:#f5f5f4;--a:#2563eb;--ab:#eff6ff;--f:'DM Sans',sans-serif;--m:'JetBrains Mono',monospace}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:var(--f);background:var(--bg);color:var(--t);font-size:13px;line-height:1.5}}
.c{{max-width:1200px;margin:0 auto;padding:16px 14px}}
header{{display:flex;justify-content:space-between;align-items:baseline;padding-bottom:12px;border-bottom:2px solid var(--t);margin-bottom:16px;flex-wrap:wrap;gap:8px}}
header h1{{font-family:var(--m);font-size:15px;font-weight:700;letter-spacing:-0.03em;text-transform:uppercase}}
header .m{{font-size:11px;color:var(--t3);font-family:var(--m)}}
.model-sw{{display:flex;gap:0;margin-bottom:16px;border-radius:8px;overflow:hidden;border:2px solid var(--t)}}
.model-sw button{{flex:1;font-family:var(--m);font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;padding:10px 20px;border:none;cursor:pointer;transition:all .15s}}
.model-sw button.on{{background:var(--t);color:var(--bg)}}
.model-sw button:not(.on){{background:var(--bg);color:var(--t3)}}
.model-sw button:not(.on):hover{{background:var(--bl)}}
.model-desc{{font-family:var(--m);font-size:9px;color:var(--t3);margin-bottom:16px;padding:6px 10px;background:var(--bl);border-radius:4px}}
.regime-hero{{padding:28px 32px;border-radius:12px;margin-bottom:20px;text-align:center}}
.regime-hero .label{{font-family:var(--m);font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.12em;opacity:.7;margin-bottom:6px}}
.regime-hero .name{{font-family:var(--f);font-size:52px;font-weight:900;letter-spacing:-0.03em;line-height:1.1;margin-bottom:8px}}
.regime-hero .conf{{font-family:var(--m);font-size:14px;font-weight:500;opacity:.8}}
.regime-hero .runner{{font-family:var(--m);font-size:11px;opacity:.5;margin-top:4px}}
.regime-hero.SUPPLY_SHOCK{{background:linear-gradient(135deg,#fff7ed,#ffedd5);color:#9a3412;border:2px solid #fb923c}}
.regime-hero.STAGFLATION{{background:linear-gradient(135deg,#faf5ff,#f3e8ff);color:#6b21a8;border:2px solid #c084fc}}
.regime-hero.GOLDILOCKS{{background:linear-gradient(135deg,#f0fdf4,#ecfdf5);color:#166534;border:2px solid #86efac}}
.regime-hero.REFLATION{{background:linear-gradient(135deg,#eff6ff,#f0f9ff);color:#1e40af;border:2px solid #93c5fd}}
.regime-hero.CRISIS{{background:linear-gradient(135deg,#1c1917,#292524);color:#fef2f2;border:2px solid #57534e}}
.regime-hero.DEFLATION{{background:linear-gradient(135deg,#f5f5f4,#e7e5e4);color:#44403c;border:2px solid #a8a29e}}
.regime-hero.OVERHEAT{{background:linear-gradient(135deg,#fffbeb,#fef3c7);color:#92400e;border:2px solid #fcd34d}}
.regime-hero.CONTRACTION{{background:linear-gradient(135deg,#faf5ff,#f3e8ff);color:#6b21a8;border:2px solid #c4b5fd}}
.regime-hero.RECESSION{{background:linear-gradient(135deg,#fef2f2,#fee2e2);color:#991b1b;border:2px solid #fca5a5}}
.regime-hero.RECOVERY{{background:linear-gradient(135deg,#ecfeff,#cffafe);color:#0e7490;border:2px solid #67e8f9}}
.regime-hero.UNKNOWN{{background:var(--bl);color:var(--t2);border:2px solid var(--b)}}
.feat-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:6px;margin-bottom:20px}}
.feat-card{{padding:8px 10px;border-radius:6px;background:var(--s);border:1px solid var(--b)}}
.feat-card .fn{{font-family:var(--m);font-size:8px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:var(--t3);margin-bottom:2px}}
.feat-card .fv{{font-family:var(--m);font-size:18px;font-weight:700}}
.feat-card .fv.pos{{color:var(--g)}}.feat-card .fv.neg{{color:var(--r)}}.feat-card .fv.neu{{color:var(--x)}}
.tl-wrap{{position:relative}}
.tl-bar{{display:flex;height:36px;border-radius:6px;overflow:hidden;margin-bottom:4px;border:1px solid var(--b)}}
.tl-seg{{position:relative;min-width:3px;display:flex;align-items:center;justify-content:center;font-family:var(--m);font-size:7px;font-weight:700;color:rgba(0,0,0,.4);overflow:hidden;cursor:pointer;transition:opacity .15s}}
.tl-seg:hover{{opacity:.8;outline:2px solid var(--t);outline-offset:-2px;z-index:2}}
.tl-tip{{display:none;position:absolute;top:-48px;left:50%;transform:translateX(-50%);background:var(--t);color:var(--s);padding:6px 10px;border-radius:6px;font-family:var(--m);font-size:10px;white-space:nowrap;pointer-events:none;z-index:10;box-shadow:0 4px 12px rgba(0,0,0,.2)}}
.tl-tip::after{{content:'';position:absolute;bottom:-6px;left:50%;transform:translateX(-50%);border-left:6px solid transparent;border-right:6px solid transparent;border-top:6px solid var(--t)}}
.tl-tip .tt-label{{font-weight:700;font-size:11px}}
.tl-tip .tt-dates{{opacity:.7;font-size:9px;margin-top:2px}}
.tl-legend{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px;font-family:var(--m);font-size:9px;color:var(--t2)}}
.tl-legend span{{display:flex;align-items:center;gap:3px}}
.tl-legend .dot{{width:10px;height:10px;border-radius:2px}}
.tl-dates{{display:flex;justify-content:space-between;font-family:var(--m);font-size:9px;color:var(--t3);margin-bottom:12px}}
.mtabs{{display:flex;gap:2px;margin-bottom:12px;background:var(--bl);border-radius:6px;padding:2px;width:fit-content}}
.mtabs button{{font-family:var(--m);font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;padding:5px 12px;border:none;border-radius:4px;background:0;color:var(--t3);cursor:pointer}}
.mtabs button.on{{background:var(--s);color:var(--t);box-shadow:0 1px 3px rgba(0,0,0,.06)}}
.cb{{margin-bottom:6px;border:1px solid var(--b);border-radius:6px;background:var(--s);overflow:hidden}}
.ch{{display:flex;justify-content:space-between;align-items:center;padding:6px 12px;cursor:pointer}}
.ch:hover{{background:var(--bl)}}
.ch h2{{font-size:11px;font-weight:700}}
.ch .st{{display:flex;align-items:center;gap:6px;font-family:var(--m);font-size:10px}}
.ch .d{{width:6px;height:6px;border-radius:50%;display:inline-block}}
.cg{{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:3px;padding:3px 8px 6px}}
.a{{display:flex;align-items:center;gap:5px;padding:4px 7px;border-radius:4px;border-left:3px solid transparent}}
.a.bu{{border-left-color:var(--g);background:var(--gb)}}.a.be{{border-left-color:var(--r);background:var(--rb)}}
.ai{{flex:1;min-width:0}}
.an{{font-family:var(--m);font-size:10px;font-weight:600}}
.ar{{display:flex;justify-content:space-between;margin-top:1px}}
.ap{{font-size:9px;color:var(--t3)}}.az{{font-family:var(--m);font-size:10px;font-weight:600}}
.al{{font-family:var(--m);font-size:8px;font-weight:700;text-transform:uppercase;padding:1px 4px;border-radius:2px}}
.al.bu{{color:var(--g);background:var(--gb)}}.al.be{{color:var(--r);background:var(--rb)}}.al.si{{color:var(--x);background:var(--xb)}}
.zb{{position:relative;width:100%;height:3px;background:var(--bl);border-radius:2px;margin-top:2px}}
.zb .md{{position:absolute;left:50%;top:0;width:1px;height:3px;background:var(--b)}}
.dt{{position:absolute;top:-1px;width:5px;height:5px;border-radius:50%;margin-left:-2px}}
.rp{{margin-bottom:12px;padding:12px;border-radius:8px;background:var(--s);border:1px solid var(--b)}}
.rp h3{{font-family:var(--m);font-size:11px;font-weight:700;margin-bottom:8px}}
.rp .bar-row{{display:flex;align-items:center;gap:6px;margin-bottom:3px}}
.rp .bar-label{{font-family:var(--m);font-size:9px;width:70px;text-align:right;color:var(--t2)}}
.rp .bar-track{{flex:1;height:6px;background:var(--bl);border-radius:3px;position:relative}}
.rp .bar-fill{{height:6px;border-radius:3px;position:absolute;top:0}}
.rp .bar-val{{font-family:var(--m);font-size:9px;width:35px;font-weight:600}}
.meth{{margin-top:16px;padding:12px;border-radius:6px;background:var(--bl);border:1px solid var(--b)}}
.meth h3{{font-family:var(--m);font-size:10px;font-weight:700;color:var(--t2);text-transform:uppercase;margin-bottom:4px}}
.meth p{{font-size:11px;color:var(--t2);line-height:1.6}}
footer{{margin-top:20px;padding-top:10px;border-top:1px solid var(--b);font-size:9px;color:var(--t3);text-align:center;font-family:var(--m)}}
.sort-ctrl{{display:flex;gap:3px;align-items:center;font-family:var(--m);font-size:9px;color:var(--t3);margin-bottom:8px}}
.sort-ctrl button{{font-family:var(--m);font-size:9px;padding:2px 8px;border:1px solid var(--b);border-radius:3px;background:var(--s);color:var(--t2);cursor:pointer}}
.sort-ctrl button.on{{background:var(--t);color:var(--s);border-color:var(--t)}}
@media(max-width:640px){{.cg{{grid-template-columns:1fr 1fr}}.regime-hero .name{{font-size:36px}}.feat-grid{{grid-template-columns:repeat(3,1fr)}}}}
</style>
</head>
<body>
<div class="c" id="app"></div>
<script>
const DATA={data_str};
const RC={{'SUPPLY SHOCK':'#ea580c','STAGFLATION':'#9333ea','GOLDILOCKS':'#16a34a','REFLATION':'#2563eb','RECOVERY':'#06b6d4','CRISIS':'#1c1917','DEFLATION':'#6b7280','OVERHEAT':'#eab308','CONTRACTION':'#be185d','RECESSION':'#dc2626','UNKNOWN':'#a8a29e','TRANSITION':'#78716c'}};
const ib=r=>r==='bull'||r==='falling'||r==='steepening';
const ie=r=>r==='bear'||r==='rising'||r==='flattening';
const rc=r=>ib(r)?'bu':ie(r)?'be':'si';
const rl=r=>({{bull:'BULL',bear:'BEAR',sideways:'SIDE',rising:'RISING',falling:'FALLING',stable:'STABLE',steepening:'STEEP',flattening:'FLAT'}}[r]||'\\u2014');
const tc=r=>ib(r)?'var(--g)':ie(r)?'var(--r)':'var(--x)';
const fP=(p,n)=>{{if(p==null)return'\\u2014';if(['ETH_BTC','JPYUSD','CreditSpread','CNYUSD','KRWUSD'].includes(n))return p.toFixed(4);if(p>10000)return p.toLocaleString('en',{{maximumFractionDigits:0}});if(p>100)return p.toLocaleString('en',{{maximumFractionDigits:1}});return p<1?p.toFixed(4):p.toFixed(2)}};
const zP=z=>{{if(z==null)return 50;return((Math.max(-3,Math.min(3,z))+3)/6)*100}};
const catLabel=n=>n.replace('cat_','').replace(/_/g,' ');
let S={{model:'macro',view:'regime',sort:'default'}};
function MD(){{return DATA[S.model]}}
function render(){{
const app=document.getElementById('app');const D=MD();const CO=D.cat_order;
let h='<header><h1>Regime Monitor</h1><div class="m">'+D.total_assets+' assets \\u00b7 '+D.days+'d \\u00b7 '+D.date+'</div></header>';
h+='<div class="model-sw">';['macro','tactical'].forEach(m=>{{h+='<button class="'+(S.model===m?'on':'')+'" onclick="U(\\'model\\',\\''+m+'\\')">'+m+'</button>'}});h+='</div>';
const p=D.params;
if(S.model==='macro')h+='<div class="model-desc">MACRO \\u2014 20d lookback \\u00b7 130d vol \\u00b7 15d smooth \\u00b7 Monthly regime shifts. Best for strategic allocation.</div>';
else h+='<div class="model-desc">TACTICAL \\u2014 10d lookback \\u00b7 65d vol \\u00b7 No smooth \\u00b7 Daily regime shifts. Best for timing & hedging.</div>';
const cur=D.current;const heroClass=cur.label.replace(/ /g,'_');
h+='<div class="regime-hero '+heroClass+'"><div class="label">Current '+S.model.toUpperCase()+' Regime</div><div class="name">'+cur.label+'</div><div class="conf">'+Math.round(cur.confidence*100)+'% confidence</div><div class="runner">Runner-up: '+cur.runner_up.label+' ('+Math.round(cur.runner_up.confidence*100)+'%)</div></div>';
const feats=cur.features;const fo=['cat_Energy','cat_Global_Equities','cat_Credit','cat_Rates','cat_Crypto','cat_Metals','cat_Currencies','cyclical_vs_defensive','energy_vs_tech','financials','sector_breadth','sector_dispersion'];
h+='<div class="feat-grid">';fo.forEach(fn=>{{const v=feats[fn];if(v==null)return;const cls=v>0.3?'pos':v<-0.3?'neg':'neu';h+='<div class="feat-card"><div class="fn">'+catLabel(fn)+'</div><div class="fv '+cls+'">'+(v>0?'+':'')+v.toFixed(2)+'</div></div>'}});h+='</div>';
h+=rTimeline(D);
h+='<div class="mtabs">';['regime','assets','method'].forEach(v=>{{h+='<button class="'+(S.view===v?'on':'')+'" onclick="U(\\'view\\',\\''+v+'\\')">'+v+'</button>'}});h+='</div>';
if(S.view==='regime')h+=rRegimes(D);else if(S.view==='assets')h+=rAssets(D);else h+=rMethod(D);
h+='<footer>14-dim feature vector \\u00b7 GMM (k='+D.n_regimes+') \\u00b7 Dual model (MACRO+TACTICAL) \\u00b7 Daily \\u00b7 Auto-updated</footer>';
app.innerHTML=h}}
function showTip(el){{const tip=document.getElementById('tl-tip');if(!tip)return;const r=el.getBoundingClientRect();const p=el.parentElement.getBoundingClientRect();tip.innerHTML='<div class="tt-label">'+el.dataset.label+'</div><div class="tt-dates">'+el.dataset.start+' \\u2192 '+el.dataset.end+'</div>';tip.style.display='block';tip.style.left=(r.left+r.width/2-p.left)+'px';tip.style.top='-48px'}}
function hideTip(){{const tip=document.getElementById('tl-tip');if(tip)tip.style.display='none'}}
function rTimeline(D){{const tl=D.timeline;if(!tl||!tl.length)return'';const t0=new Date(tl[0].start).getTime();const t1=new Date(tl[tl.length-1].end).getTime()+86400000*7;const span=t1-t0||1;let h='<div class="tl-wrap" style="position:relative"><div id="tl-tip" class="tl-tip"></div><div class="tl-bar">';tl.forEach((seg,i)=>{{const s=new Date(seg.start).getTime();const e=new Date(seg.end).getTime()+86400000*7;const w=Math.max(0.5,((e-s)/span)*100);const col=RC[seg.l]||'#a8a29e';const ic=i===tl.length-1;h+='<div class="tl-seg" style="width:'+w+'%;background:'+col+(ic?';box-shadow:inset 0 0 0 2px rgba(0,0,0,.3)':'')+'" data-label="'+seg.l+'" data-start="'+seg.start+'" data-end="'+seg.end+'" onmouseenter="showTip(this)" onmouseleave="hideTip()"></div>'}});h+='</div></div>';h+='<div class="tl-dates"><span>'+tl[0].start.substring(0,7)+'</span><span>'+tl[tl.length-1].end.substring(0,7)+'</span></div>';const seen=new Set();h+='<div class="tl-legend">';tl.forEach(seg=>{{if(!seen.has(seg.l)){{seen.add(seg.l);h+='<span><span class="dot" style="background:'+(RC[seg.l]||'#a8a29e')+'"></span>'+seg.l+'</span>'}}}});h+='</div>';return h}}
function rRegimes(D){{let h='';for(let r=0;r<D.n_regimes;r++){{const info=D.regimes[r];if(!info)continue;const col=RC[info.label]||'#a8a29e';const ic=r===D.current.regime_id;h+='<div class="rp" style="'+(ic?'border:2px solid '+col:'')+'"><h3 style="color:'+col+'">'+(ic?'\\u25b6 ':'')+info.label+' \\u2014 '+info.n_days+'d ('+info.pct+'%)</h3>';h+='<div style="font-size:10px;color:var(--t3);margin-bottom:8px">'+info.periods.slice(0,5).join(', ')+'</div>';const p=info.profile;['cat_Energy','cat_Global_Equities','cat_Credit','cat_Rates','cat_Crypto','cat_Metals','cyclical_vs_defensive','energy_vs_tech'].forEach(fn=>{{const v=p[fn]||0;const pct=Math.min(100,Math.abs(v)*30);const col2=v>0.2?'var(--g)':v<-0.2?'var(--r)':'var(--x)';const left=v>=0?'50%':(50-pct)+'%';h+='<div class="bar-row"><span class="bar-label">'+catLabel(fn)+'</span><div class="bar-track"><div class="bar-fill" style="left:'+left+'%;width:'+pct+'%;background:'+col2+'"></div><div style="position:absolute;left:50%;top:0;width:1px;height:6px;background:var(--b)"></div></div><span class="bar-val" style="color:'+col2+'">'+(v>0?'+':'')+v.toFixed(2)+'</span></div>'}});h+='</div>'}}return h}}
function rAssets(D){{const cats=D.assets;const CO=D.cat_order;let h='<div class="sort-ctrl">Sort: '+['default','z-desc','z-asc','alpha','regime'].map(s=>'<button class="'+(S.sort===s?'on':'')+'" onclick="U(\\'sort\\',\\''+s+'\\')">'+({{'z-desc':'z\\u2193','z-asc':'z\\u2191'}}[s]||s)+'</button>').join('')+'</div>';CO.forEach(k=>{{const assets=cats[k];if(!assets)return;let entries=Object.entries(assets);if(S.sort==='z-asc')entries.sort((a,b)=>(a[1].score||0)-(b[1].score||0));else if(S.sort==='z-desc')entries.sort((a,b)=>(b[1].score||0)-(a[1].score||0));else if(S.sort==='alpha')entries.sort((a,b)=>a[0].localeCompare(b[0]));else if(S.sort==='regime'){{const ro=r=>ib(r)?0:ie(r)?2:1;entries.sort((a,b)=>ro(a[1].regime)-ro(b[1].regime))}}const nb=entries.filter(([,a])=>ib(a.regime)).length,nr=entries.filter(([,a])=>ie(a.regime)).length,ns=entries.length-nb-nr;h+='<div class="cb"><div class="ch"><h2>'+k+'</h2><div class="st">';if(nb)h+='<span><span class="d" style="background:var(--g)"></span>'+nb+'</span>';if(ns)h+='<span><span class="d" style="background:var(--x)"></span>'+ns+'</span>';if(nr)h+='<span><span class="d" style="background:var(--r)"></span>'+nr+'</span>';h+='</div></div><div class="cg">';entries.forEach(([n,d])=>{{const c=rc(d.regime),z=d.score,zc=tc(d.regime);h+='<div class="a '+c+'"><div class="ai"><div style="display:flex;justify-content:space-between;align-items:center"><span class="an">'+n+'</span><span class="al '+c+'">'+rl(d.regime)+'</span></div><div class="ar"><span class="ap">'+fP(d.price,n)+'</span><span class="az" style="color:'+zc+'">'+(z!=null?(z>0?'+':'')+z.toFixed(2):'\\u2014')+'</span></div><div class="zb"><div class="md"></div>'+(z!=null?'<div class="dt" style="left:'+zP(z)+'%;background:'+zc+'"></div>':'')+'</div></div></div>'}});h+='</div></div>'}});return h}}
function rMethod(D){{const p=D.params;return'<div class="meth"><h3>'+S.model.toUpperCase()+' Model Configuration</h3><p><b>Lookback:</b> '+p.lookback+'d returns<br><b>Vol Window:</b> '+p.vol_window+'d rolling std<br><b>Smoothing:</b> '+(p.smooth>1?p.smooth+'d rolling mean':'None (raw)')+'<br><b>Min Duration:</b> '+(p.min_dur>1?p.min_dur+'d':'None')+'<br><b>Clusters:</b> GMM k='+D.n_regimes+'<br><br><b>Feature Vector (14-dim):</b> 9 asset class z-scores + 5 sectoral internals (cyclical vs defensive, energy vs tech, financials, dispersion, breadth).<br><br>'+(S.model==='macro'?'<b>Use Case:</b> Strategic allocation, portfolio construction, risk budgeting. Identifies multi-month macro environments.':'<b>Use Case:</b> Tactical hedging, timing entries/exits, event response. Captures daily regime shifts and V-shaped reversals.')+'</p></div>'}}
function U(k,v){{S[k]=v;render()}}
render();
</script>
</body>
</html>'''

with open('index.html', 'w') as f:
    f.write(html)

print(f"✅ index.html: {len(html)/1024:.1f} KB")
