"""
Regime Monitor - 4+2 Investment Clock + Market Internals
REGIME: Growth x Inflation 2-axis, STRATEGIC + TACTICAL
INTERNALS: 40 thematic baskets, sectoral relative strength
"""
import pandas as pd
import numpy as np
import yfinance as yf
import json, warnings
from datetime import datetime
warnings.filterwarnings('ignore')

END = datetime.now().strftime('%Y-%m-%d')
START = '2018-01-01'

# ═══════════════ REGIME UNIVERSE ═══════════════
UNIVERSE = {
    'Crypto': {'BTC-USD':'BTC','ETH-USD':'ETH','SOL-USD':'SOL'},
    'Metals': {'GC=F':'Gold','SI=F':'Silver','HG=F':'Copper','PA=F':'Palladium','PL=F':'Platinum','ALI=F':'Aluminum'},
    'Energy': {'CL=F':'WTI','BZ=F':'Brent','NG=F':'NatGas','RB=F':'Gasoline','HO=F':'HeatingOil'},
    'US Sectors': {'XLK':'Tech','XLF':'Financials','XLE':'Energy_Eq','XLV':'Healthcare','XLI':'Industrials','XLP':'Staples','XLY':'Discretionary','XLU':'Utilities','XLRE':'RealEstate','XLB':'Materials','XLC':'CommSvc'},
    'Global Equities': {'^GSPC':'US_SP500','^IXIC':'US_Nasdaq','^STOXX50E':'EU_Stoxx50','EWJ':'Japan','EWY':'Korea','EWT':'Taiwan','FXI':'China','EWG':'Germany','EWU':'UK','EWZ':'Brazil','INDA':'India','EEM':'EM_Broad','EWA':'Australia','EWC':'Canada','EWS':'Singapore','THD':'Thailand','EWW':'Mexico','EIDO':'Indonesia','VNM':'Vietnam','EZA':'SouthAfrica','QAT':'Qatar','KSA':'SaudiArabia','TUR':'Turkey'},
    'Rates': {'^IRX':'US_3M','^FVX':'US_5Y','^TNX':'US_10Y','^TYX':'US_30Y'},
    'Currencies': {'EURUSD=X':'EURUSD','JPYUSD=X':'JPYUSD','GBPUSD=X':'GBPUSD','CNYUSD=X':'CNYUSD','AUDUSD=X':'AUDUSD','CHFUSD=X':'CHFUSD','KRWUSD=X':'KRWUSD','SGDUSD=X':'SGDUSD'},
    'Credit': {'HYG':'HY_Bond','LQD':'IG_Bond','JNK':'HY_Junk','BKLN':'BankLoans','EMB':'EM_Bond'},
}
RATE_ASSETS = {'US_3M','US_5Y','US_10Y','US_30Y'}
CURVE_ASSETS = {'YC_10Y3M','YC_10Y5Y','YC_30Y10Y'}
SECTORS = ['Tech','Financials','Energy_Eq','Healthcare','Industrials','Staples','Discretionary','Utilities','RealEstate','Materials','CommSvc']
CYCLICAL = ['Discretionary','Industrials','Financials','Materials']
DEFENSIVE = ['Staples','Utilities','Healthcare','RealEstate']
CAT_ORDER = ["Crypto","Metals","Energy","US Sectors","Global Equities","Rates","Curves","Currencies","Credit"]

# ═══════════════ INTERNALS BASKETS ═══════════════
BASKETS = {
    'Staffing':{'t':['RHI','MAN','KFRC','HSII','NSP'],'cat':'Labor'},
    'Homebuilders':{'t':['DHI','LEN','PHM','TOL','KBH','NVR','MDC','TMHC'],'cat':'Rate Sensitive'},
    'Building Materials':{'t':['BLDR','SHW','MLM','VMC','AZEK'],'cat':'Rate Sensitive'},
    'Regional Banks':{'t':['ZION','KEY','HBAN','RF','CFG','MTB','FHN','EWBC','WAL'],'cat':'Credit Cycle'},
    'Railroads':{'t':['UNP','CSX','NSC','CP'],'cat':'Transport'},
    'Dry Bulk Shipping':{'t':['SBLK','GOGL','GNK','EGLE','DSX'],'cat':'Global Trade'},
    'Restaurants QSR':{'t':['MCD','SBUX','YUM','DPZ','CMG','WING','CAVA'],'cat':'Consumer'},
    'Leisure Travel':{'t':['MAR','HLT','BKNG','EXPE','RCL','CCL','NCLH'],'cat':'Consumer'},
    'Airlines':{'t':['DAL','UAL','LUV','JBLU','AAL'],'cat':'Transport'},
    'Specialty Chemicals':{'t':['DOW','LYB','CE','DD','EMN','APD'],'cat':'Industrial'},
    'Packaging':{'t':['BLL','CCK','SEE','AMCR','IP','PKG'],'cat':'Industrial'},
    'Medical Devices':{'t':['MDT','SYK','BSX','EW','ISRG','ABT'],'cat':'Healthcare'},
    'P&C Insurers':{'t':['PGR','ALL','TRV','CB','AIG'],'cat':'Financials'},
    'US Utilities':{'t':['NEE','DUK','SO','D','AEP','EXC','SRE'],'cat':'Defensive'},
    'Tobacco Sin':{'t':['PM','MO','BTI'],'cat':'Defensive'},
    'Waste Mgmt':{'t':['WM','RSG','CLH','CWST'],'cat':'Industrial'},
    'Timber Lumber':{'t':['WY','RYN','PCH'],'cat':'Rate Sensitive'},
    'Analog Semis':{'t':['TXN','ADI','ON','MCHP','NXPI'],'cat':'Inventory Cycle'},
    'Electrical Grid':{'t':['ETN','POWL','HWM','HUBB'],'cat':'Infra'},
    'Capital Goods':{'t':['CAT','DE','ETN','ROK','EMR','ITW','PH'],'cat':'Capex'},
    'Software SaaS':{'t':['CRM','NOW','PANW','DDOG','ZS','CRWD','WDAY'],'cat':'Tech Growth'},
    'Data Center AI':{'t':['NVDA','AVGO','ANET','VRT','DELL','SMCI','EQIX'],'cat':'AI Capex'},
    'GLP1 Obesity':{'t':['LLY','NVO','HIMS','VKTX','AMGN'],'cat':'Healthcare'},
    'Autos':{'t':['GM','F','STLA'],'cat':'Consumer'},
    'Auto Parts':{'t':['APTV','BWA','LEA','ALV'],'cat':'Manufacturing'},
    'Ag Fertilizers':{'t':['MOS','NTR','CF','FMC'],'cat':'Inflation'},
    'Ag Equipment':{'t':['DE','AGCO','CNHI'],'cat':'Ag Cycle'},
    'Steel Metals':{'t':['NUE','STLD','X','CLF','RS'],'cat':'Industrial'},
    'Cybersecurity':{'t':['PANW','CRWD','ZS','FTNT','NET'],'cat':'Security'},
    'Gold Miners':{'t':['NEM','GOLD','AEM','FNV','WPM','GFI'],'cat':'Fear'},
    'Defense':{'t':['LMT','RTX','NOC','GD','LHX','HII'],'cat':'Geopolitics'},
    'Tankers':{'t':['STNG','FRO','INSW','DHT'],'cat':'Geopolitics'},
    'Energy E&P':{'t':['XOM','CVX','OXY','COP','SLB'],'cat':'Energy'},
    'Nuclear SMR':{'t':['CEG','VST','CCJ','SMR','OKLO'],'cat':'Energy'},
    'Robotics':{'t':['ISRG','ROK','TER','IRBT'],'cat':'Automation'},
    'China ADRs':{'t':['BABA','JD','PDD','BIDU','NTES'],'cat':'China'},
    'Clean Energy':{'t':['ENPH','FSLR','SEDG','RUN'],'cat':'Policy'},
    'Luxury':{'t':['RL','CPRI','TPR'],'cat':'Wealth Effect'},
    'DC REITs':{'t':['EQIX','DLR','AMT'],'cat':'AI Infra'},
    'Residential REITs':{'t':['AVB','EQR','MAA','INVH'],'cat':'Rate Sensitive'},
}

BASKET_CAT_ORDER = ['Labor','Rate Sensitive','Credit Cycle','Transport','Global Trade','Consumer',
                     'Industrial','Manufacturing','Inventory Cycle','Capex','Infra','Financials',
                     'Healthcare','Inflation','Ag Cycle','Energy','Geopolitics','Security',
                     'Tech Growth','AI Capex','AI Infra','Automation','China','Policy','Wealth Effect',
                     'Defensive','Fear']

# ═══════════════ 1. DOWNLOAD ALL ═══════════════
print(f"Regime Monitor: {START} -> {END}")

# Combine all tickers: regime + internals
regime_tickers = {}
for cat, tickers in UNIVERSE.items():
    for t, n in tickers.items():
        regime_tickers[t] = n

internal_tickers = set()
for bname, binfo in BASKETS.items():
    for t in binfo['t']:
        internal_tickers.add(t)
internal_tickers.add('SPY')

# Merge (internals tickers use themselves as names)
all_dl = list(set(list(regime_tickers.keys()) + list(internal_tickers)))
print(f"Downloading {len(all_dl)} tickers...")
raw = yf.download(all_dl, start=START, end=END, progress=False, group_by='ticker')

# Parse regime assets
df_regime = pd.DataFrame()
success = []
for t, n in regime_tickers.items():
    try:
        if t in raw.columns.get_level_values(0):
            s = raw[t]['Close'].squeeze()
            if isinstance(s, pd.Series) and s.notna().sum() > 100:
                s.name = n; df_regime = pd.concat([df_regime, s], axis=1); success.append(n)
    except: pass

# Parse internals assets
df_int = pd.DataFrame()
int_ok = []
for t in sorted(internal_tickers):
    try:
        if t in raw.columns.get_level_values(0):
            s = raw[t]['Close'].squeeze()
            if isinstance(s, pd.Series) and s.notna().sum() > 100:
                s.name = t; df_int = pd.concat([df_int, s], axis=1); int_ok.append(t)
    except: pass

print(f"OK regime={len(success)} internals={len(int_ok)}")

# Prepare daily data
for dframe in [df_regime, df_int]:
    dframe.index = pd.to_datetime(dframe.index).tz_localize(None)

df_regime = df_regime.sort_index().ffill()
daily = df_regime[df_regime.index.dayofweek < 5].dropna(how='all')

df_int = df_int.sort_index().ffill()
daily_int = df_int[df_int.index.dayofweek < 5].dropna(how='all')

# Derived series for regime
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

# ═══════════════ 2. REGIME PIPELINE ═══════════════
def run_model(daily, lookback, vol_window, smooth, min_dur):
    zscores = pd.DataFrame(index=daily.index)
    for col in daily.columns:
        ir = col in RATE_ASSETS or col in CURVE_ASSETS
        if ir: zscores[col] = daily[col].diff(lookback) / (daily[col].diff(1).rolling(vol_window).std() * np.sqrt(lookback))
        else: zscores[col] = daily[col].pct_change(lookback) / (daily[col].pct_change(1).rolling(vol_window).std() * np.sqrt(lookback))
    scols = [c for c in SECTORS if c in zscores.columns]
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
    def breadth(i):
        return sum(1 for c in scols if pd.notna(zscores[c].iloc[i]) and zscores[c].iloc[i] > 0.8) / max(1,len(scols))
    features['sector_breadth'] = [breadth(i) for i in range(len(daily))]
    features = features.dropna()
    feat_names = list(features.columns)
    fs = features.rolling(smooth, min_periods=1, center=True).mean() if smooth > 1 else features
    growth = (fs['cat_Global_Equities'] + fs['cat_Credit'] + fs['cyclical_vs_defensive']) / 3
    inflation = (fs['cat_Energy'] + fs['cat_Rates'] + fs['energy_vs_tech']) / 3
    labels = []
    for i in range(len(fs)):
        g, inf = growth.iloc[i], inflation.iloc[i]
        eq, cr = fs['cat_Global_Equities'].iloc[i], fs['cat_Credit'].iloc[i]
        cy, me = fs['cat_Crypto'].iloc[i], fs['cat_Metals'].iloc[i]
        en, et = fs['cat_Energy'].iloc[i], fs['energy_vs_tech'].iloc[i]
        if (eq + cr + cy + me) / 4 < -1.0: labels.append('CRISIS'); continue
        if en > 1.0 and et > 1.0: labels.append('SUPPLY SHOCK'); continue
        if g >= 0 and inf >= 0: labels.append('OVERHEAT')
        elif g >= 0 and inf < 0: labels.append('GOLDILOCKS')
        elif g < 0 and inf >= 0: labels.append('STAGFLATION')
        else: labels.append('RECESSION')
    labels = np.array(labels)
    if min_dur > 1:
        changed = True
        while changed:
            changed = False
            runs = []; i = 0
            while i < len(labels):
                j = i
                while j < len(labels) and labels[j] == labels[i]: j += 1
                runs.append((i, j, labels[i])); i = j
            for ri, (s, e, lbl) in enumerate(runs):
                if ri == len(runs) - 1: continue
                if e - s < min_dur and len(runs) > 1:
                    if ri > 0 and ri < len(runs) - 1:
                        pl = runs[ri-1][1] - runs[ri-1][0]; nl = runs[ri+1][1] - runs[ri+1][0]
                        new = runs[ri-1][2] if pl >= nl else runs[ri+1][2]
                    elif ri == 0: new = runs[ri+1][2]
                    else: new = runs[ri-1][2]
                    labels[s:e] = new; changed = True; break
    unique = sorted(set(labels))
    regimes = {}
    for idx, lbl in enumerate(unique):
        mask = labels == lbl; n = mask.sum()
        profile = {fn: float(features.iloc[np.where(mask)[0]][fn].mean()) for fn in feat_names}
        dates = features.index[mask]; periods = []
        if len(dates) > 0:
            sd = dates[0]
            for ii in range(1, len(dates)):
                if (dates[ii]-dates[ii-1]).days > 5:
                    periods.append(f"{sd.strftime('%Y-%m-%d')}->{dates[ii-1].strftime('%Y-%m-%d')}"); sd = dates[ii]
            periods.append(f"{sd.strftime('%Y-%m-%d')}->{dates[-1].strftime('%Y-%m-%d')}")
        regimes[str(idx)] = {'label':lbl,'n_days':int(n),'pct':round(n/len(features)*100,1),
            'profile':{k:round(v,3) for k,v in profile.items()},'periods':periods[:10]}
    timeline = []; prev = None
    for i in range(len(labels)):
        lbl = labels[i]; d = features.index[i].strftime('%Y-%m-%d')
        if lbl != prev:
            if timeline: timeline[-1]['end'] = features.index[i-1].strftime('%Y-%m-%d')
            timeline.append({'start':d,'end':d,'l':lbl}); prev = lbl
        else: timeline[-1]['end'] = d
    assets_out = {}
    for cat in CAT_ORDER:
        if cat not in CAT_ASSETS: continue
        cd = {}
        for asset in CAT_ASSETS[cat]:
            if asset not in daily.columns: continue
            price = float(daily[asset].iloc[-1]) if pd.notna(daily[asset].iloc[-1]) else None
            z = float(zscores[asset].iloc[-1]) if asset in zscores.columns and pd.notna(zscores[asset].iloc[-1]) else None
            ir2 = asset in RATE_ASSETS; ic2 = asset in CURVE_ASSETS
            if z is not None:
                if ir2: regime = 'rising' if z>0.8 else 'falling' if z<-0.8 else 'stable'
                elif ic2: regime = 'steepening' if z>0.8 else 'flattening' if z<-0.8 else 'stable'
                else: regime = 'bull' if z>0.8 else 'bear' if z<-0.8 else 'sideways'
            else: regime = 'sideways'
            cd[asset] = {'regime':regime,'score':round(z,3) if z else None,'price':round(price,4) if price else None}
        if cd: assets_out[cat] = cd
    return {'date':features.index[-1].strftime('%Y-%m-%d'),'total_assets':len(success),'days':len(features),'n_regimes':len(unique),
            'params':{'lookback':lookback,'vol_window':vol_window,'smooth':smooth,'min_dur':min_dur},
            'current':{'label':labels[-1],'growth':round(float(growth.iloc[-1]),3),'inflation':round(float(inflation.iloc[-1]),3),
                'features':{fn:round(float(features.iloc[-1][fn]),3) for fn in feat_names}},
            'regimes':regimes,'timeline':timeline,'assets':assets_out,'cat_order':CAT_ORDER}

print("STRATEGIC (20d/130d/15d smooth)...")
strategic = run_model(daily, 20, 130, 15, 15)
print(f"  -> {strategic['current']['label']} G={strategic['current']['growth']:+.2f} I={strategic['current']['inflation']:+.2f}")
print("TACTICAL (10d/65d/raw)...")
tactical = run_model(daily, 10, 65, 1, 5)
print(f"  -> {tactical['current']['label']} G={tactical['current']['growth']:+.2f} I={tactical['current']['inflation']:+.2f}")

# ═══════════════ 3. INTERNALS PIPELINE ═══════════════
print("INTERNALS (20d z-scores, SPY relative)...")
lookback_int = 20
vol_int = 130
zscores_int = pd.DataFrame(index=daily_int.index)
for col in daily_int.columns:
    zscores_int[col] = daily_int[col].pct_change(lookback_int) / (daily_int[col].pct_change(1).rolling(vol_int).std() * np.sqrt(lookback_int))
zscores_int = zscores_int.dropna(how='all')

spy_z = zscores_int['SPY'].iloc[-1] if 'SPY' in zscores_int.columns and pd.notna(zscores_int['SPY'].iloc[-1]) else 0.0

baskets_out = []
for bname, binfo in BASKETS.items():
    tickers = [t for t in binfo['t'] if t in zscores_int.columns]
    if not tickers: continue
    scores = [float(zscores_int[t].iloc[-1]) for t in tickers if pd.notna(zscores_int[t].iloc[-1])]
    if not scores: continue
    avg_z = sum(scores) / len(scores)
    rel_z = avg_z - float(spy_z)
    # Per-stock detail
    stocks = []
    for t in tickers:
        z = float(zscores_int[t].iloc[-1]) if pd.notna(zscores_int[t].iloc[-1]) else None
        p = float(daily_int[t].iloc[-1]) if t in daily_int.columns and pd.notna(daily_int[t].iloc[-1]) else None
        if z is not None:
            stocks.append({'t':t,'z':round(z,2),'rz':round(z - float(spy_z),2),'p':round(p,2) if p else None})
    baskets_out.append({
        'name': bname, 'cat': binfo['cat'],
        'z': round(avg_z, 2), 'rel': round(rel_z, 2),
        'n': len(tickers), 'n_ok': len(scores),
        'stocks': sorted(stocks, key=lambda x: -x['rz'])
    })

baskets_out.sort(key=lambda x: -x['rel'])
spy_z_val = round(float(spy_z), 2)
print(f"  -> {len(baskets_out)} baskets, SPY z={spy_z_val}")
print(f"  Top 3: {', '.join(b['name']+' '+str(b['rel']) for b in baskets_out[:3])}")
print(f"  Bot 3: {', '.join(b['name']+' '+str(b['rel']) for b in baskets_out[-3:])}")

# ═══════════════ 4. BUILD OUTPUT ═══════════════
data = {
    'strategic': strategic,
    'tactical': tactical,
    'internals': {
        'date': zscores_int.index[-1].strftime('%Y-%m-%d'),
        'spy_z': spy_z_val,
        'params': {'lookback': lookback_int, 'vol_window': vol_int},
        'baskets': baskets_out,
        'cat_order': BASKET_CAT_ORDER,
    }
}
data_str = json.dumps(data, separators=(',',':'))

# ═══════════════ 5. HTML ═══════════════
FAVICON = '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'

html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Regime Monitor</title>
<link rel="icon" href="data:image/png;base64,{FAVICON}">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{{--bg:#fafaf9;--s:#fff;--b:#e7e5e4;--bl:#f5f5f4;--t:#1c1917;--t2:#57534e;--t3:#a8a29e;--g:#16a34a;--gb:#f0fdf4;--r:#dc2626;--rb:#fef2f2;--x:#78716c;--xb:#f5f5f4;--f:'DM Sans',sans-serif;--m:'JetBrains Mono',monospace}}
*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:var(--f);background:var(--bg);color:var(--t);font-size:13px;line-height:1.5}}
.c{{max-width:1200px;margin:0 auto;padding:16px 14px}}
header{{display:flex;justify-content:space-between;align-items:baseline;padding-bottom:12px;border-bottom:2px solid var(--t);margin-bottom:16px;flex-wrap:wrap;gap:8px}}
header h1{{font-family:var(--m);font-size:15px;font-weight:700;letter-spacing:-0.03em;text-transform:uppercase}}
header .m{{font-size:11px;color:var(--t3);font-family:var(--m)}}
.topnav{{display:flex;gap:0;margin-bottom:16px;border-radius:8px;overflow:hidden;border:2px solid var(--t)}}
.topnav button{{flex:1;font-family:var(--m);font-size:13px;font-weight:800;text-transform:uppercase;letter-spacing:.1em;padding:12px 20px;border:none;cursor:pointer;transition:all .15s}}
.topnav button.on{{background:var(--t);color:var(--bg)}}.topnav button:not(.on){{background:var(--bg);color:var(--t3)}}.topnav button:not(.on):hover{{background:var(--bl)}}
.msw{{display:flex;gap:0;margin-bottom:12px;border-radius:6px;overflow:hidden;border:1px solid var(--b)}}
.msw button{{flex:1;font-family:var(--m);font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;padding:8px 16px;border:none;cursor:pointer}}
.msw button.on{{background:var(--t);color:var(--bg)}}.msw button:not(.on){{background:var(--s);color:var(--t3)}}
.mdesc{{font-family:var(--m);font-size:9px;color:var(--t3);margin-bottom:16px;padding:6px 10px;background:var(--bl);border-radius:4px}}
.hero{{padding:28px 32px;border-radius:12px;margin-bottom:20px;text-align:center}}
.hero .lb{{font-family:var(--m);font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.12em;opacity:.7;margin-bottom:6px}}
.hero .nm{{font-family:var(--f);font-size:52px;font-weight:900;letter-spacing:-0.03em;line-height:1.1;margin-bottom:8px}}
.hero .cf{{font-family:var(--m);font-size:13px;font-weight:500;opacity:.8}}
.hero.OVERHEAT{{background:linear-gradient(135deg,#fffbeb,#fef3c7);color:#92400e;border:2px solid #fcd34d}}
.hero.GOLDILOCKS{{background:linear-gradient(135deg,#f0fdf4,#ecfdf5);color:#166534;border:2px solid #86efac}}
.hero.STAGFLATION{{background:linear-gradient(135deg,#faf5ff,#f3e8ff);color:#6b21a8;border:2px solid #c084fc}}
.hero.RECESSION{{background:linear-gradient(135deg,#fef2f2,#fee2e2);color:#991b1b;border:2px solid #fca5a5}}
.hero.CRISIS{{background:linear-gradient(135deg,#1c1917,#292524);color:#fef2f2;border:2px solid #57534e}}
.hero.SUPPLY_SHOCK{{background:linear-gradient(135deg,#fff7ed,#ffedd5);color:#9a3412;border:2px solid #fb923c}}
.axes{{display:flex;gap:20px;margin-bottom:20px;font-family:var(--m)}}.ax{{flex:1;padding:12px 16px;border-radius:8px;background:var(--s);border:1px solid var(--b)}}.ax .al{{font-size:9px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:var(--t3);margin-bottom:4px}}.ax .av{{font-size:28px;font-weight:800}}.ax .av.pos{{color:var(--g)}}.ax .av.neg{{color:var(--r)}}.ax .av.neu{{color:var(--x)}}
.fg{{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:6px;margin-bottom:20px}}.fc{{padding:8px 10px;border-radius:6px;background:var(--s);border:1px solid var(--b)}}.fc .fn{{font-family:var(--m);font-size:8px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:var(--t3);margin-bottom:2px}}.fc .fv{{font-family:var(--m);font-size:18px;font-weight:700}}.fc .fv.pos{{color:var(--g)}}.fc .fv.neg{{color:var(--r)}}.fc .fv.neu{{color:var(--x)}}
.tw{{position:relative}}.tb{{display:flex;height:36px;border-radius:6px;overflow:hidden;margin-bottom:4px;border:1px solid var(--b)}}.ts{{min-width:3px;cursor:pointer;transition:opacity .15s}}.ts:hover{{opacity:.8;outline:2px solid var(--t);outline-offset:-2px;z-index:2}}.tt{{display:none;position:absolute;top:-48px;left:50%;transform:translateX(-50%);background:var(--t);color:var(--s);padding:6px 10px;border-radius:6px;font-family:var(--m);font-size:10px;white-space:nowrap;pointer-events:none;z-index:10;box-shadow:0 4px 12px rgba(0,0,0,.2)}}.tt::after{{content:'';position:absolute;bottom:-6px;left:50%;transform:translateX(-50%);border-left:6px solid transparent;border-right:6px solid transparent;border-top:6px solid var(--t)}}.tleg{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px;font-family:var(--m);font-size:9px;color:var(--t2)}}.tleg span{{display:flex;align-items:center;gap:3px}}.tleg .dot{{width:10px;height:10px;border-radius:2px}}.td{{display:flex;justify-content:space-between;font-family:var(--m);font-size:9px;color:var(--t3);margin-bottom:12px}}
.mt{{display:flex;gap:2px;margin-bottom:12px;background:var(--bl);border-radius:6px;padding:2px;width:fit-content}}.mt button{{font-family:var(--m);font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;padding:5px 12px;border:none;border-radius:4px;background:0;color:var(--t3);cursor:pointer}}.mt button.on{{background:var(--s);color:var(--t);box-shadow:0 1px 3px rgba(0,0,0,.06)}}
.cb{{margin-bottom:6px;border:1px solid var(--b);border-radius:6px;background:var(--s);overflow:hidden}}.ch{{display:flex;justify-content:space-between;align-items:center;padding:6px 12px;cursor:pointer}}.ch:hover{{background:var(--bl)}}.ch h2{{font-size:11px;font-weight:700}}.ch .st{{display:flex;align-items:center;gap:6px;font-family:var(--m);font-size:10px}}.ch .d{{width:6px;height:6px;border-radius:50%;display:inline-block}}.cg{{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:3px;padding:3px 8px 6px}}.a{{display:flex;align-items:center;gap:5px;padding:4px 7px;border-radius:4px;border-left:3px solid transparent}}.a.bu{{border-left-color:var(--g);background:var(--gb)}}.a.be{{border-left-color:var(--r);background:var(--rb)}}.ai{{flex:1;min-width:0}}.an{{font-family:var(--m);font-size:10px;font-weight:600}}.ar{{display:flex;justify-content:space-between;margin-top:1px}}.ap{{font-size:9px;color:var(--t3)}}.az{{font-family:var(--m);font-size:10px;font-weight:600}}.al2{{font-family:var(--m);font-size:8px;font-weight:700;text-transform:uppercase;padding:1px 4px;border-radius:2px}}.al2.bu{{color:var(--g);background:var(--gb)}}.al2.be{{color:var(--r);background:var(--rb)}}.al2.si{{color:var(--x);background:var(--xb)}}.zb{{position:relative;width:100%;height:3px;background:var(--bl);border-radius:2px;margin-top:2px}}.zb .md{{position:absolute;left:50%;top:0;width:1px;height:3px;background:var(--b)}}.dt{{position:absolute;top:-1px;width:5px;height:5px;border-radius:50%;margin-left:-2px}}
.rp{{margin-bottom:12px;padding:12px;border-radius:8px;background:var(--s);border:1px solid var(--b)}}.rp h3{{font-family:var(--m);font-size:11px;font-weight:700;margin-bottom:8px}}.rp .br{{display:flex;align-items:center;gap:6px;margin-bottom:3px}}.rp .bl2{{font-family:var(--m);font-size:9px;width:70px;text-align:right;color:var(--t2)}}.rp .bt{{flex:1;height:6px;background:var(--bl);border-radius:3px;position:relative}}.rp .bf{{height:6px;border-radius:3px;position:absolute;top:0}}.rp .bv{{font-family:var(--m);font-size:9px;width:35px;font-weight:600}}
.me{{margin-top:16px;padding:12px;border-radius:6px;background:var(--bl);border:1px solid var(--b)}}.me h3{{font-family:var(--m);font-size:10px;font-weight:700;color:var(--t2);text-transform:uppercase;margin-bottom:4px}}.me p{{font-size:11px;color:var(--t2);line-height:1.6}}
footer{{margin-top:20px;padding-top:10px;border-top:1px solid var(--b);font-size:9px;color:var(--t3);text-align:center;font-family:var(--m)}}
.sc{{display:flex;gap:3px;align-items:center;font-family:var(--m);font-size:9px;color:var(--t3);margin-bottom:8px}}.sc button{{font-family:var(--m);font-size:9px;padding:2px 8px;border:1px solid var(--b);border-radius:3px;background:var(--s);color:var(--t2);cursor:pointer}}.sc button.on{{background:var(--t);color:var(--s);border-color:var(--t)}}
.bcat{{margin-bottom:16px}}.bcat h3{{font-family:var(--m);font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--t3);margin-bottom:6px;padding-bottom:4px;border-bottom:1px solid var(--b)}}
.bgrid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:6px}}
.bcard{{padding:10px 12px;border-radius:6px;background:var(--s);border:1px solid var(--b);cursor:pointer;transition:all .15s}}.bcard:hover{{border-color:var(--t3)}}
.bcard .bn{{font-family:var(--m);font-size:11px;font-weight:700;margin-bottom:4px;display:flex;justify-content:space-between;align-items:center}}
.bcard .bz{{font-family:var(--m);font-size:20px;font-weight:800}}.bcard .bz.pos{{color:var(--g)}}.bcard .bz.neg{{color:var(--r)}}.bcard .bz.neu{{color:var(--x)}}
.bcard .bsub{{font-family:var(--m);font-size:8px;color:var(--t3);margin-top:2px}}
.bcard .bstocks{{display:none;margin-top:8px;padding-top:6px;border-top:1px solid var(--bl)}}.bcard.open .bstocks{{display:block}}
.bcard .bs{{display:flex;justify-content:space-between;font-family:var(--m);font-size:9px;padding:2px 0;border-bottom:1px solid var(--bl)}}.bcard .bs .st{{font-weight:600}}.bcard .bs .sz{{font-weight:700}}
.spy-ref{{font-family:var(--m);font-size:11px;padding:8px 12px;background:var(--s);border:1px solid var(--b);border-radius:6px;margin-bottom:16px;display:flex;justify-content:space-between;align-items:center}}.spy-ref .sv{{font-weight:800;font-size:16px}}
@media(max-width:640px){{.cg{{grid-template-columns:1fr 1fr}}.hero .nm{{font-size:36px}}.fg{{grid-template-columns:repeat(3,1fr)}}.axes{{flex-direction:column;gap:8px}}.bgrid{{grid-template-columns:1fr}}}}
</style></head><body><div class="c" id="app"></div>
<script>
const D={data_str};
const RC={{'OVERHEAT':'#eab308','GOLDILOCKS':'#16a34a','STAGFLATION':'#9333ea','RECESSION':'#dc2626','CRISIS':'#1c1917','SUPPLY SHOCK':'#ea580c'}};
const ib=r=>r==='bull'||r==='falling'||r==='steepening';const ie=r=>r==='bear'||r==='rising'||r==='flattening';const rc=r=>ib(r)?'bu':ie(r)?'be':'si';
const rl=r=>({{bull:'BULL',bear:'BEAR',sideways:'SIDE',rising:'RISING',falling:'FALLING',stable:'STABLE',steepening:'STEEP',flattening:'FLAT'}}[r]||'\\u2014');
const tc=r=>ib(r)?'var(--g)':ie(r)?'var(--r)':'var(--x)';
const fP=(p,n)=>{{if(p==null)return'\\u2014';if(p>10000)return p.toLocaleString('en',{{maximumFractionDigits:0}});if(p>100)return p.toLocaleString('en',{{maximumFractionDigits:1}});return p<1?p.toFixed(4):p.toFixed(2)}};
const zP=z=>{{if(z==null)return 50;return((Math.max(-3,Math.min(3,z))+3)/6)*100}};const cl=n=>n.replace('cat_','').replace(/_/g,' ');
let S={{page:'regime',model:'strategic',view:'regime',sort:'default'}};
function MR(){{return D[S.model]}}
function render(){{
const app=document.getElementById('app');
let h='<header><h1>Regime Monitor</h1><div class="m">'+D.strategic.date+'</div></header>';
h+='<div class="topnav">';['regime','internals'].forEach(p=>{{h+='<button class="'+(S.page===p?'on':'')+'" onclick="U(\\'page\\',\\''+p+'\\')">'+p+'</button>'}});h+='</div>';
if(S.page==='regime')h+=renderRegime();else h+=renderInternals();
h+='<footer>4+2 Investment Clock + Market Internals \\u00b7 Daily</footer>';
app.innerHTML=h}}
function renderRegime(){{
const d=MR();const p=d.params;const cur=d.current;
let h='<div class="msw">';['strategic','tactical'].forEach(m=>{{h+='<button class="'+(S.model===m?'on':'')+'" onclick="U(\\'model\\',\\''+m+'\\')">'+m+'</button>'}});h+='</div>';
if(S.model==='strategic')h+='<div class="mdesc">STRATEGIC \\u2014 '+p.lookback+'d lookback \\u00b7 '+p.vol_window+'d vol \\u00b7 '+p.smooth+'d smooth \\u00b7 '+p.min_dur+'d min</div>';
else h+='<div class="mdesc">TACTICAL \\u2014 '+p.lookback+'d lookback \\u00b7 '+p.vol_window+'d vol \\u00b7 No smooth \\u00b7 '+p.min_dur+'d min</div>';
const hc=cur.label.replace(/ /g,'_');
h+='<div class="hero '+hc+'"><div class="lb">Current '+S.model.toUpperCase()+' Regime</div><div class="nm">'+cur.label+'</div><div class="cf">Growth: '+(cur.growth>=0?'+':'')+cur.growth.toFixed(2)+' \\u00b7 Inflation: '+(cur.inflation>=0?'+':'')+cur.inflation.toFixed(2)+'</div></div>';
const gc=cur.growth>0.3?'pos':cur.growth<-0.3?'neg':'neu';const ic=cur.inflation>0.3?'pos':cur.inflation<-0.3?'neg':'neu';
h+='<div class="axes"><div class="ax"><div class="al">Growth Axis</div><div class="av '+gc+'">'+(cur.growth>=0?'+':'')+cur.growth.toFixed(2)+'</div></div><div class="ax"><div class="al">Inflation Axis</div><div class="av '+ic+'">'+(cur.inflation>=0?'+':'')+cur.inflation.toFixed(2)+'</div></div></div>';
const feats=cur.features;const fo=['cat_Energy','cat_Global_Equities','cat_Credit','cat_Rates','cat_Crypto','cat_Metals','cat_Currencies','cyclical_vs_defensive','energy_vs_tech','financials','sector_breadth','sector_dispersion'];
h+='<div class="fg">';fo.forEach(fn=>{{const v=feats[fn];if(v==null)return;const c2=v>0.3?'pos':v<-0.3?'neg':'neu';h+='<div class="fc"><div class="fn">'+cl(fn)+'</div><div class="fv '+c2+'">'+(v>0?'+':'')+v.toFixed(2)+'</div></div>'}});h+='</div>';
h+=rTL(d);h+='<div class="mt">';['regime','assets','method'].forEach(v=>{{h+='<button class="'+(S.view===v?'on':'')+'" onclick="U(\\'view\\',\\''+v+'\\')">'+v+'</button>'}});h+='</div>';
if(S.view==='regime')h+=rR(d);else if(S.view==='assets')h+=rA(d);else h+=rMth(d);
return h}}
function renderInternals(){{
const I=D.internals;const bs=I.baskets;const co=I.cat_order;
let h='<div class="spy-ref"><span>SPY z-score (20d)</span><span class="sv">'+(I.spy_z>=0?'+':'')+I.spy_z.toFixed(2)+'</span></div>';
h+='<div class="mdesc">Relative to SPY \\u2014 '+I.params.lookback+'d lookback \\u00b7 '+I.params.vol_window+'d vol \\u00b7 '+bs.length+' baskets</div>';
h+='<div class="sc">Sort: <button class="'+(S.sort==='rel'||S.sort==='default'?'on':'')+'" onclick="U(\\'sort\\',\\'rel\\')">Rel \\u2193</button><button class="'+(S.sort==='abs'?'on':'')+'" onclick="U(\\'sort\\',\\'abs\\')">Abs \\u2193</button><button class="'+(S.sort==='cat'?'on':'')+'" onclick="U(\\'sort\\',\\'cat\\')">Category</button></div>';
if(S.sort==='cat'){{
co.forEach(cat=>{{const cbs=bs.filter(b=>b.cat===cat);if(!cbs.length)return;h+='<div class="bcat"><h3>'+cat+' ('+cbs.length+')</h3><div class="bgrid">';cbs.sort((a,b)=>b.rel-a.rel);cbs.forEach(b=>{{h+=bCard(b)}});h+='</div></div>'}})}}
else{{const sorted=S.sort==='abs'?[...bs].sort((a,b)=>Math.abs(b.z)-Math.abs(a.z)):[...bs].sort((a,b)=>b.rel-a.rel);h+='<div class="bgrid">';sorted.forEach(b=>{{h+=bCard(b)}});h+='</div>'}}
return h}}
function bCard(b){{
const zc=b.rel>0.5?'pos':b.rel<-0.5?'neg':'neu';
let h='<div class="bcard" onclick="this.classList.toggle(\\'open\\')">';
h+='<div class="bn"><span>'+b.name+'</span><span class="al2 '+(b.rel>0.3?'bu':b.rel<-0.3?'be':'si')+'">'+(b.rel>0?'OUT':'UNDER')+'</span></div>';
h+='<div class="bz '+zc+'">'+(b.rel>=0?'+':'')+b.rel.toFixed(2)+'</div>';
h+='<div class="bsub">'+b.cat+' \\u00b7 Abs: '+(b.z>=0?'+':'')+b.z.toFixed(2)+' \\u00b7 '+b.n_ok+'/'+b.n+' stocks</div>';
h+='<div class="bstocks">';b.stocks.forEach(s=>{{const sc=s.rz>0.3?'var(--g)':s.rz<-0.3?'var(--r)':'var(--x)';h+='<div class="bs"><span class="st">'+s.t+'</span><span>'+(s.p?fP(s.p,s.t):'')+'</span><span class="sz" style="color:'+sc+'">'+(s.rz>=0?'+':'')+s.rz.toFixed(2)+'</span></div>'}});
h+='</div></div>';return h}}
function showT(el){{const t=document.getElementById('tip');if(!t)return;const r=el.getBoundingClientRect();const p=el.parentElement.getBoundingClientRect();t.innerHTML='<b>'+el.dataset.label+'</b><br><span style="opacity:.7;font-size:9px">'+el.dataset.start+' \\u2192 '+el.dataset.end+'</span>';t.style.display='block';t.style.left=(r.left+r.width/2-p.left)+'px';t.style.top='-48px'}}
function hideT(){{const t=document.getElementById('tip');if(t)t.style.display='none'}}
function rTL(d){{const tl=d.timeline;if(!tl||!tl.length)return'';const t0=new Date(tl[0].start).getTime();const t1=new Date(tl[tl.length-1].end).getTime()+864e5;const sp=t1-t0||1;let h='<div class="tw"><div id="tip" class="tt"></div><div class="tb">';tl.forEach((s,i)=>{{const a=new Date(s.start).getTime();const b=new Date(s.end).getTime()+864e5;const w=Math.max(0.5,((b-a)/sp)*100);const col=RC[s.l]||'#a8a29e';const ic=i===tl.length-1;h+='<div class="ts" style="width:'+w+'%;background:'+col+(ic?';box-shadow:inset 0 0 0 2px rgba(0,0,0,.3)':'')+'" data-label="'+s.l+'" data-start="'+s.start+'" data-end="'+s.end+'" onmouseenter="showT(this)" onmouseleave="hideT()"></div>'}});h+='</div></div>';h+='<div class="td"><span>'+tl[0].start+'</span><span>'+tl[tl.length-1].end+'</span></div>';const seen=new Set();h+='<div class="tleg">';tl.forEach(s=>{{if(!seen.has(s.l)){{seen.add(s.l);h+='<span><span class="dot" style="background:'+(RC[s.l]||'#a8a29e')+'"></span>'+s.l+'</span>'}}}});h+='</div>';return h}}
function rR(d){{let h='';Object.values(d.regimes).forEach(info=>{{const col=RC[info.label]||'#a8a29e';const ic=info.label===d.current.label;h+='<div class="rp" style="'+(ic?'border:2px solid '+col:'')+'"><h3 style="color:'+col+'">'+(ic?'\\u25b6 ':'')+info.label+' \\u2014 '+info.n_days+'d ('+info.pct+'%)</h3>';h+='<div style="font-size:10px;color:var(--t3);margin-bottom:8px">'+info.periods.slice(0,5).join(', ')+'</div>';const p=info.profile;['cat_Energy','cat_Global_Equities','cat_Credit','cat_Rates','cat_Crypto','cat_Metals','cyclical_vs_defensive','energy_vs_tech'].forEach(fn=>{{const v=p[fn]||0;const pct=Math.min(100,Math.abs(v)*30);const c2=v>0.2?'var(--g)':v<-0.2?'var(--r)':'var(--x)';const left=v>=0?'50%':(50-pct)+'%';h+='<div class="br"><span class="bl2">'+cl(fn)+'</span><div class="bt"><div class="bf" style="left:'+left+'%;width:'+pct+'%;background:'+c2+'"></div><div style="position:absolute;left:50%;top:0;width:1px;height:6px;background:var(--b)"></div></div><span class="bv" style="color:'+c2+'">'+(v>0?'+':'')+v.toFixed(2)+'</span></div>'}});h+='</div>'}});return h}}
function rA(d){{const cats=d.assets;const CO=d.cat_order;let h='<div class="sc">Sort: '+['default','z-desc','z-asc','alpha','regime'].map(s=>'<button class="'+(S.sort===s?'on':'')+'" onclick="U(\\'sort\\',\\''+s+'\\')">'+({{'z-desc':'z\\u2193','z-asc':'z\\u2191'}}[s]||s)+'</button>').join('')+'</div>';CO.forEach(k=>{{const a2=cats[k];if(!a2)return;let en=Object.entries(a2);if(S.sort==='z-asc')en.sort((a,b)=>(a[1].score||0)-(b[1].score||0));else if(S.sort==='z-desc')en.sort((a,b)=>(b[1].score||0)-(a[1].score||0));else if(S.sort==='alpha')en.sort((a,b)=>a[0].localeCompare(b[0]));else if(S.sort==='regime'){{const ro=r=>ib(r)?0:ie(r)?2:1;en.sort((a,b)=>ro(a[1].regime)-ro(b[1].regime))}}const nb=en.filter(([,x])=>ib(x.regime)).length,nr=en.filter(([,x])=>ie(x.regime)).length,ns=en.length-nb-nr;h+='<div class="cb"><div class="ch"><h2>'+k+'</h2><div class="st">';if(nb)h+='<span><span class="d" style="background:var(--g)"></span>'+nb+'</span>';if(ns)h+='<span><span class="d" style="background:var(--x)"></span>'+ns+'</span>';if(nr)h+='<span><span class="d" style="background:var(--r)"></span>'+nr+'</span>';h+='</div></div><div class="cg">';en.forEach(([n,x])=>{{const c=rc(x.regime),z=x.score,zc=tc(x.regime);h+='<div class="a '+c+'"><div class="ai"><div style="display:flex;justify-content:space-between;align-items:center"><span class="an">'+n+'</span><span class="al2 '+c+'">'+rl(x.regime)+'</span></div><div class="ar"><span class="ap">'+fP(x.price,n)+'</span><span class="az" style="color:'+zc+'">'+(z!=null?(z>0?'+':'')+z.toFixed(2):'\\u2014')+'</span></div><div class="zb"><div class="md"></div>'+(z!=null?'<div class="dt" style="left:'+zP(z)+'%;background:'+zc+'"></div>':'')+'</div></div></div>'}});h+='</div></div>'}});return h}}
function rMth(d){{const p=d.params;return'<div class="me"><h3>'+S.model.toUpperCase()+' \\u2014 4+2 Framework</h3><p><b>Growth</b> = (Equities + Credit + Cyclical/Defensive) / 3<br><b>Inflation</b> = (Energy + Rates + E/T Spread) / 3<br><br>G\\u22650 I\\u22650 \\u2192 OVERHEAT \\u00b7 G\\u22650 I&lt;0 \\u2192 GOLDILOCKS<br>G&lt;0 I\\u22650 \\u2192 STAGFLATION \\u00b7 G&lt;0 I&lt;0 \\u2192 RECESSION<br><br>Overrides: CRISIS (all&lt;-1.0) \\u00b7 SUPPLY SHOCK (Energy&gt;1.0 & E/T&gt;1.0)<br><br>'+p.lookback+'d lookback, '+p.vol_window+'d vol'+(p.smooth>1?', '+p.smooth+'d smooth':'')+', '+p.min_dur+'d min duration</p></div>'}}
function U(k,v){{S[k]=v;render()}}render();
</script></body></html>"""

with open('index.html', 'w') as f:
    f.write(html)
print(f"OK index.html: {len(html)/1024:.1f} KB")
