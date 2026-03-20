"""Regime Monitor v2 — Global + Korea, 4+2 Investment Clock + Market Internals"""
import pandas as pd, numpy as np, yfinance as yf, json, warnings
from datetime import datetime
warnings.filterwarnings('ignore')
END = datetime.now().strftime('%Y-%m-%d')
START = '2018-01-01'

# ═══ GLOBAL MACRO UNIVERSE ═══
G_UNI = {
    'Crypto':{'BTC-USD':'BTC','ETH-USD':'ETH','SOL-USD':'SOL'},
    'Metals':{'GC=F':'Gold','SI=F':'Silver','HG=F':'Copper','PA=F':'Palladium','PL=F':'Platinum','ALI=F':'Aluminum'},
    'Energy':{'CL=F':'WTI','BZ=F':'Brent','NG=F':'NatGas','RB=F':'Gasoline','HO=F':'HeatingOil'},
    'US Sectors':{'XLK':'Tech','XLF':'Financials','XLE':'Energy_Eq','XLV':'Healthcare','XLI':'Industrials','XLP':'Staples','XLY':'Discretionary','XLU':'Utilities','XLRE':'RealEstate','XLB':'Materials','XLC':'CommSvc'},
    'Global Equities':{'^GSPC':'US_SP500','^IXIC':'US_Nasdaq','^STOXX50E':'EU_Stoxx50','EWJ':'Japan','EWY':'Korea','EWT':'Taiwan','FXI':'China','EWG':'Germany','EWU':'UK','EWZ':'Brazil','INDA':'India','EEM':'EM_Broad','EWA':'Australia','EWC':'Canada','EWS':'Singapore','THD':'Thailand','EWW':'Mexico','EIDO':'Indonesia','VNM':'Vietnam','EZA':'SouthAfrica','QAT':'Qatar','KSA':'SaudiArabia','TUR':'Turkey'},
    'Rates':{'^IRX':'US_3M','^FVX':'US_5Y','^TNX':'US_10Y','^TYX':'US_30Y'},
    'Currencies':{'EURUSD=X':'EURUSD','JPYUSD=X':'JPYUSD','GBPUSD=X':'GBPUSD','CNYUSD=X':'CNYUSD','AUDUSD=X':'AUDUSD','CHFUSD=X':'CHFUSD','KRWUSD=X':'KRWUSD','SGDUSD=X':'SGDUSD'},
    'Credit':{'HYG':'HY_Bond','LQD':'IG_Bond','JNK':'HY_Junk','BKLN':'BankLoans','EMB':'EM_Bond'},
}
RATE_A = {'US_3M','US_5Y','US_10Y','US_30Y'}
CURVE_A = {'YC_10Y3M','YC_10Y5Y','YC_30Y10Y'}
SECTORS = ['Tech','Financials','Energy_Eq','Healthcare','Industrials','Staples','Discretionary','Utilities','RealEstate','Materials','CommSvc']
CYCLICAL = ['Discretionary','Industrials','Financials','Materials']
DEFENSIVE = ['Staples','Utilities','Healthcare','RealEstate']
CAT_ORD = ["Crypto","Metals","Energy","US Sectors","Global Equities","Rates","Curves","Currencies","Credit"]

# ═══ GLOBAL INTERNALS ═══
G_BASK = {
    'Staffing':{'t':['RHI','MAN','KFRC','NSP'],'cat':'Labor'},
    'Homebuilders':{'t':['DHI','LEN','PHM','TOL','KBH','NVR','TMHC'],'cat':'Rate Sensitive'},
    'Building Materials':{'t':['BLDR','SHW','MLM','VMC'],'cat':'Rate Sensitive'},
    'Regional Banks':{'t':['ZION','KEY','HBAN','RF','CFG','MTB','FHN','EWBC','WAL'],'cat':'Credit Cycle'},
    'Railroads':{'t':['UNP','CSX','NSC','CP'],'cat':'Transport'},
    'Dry Bulk':{'t':['SBLK','GNK','EGLE','DSX'],'cat':'Global Trade'},
    'Restaurants':{'t':['MCD','SBUX','YUM','DPZ','CMG','WING','CAVA'],'cat':'Consumer'},
    'Leisure Travel':{'t':['MAR','HLT','BKNG','EXPE','RCL','CCL','NCLH'],'cat':'Consumer'},
    'Airlines':{'t':['DAL','UAL','LUV','JBLU','AAL'],'cat':'Transport'},
    'Chemicals':{'t':['DOW','LYB','CE','DD','EMN','APD'],'cat':'Industrial'},
    'Packaging':{'t':['CCK','SEE','AMCR','IP','PKG'],'cat':'Industrial'},
    'Medical Devices':{'t':['MDT','SYK','BSX','EW','ISRG','ABT'],'cat':'Healthcare'},
    'P&C Insurers':{'t':['PGR','ALL','TRV','CB','AIG'],'cat':'Financials'},
    'US Utilities':{'t':['NEE','DUK','SO','D','AEP','EXC','SRE'],'cat':'Defensive'},
    'Tobacco':{'t':['PM','MO','BTI'],'cat':'Defensive'},
    'Waste Mgmt':{'t':['WM','RSG','CLH','CWST'],'cat':'Industrial'},
    'Timber':{'t':['WY','RYN','PCH'],'cat':'Rate Sensitive'},
    'Analog Semis':{'t':['TXN','ADI','ON','MCHP','NXPI'],'cat':'Inventory Cycle'},
    'Electrical Grid':{'t':['ETN','POWL','HWM','HUBB'],'cat':'Infra'},
    'Capital Goods':{'t':['CAT','DE','ETN','ROK','EMR','ITW','PH'],'cat':'Capex'},
    'Software SaaS':{'t':['CRM','NOW','PANW','DDOG','ZS','CRWD','WDAY'],'cat':'Tech Growth'},
    'Data Center AI':{'t':['NVDA','AVGO','ANET','VRT','DELL','SMCI','EQIX'],'cat':'AI Capex'},
    'GLP1 Obesity':{'t':['LLY','NVO','HIMS','VKTX','AMGN'],'cat':'Healthcare'},
    'Autos':{'t':['GM','F','STLA'],'cat':'Consumer'},
    'Auto Parts':{'t':['APTV','BWA','LEA','ALV'],'cat':'Manufacturing'},
    'Ag Fertilizers':{'t':['MOS','NTR','CF','FMC'],'cat':'Inflation'},
    'Ag Equipment':{'t':['DE','AGCO'],'cat':'Ag Cycle'},
    'Steel Metals':{'t':['NUE','STLD','CLF','RS'],'cat':'Industrial'},
    'Cybersecurity':{'t':['PANW','CRWD','ZS','FTNT','NET'],'cat':'Security'},
    'Gold Miners':{'t':['NEM','GOLD','AEM','FNV','WPM','GFI'],'cat':'Fear'},
    'Defense':{'t':['LMT','RTX','NOC','GD','LHX','HII'],'cat':'Geopolitics'},
    'Tankers':{'t':['STNG','FRO','INSW','DHT'],'cat':'Geopolitics'},
    'Energy E&P':{'t':['XOM','CVX','OXY','COP','SLB'],'cat':'Energy'},
    'Nuclear SMR':{'t':['CEG','VST','CCJ','SMR','OKLO'],'cat':'Energy'},
    'Robotics':{'t':['ISRG','ROK','TER'],'cat':'Automation'},
    'China ADRs':{'t':['BABA','JD','PDD','BIDU','NTES'],'cat':'China'},
    'Clean Energy':{'t':['ENPH','FSLR','SEDG','RUN'],'cat':'Policy'},
    'Luxury':{'t':['RL','CPRI','TPR'],'cat':'Wealth Effect'},
    'DC REITs':{'t':['EQIX','DLR','AMT'],'cat':'AI Infra'},
    'Resi REITs':{'t':['AVB','EQR','MAA','INVH'],'cat':'Rate Sensitive'},
}
G_BCAT = ['Labor','Rate Sensitive','Credit Cycle','Transport','Global Trade','Consumer',
           'Industrial','Manufacturing','Inventory Cycle','Capex','Infra','Financials',
           'Healthcare','Inflation','Ag Cycle','Energy','Geopolitics','Security',
           'Tech Growth','AI Capex','AI Infra','Automation','China','Policy','Wealth Effect','Defensive','Fear']

# ═══ KOREA MACRO UNIVERSE ═══
# Growth: KOSPI broad + banks + cyclical/defensive
# Inflation: Global energy + USDKRW + Korean energy/materials vs tech
KR_UNI = {
    'KR Equities':{'^KS11':'KOSPI','^KQ11':'KOSDAQ','005930.KS':'Samsung','000660.KS':'SK_Hynix','005380.KS':'Hyundai_Motor','000270.KS':'Kia'},
    'KR Banks':{'105560.KS':'KB_Financial','055550.KS':'Shinhan','086790.KS':'Hana','316140.KS':'Woori'},
    'KR Cyclical':{'005380.KS':'Hyundai_Motor','000270.KS':'Kia','005490.KS':'POSCO','004020.KS':'Hyundai_Steel','028260.KS':'Samsung_CT'},
    'KR Defensive':{'015760.KS':'KEPCO','017670.KS':'SK_Telecom','030200.KS':'KT','097950.KS':'CJ_Cheil'},
    'Energy':{'CL=F':'WTI','BZ=F':'Brent'},  # shared
    'KR Currency':{'KRW=X':'USDKRW'},
}
KR_RATE_A = set()
KR_SECTORS_CYC = ['Hyundai_Motor','Kia','POSCO','Hyundai_Steel','Samsung_CT']
KR_SECTORS_DEF = ['KEPCO','SK_Telecom','KT','CJ_Cheil']
KR_CAT_ORD = ["KR Equities","KR Banks","KR Cyclical","KR Defensive","Energy","KR Currency"]

# ═══ KOREA INTERNALS ═══
KR_BASK = {
    'KR Semis':{'t':['005930.KS','000660.KS','042700.KQ','058470.KS'],'cat':'Tech'},
    'KR Battery':{'t':['373220.KS','006400.KS','247540.KQ','003670.KS'],'cat':'EV/Battery'},
    'KR Shipbuilding':{'t':['329180.KS','010140.KS','042660.KS'],'cat':'Industrial'},
    'KR Defense':{'t':['012450.KS','079550.KS','047810.KS'],'cat':'Geopolitics'},
    'KR Autos':{'t':['005380.KS','000270.KS','012330.KS'],'cat':'Consumer'},
    'KR Chemicals':{'t':['051910.KS','011170.KS','011780.KS'],'cat':'Industrial'},
    'KR Steel':{'t':['005490.KS','004020.KS'],'cat':'Industrial'},
    'KR Construction':{'t':['028260.KS','000720.KS'],'cat':'Rate Sensitive'},
    'KR Banks':{'t':['105560.KS','055550.KS','086790.KS','316140.KS'],'cat':'Financials'},
    'KR Bio':{'t':['207940.KS','068270.KS'],'cat':'Healthcare'},
    'KR Entertainment':{'t':['352820.KS','041510.KS','035900.KS'],'cat':'Consumer'},
    'KR Retail':{'t':['004170.KS','139480.KS','097950.KS'],'cat':'Consumer'},
    'KR Telecom':{'t':['017670.KS','030200.KS'],'cat':'Defensive'},
    'KR Utilities':{'t':['015760.KS','036460.KS'],'cat':'Defensive'},
    'KR Nuclear':{'t':['034020.KS','052690.KS'],'cat':'Energy'},
    'KR Internet':{'t':['035420.KS','035720.KS'],'cat':'Tech'},
    'KR Gaming':{'t':['259960.KS','251270.KS'],'cat':'Consumer'},
    'KR Robotics':{'t':['454910.KS','277810.KQ'],'cat':'Automation'},
}
KR_BCAT = ['Tech','EV/Battery','Industrial','Geopolitics','Consumer','Rate Sensitive',
            'Financials','Healthcare','Energy','Defensive','Automation']

# ═══ 1. DOWNLOAD ALL ═══
print(f"Regime Monitor v2: {START} -> {END}")

# Collect all tickers
all_tickers = set()
g_regime_map = {}
for cat, tks in G_UNI.items():
    for t, n in tks.items(): g_regime_map[t] = n; all_tickers.add(t)
kr_regime_map = {}
for cat, tks in KR_UNI.items():
    for t, n in tks.items(): kr_regime_map[t] = n; all_tickers.add(t)
for bk in [G_BASK, KR_BASK]:
    for bn, bi in bk.items():
        for t in bi['t']: all_tickers.add(t)
all_tickers.add('SPY'); all_tickers.add('^KS11')

print(f"Downloading {len(all_tickers)} tickers...")
raw = yf.download(list(all_tickers), start=START, end=END, progress=False, group_by='ticker')

def parse_tickers(ticker_map):
    df = pd.DataFrame()
    ok = []
    for t, n in ticker_map.items():
        try:
            if t in raw.columns.get_level_values(0):
                s = raw[t]['Close'].squeeze()
                if isinstance(s, pd.Series) and s.notna().sum() > 100:
                    s.name = n; df = pd.concat([df, s], axis=1); ok.append(n)
        except: pass
    df.index = pd.to_datetime(df.index).tz_localize(None)
    return df.sort_index().ffill(), ok

def parse_raw_tickers(tickers):
    df = pd.DataFrame()
    ok = []
    for t in sorted(tickers):
        try:
            if t in raw.columns.get_level_values(0):
                s = raw[t]['Close'].squeeze()
                if isinstance(s, pd.Series) and s.notna().sum() > 100:
                    s.name = t; df = pd.concat([df, s], axis=1); ok.append(t)
        except: pass
    df.index = pd.to_datetime(df.index).tz_localize(None)
    return df.sort_index().ffill(), ok

# Global regime data
df_g, g_ok = parse_tickers(g_regime_map)
daily_g = df_g[df_g.index.dayofweek < 5].dropna(how='all')
# Derived
for a,b,nm in [('US_10Y','US_3M','YC_10Y3M'),('US_30Y','US_10Y','YC_30Y10Y'),('US_10Y','US_5Y','YC_10Y5Y')]:
    if a in daily_g.columns and b in daily_g.columns: daily_g[nm] = daily_g[a]-daily_g[b]
if 'ETH' in daily_g.columns and 'BTC' in daily_g.columns: daily_g['ETH_BTC'] = daily_g['ETH']/daily_g['BTC']
if 'IG_Bond' in daily_g.columns and 'HY_Bond' in daily_g.columns: daily_g['CreditSpread'] = daily_g['IG_Bond']/daily_g['HY_Bond']
G_CAT_A = {}
for cat, tks in G_UNI.items():
    assets = [n for n in tks.values() if n in daily_g.columns]
    if cat == 'Crypto' and 'ETH_BTC' in daily_g.columns: assets.append('ETH_BTC')
    if assets: G_CAT_A[cat] = assets
curves = [c for c in ['YC_10Y3M','YC_10Y5Y','YC_30Y10Y'] if c in daily_g.columns]
if curves: G_CAT_A['Curves'] = curves
if 'Credit' in G_CAT_A and 'CreditSpread' in daily_g.columns: G_CAT_A['Credit'].append('CreditSpread')

# Korea regime data
df_kr, kr_ok = parse_tickers(kr_regime_map)
daily_kr = df_kr[df_kr.index.dayofweek < 5].dropna(how='all')
KR_CAT_A = {}
for cat, tks in KR_UNI.items():
    assets = [n for n in tks.values() if n in daily_kr.columns]
    if assets: KR_CAT_A[cat] = assets

# Global internals data
g_int_tks = set(['SPY'])
for bn, bi in G_BASK.items():
    for t in bi['t']: g_int_tks.add(t)
df_gi, gi_ok = parse_raw_tickers(g_int_tks)
daily_gi = df_gi[df_gi.index.dayofweek < 5].dropna(how='all')

# Korea internals data
kr_int_tks = set(['^KS11'])
for bn, bi in KR_BASK.items():
    for t in bi['t']: kr_int_tks.add(t)
df_ki, ki_ok = parse_raw_tickers(kr_int_tks)
daily_ki = df_ki[df_ki.index.dayofweek < 5].dropna(how='all')

print(f"OK g_regime={len(g_ok)} kr_regime={len(kr_ok)} g_int={len(gi_ok)} kr_int={len(ki_ok)}")

# ═══ 2. REGIME PIPELINE (generic) ═══
def run_regime(daily, cat_assets, cat_order, rate_assets, curve_assets, sectors, cyclical, defensive, lookback, vol_window, smooth, min_dur):
    zs = pd.DataFrame(index=daily.index)
    for col in daily.columns:
        ir = col in rate_assets or col in curve_assets
        if ir: zs[col] = daily[col].diff(lookback)/(daily[col].diff(1).rolling(vol_window).std()*np.sqrt(lookback))
        else: zs[col] = daily[col].pct_change(lookback)/(daily[col].pct_change(1).rolling(vol_window).std()*np.sqrt(lookback))
    scols = [c for c in sectors if c in zs.columns]
    ft = pd.DataFrame(index=daily.index)
    for cat in cat_order:
        fn = f"cat_{cat.replace(' ','_')}"
        if cat not in cat_assets: ft[fn]=0.0; continue
        cols = [a for a in cat_assets[cat] if a in zs.columns]
        ft[fn] = zs[cols].mean(axis=1) if cols else 0.0
    cyc = [c for c in cyclical if c in zs.columns]
    dfc = [c for c in defensive if c in zs.columns]
    ft['cyc_def'] = (zs[cyc].mean(axis=1)-zs[dfc].mean(axis=1)) if cyc and dfc else 0.0
    # Energy vs tech: use first energy cat and first tech-like cat
    e_cols = [c for c in cat_assets.get('Energy',[])+cat_assets.get('US Sectors',[]) if 'Energy' in c and c in zs.columns]
    t_cols = [c for c in cat_assets.get('US Sectors',[])+cat_assets.get('KR Equities',[]) if 'Tech' in c or 'Samsung' in c or 'Nasdaq' in c and c in zs.columns]
    if e_cols and t_cols:
        ft['e_vs_t'] = zs[e_cols].mean(axis=1) - zs[t_cols].mean(axis=1)
    else:
        ft['e_vs_t'] = 0.0
    ft['dispersion'] = zs[scols].std(axis=1) if scols else 0.0
    def brd(i):
        return sum(1 for c in scols if pd.notna(zs[c].iloc[i]) and zs[c].iloc[i]>0.8)/max(1,len(scols))
    ft['breadth'] = [brd(i) for i in range(len(daily))]
    ft = ft.dropna()
    fnames = list(ft.columns)
    fs = ft.rolling(smooth, min_periods=1, center=True).mean() if smooth>1 else ft
    # Find growth/inflation columns
    eq_col = [c for c in fnames if 'Equities' in c or 'KR_Equities' in c]
    cr_col = [c for c in fnames if 'Credit' in c or 'Banks' in c]
    eq_c = eq_col[0] if eq_col else fnames[0]
    cr_c = cr_col[0] if cr_col else 'cyc_def'
    en_col = [c for c in fnames if 'Energy' in c]
    ra_col = [c for c in fnames if 'Rates' in c or 'Currency' in c]
    en_c = en_col[0] if en_col else fnames[0]
    ra_c = ra_col[0] if ra_col else 'e_vs_t'
    growth = (fs[eq_c] + fs[cr_c] + fs['cyc_def'])/3
    inflation = (fs[en_c] + fs[ra_c] + fs['e_vs_t'])/3
    labels = []
    for i in range(len(fs)):
        g,inf = growth.iloc[i], inflation.iloc[i]
        eq,cr = fs[eq_c].iloc[i], fs[cr_c].iloc[i]
        # Crisis check - use available broad metrics
        broad = [fs[c].iloc[i] for c in fnames if c.startswith('cat_')]
        avg_broad = np.mean(broad) if broad else 0
        en_v = fs[en_c].iloc[i]; et_v = fs['e_vs_t'].iloc[i]
        if avg_broad < -1.0: labels.append('CRISIS')
        elif en_v > 1.0 and et_v > 1.0: labels.append('SUPPLY SHOCK')
        elif g>=0 and inf>=0: labels.append('OVERHEAT')
        elif g>=0 and inf<0: labels.append('GOLDILOCKS')
        elif g<0 and inf>=0: labels.append('STAGFLATION')
        else: labels.append('RECESSION')
    labels = np.array(labels)
    # Stabilize
    if min_dur > 1:
        changed = True
        while changed:
            changed = False
            runs=[]; i=0
            while i<len(labels):
                j=i
                while j<len(labels) and labels[j]==labels[i]: j+=1
                runs.append((i,j,labels[i])); i=j
            for ri,(s,e,lbl) in enumerate(runs):
                if ri==len(runs)-1: continue
                if e-s < min_dur and len(runs)>1:
                    if 0<ri<len(runs)-1:
                        pl=runs[ri-1][1]-runs[ri-1][0]; nl=runs[ri+1][1]-runs[ri+1][0]
                        new=runs[ri-1][2] if pl>=nl else runs[ri+1][2]
                    elif ri==0: new=runs[ri+1][2]
                    else: new=runs[ri-1][2]
                    labels[s:e]=new; changed=True; break
    # Build output
    unique = sorted(set(labels))
    regimes = {}
    for idx,lbl in enumerate(unique):
        mask=labels==lbl; n=int(mask.sum())
        prof={fn:float(ft.iloc[np.where(mask)[0]][fn].mean()) for fn in fnames}
        dates=ft.index[mask]; periods=[]
        if len(dates)>0:
            sd=dates[0]
            for ii in range(1,len(dates)):
                if (dates[ii]-dates[ii-1]).days>5:
                    periods.append(f"{sd.strftime('%Y-%m-%d')}->{dates[ii-1].strftime('%Y-%m-%d')}"); sd=dates[ii]
            periods.append(f"{sd.strftime('%Y-%m-%d')}->{dates[-1].strftime('%Y-%m-%d')}")
        regimes[str(idx)]={'label':lbl,'n_days':n,'pct':round(n/len(ft)*100,1),
            'profile':{k:round(v,3) for k,v in prof.items()},'periods':periods[:10]}
    tl=[]; prev=None
    for i in range(len(labels)):
        lbl=labels[i]; d=ft.index[i].strftime('%Y-%m-%d')
        if lbl!=prev:
            if tl: tl[-1]['end']=ft.index[i-1].strftime('%Y-%m-%d')
            tl.append({'start':d,'end':d,'l':lbl}); prev=lbl
        else: tl[-1]['end']=d
    assets_out={}
    for cat in cat_order:
        if cat not in cat_assets: continue
        cd={}
        for asset in cat_assets[cat]:
            if asset not in daily.columns: continue
            price=float(daily[asset].iloc[-1]) if pd.notna(daily[asset].iloc[-1]) else None
            z=float(zs[asset].iloc[-1]) if asset in zs.columns and pd.notna(zs[asset].iloc[-1]) else None
            ir=asset in rate_assets; ic=asset in curve_assets
            if z is not None:
                if ir: regime='rising' if z>0.8 else 'falling' if z<-0.8 else 'stable'
                elif ic: regime='steepening' if z>0.8 else 'flattening' if z<-0.8 else 'stable'
                else: regime='bull' if z>0.8 else 'bear' if z<-0.8 else 'sideways'
            else: regime='sideways'
            cd[asset]={'regime':regime,'score':round(z,3) if z else None,'price':round(price,4) if price else None}
        if cd: assets_out[cat]=cd
    return {'date':ft.index[-1].strftime('%Y-%m-%d'),'total_assets':len([a for a in daily.columns]),'days':len(ft),
            'n_regimes':len(unique),'params':{'lookback':lookback,'vol_window':vol_window,'smooth':smooth,'min_dur':min_dur},
            'current':{'label':labels[-1],'growth':round(float(growth.iloc[-1]),3),'inflation':round(float(inflation.iloc[-1]),3),
                'features':{fn:round(float(ft.iloc[-1][fn]),3) for fn in fnames}},
            'regimes':regimes,'timeline':tl,'assets':assets_out,'cat_order':cat_order}

# ═══ 3. INTERNALS PIPELINE (generic, with 200d breadth) ═══
def run_internals(daily_int, baskets, cat_order, bench_ticker, lookback, vol_window, label):
    zs = pd.DataFrame(index=daily_int.index)
    for col in daily_int.columns:
        zs[col] = daily_int[col].pct_change(lookback)/(daily_int[col].pct_change(1).rolling(vol_window).std()*np.sqrt(lookback))
    zs = zs.dropna(how='all')
    # 200-day MA
    ma200 = daily_int.rolling(200, min_periods=150).mean()
    bench_z = float(zs[bench_ticker].iloc[-1]) if bench_ticker in zs.columns and pd.notna(zs[bench_ticker].iloc[-1]) else 0.0
    baskets_out = []
    total_above200 = 0; total_counted200 = 0
    for bname, binfo in baskets.items():
        tickers = [t for t in binfo['t'] if t in zs.columns]
        if not tickers: continue
        scores = [float(zs[t].iloc[-1]) for t in tickers if pd.notna(zs[t].iloc[-1])]
        if not scores: continue
        avg_z = sum(scores)/len(scores); rel_z = avg_z - bench_z
        # 200d breadth
        n_above = 0; n_counted = 0
        stocks = []
        for t in tickers:
            z = float(zs[t].iloc[-1]) if pd.notna(zs[t].iloc[-1]) else None
            p = float(daily_int[t].iloc[-1]) if t in daily_int.columns and pd.notna(daily_int[t].iloc[-1]) else None
            above200 = None
            if t in ma200.columns and p is not None and pd.notna(ma200[t].iloc[-1]):
                above200 = p > float(ma200[t].iloc[-1])
                n_counted += 1; total_counted200 += 1
                if above200: n_above += 1; total_above200 += 1
            if z is not None:
                stocks.append({'t':t,'z':round(z,2),'rz':round(z-bench_z,2),'p':round(p,2) if p else None,'a200':above200})
        pct200 = round(n_above/n_counted*100) if n_counted>0 else None
        baskets_out.append({'name':bname,'cat':binfo['cat'],'z':round(avg_z,2),'rel':round(rel_z,2),
            'n':len(tickers),'n_ok':len(scores),'pct200':pct200,
            'stocks':sorted(stocks, key=lambda x:-x['rz'])})
    baskets_out.sort(key=lambda x:-x['rel'])
    total_pct200 = round(total_above200/total_counted200*100) if total_counted200>0 else None

    # ── Signals ──
    CYCL_CATS = {'Transport','Consumer','Industrial','Manufacturing','Capex','Inventory Cycle','Credit Cycle','Labor','Global Trade','Ag Cycle','EV/Battery'}
    DEF_CATS = {'Defensive','Fear'}
    n_out = sum(1 for b in baskets_out if b['rel']>0.3); n_total = len(baskets_out)
    breadth_pct = round(n_out/n_total*100) if n_total else 0
    cyc_s = [b['rel'] for b in baskets_out if b['cat'] in CYCL_CATS]
    def_s = [b['rel'] for b in baskets_out if b['cat'] in DEF_CATS]
    rate_s = [b['rel'] for b in baskets_out if b['cat'] in ('Rate Sensitive','Credit Cycle')]
    avg_cyc = np.mean(cyc_s) if cyc_s else 0
    avg_def = np.mean(def_s) if def_s else 0
    avg_rate = np.mean(rate_s) if rate_s else 0
    cvd = avg_cyc - avg_def
    cycle = []
    if breadth_pct>=60: cycle.append(f'{n_out} of {n_total} baskets beating the market — broad strength')
    elif breadth_pct<=25: cycle.append(f'Only {n_out} of {n_total} baskets beating the market — narrow leadership')
    else: cycle.append(f'{n_out} of {n_total} baskets beating the market')
    if total_pct200 is not None:
        cycle.append(f'{total_pct200}% of stocks above their 200-day average')
    if cvd>0.4: cycle.append('Cyclical stocks leading defensives — economy looks strong')
    elif cvd>0.15: cycle.append('Cyclical stocks slightly ahead of defensives')
    elif cvd<-0.4: cycle.append('Defensive stocks leading cyclicals — market worried about growth')
    elif cvd<-0.15: cycle.append('Defensive stocks slightly ahead of cyclicals')
    if avg_rate>0.5: cycle.append('Rate-sensitive stocks recovering — market expects lower rates')
    elif avg_rate<-0.5: cycle.append('Rate-sensitive stocks under pressure — tight money hurting')
    if bench_z<-1.5: cycle.append('Market in sharp decline')
    elif bench_z<-0.8: cycle.append('Market trending lower')
    elif bench_z>1.5: cycle.append('Market in strong rally')
    elif bench_z>0.8: cycle.append('Market trending higher')
    themes = []
    top7 = [b['cat'] for b in baskets_out[:7]]; bot7 = [b['cat'] for b in baskets_out[-7:]]
    if sum(1 for c in top7 if c in ('Geopolitics','Security'))>=2: themes.append('Defense & security stocks leading')
    if sum(1 for c in top7 if c in ('Energy','Inflation'))>=2: themes.append('Energy & commodities outperforming')
    if sum(1 for c in top7 if c in ('Tech Growth','AI Capex','AI Infra','Tech'))>=2: themes.append('Tech & AI theme leading')
    if sum(1 for c in top7 if c in ('Defensive','Fear'))>=2: themes.append('Money rotating into safe havens')
    if sum(1 for c in top7 if c=='Consumer')>=2: themes.append('Consumer stocks outperforming')
    if sum(1 for c in top7 if c=='Transport')>=2: themes.append('Transport stocks leading')
    if sum(1 for c in top7 if c=='EV/Battery')>=1: themes.append('EV/Battery theme strong')
    if sum(1 for c in bot7 if c=='Consumer')>=2: themes.append('Consumer stocks lagging')
    if sum(1 for c in bot7 if c in ('Industrial','Manufacturing'))>=2: themes.append('Industrial stocks lagging')
    if not themes: themes.append('No clear thematic rotation')
    catchphrase = {'cycle':cycle[:5],'themes':themes[:4]}
    bench_z_val = round(bench_z,2)
    print(f"  {label}: {len(baskets_out)} baskets, bench z={bench_z_val}, 200d={total_pct200}%")
    return {'date':zs.index[-1].strftime('%Y-%m-%d'),'spy_z':bench_z_val,'pct200':total_pct200,
            'params':{'lookback':lookback,'vol_window':vol_window},
            'baskets':baskets_out,'cat_order':cat_order,'catchphrase':catchphrase}

# ═══ 4. RUN ALL ═══
print("Global regime...")
g_strat = run_regime(daily_g, G_CAT_A, CAT_ORD, RATE_A, CURVE_A, SECTORS, CYCLICAL, DEFENSIVE, 25,130,15,15)
print(f"  STRATEGIC -> {g_strat['current']['label']}")
g_tact = run_regime(daily_g, G_CAT_A, CAT_ORD, RATE_A, CURVE_A, SECTORS, CYCLICAL, DEFENSIVE, 10,65,1,5)
print(f"  TACTICAL -> {g_tact['current']['label']}")

print("Global internals...")
gi_strat = run_internals(daily_gi, G_BASK, G_BCAT, 'SPY', 25,130,'G-STRATEGIC')
gi_tact = run_internals(daily_gi, G_BASK, G_BCAT, 'SPY', 10,65,'G-TACTICAL')

print("Korea regime...")
kr_sectors = KR_CAT_A.get('KR Equities',[]) + KR_CAT_A.get('KR Banks',[])
kr_strat = run_regime(daily_kr, KR_CAT_A, KR_CAT_ORD, KR_RATE_A, set(), kr_sectors, KR_SECTORS_CYC, KR_SECTORS_DEF, 25,130,15,15)
print(f"  STRATEGIC -> {kr_strat['current']['label']}")
kr_tact = run_regime(daily_kr, KR_CAT_A, KR_CAT_ORD, KR_RATE_A, set(), kr_sectors, KR_SECTORS_CYC, KR_SECTORS_DEF, 10,65,1,5)
print(f"  TACTICAL -> {kr_tact['current']['label']}")

print("Korea internals...")
ki_strat = run_internals(daily_ki, KR_BASK, KR_BCAT, '^KS11', 25,130,'KR-STRATEGIC')
ki_tact = run_internals(daily_ki, KR_BASK, KR_BCAT, '^KS11', 10,65,'KR-TACTICAL')

data = {
    'global':{'strategic':g_strat,'tactical':g_tact,'int_strategic':gi_strat,'int_tactical':gi_tact},
    'korea':{'strategic':kr_strat,'tactical':kr_tact,'int_strategic':ki_strat,'int_tactical':ki_tact},
}
data_str = json.dumps(data, separators=(',',':'))
print(f"Data JSON: {len(data_str)/1024:.0f} KB")

# ═══ 5. HTML ═══
FAVICON = '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'

html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Regime Monitor</title><link rel="icon" href="data:image/png;base64,{FAVICON}">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{{--bg:#fafaf9;--s:#fff;--b:#e7e5e4;--bl:#f5f5f4;--t:#1c1917;--t2:#57534e;--t3:#a8a29e;--g:#16a34a;--gb:#f0fdf4;--r:#dc2626;--rb:#fef2f2;--x:#78716c;--xb:#f5f5f4;--f:'DM Sans',sans-serif;--m:'JetBrains Mono',monospace}}
*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:var(--f);background:var(--bg);color:var(--t);font-size:13px;line-height:1.5}}
.c{{max-width:1200px;margin:0 auto;padding:16px 14px}}
header{{display:flex;justify-content:space-between;align-items:baseline;padding-bottom:12px;border-bottom:2px solid var(--t);margin-bottom:16px;flex-wrap:wrap;gap:8px}}
header h1{{font-family:var(--m);font-size:15px;font-weight:700;letter-spacing:-0.03em}}header .m{{font-size:11px;color:var(--t3);font-family:var(--m)}}
.tn{{display:flex;gap:0;margin-bottom:12px;border-radius:8px;overflow:hidden;border:2px solid var(--t)}}
.tn button{{flex:1;font-family:var(--m);font-size:13px;font-weight:800;letter-spacing:.02em;padding:12px 20px;border:none;cursor:pointer;transition:all .15s}}
.tn button.on{{background:var(--t);color:var(--bg)}}.tn button:not(.on){{background:var(--bg);color:var(--t3)}}
.sw{{display:flex;gap:0;margin-bottom:10px;border-radius:6px;overflow:hidden;border:1px solid var(--b)}}
.sw button{{flex:1;font-family:var(--m);font-size:11px;font-weight:700;padding:8px 16px;border:none;cursor:pointer}}
.sw button.on{{background:var(--t);color:var(--bg)}}.sw button:not(.on){{background:var(--s);color:var(--t3)}}
.md{{font-family:var(--m);font-size:9px;color:var(--t3);margin-bottom:14px;padding:6px 10px;background:var(--bl);border-radius:4px}}
.hero{{padding:24px 28px;border-radius:12px;margin-bottom:16px;text-align:center}}
.hero .lb{{font-family:var(--m);font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.12em;opacity:.7;margin-bottom:6px}}
.hero .nm{{font-family:var(--f);font-size:48px;font-weight:900;letter-spacing:-0.03em;line-height:1.1;margin-bottom:6px}}
.hero .cf{{font-family:var(--m);font-size:12px;font-weight:500;opacity:.8}}
.hero.OVERHEAT{{background:linear-gradient(135deg,#fffbeb,#fef3c7);color:#92400e;border:2px solid #fcd34d}}
.hero.GOLDILOCKS{{background:linear-gradient(135deg,#f0fdf4,#ecfdf5);color:#166534;border:2px solid #86efac}}
.hero.STAGFLATION{{background:linear-gradient(135deg,#faf5ff,#f3e8ff);color:#6b21a8;border:2px solid #c084fc}}
.hero.RECESSION{{background:linear-gradient(135deg,#fef2f2,#fee2e2);color:#991b1b;border:2px solid #fca5a5}}
.hero.CRISIS{{background:linear-gradient(135deg,#1c1917,#292524);color:#fef2f2;border:2px solid #57534e}}
.hero.SUPPLY_SHOCK{{background:linear-gradient(135deg,#fff7ed,#ffedd5);color:#9a3412;border:2px solid #fb923c}}
.fg{{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:5px;margin-bottom:16px}}
.fc{{padding:7px 9px;border-radius:6px;background:var(--s);border:1px solid var(--b)}}.fc .fn{{font-family:var(--m);font-size:8px;font-weight:600;text-transform:uppercase;color:var(--t3);margin-bottom:2px}}.fc .fv{{font-family:var(--m);font-size:16px;font-weight:700}}.fc .fv.pos{{color:var(--g)}}.fc .fv.neg{{color:var(--r)}}.fc .fv.neu{{color:var(--x)}}
.tw{{position:relative}}.tb{{display:flex;height:32px;border-radius:6px;overflow:hidden;margin-bottom:4px;border:1px solid var(--b)}}
.ts{{min-width:3px;cursor:pointer;transition:opacity .15s}}.ts:hover{{opacity:.8;outline:2px solid var(--t);outline-offset:-2px;z-index:2}}
.tt{{display:none;position:absolute;top:-44px;left:50%;transform:translateX(-50%);background:var(--t);color:var(--s);padding:5px 9px;border-radius:6px;font-family:var(--m);font-size:9px;white-space:nowrap;pointer-events:none;z-index:10}}
.tt::after{{content:'';position:absolute;bottom:-5px;left:50%;transform:translateX(-50%);border-left:5px solid transparent;border-right:5px solid transparent;border-top:5px solid var(--t)}}
.tl{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;font-family:var(--m);font-size:9px;color:var(--t2)}}.tl span{{display:flex;align-items:center;gap:3px}}.tl .dot{{width:9px;height:9px;border-radius:2px}}
.td{{display:flex;justify-content:space-between;font-family:var(--m);font-size:9px;color:var(--t3);margin-bottom:10px}}
.mt{{display:flex;gap:2px;margin-bottom:10px;background:var(--bl);border-radius:6px;padding:2px;width:fit-content}}.mt button{{font-family:var(--m);font-size:10px;font-weight:600;padding:4px 10px;border:none;border-radius:4px;background:0;color:var(--t3);cursor:pointer}}.mt button.on{{background:var(--s);color:var(--t);box-shadow:0 1px 3px rgba(0,0,0,.06)}}
.cb{{margin-bottom:5px;border:1px solid var(--b);border-radius:6px;background:var(--s);overflow:hidden}}.ch{{display:flex;justify-content:space-between;align-items:center;padding:5px 10px;cursor:pointer}}.ch:hover{{background:var(--bl)}}.ch h2{{font-size:10px;font-weight:700}}.ch .st{{display:flex;align-items:center;gap:5px;font-family:var(--m);font-size:9px}}.ch .d{{width:5px;height:5px;border-radius:50%;display:inline-block}}
.cg{{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:3px;padding:3px 6px 5px}}.a{{display:flex;align-items:center;gap:4px;padding:3px 6px;border-radius:4px;border-left:3px solid transparent}}.a.bu{{border-left-color:var(--g);background:var(--gb)}}.a.be{{border-left-color:var(--r);background:var(--rb)}}.ai{{flex:1;min-width:0}}.an{{font-family:var(--m);font-size:9px;font-weight:600}}.ar{{display:flex;justify-content:space-between;margin-top:1px}}.ap{{font-size:8px;color:var(--t3)}}.az{{font-family:var(--m);font-size:9px;font-weight:600}}.al{{font-family:var(--m);font-size:7px;font-weight:700;text-transform:uppercase;padding:1px 3px;border-radius:2px}}.al.bu{{color:var(--g);background:var(--gb)}}.al.be{{color:var(--r);background:var(--rb)}}.al.si{{color:var(--x);background:var(--xb)}}
.rp{{margin-bottom:10px;padding:10px;border-radius:8px;background:var(--s);border:1px solid var(--b)}}.rp h3{{font-family:var(--m);font-size:10px;font-weight:700;margin-bottom:6px}}.rp .br{{display:flex;align-items:center;gap:5px;margin-bottom:2px}}.rp .bl{{font-family:var(--m);font-size:8px;width:65px;text-align:right;color:var(--t2)}}.rp .bt{{flex:1;height:5px;background:var(--bl);border-radius:3px;position:relative}}.rp .bf{{height:5px;border-radius:3px;position:absolute;top:0}}.rp .bv{{font-family:var(--m);font-size:8px;width:32px;font-weight:600}}
.me{{margin-top:12px;padding:10px;border-radius:6px;background:var(--bl);border:1px solid var(--b)}}.me h3{{font-family:var(--m);font-size:9px;font-weight:700;color:var(--t2);text-transform:uppercase;margin-bottom:4px}}.me p{{font-size:10px;color:var(--t2);line-height:1.6}}
footer{{margin-top:16px;padding-top:8px;border-top:1px solid var(--b);font-size:8px;color:var(--t3);text-align:center;font-family:var(--m)}}
.sc{{display:flex;gap:3px;align-items:center;font-family:var(--m);font-size:9px;color:var(--t3);margin-bottom:6px}}.sc button{{font-family:var(--m);font-size:8px;padding:2px 6px;border:1px solid var(--b);border-radius:3px;background:var(--s);color:var(--t2);cursor:pointer}}.sc button.on{{background:var(--t);color:var(--s);border-color:var(--t)}}
.bgrid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:5px;margin-bottom:12px}}
.bc{{padding:9px 10px;border-radius:6px;background:var(--s);border:1px solid var(--b);cursor:pointer;transition:all .15s}}.bc:hover{{border-color:var(--t3)}}
.bc .bn{{font-family:var(--m);font-size:10px;font-weight:700;margin-bottom:3px;display:flex;justify-content:space-between;align-items:center}}
.bc .bz{{font-family:var(--m);font-size:18px;font-weight:800}}.bc .bz.pos{{color:var(--g)}}.bc .bz.neg{{color:var(--r)}}.bc .bz.neu{{color:var(--x)}}
.bc .bsub{{font-family:var(--m);font-size:8px;color:var(--t3);margin-top:2px}}
.bc .bst{{display:none;margin-top:6px;padding-top:5px;border-top:1px solid var(--bl)}}.bc.open .bst{{display:block}}
.bc .bs{{display:flex;justify-content:space-between;font-family:var(--m);font-size:8px;padding:2px 0;border-bottom:1px solid var(--bl)}}.bc .bs .st{{font-weight:600}}.bc .bs .sz{{font-weight:700}}
.bcat{{margin-bottom:12px}}.bcat h3{{font-family:var(--m);font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--t3);margin-bottom:5px;padding-bottom:3px;border-bottom:1px solid var(--b)}}
.sig{{display:flex;gap:10px;margin-bottom:14px}}.sig>div{{flex:1;padding:14px;border-radius:10px;background:var(--s);border:1px solid var(--b)}}.sig .sh{{font-family:var(--m);font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:var(--t3);margin-bottom:6px}}.sig .sl{{font-family:var(--m);font-size:12px;font-weight:600;line-height:1.7}}
@media(max-width:640px){{.cg{{grid-template-columns:1fr 1fr}}.hero .nm{{font-size:32px}}.fg{{grid-template-columns:repeat(3,1fr)}}.sig{{flex-direction:column;gap:6px}}.bgrid{{grid-template-columns:1fr}}}}
</style></head><body><div class="c" id="app"></div>
<script>
const D={data_str};
const RC={{'OVERHEAT':'#eab308','GOLDILOCKS':'#16a34a','STAGFLATION':'#9333ea','RECESSION':'#dc2626','CRISIS':'#1c1917','SUPPLY SHOCK':'#ea580c'}};
const ib=r=>r==='bull'||r==='falling'||r==='steepening';const ie=r=>r==='bear'||r==='rising'||r==='flattening';
const rc=r=>ib(r)?'bu':ie(r)?'be':'si';const rl=r=>({{bull:'BULL',bear:'BEAR',sideways:'SIDE',rising:'UP',falling:'DOWN',stable:'FLAT',steepening:'STEEP',flattening:'FLAT'}}[r]||'-');
const tc=r=>ib(r)?'var(--g)':ie(r)?'var(--r)':'var(--x)';
const fP=(p,n)=>{{if(p==null)return'-';if(p>10000)return p.toLocaleString('en',{{maximumFractionDigits:0}});if(p>100)return p.toLocaleString('en',{{maximumFractionDigits:1}});return p<1?p.toFixed(4):p.toFixed(2)}};
const cl=n=>n.replace('cat_','').replace(/_/g,' ');
let S={{region:'global',page:'regime',model:'strategic',view:'regime',sort:'default'}};
function R(){{return D[S.region]}}
function render(){{
const app=document.getElementById('app');const r=R();
let h='<header><h1>Regime Monitor</h1><div class="m">'+r.strategic.date+'</div></header>';
h+='<div class="tn">';[['global','Global'],['korea','Korea']].forEach(([k,v])=>{{h+='<button class="'+(S.region===k?'on':'')+'" onclick="U(\\'region\\',\\''+k+'\\')">'+v+'</button>'}});h+='</div>';
h+='<div class="sw">';[['regime','Macro Indicators'],['internals','Stock Market Internals']].forEach(([k,v])=>{{h+='<button class="'+(S.page===k?'on':'')+'" onclick="U(\\'page\\',\\''+k+'\\')">'+v+'</button>'}});h+='</div>';
if(S.page==='regime')h+=pgRegime();else h+=pgInternals();
h+='<footer>4+2 Investment Clock + Market Internals \\u00b7 Global + Korea \\u00b7 Daily</footer>';
app.innerHTML=h}}
function pgRegime(){{
const d=R()[S.model];const p=d.params;const cur=d.current;
let h='<div class="sw">';['strategic','tactical'].forEach(m=>{{h+='<button class="'+(S.model===m?'on':'')+'" onclick="U(\\'model\\',\\''+m+'\\')">'+m[0].toUpperCase()+m.slice(1)+'</button>'}});h+='</div>';
h+='<div class="md">'+S.model[0].toUpperCase()+S.model.slice(1)+' \\u2014 '+p.lookback+'d lookback \\u00b7 '+p.vol_window+'d vol'+(p.smooth>1?' \\u00b7 '+p.smooth+'d smooth':'')+'</div>';
const hc=cur.label.replace(/ /g,'_');
h+='<div class="hero '+hc+'"><div class="lb">'+S.region[0].toUpperCase()+S.region.slice(1)+' '+S.model[0].toUpperCase()+S.model.slice(1)+' Regime</div><div class="nm">'+cur.label+'</div><div class="cf">Growth: '+(cur.growth>=0?'+':'')+cur.growth.toFixed(2)+' \\u00b7 Inflation: '+(cur.inflation>=0?'+':'')+cur.inflation.toFixed(2)+'</div></div>';
const f=cur.features;const fk=Object.keys(f);
h+='<div class="fg">';fk.forEach(fn=>{{const v=f[fn];if(v==null)return;const c2=v>0.3?'pos':v<-0.3?'neg':'neu';h+='<div class="fc"><div class="fn">'+cl(fn)+'</div><div class="fv '+c2+'">'+(v>0?'+':'')+v.toFixed(2)+'</div></div>'}});h+='</div>';
h+=mkTL(d);
h+='<div class="mt">';['regime','assets','method'].forEach(v=>{{h+='<button class="'+(S.view===v?'on':'')+'" onclick="U(\\'view\\',\\''+v+'\\')">'+v+'</button>'}});h+='</div>';
if(S.view==='regime')h+=vReg(d);else if(S.view==='assets')h+=vAss(d);else h+=vMth(d);
return h}}
function pgInternals(){{
const ik=S.model==='tactical'?'int_tactical':'int_strategic';const I=R()[ik];const bs=I.baskets;const co=I.cat_order;
let h='<div class="sw">';['strategic','tactical'].forEach(m=>{{h+='<button class="'+(S.model===m?'on':'')+'" onclick="U(\\'model\\',\\''+m+'\\')">'+m[0].toUpperCase()+m.slice(1)+'</button>'}});h+='</div>';
const p=I.params;h+='<div class="md">'+S.model[0].toUpperCase()+S.model.slice(1)+' \\u2014 '+p.lookback+'d lookback \\u00b7 '+p.vol_window+'d vol \\u00b7 '+bs.length+' baskets \\u00b7 Bench z: '+(I.spy_z>=0?'+':'')+I.spy_z.toFixed(2)+(I.pct200!=null?' \\u00b7 200d breadth: '+I.pct200+'%':'')+'</div>';
const cp=I.catchphrase;
h+='<div class="sig"><div><div class="sh">Cycle Assessment</div><div class="sl">'+cp.cycle.join('<br>')+'</div></div><div><div class="sh">Thematic Rotation</div><div class="sl">'+cp.themes.join('<br>')+'</div></div></div>';
h+='<div class="sc">Sort: <button class="'+(S.sort==='rel'||S.sort==='default'?'on':'')+'" onclick="U(\\'sort\\',\\'rel\\')">Rel \\u2193</button><button class="'+(S.sort==='abs'?'on':'')+'" onclick="U(\\'sort\\',\\'abs\\')">Abs \\u2193</button><button class="'+(S.sort==='cat'?'on':'')+'" onclick="U(\\'sort\\',\\'cat\\')">Category</button></div>';
if(S.sort==='cat'){{co.forEach(cat=>{{const cbs=bs.filter(b=>b.cat===cat);if(!cbs.length)return;h+='<div class="bcat"><h3>'+cat+' ('+cbs.length+')</h3><div class="bgrid">';cbs.sort((a,b)=>b.rel-a.rel);cbs.forEach(b=>{{h+=mkBC(b)}});h+='</div></div>'}})}}
else{{const sorted=S.sort==='abs'?[...bs].sort((a,b)=>Math.abs(b.z)-Math.abs(a.z)):[...bs].sort((a,b)=>b.rel-a.rel);h+='<div class="bgrid">';sorted.forEach(b=>{{h+=mkBC(b)}});h+='</div>'}}
return h}}
function mkBC(b){{const zc=b.rel>0.5?'pos':b.rel<-0.5?'neg':'neu';let h='<div class="bc" onclick="this.classList.toggle(\\'open\\')"><div class="bn"><span>'+b.name+'</span><span class="al '+(b.rel>0.3?'bu':b.rel<-0.3?'be':'si')+'">'+( b.rel>0?'OUT':'UNDER')+'</span></div><div class="bz '+zc+'">'+(b.rel>=0?'+':'')+b.rel.toFixed(2)+'</div><div class="bsub">'+b.cat+(b.pct200!=null?' \\u00b7 '+b.pct200+'% >200d':'')+'</div><div class="bst">';b.stocks.forEach(s=>{{const sc=s.rz>0.3?'var(--g)':s.rz<-0.3?'var(--r)':'var(--x)';const a2=s.a200===true?'\\u25b2':s.a200===false?'\\u25bc':'';h+='<div class="bs"><span class="st">'+s.t+'</span><span>'+a2+(s.p?fP(s.p,s.t):'')+'</span><span class="sz" style="color:'+sc+'">'+(s.rz>=0?'+':'')+s.rz.toFixed(2)+'</span></div>'}});h+='</div></div>';return h}}
function showT(el){{const t=document.getElementById('tip');if(!t)return;const r=el.getBoundingClientRect();const p=el.parentElement.getBoundingClientRect();t.innerHTML='<b>'+el.dataset.label+'</b><br><span style="opacity:.7;font-size:8px">'+el.dataset.start+' \\u2192 '+el.dataset.end+'</span>';t.style.display='block';t.style.left=(r.left+r.width/2-p.left)+'px';t.style.top='-44px'}}
function hideT(){{const t=document.getElementById('tip');if(t)t.style.display='none'}}
function mkTL(d){{const tl=d.timeline;if(!tl||!tl.length)return'';const t0=new Date(tl[0].start).getTime();const t1=new Date(tl[tl.length-1].end).getTime()+864e5;const sp=t1-t0||1;let h='<div class="tw"><div id="tip" class="tt"></div><div class="tb">';tl.forEach((s,i)=>{{const a=new Date(s.start).getTime();const b=new Date(s.end).getTime()+864e5;const w=Math.max(0.5,((b-a)/sp)*100);const col=RC[s.l]||'#a8a29e';h+='<div class="ts" style="width:'+w+'%;background:'+col+(i===tl.length-1?';box-shadow:inset 0 0 0 2px rgba(0,0,0,.3)':'')+'" data-label="'+s.l+'" data-start="'+s.start+'" data-end="'+s.end+'" onmouseenter="showT(this)" onmouseleave="hideT()"></div>'}});h+='</div></div><div class="td"><span>'+tl[0].start+'</span><span>'+tl[tl.length-1].end+'</span></div>';const seen=new Set();h+='<div class="tl">';tl.forEach(s=>{{if(!seen.has(s.l)){{seen.add(s.l);h+='<span><span class="dot" style="background:'+(RC[s.l]||'#a8a29e')+'"></span>'+s.l+'</span>'}}}});h+='</div>';return h}}
function vReg(d){{let h='';Object.values(d.regimes).forEach(info=>{{const col=RC[info.label]||'#a8a29e';const ic=info.label===d.current.label;h+='<div class="rp" style="'+(ic?'border:2px solid '+col:'')+'"><h3 style="color:'+col+'">'+(ic?'\\u25b6 ':'')+info.label+' \\u2014 '+info.n_days+'d ('+info.pct+'%)</h3><div style="font-size:9px;color:var(--t3);margin-bottom:6px">'+info.periods.slice(0,4).join(', ')+'</div>';const p=info.profile;Object.entries(p).slice(0,8).forEach(([fn,v])=>{{const pct=Math.min(100,Math.abs(v)*30);const c2=v>0.2?'var(--g)':v<-0.2?'var(--r)':'var(--x)';const left=v>=0?'50%':(50-pct)+'%';h+='<div class="br"><span class="bl">'+cl(fn)+'</span><div class="bt"><div class="bf" style="left:'+left+'%;width:'+pct+'%;background:'+c2+'"></div><div style="position:absolute;left:50%;top:0;width:1px;height:5px;background:var(--b)"></div></div><span class="bv" style="color:'+c2+'">'+(v>0?'+':'')+v.toFixed(2)+'</span></div>'}});h+='</div>'}});return h}}
function vAss(d){{const cats=d.assets;const CO=d.cat_order;let h='';CO.forEach(k=>{{const a2=cats[k];if(!a2)return;let en=Object.entries(a2);const nb=en.filter(([,x])=>ib(x.regime)).length,nr=en.filter(([,x])=>ie(x.regime)).length,ns=en.length-nb-nr;h+='<div class="cb"><div class="ch"><h2>'+k+'</h2><div class="st">';if(nb)h+='<span><span class="d" style="background:var(--g)"></span>'+nb+'</span>';if(ns)h+='<span><span class="d" style="background:var(--x)"></span>'+ns+'</span>';if(nr)h+='<span><span class="d" style="background:var(--r)"></span>'+nr+'</span>';h+='</div></div><div class="cg">';en.forEach(([n,x])=>{{const c=rc(x.regime),z=x.score,zc=tc(x.regime);h+='<div class="a '+c+'"><div class="ai"><div style="display:flex;justify-content:space-between;align-items:center"><span class="an">'+n+'</span><span class="al '+c+'">'+rl(x.regime)+'</span></div><div class="ar"><span class="ap">'+fP(x.price,n)+'</span><span class="az" style="color:'+zc+'">'+(z!=null?(z>0?'+':'')+z.toFixed(2):'-')+'</span></div></div></div>'}});h+='</div></div>'}});return h}}
function vMth(d){{const p=d.params;return'<div class="me"><h3>4+2 Investment Clock</h3><p><b>Growth</b> = (Equities + Credit/Banks + Cyclical/Defensive) / 3<br><b>Inflation</b> = (Energy + Rates/Currency + Energy vs Tech) / 3<br><br>G\\u22650 I\\u22650 \\u2192 OVERHEAT \\u00b7 G\\u22650 I&lt;0 \\u2192 GOLDILOCKS<br>G&lt;0 I\\u22650 \\u2192 STAGFLATION \\u00b7 G&lt;0 I&lt;0 \\u2192 RECESSION<br>CRISIS: broad collapse \\u00b7 SUPPLY SHOCK: energy extreme<br><br>'+p.lookback+'d lookback, '+p.vol_window+'d vol'+(p.smooth>1?', '+p.smooth+'d smooth':'')+', '+p.min_dur+'d min</p></div>'}}
function U(k,v){{S[k]=v;render()}}render();
</script></body></html>"""

with open('index.html', 'w') as f:
    f.write(html)
print(f"OK index.html: {len(html)/1024:.1f} KB")
