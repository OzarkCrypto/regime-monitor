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
    'Money Ctr Banks':{'t':['JPM','BAC','C','WFC','GS'],'cat':'Credit Cycle'},
    'Consumer Staples':{'t':['PG','KO','PEP','CL','MDLZ'],'cat':'Defensive'},
    'Retail':{'t':['WMT','TGT','COST','HD','LOW'],'cat':'Consumer'},
    'Payments':{'t':['V','MA','PYPL','XYZ'],'cat':'Consumer'},
    'Digital Ads':{'t':['GOOGL','META','TTD','SNAP'],'cat':'Capex'},
    'Broad Semis':{'t':['NVDA','AMD','MU','QCOM','INTC'],'cat':'Inventory Cycle'},
    'Life Insurance':{'t':['MET','PRU','AFL','LNC'],'cat':'Rate Sensitive'},
    'Aerospace OEM':{'t':['BA','GE','TDG','HWM'],'cat':'Capex'},
    'Healthcare Svc':{'t':['UNH','HCA','THC','CI'],'cat':'Healthcare'},
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
    'KR Securities':{'t':['006800.KS','071050.KS','005940.KS'],'cat':'Financials'},
    'KR Insurance':{'t':['000810.KS','005830.KS','088350.KS'],'cat':'Rate Sensitive'},
    'KR Food':{'t':['003230.KS','007310.KS','004370.KS','097950.KS'],'cat':'Defensive'},
    'KR Cosmetics':{'t':['090430.KS','051900.KS','192820.KQ'],'cat':'Consumer'},
    'KR Logistics':{'t':['000120.KS','086280.KS'],'cat':'Transport'},
    'KR Airlines':{'t':['003490.KS','089590.KS'],'cat':'Transport'},
    'KR Leisure':{'t':['008770.KS','034230.KS','035250.KS'],'cat':'Consumer'},
    'KR Semi Equip':{'t':['042700.KQ','036930.KQ','240810.KS'],'cat':'Tech'},
    'KR Batt Materials':{'t':['247540.KQ','066970.KS','278280.KQ'],'cat':'EV/Battery'},
}
KR_BCAT = ['Tech','EV/Battery','Industrial','Geopolitics','Consumer','Transport',
            'Rate Sensitive','Financials','Healthcare','Energy','Defensive','Automation']

# ═══ 52-WEEK HIGH: BROAD UNIVERSE ═══
# Korean stock name map: ticker code -> Korean name (~250 stocks covering KOSPI/KOSDAQ major)
KR_NAMES_FALLBACK = {
    # Top 30 by market cap
    '005930':'삼성전자','000660':'SK하이닉스','005380':'현대자동차','000270':'기아',
    '005490':'POSCO홀딩스','035420':'NAVER','035720':'카카오','051910':'LG화학',
    '006400':'삼성SDI','373220':'LG에너지솔루션','207940':'삼성바이오로직스',
    '068270':'셀트리온','105560':'KB금융','055550':'신한지주','086790':'하나금융지주',
    '316140':'우리금융지주','003550':'LG','000810':'삼성화재','034730':'SK',
    '032830':'삼성생명','066570':'LG전자','012330':'현대모비스','028260':'삼성물산',
    '096770':'SK이노베이션','009150':'삼성전기','015760':'한국전력',
    '017670':'SK텔레콤','030200':'KT','402340':'SK스퀘어',
    # Defense/Aerospace
    '012450':'한화에어로스페이스','079550':'LIG넥스원','047810':'한국항공우주',
    '272210':'한화시스템','298040':'효성중공업','000880':'한화',
    # Nuclear/Energy
    '034020':'두산에너빌리티','052690':'한전기술','267260':'HD현대일렉트릭',
    '036460':'한국가스공사','010950':'S-Oil','336260':'두산퓨얼셀',
    # Construction ★ EXPANDED
    '000720':'현대건설','006360':'GS건설','375500':'DL이앤씨','047040':'대우건설',
    '000210':'DL','044490':'태웅','294870':'HDC현대산업개발','002960':'한국쉘석유',
    '014820':'동원시스템즈','069960':'현대백화점','047050':'포스코인터내셔널',
    # Shipbuilding
    '329180':'HD한국조선해양','010140':'삼성중공업','042660':'한화오션',
    '009540':'HD한국조선','267250':'HD현대',
    # Steel/Chemical
    '004020':'현대제철','011170':'롯데케미칼','011780':'금호석유화학',
    '009830':'한화솔루션','005490':'POSCO홀딩스',
    # Banks/Securities/Insurance
    '138040':'메리츠금융지주','024110':'기업은행','006800':'미래에셋증권',
    '071050':'한국금융지주','005940':'NH투자증권','000810':'삼성화재',
    '005830':'DB손해보험','088350':'한화생명','016360':'삼성증권',
    '001450':'현대해상','003490':'대한항공',
    # Auto/Parts
    '161390':'한국타이어',
    # Food/Beverages
    '003230':'삼양식품','007310':'오뚜기','004370':'농심','097950':'CJ제일제당',
    '271560':'오리온','033780':'KT&G',
    # Retail/Consumer
    '004170':'신세계','139480':'이마트','020000':'한섬','383220':'F&F',
    # Internet/Software
    '018260':'삼성SDS','323410':'카카오뱅크','036570':'NCsoft',
    # Entertainment/Gaming
    '259960':'크래프톤','251270':'넷마블','352820':'하이브',
    '041510':'SM엔터','035900':'JYP엔터','263750':'펄어비스',
    # Bio/Pharma
    '128940':'한미약품','326030':'SK바이오팜','195940':'HK이노엔',
    '003850':'보령','009420':'한올바이오파마','214370':'케어젠',
    # Cosmetics
    '090430':'아모레퍼시픽','051900':'LG생활건강',
    # Logistics/Travel
    '000120':'CJ대한통운','086280':'현대글로비스','089590':'제주항공',
    '180640':'한진칼','008770':'호텔신라','034230':'파라다이스','035250':'강원랜드',
    # Conglomerates/Holdings
    '078930':'GS','004990':'롯데지주','001040':'CJ','000150':'두산',
    '003670':'포스코퓨처엠',
    # Utility/Telecom
    '010130':'고려아연','241560':'두산밥캣',
    # Semi/Tech
    '042700':'한미반도체','036930':'주성엔지니어링','058470':'리노공업',
    '240810':'원익IPS','112610':'씨에스윈드','357780':'솔브레인',
    # Battery materials
    '247540':'에코프로비엠','066970':'엘앤에프','278280':'천보',
    # Robotics
    '454910':'두산로보틱스','277810':'레인보우로보틱스',
    # KOSDAQ majors
    '192820':'코스맥스','039030':'이오테크닉스','095340':'ISC',
    '403870':'HPSP','214150':'클래시스','145020':'휴젤','328130':'루닛',
    '086900':'메디톡스','067160':'아프리카TV','293490':'카카오게임즈',
    '352480':'씨이랩','361610':'SK아이이테크놀로지','178920':'PI첨단소재',
    # Additional important stocks
    '006280':'녹십자','285130':'SK케미칼','950160':'코오롱인더',
    '307950':'현대오토에버','377300':'카카오페이','002380':'KCC',
    '111770':'영원무역','003410':'쌍용C&E','069500':'KODEX200',
    # Extra construction/infra/civil engineering
    '000150':'두산','047050':'포스코인터내셔널',
}

def scrape_us_52w_highs():
    """Scrape Finviz for US stocks at 52-week new high. All exchanges, all market caps."""
    import requests, time
    from io import StringIO
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    all_stocks = []
    for start in range(1, 3000, 20):
        try:
            url = f'https://finviz.com/screener.ashx?v=111&f=ind_stocksonly,ta_highlow52w_nh&ft=4&r={start}'
            r = requests.get(url, headers=headers, timeout=15)
            tables = pd.read_html(StringIO(r.text), flavor='html5lib')
            found = None
            for t in tables:
                if len(t.columns) == 11:
                    first_col = t.iloc[:,0]
                    if pd.to_numeric(first_col, errors='coerce').notna().sum() >= 1:
                        found = t; break
            if found is None or len(found) == 0: break
            all_stocks.append(found)
            if len(found) < 20: break
            time.sleep(0.3)
        except: break
    if not all_stocks: return []
    df = pd.concat(all_stocks, ignore_index=True)
    df.columns = ['No','Ticker','Company','Sector','Industry','Country','MCap','PE','Price','Change','Volume']
    df = df[pd.to_numeric(df['No'], errors='coerce').notna()].copy()
    # Filter: only stocks, not ETFs/ETNs (keep stocks-only by excluding known ETF patterns)
    highs = []
    for _, row in df.iterrows():
        try:
            price = float(str(row['Price']).replace(',',''))
            highs.append({'t': str(row['Ticker']).strip(), 'n': str(row['Company']).strip(),
                         'p': round(price, 2), 'sector': str(row['Sector']).strip(), 'pct': 0.0})
        except: pass
    print(f"  Finviz: {len(highs)} US stocks at 52-week new high")
    return highs

def scrape_kr_52w_highs():
    """Get Korean stocks at 52-week high via pykrx (KRX direct) then Naver fallback."""
    # Method 1: pykrx
    try:
        from pykrx import stock
        from datetime import timedelta
        print("  KR: trying pykrx (KRX API)...")
        today_str = None
        for delta in range(0, 10):
            dt = (datetime.now() - timedelta(days=delta)).strftime('%Y%m%d')
            tickers = stock.get_market_ticker_list(dt, market='KOSPI')
            if tickers: today_str = dt; break
        if not today_str: raise Exception("No trading date found")
        kospi = stock.get_market_ticker_list(today_str, market='KOSPI')
        kosdaq = stock.get_market_ticker_list(today_str, market='KOSDAQ')
        all_kr = kospi + kosdaq
        print(f"  pykrx: {len(kospi)} KOSPI + {len(kosdaq)} KOSDAQ")
        ohlcv_today = stock.get_market_ohlcv_by_ticker(today_str)
        year_ago = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        max_highs = pd.Series(dtype='float64')
        sample_dates = pd.bdate_range(year_ago, today_str, freq='5D')
        for sd in sample_dates:
            try:
                d = stock.get_market_ohlcv_by_ticker(sd.strftime('%Y%m%d'))
                if len(d) > 0 and '고가' in d.columns:
                    h = d['고가']
                    max_highs = max_highs.combine(h, max, fill_value=0) if len(max_highs) > 0 else h
            except: pass
        print(f"  pykrx: sampled {len(sample_dates)} dates")
        if '고가' in ohlcv_today.columns:
            max_highs = max_highs.combine(ohlcv_today['고가'], max, fill_value=0) if len(max_highs) > 0 else ohlcv_today['고가']
        highs = []
        for ticker in all_kr:
            try:
                if ticker not in ohlcv_today.index: continue
                cur = float(ohlcv_today.loc[ticker, '종가'])
                if cur <= 0: continue
                h52 = float(max_highs.get(ticker, 0))
                if h52 <= 0: continue
                pct = (cur / h52 - 1) * 100
                if pct >= -0.5:
                    name = stock.get_market_ticker_name(ticker)
                    highs.append({'t': ticker, 'n': name, 'p': round(cur, 0), 'pct': round(pct, 1)})
            except: pass
        highs.sort(key=lambda x: -x['pct'])
        print(f"  pykrx: {len(highs)} KR stocks at 52-week high")
        if highs: return highs
    except Exception as e:
        print(f"  pykrx failed: {e}")
    # Method 2: Naver Finance
    try:
        import requests
        from io import StringIO
        print("  KR: trying Naver Finance...")
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
        all_stocks = []
        for sosok in [1, 2]:
            for page in range(1, 30):
                try:
                    url = f'https://finance.naver.com/sise/sise_new_high.naver?sosok={sosok}&page={page}'
                    r = requests.get(url, headers=headers, timeout=10)
                    if r.status_code != 200: break
                    r.encoding = 'euc-kr'
                    tables = pd.read_html(StringIO(r.text), flavor='html5lib')
                    found = None
                    for t in tables:
                        if len(t) >= 3 and len(t.columns) >= 8:
                            try:
                                num_check = pd.to_numeric(t.iloc[:,3].dropna(), errors='coerce')
                                if num_check.notna().sum() >= 2: found = t; break
                            except: pass
                    if found is None or len(found) < 2: break
                    found = found.dropna(how='all')
                    found = found[found.iloc[:,1].notna()]
                    all_stocks.append(found)
                    if len(found) < 20: break
                except: break
        if all_stocks:
            df = pd.concat(all_stocks, ignore_index=True)
            highs = []
            for _, row in df.iterrows():
                try:
                    name = str(row.iloc[1]).strip()
                    price = float(str(row.iloc[3]).replace(',',''))
                    if name and price > 0 and len(name) > 1:
                        highs.append({'t': '', 'n': name, 'p': round(price, 0), 'pct': 0.0})
                except: pass
            print(f"  Naver: {len(highs)} KR stocks")
            if highs: return highs
    except Exception as e:
        print(f"  Naver failed: {e}")
    return None

def fallback_kr_52w_highs(raw):
    """Compute 52-week highs from basket tickers as fallback"""
    highs = []
    for t in raw.columns.get_level_values(0).unique():
        t = str(t)
        if '.KS' not in t and '.KQ' not in t: continue
        try:
            s = raw[t]['Close'].squeeze()
            if not isinstance(s, pd.Series) or s.notna().sum() < 200: continue
            s = s.dropna()
            cur = float(s.iloc[-1])
            lb = min(252, len(s)-1)
            h252 = float(s.iloc[-lb:].max())
            if h252 <= 0: continue
            pct = (cur/h252-1)*100
            if pct >= -2.0:
                code = t.replace('.KS','').replace('.KQ','')
                name = KR_NAMES_FALLBACK.get(code, code)
                highs.append({'t':code,'n':name,'p':round(cur,0),'pct':round(pct,1)})
        except: pass
    highs.sort(key=lambda x: -x['pct'])
    return highs

# ═══ 1. DOWNLOAD ═══
print(f"Regime Monitor v2: {START} -> {END}")

# Phase 1: Regime + Basket tickers (full history)
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

print(f"Downloading {len(all_tickers)} regime+basket tickers...")
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
daily_g = df_g.dropna(how='all')
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
daily_kr = df_kr.dropna(how='all')
KR_CAT_A = {}
for cat, tks in KR_UNI.items():
    assets = [n for n in tks.values() if n in daily_kr.columns]
    if assets: KR_CAT_A[cat] = assets

# Global internals data
g_int_tks = set(['SPY'])
for bn, bi in G_BASK.items():
    for t in bi['t']: g_int_tks.add(t)
df_gi, gi_ok = parse_raw_tickers(g_int_tks)
daily_gi = df_gi.dropna(how='all')

# Korea internals data
kr_int_tks = set(['^KS11'])
for bn, bi in KR_BASK.items():
    for t in bi['t']: kr_int_tks.add(t)
df_ki, ki_ok = parse_raw_tickers(kr_int_tks)
daily_ki = df_ki.dropna(how='all')

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
    if n_out == 0: cycle.append(f'No baskets beating the market — everything lagging')
    elif breadth_pct>=60: cycle.append(f'{n_out} of {n_total} baskets beating the market — broad strength')
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
    # Discretionary vs Staples
    disc_s = [b['rel'] for b in baskets_out if b['cat']=='Consumer']
    stap_s = [b['rel'] for b in baskets_out if b['name'] in ('Consumer Staples','KR Food') or (b['cat']=='Defensive' and 'Staple' in b['name'])]
    if disc_s and stap_s:
        dvs = np.mean(disc_s) - np.mean(stap_s)
        if dvs > 0.5: cycle.append('Discretionary spending stocks beating staples — consumer confident')
        elif dvs < -0.5: cycle.append('Staples beating discretionary — consumer pulling back to essentials')
    # Payments as real-time spending indicator
    pay_b = [b for b in baskets_out if b['name']=='Payments']
    if pay_b and pay_b[0]['rel'] < -0.5:
        cycle.append('Payment stocks weak — transaction volumes may be slowing')
    elif pay_b and pay_b[0]['rel'] > 0.5:
        cycle.append('Payment stocks strong — transaction volumes healthy')
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

# ═══ 52-WEEK HIGHS (scraping) ═══
print("52-week highs (scraping)...")
try:
    us_highs = scrape_us_52w_highs()
except Exception as e:
    print(f"  US scraping failed: {e}")
    us_highs = []

try:
    kr_highs = scrape_kr_52w_highs()
except Exception as e:
    print(f"  KR scraping failed: {e}")
    kr_highs = None

if kr_highs is None:
    kr_highs = fallback_kr_52w_highs(raw)
    print(f"  KR fallback: {len(kr_highs)} stocks from basket universe")

print(f"  Final: US={len(us_highs)} | KR={len(kr_highs)}")

data = {
    'global':{'strategic':g_strat,'tactical':g_tact,'int_strategic':gi_strat,'int_tactical':gi_tact},
    'korea':{'strategic':kr_strat,'tactical':kr_tact,'int_strategic':ki_strat,'int_tactical':ki_tact},
    'highs_us': us_highs[:200],
    'highs_kr': kr_highs[:200],
}
data_str = json.dumps(data, separators=(',',':'))
print(f"Data JSON: {len(data_str)/1024:.0f} KB")

# ═══ 5. HTML ═══
FAVICON = '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'

LOGO = '/9j/4AAQSkZJRgABAQAAAQABAAD/4gHYSUNDX1BST0ZJTEUAAQEAAAHIAAAAAAQwAABtbnRyUkdCIFhZWiAH4AABAAEAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAACRyWFlaAAABFAAAABRnWFlaAAABKAAAABRiWFlaAAABPAAAABR3dHB0AAABUAAAABRyVFJDAAABZAAAAChnVFJDAAABZAAAAChiVFJDAAABZAAAAChjcHJ0AAABjAAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAAgAAAAcAHMAUgBHAEJYWVogAAAAAAAAb6IAADj1AAADkFhZWiAAAAAAAABimQAAt4UAABjaWFlaIAAAAAAAACSgAAAPhAAAts9YWVogAAAAAAAA9tYAAQAAAADTLXBhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABtbHVjAAAAAAAAAAEAAAAMZW5VUwAAACAAAAAcAEcAbwBvAGcAbABlACAASQBuAGMALgAgADIAMAAxADb/2wBDAAUDBAQEAwUEBAQFBQUGBwwIBwcHBw8LCwkMEQ8SEhEPERETFhwXExQaFRERGCEYGh0dHx8fExciJCIeJBweHx7/2wBDAQUFBQcGBw4ICA4eFBEUHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh4eHh7/wAARCADjBEkDASIAAhEBAxEB/8QAHAABAAMBAQEBAQAAAAAAAAAAAAMEBQIBCAcG/8QASRAAAgECAwMHCAgFAQcEAwAAAAECAxEEITESQVEFM2FxgbHBEyIycpGh0fAGFDRCUnOy4SNTYoKSogcVJEOT0vEIY4PCRGSU/8QAGwEBAAMBAQEBAAAAAAAAAAAAAAMEBQIBBwb/xAArEQEAAgIBBAIBAwQDAQAAAAAAAQIDEQQSITEyE0FRBSIzBhRhgSNCcZH/2gAMAwEAAhEDEQA/APjIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA6px26kY8WkckmG+0U/XXeBfpYXCumpSpVW2s7VV/2nawuCtnQr/9Zf8Aae0eZj1HbtwNSOPj6YnSnOW0TrbO5Qo06NSHk1JRnDatJ3azfQisXeVvTofleLKRm3jVphbrO4AAcvQAAAAAAAAAAAAAAAFrAUIVlVlPaagk7J2vd2LawuE30az/APmX/aRckczivVj+pFpl3j4qXru0K+bJNZ1DmODwM5QhGjXTnJRu6yerte2yZM1szlHg7G5h3bE0fzI/qRiVuen6zI+TjrSY6XWG82ju4ABWTAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASYb7RS9dd5GSYb7RT9dd4Gph+ZgdM5w/Mx6kdM26+sM+3sp8renQ/K8WUS9yt6dD8rxZRMjL7yvU9YAARugAAAAAAAAAAAAAAAGhyTzWJXGMf1ItPUqclc3ifVj+pFt6mlxPRUz+zuh9opfmLvRi1udn6zNqjz9P113oxa3Oz9ZkXM8w74/iXAAKSwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAdU4TqSUYRcm9yA5Bbp4Jv06iXRHN/AsQwdBN7UJS4XqfBEtcN7eIcTkrDMBqfVKOvk49V5fE5qYSg84wlBb7TudzxskfTyMtZZoLdTBSXoTUuiSs/h7yrOMoScZRcWtzRDas18u4mJ8PAAcvQAvYPDRdJTnBScrtJ307GjqtZtOoeTMRG5UQaqw9F/8il/q/wC4fVqW6hSfBedv/u4ks8a8eXEZaz2ZRJhvtFP113ivseWl5NJRTsraDDfaKfrrvIUjUo5UY9SOmcUOYids2q+sM+3sp8renQ/K8WUS7yt6dH8vxZSMjL7yvU9YAARugAnpYWpNKUvMi9G9X1I9iJmdQTOkANGGDpK11OTt952XsX7E0aFOKSVGi+nZb72TV417I5y1hkA1/Ixv6FNrppr4HlTD05pfwKa9VNeJ1PFvDn56skGhPBUn6MpwfC20irWw9SmnJrainbajp28O0htjtXzCSLRPhCADh0AAC/yV6GI6o/qRbepU5J5vE+rH9SLb1NLieipn9nVN/wAam/6496Matzs/WZtUs61Nf1x70YtXnZ+syLmeYd8fxLgFmhhJzSlN7EbX0u2uNi3DC0oNfw02tdtt91itTFa3hLa9a+WWDX8jH+XTWeX8NHrpwaadCg/7fhYm/tLuPmqxwaVTB0ZK6jOGX3XfPqfxKlbDVKaclacVneO7sIbYrV8wkreLeEAAI3QAAAAAAFilhak7OXmJ6X1fUj2ImZ1BM6VwaMMHSSu1Obz9J2z6lfwJoUKcVZUqT6dlvxJ442SfpHOWsMgGv5GKz2Kb6NhWOZ4alN38lBdEbrxPZ4t4efNVlAvVMFG3mymnvurr4+4q1aNSl6Sy4rQhtjtXzDuLRPhGADh0AAAAAABNSw1WcdqyhF6OW/q3s9iJntAhBfjgYJPanOT6Fsr3kkcLQtbyTvxc8iWMGSfpHOSsMwGnHC0fvUk+qTXecSwVPXzo8LO/fY9njZI+iMtZZ4LU8HNNKElJtZJ5PqK0oyjJxkmmtUyK1ZrOpdxMT4eAA5egAAAAAAWKeEqzV3aC/q19mp7ETPh5M6VwX1gYK95Sk0/VXiyT6pR2cqWdtXNvuJY4+SfpxOSsMwGn9VouNvJ58VNr3Milgo7N7zi+q6t7hPHyR9EZayogsVMLUirxtPoWvseZXIpiY8u4nYADx6AAAAAAPYpyaUU23uRZp4Kbf8SShZXatdr2HVazbw8mYjyqg0FgqS/HLLO72e65JLC0X6FFLrk38CWONkn6cTlrDLBpywtBw5q0uKqf+SOeChZWlOL35XR5PHyRG9EZayoAnqYarCO0kpx3uO7rRARTEx5Sb2AA8AAAAAAB1ThOpJRhFyb3JFmngpP06kV0R85/D3nVazbxDyZiPKoDRWCpJ6TkumVu5ZHbwlK+VKKXTJv3kkce8/TictYZYNOphKDVo03FrV+U16lYhngo38ycl6yy9v7CcF4+iMtZ+1IEtXD1aSvKN4/iWaIiHWkgAAAAAAAAD2MZSkoxTbeiRZhgpvOc4x6F5z93idVrNvEPJmIVQaKwVJNZTkulqPxOnhKWWzSS65NkscbJP04nLWGYDTqYSja0abTtun4NEU8FF32aji0r5q69q+B5ODJH09jJWftRBLWw9SktppSj+KLuiIimJjtLsAB4AAAAAAAAABPhKPlZ3knsLW2r6EexEzOoJnT3DYaVVbcrqF7LjLoRo04qENiCUYPVLf1vV/Nj1KyySWWVt3Ue2emqWnQaWLBFIiZ8ql8s27Q8XTqxqxKy3r4s5lVjC+3KMLfiefsJ5vFPMoorNvEO37+B5u8CL6xQtz8LvVWlbuJYyjLm5wnl9x392pxGakz5e/HaPp7k1ZptdOZxWpRnFwmtpaR3NdTOlbc78bbg81xT9h7atb+XlbTWWZisPKi0/Sg9H4PpIDaqwjKDTjtJ7nl87+oycRT8lVcL3WqfQZ2bD8c/4XMd4tBh6flKqi3aOrfBGtBWSyz+cupZIrYGi4UlJ5Slm+hbvnqLVlokkWuLj1Xqn7Q57b/aPS+vQQYyt5Oi7POXmx8X4dpNfdv3GXi6vla10/NitmPUOVk6a9P28wU3O5QkmG+0U/XXeRkmH+0U/XXeZy206HMRO2cUOZj1I7Zt19YZ9vZS5W9Oh+V4spF7lb06H5XiyiZGX3lep6wHUIynJRim5PRHJp4Oh5KF3zkl53GK4fE8x0m86gtaKxt5hsNGkru0qn4ty6viWHxzvv3+8N5JLRZ5aHuivc1MeOtI7Kd7zZ57uCHbmeTqQhBSlJRT3v4asrVMdTUvMVSVt99n4nNs1KdtlcVrLfaeZ3Kv+8IWs8N2+UZ7DG0pZS24Z6u0l4HH9zjl18FlndfVB8U3e2t7M8jOMleMlKL3r5yOuLWa4k0atG/pxq1ZU8VhFKV6SSlbRaSfg/nIotNNpqzRtprek+jc+kpY6ht7VWKzis/6kt/WU8/H1HVXwsYsu+0qAAKadf5J5vE+rH9SLZU5K5vEerH9SLZpcT0VM/skoJuvSS31I9eqKdLCSpVnOrH+I3dRkvRXF338C1CThJTi3GSaaktU186ipUqVakp1Zuc5N7UpNttvVt7yTJii8xafpzS81iYgatxfXx4vpPNLZ7sjmdWMY3lJRjo2/nNlaeOpp+bGcl/j8Ty2alfMvIxWst3lfpPM27byr/vGFvsyXSqjuIY2nJ+cpwfSk14HMcrHMuvhst9TtvPGk7bnxWpzTnGaums/Yzt5OxNE1vCOd1lSxWFbvKnHzkrtJalE29d7Wfv4mdjqOzJVFa0tbbmUORhik7jwtYsnV2lVABVTB1CMpyUYq7Z4k27JXbNPC4eFODUs5/e6Oj53kmPHN51Dm9orG5c4fDRppO6cmvS+HxLHjr0vi+k9atplxt3nj0easjTx46Ujsp2vaz156XPM0s734M4qVoQXnyUV0q9+pfKK8sdC+UZy62l8Tm/IpXtt7GK0wuZ333PNPaVHyhBq31e3T5RndLG0pWU3KD6VtL57DiOTSZ8vfhtpZa3NXOZRun093Tx7RGSla0k03ZNPL2nVsuknjpvCPvSWfisLZuVNf2/D4FQ2mtpW/Z67ukoY6hsfxVbP0kt3T1FDPg6O8eFrFl6u0qgAKqYPYxcpKMVdvRHhoYGilHakvOkr9SfxO8dJvbUPLW6Y29wuGUPOdpS42ul1fEtRXHXi8+3PUWS1b7fnQK/V1mnjxRSNQpWyTZ7ks+OdlxPFd6I4nVjCKbkordfL9yF42inZucl0Rt3sWz0r2mSuK0rOm63QxcqrG4f8NbtsySlXpztszi3bSzTPI5GOe0S9nFaEztmrJrhbXr4kdalCqrSu1ay0uuok1fuC3N5cDuaVvHeHEWtVkVqUqTzzT0ZGbGIpwnTe0snr8evwMqrTlSqSpy1i7GZmxTjn/C7S8WhwACJ2HdKlOrK0Vpq3ohRpyq1FTja74mpQpRpwUVay97tr86EuLFOSXF7xWHmGoQpK8PS/E1n2cCRZXzebu89XxfE9etkeaZt9hp0x1pGohTm1rd5e8Fme77a8egiq1oU8pTUH239hF9doZ3VV8LJLvbObZ6V7TL2MVp+lnJB5rW5WeNw7ts+Wj1pPusS060Kj8ycZvdqn7H+55XPS3iScVoSdbyvfp7OBDiaEKkW5el+JLP8Acl1zXE9Sy6zu+OLxqYeRaazuGRWpTpSSlo801oyM169ONSDjJJp69HSjLrU5UqjhJZr3mZlxTjlcpeLw4ABE7CSjSlVlZZLezmnB1JxhHVuxq4anCnFKyaXvvq2S4sfyS4veKwUKMaSahkuO99fw0O0klbdw4Hr0Vjx5K/YadKRSNQpTa1nqzdtWG1vIqmIpQynKKfC12uzT2kSxtFaxqPpSS+JxPIpXtMu4xWn6Wr+wcCusbQb1qRT/ABRv3MkhVhNXhJSXGO7rPa5628S8nFaPp3bO+jvr/wCCtisMqnnJKMuO59Zazvqg96faj2+Kt41Lyt7VlizjKEnGSs1qjw0MbQ24OSfnQXtS3dhnmXkpNLaldrbqjYADh0FjDYaVRbUso7lvfV8Rg6CqzvP0Fu/E+BoxSiunflkWcGD5O8+EWTJ0vKcIwhsqK2d6jkn4s6XSetZ3suiwTWe/xL/TWsdlWZtYTd7LIXusnchq4mjD/mK/CK2vgjn69h98a7fWkRzyMcT5dRhtrwsWd3x3B5JkCxmGlLKU4etC/c/AljUi43i01xjp+x1TNW3iXlsdo8w9td7SybyyKuJwilnTSjLhufwLfStBa6zzTysMmCLwUyTWWK002mmmtUeGjjKCqR2oXc1/qXxM4zL0mk6ldraLRuAAHD0J8Nh5VWnJ7MONteo5w1F1ZZ5RWvwNSEVBLJX0tuXUT4cM5J3PhHkydPjy5oU4wg1BKKaztv63v7ugkdlklZdVguk8lK2WbfBGlFa0jXhUmbXkW/ozPbvWxBUxNKGtRX/pVzn67hredGu97tZEc8ile23UYbT9LLfYeZkH1zDt2UqsU9dqKfcySFanJXi00uHzc9rnpbxLycdo+nf3m7tO1tcypiMLGV3G0ZdVky4rNJ63GWmt+J7kw1vHeCuS1ZYs4yhJxkmmtUzw08XhvKrzPSS83p6PnqMwy70mk6lcraLRsABw6AAAAAHqTbSSu2auHpxhBQVvN38ePh7ClyfFPEqbV1BbXbu99jRVopJaJWLnFpEz1SgzW1Gnq1v7Tmc1FXeuersl0nqta7vZZvqKPKNW8/Jqy3u3uRZzZPjrtDip1S5xGKlKTVJtL8W9/AqgGXa02ncrkREdoAAePVuhi5Lzasrr8VrtfE0IyjLP5+d/SYhd5PrZOlLOyuupZteJZwZprPTPhDlxxaNwuVJKMW5XUUrvqM6jF4nEOUll6UkuHDwJeUKqcVTi85edLq3LxJ8FR8nRSa86S2pZez2LPt6DvJPzZOmPEPK/8dNymjxyuere3pqG3d316jxu2rs+PAu6isK3e0oMfVVOjJJ3lPzU+je+34mYS4qr5Ws5K+ysop8CIysl+u216lemNBJh+fp+su8jJMPz9P1l3kbpp4fmYdh2zjD8zDsO2bdfEM+3sp8renQ/K8WUS9yt6dD8rxZRMjL7yvU9YWMDS8pV2pejBbT8EaUenfm316lfk6Cjh9prOcm+xK1veyxqy7xqapv7lWz23Onqsmm8ror4rEKlC6tJy0XHp6ugnb817TyzcnbRLX3GRWqOrUlN793BcDzk5ZrHTD3DTfeXk5ynJyk22zkAz1oAAHVKpOnPag7M0sLX8rF633rh8/sZZJh6nk6qlu0a4olxZJpbbi9YtDXfRoeWyvZNq/aeptx6VfNbwzU31Qo96yysXTVKs1G+y849RCaHKUE6MZpZxlZu+56dzM8yclem0wv0ncbX+SvQxHVH9SLZU5K5vEerH9SLb1L/ABPRWz+z3dYir1Y0oubzjpa+bfAkvbPeihynJquqT+4s+t5v4dh7yb9FNPMNdz3V61SdWe3N3e7gug4AMxcAABJQqyo1FJZrenozUpVI1I3jfPNZmOW+T52vFtq2a7cn4FjjZOm+kWWu420NOrjxI68FOlOD+8suvVfAkeVlpY8bcVtK91n1Z6mjkr1VmJVaTq22KCTERUcRUitFJ2IzGX1vk6m3UdX8DtG6+9u8WaFlGNkrW0K+Chs0ILjeTXX+3eT7veaXGpFa7/Knmtu2iO95WWbbyt03K2MxKgko5zeaV/R6X0snqzVODm81HNrjwRkTk5zcpO7bu2ccrL0/tq7w0ie8km5NuTbb3s8AKCyAADunUlBuzyeq3M08LWVSOV8+nNvgZJNhJ7NVRbtGWT8GTYck0t/hxekWhqp5p5rqPJxUouMvRtZ5nrbau1Z3zXBrULNW45GneIvGlKJ6ZY9WDp1JU5axdjgt8ox/iQqXb2lZtq2ay+BUMi0dMzC/E7jaTDU1UrRhJ2jq+pamtG1r5K73brFHk2CbqSfBRXb+yZfvdtvUu8SuqzP5V89p3qB631K+KrqlF2zk/RXxJ5aWTSbyv1tIycTPylaTXorKPUdcnJ0RqHOGm53LmcpTk5Sd2zkAzlsAAFvCYmUXsTd1om+7qNCNnbddX6mYhrYOTnRjNtXeT43Xyi7xcs76ZV81I1tLZopcpU/NjUW7zX1ar3dxdbzuRYuClQmrK7jddad/iT8ivVSUWG2rMkA9hFymorVuxlrq/wAnUnGnt2V58V92/wA+wtvjv3ZHkdlLzL2WSy3LI9vkjWw06KxCjktNrPJNJXeay9+naUcVipKbjSlbc2n7bfEmxtZwotLKUvNXVv8AAzSrycs76aynxY4iNyAAppwAAXMLintbNaTd1ZSe7rLqd34GMaOBqOdKzzcMn1bn4ewucfPMT0zKDLSJjcLPG2ZX5QpbdHbXpQu+uP7FjqEkrWknsvKS6N5azUi9dIMdumdsUHVSLhUlB6xdjkyV5d5NptKVW2vmR8fd3l3TJaW0IsItnDU46ZXa43/axMjU41emkKea27PHp22XSyhi8RK+xHJrJvh0It4qcoU5TX3Vl1vJfPQZJByss76YlJhpGtgAKSwHUJShNThJxktGjkAaWCr7cdl5NOz7fn29ZZaz4voMnDVPJV4zauk81xW81tJNXvZ2vbXpNHi5OqNT9Kmeuu8DumpLNrTp6DKxlJUq8ox9F+dHqeaNVezMo8pwypz64vsz8Tzl03WLPcFu+lI9hFzkoxV23ZI8LPJ8b1ZTsnsxyT3t5eJQrG50szOo2v0YKnBRjuVr23/Pgd2zbXsPNFa9xdLN7szYrWK11ChMzaXlWoqcG27W38Pnd/5MzEYiVVtLzY8OPSzvHzbq+T/D6XX+2hWM3Plm86jwuY6RWAAECQOoTlCW1CTi+g5AGlhcSqi2ZWUlqujo+BYettHwMeEpQmpxdmndM16U/KQUqcZOLSdlu6My9x8/bpsrZcf3Dpp7nZqz04aGXjafk620laM810cUar2lrCXsKmPW1hm2mnCSautzVmvcvee8rptXcPME2idSzgs3ZAnwUb4iLekfO0v1e8oxG50szOl/DUVTgoqzcdX0vX56CVrjpuPIJpLN+B7ez2tTXx16K6UbW6rOZyjGL25WVs+hGZiMRKpKSTag3pfN9ZNyhVvs0ovKylLr3L54lMz8+WbW1Hhax0isAAK6UPU3F3TafFHgAu4TFS2tmWr4by89FbVr2GKm07p2aNXCzc6MZaJ9+/w9pf4uWbT0SrZqfcJGlJNNZ8VqZ/KNLZqKqlZT16JbzRt0kGLht4eorZpKSa4r9n7jrk4903+HGC2p0ywAZy4AAAAAL/Jaj5Ks3a7cUr9d/AuWyKfJivSqf0yi/c0XL5mlxv41PP7PMm4pp2bV10b/AHGPVm6lSU3rJtmyspRy+8vh4mIQ8vfVCTj+JAAU1gAAA6hKUJqcXZxd0cgCxhouviXOpml50unoNJZZ73q+P77yDB0vJ00ms3m+vh88WWN+nUjS42Ppr1T5lVzX3Ojdud8ipj6qjT2YvzpcNLfPiWZNWzdlnd8OPuMrEVHVrSnonouC3HPKyar0/Zgp32jABnrQSYfn6frLvIyTD8/T9Zd4Gnh+Zh2HbOMPzMOw7Zt19YZ9vZS5W9Oh+Uu9lIu8renQ/L8WUjIy+8r1PWGthY7NCmnvgmvbIkWpxh86UL7oRS9lyRe408UapCnkn90ocZJLC1ZXtLzYrqefgZRpY9N4WTW6cb/6jNM/kTvJK1i9QAECQAAAAAa2FntUKbTd9lb96bXciV8CtgrqlDLWN79rLG81sE7xwpZY/cjxlNSw1ae+MU1x9IyTVxqk6E2tErvp3eJlFLlR/wAixh9V/krm8R1R/Ui29SpyVzeI6o/qRbepZ4nohz+z2MVKUYtXUmk+12MvHy28dXnxqSfvNfD/AGij+ZF9eaMStz0/WZFzJ8O+P4lwACksAAAE+Cls1/7X3EBLhueXU+5nVfaHk+Gq80r68WJc3JdDPXolwR415r4WNie7PZmPjs4qStbJP3IgLXKn2x+rH9KKpj29paFfDZhHZyvokv8ASj1ahJqUr8WDWp6woW8yr8pebhsn6U7NdSv4maX+U4vyMJbttr3IoGZn/kldx+sAAInYAAAAA2KMlOLlazsm8+Ku/edbmcYWzoxsrWir9OR3vua+KZ6ImVDJ7Sqcoq9NS4Stbs/YoGnygv8Ag2//AHF4mYZ3IjWSVvF6wv8AJy/gOXGfcmW3qVuTvsy9d9yLS1L3G7Y4Vs0/ulzOWzFuydlJ+xNr39xjGxW5qp6ku4xyry/dPg9QAFVMAAAaHJso+QlFptqaa9j+CM8ucnXtO34l3MmwfyQ4yesr2jPKsdqNlvTX+lnrDzlHpZpZI/bKnT2hik+BjtYumuDv7EQE+Av9ajZ2dn3Mya+0L0+GlG/k1luWXSet2XE9foo8ejtrY1/pQ8yzuUZXrRindRgvfn4lYmxtvrDtpsxt7EQmRed2lfjwAA5egAAFjAStX2bXUoteK96K5a5L2VyhRcvRUrvqOqe0PLeGjqkzx5xktbq2Yg7QXUerK5sTHZn+JZeOVsS3e90n7UiAnx1vLK34I9xAY9vaWhHhr0bOlHLSMV7jtexnNP0X2dyOtxrY/SFDJ5VuUlbCxlfOVRq3QkviZxf5Sv5GHry7olAzM87vK7jjVYAAROwAADZptyhGTzbjF+5GMbNLmKP5a8S1xPdDn9XpV5R+z9U13fsWipyhzb64+Ja5MbpKDD7KBe5Ma2ZRaWck03usUS/yc15NR37T8CjgjeSFrJ6yuPQKO00ssrvPR2V7e5nj16Tme01JLXZl+lmleZ6ZUqd7QyJNyk5PVu7PADHaAAAAAAAAAAABb5OT2pvdkmVC5yc0lO/FeJLh/khxf1lfbW4816w0+AXsRrTHfahDqpszk5SpUXJ5vzEc7FNPmaL/ALEN9r2fA9szj46z307m9vybNP8Ak0f+mhs091Cj/wBNCzFmPjr+HnXb8mzT/lUF/wDGhswWfkaH+CFmLMfFX8HXb8vGoX5mj/00dX81RUYRSv6MUrt66HmYt1nsUrHiCbWmNPLZ9AlFSaT33WWma/c9t1nsV/Fp685HvQvH7Jh7T2hhgPUGMvgAAAAC3ydO0qkN0o39jv8AE0Gm3dZGRh6jpVo1FuZqwl5is7pLJ+PbkX+JeNTWVbPWfMOmnbJtO6676pmXjYbGIk0rRk7o1OLvmiDFUPKxycU1mjrk4ptG4cYb9M6llg9nGUJOMlZo8M5cAAAJ8HT26u01eMM2nve5EVOEpyUYq7NPD0lTpqKeWt7a5ak2HH12/wAOL3isJY5Rs228/bvDvxC4iq4xi23ZLNtdRqTPTG58QpR3lTx9W0PJp+l3fuf2f0P/ANnOI5d+guO5e2pRrJv6pD8Sj6TfW8l1M/kOQ+TsTy/y/huTsNG9XFVVBf0rj2I+uOQ+TMNyVyRhuTcLBQoUKShFdCybfWZNrddptLC/qb9dn9JxUpj97Tv/AFHn/wC+HxtKLjJxkmpJ2ae48P0H/bh9FnyB9KJYzD02sFjm6kbLKM968T8+I5fo+Fy8fMwUz4/Fo2HdDn6frLvODuhz9P1l3haamH5mHYds4w/Mw7Dtm3X1hn29lLlb06P5fiykXeVvTo/l+LKRkZfeV6nrDXw/NR9SPcSLJ56EeH5qPqR7jtampj9IUb+0uMSnPD1Kd/SjddLWfdcyDaS0adradGZmY2j5Kq3FeZLTo6Cny8ep6lnDaJjSAAFNOAAAAWMFT26qk1knl0s9rE2nUPJnTQoJxpxhdPZjb437bne+54lZJJ9bvn2hGxjrFa6ULT1TtFjpbOGqJLKSS95lF7lKa2YwW97WvYvEomZyLdWSVzFGqr3JfoV+qP6kXHqU+S/Qr9Uf1IuPUt8X0V+R7O6H2il+Yv1Ixa3PT9Zm1R+0UvzI96MWtzs/WZxzfMJOP4lwACisAAAEmG53+2XcyMkw3O/2y7mdV9oJa8tF1Hn3Wey0XUefdZsM5n8qfbJerH9KKpa5U+2S9WP6UVTHv7S0K+IbFGW3FPVtLuR3bMrcnzcqC/pezrnx+JZe9Zdm81MNurHCllrMWV8enLDyV72akl7n4GYbM43WaT6OK0sZWIpOlUtuecX0FPlU1baxhtE10jABVTAAAHsU5SUVq3Y8LWBpNy23r93xZ1Ws2nUPJnUbX4WteKVlkrb93gjreHZJJWSWljxamxWNRpn2nc7QcofY3668TMNPlD7G/XXiZhmcj3XMPq0eTvsy9eXciytSvyd9m/8AkfciwtS5x/RWze0ua3NVPy5dxjmxW5qp6ku4xyry/dYweoACsmAAALnJ33vWXcymXOTfvesu5kuD+SHGT1leZ7HnIHjPY85A08nrKnT2hiE2Cls4qm+mxCep2d0ZETqdr7Zp+hG/ASV8l7zmnNSSkt6v0HaNiluqNs+0aszuUkvKxmkknG2XFZd1iqamLo+UpuKte910PgZbydmZmek0uu0t1QAAhdgAAFnk+G1VlJptRi/a8vErGnhKPk6ajL0r3l17l7CbBSb3jTi9umqdaK3UH6DfBXPckre5HM5KMbySaXnPPhuNS86jalWOqWbjnfFT6LR9isQHsm5SbebbueGNM7nbQhsw0fZ3I63HMfBdyPdxr09YZ9/ZT5R5mHry7olEv8pcxD8yXdEoGZm/kldx+sAAInYAABsUeYo/lrxMc2KHM0vy14lnie6HP6u1oU+UObfXH/7FtaFTlDm5etHxLfI/jlBh9lAu8mtJT4pqyKRYwM9mva7tNbPw95nYrdN4lbvG66aTyF7O93bflnbf7hF3iMrdJrz3iVGvaWPUi4VJQesXY5LePpO/lEtMpeDKhj3rNZ1K/E7jYADl6AAASQo1Zx2o05yXFRPKFN1aigsuL4I1nTpWWzBWSSjfcTYsM5PDi94qyvIV/wCTU/xZ5OjVhHanTnFcWjV8nD8EfYityhsRopRik5ye7RL9+47y8f469W3NMsWnUKBa5O9OSulo8/npKpLhJ7GIi7pJuzb3XIKW6bRKS0bjTWSvxPHezta9shHPc73t1WBseY7M/WpUcTXnTrTgoxcb3Tu809N5GsVJfch7X8SblCi3FVEs4qz6t3z1FEyrzetpja9WKzCysZNf8qn7/idLHT/k0fY/iVAc/Jb8vemv4XPr8/5FH/V8Tn67P+TS9/xKoHyX/J01/Cz9cl/Kp/6vie/XJfyaf+r4laMXKSjFXb0RaXJ2NausPJ9qPYvf6k6auXi5fyqftl8TxYuSkpKnBNO6d5ZP2ki5Mx7/APx5e1EFfD1qDtVg4vpE3v8AckRX6RAAjdAAAAAAXcFWyUJWvHTPcUj1Nppp2aOqXmk7h5aNxpsqzV01xy0PU8n1FPCYhStCW5aW7i4mmk00753TNWmWMkRMKV6TWUVajTqR86KfTfNfPsKrwMm0oTWe6St79C94hW3o4vx637va5bVZ6wNdy2b0uvyisdQwL2mp1Fl+DP36F7LgO4jjiV/Lv55cUaUKcNmMbX13t9vyiR2v0hLOzDsk23a2tyxWkVjshm02nu8vspt5W9xRx9a72F29XxJMXidhbMH53d1lBtt3ebKXIz9X7YWcWPXeX7T/AOmzkLC1FjuXqrhKvCSoUk9YK15PrZ+2WcXbe9T5m/2J/Sl/R76UQw2IqKOCxzVOpfSMr+bLw7T6YjJSScfOT0ZXr4fI/wCt+Pnx/qHyXndbR2/19P53/aL9G6X0l+i+J5Oml5dJ1KErZxmll8O0+UMTRq4bEVMPWg4VacnCcXqmnZn2mlm9rJcT58/9QP0V/wB28tx5ewlK2GxjtWtpGpx7V4nktT+hv1jptPByT571/wDfuP8Ab8rO6HP0/WXecHdDnoesu85fT2pQ5iHYds4o8zDqR3vNuvrDPv7KXK3p0fy/FlIu8q+nR/L8WUjIy+8r1PWGvh+aj6ke4kWbsiOhzUPUj3Hb1NXF6QpX9jp0Oa9KNSm1Kz3vP2dpcoRwbwOIqV6s6eIU4RoRSWzJtNvae70cullZdqs/fw6zmem/7ZI3XvDMrYWpC7h/EiuCzXWiublldPR9GT7Hu7NDmUYys5QjO2VpRv79feVL8SYn9srFc8fbFCzdkbPkqG3tfVaPV53xEYRS8xKGf3Vss4ji3l789WfRwk5Z1E4rhvfwNClBQitlJJK1l85ntks1a7edt56vZ1lzFx4x90GTLNh77HMnFJ7T2VveuXV87jq67bZGdja6k/Jwd0sm+PR1DNljHX/L3FjmZQ4ip5WtKdrJ6LgiMAylxe5K9DEdUf1IuPUqclc3iPVj+pFt6mlxPRUz+zuh9opfmLvRiVedn6zNyjz9L1496MOrzs/WZFzPMO+P4lyACksAAAEmH53sfcyMkw/O9j7mdV9oJa8tF1Hn3Wey0XUefdZss5n8qfbJerH9KKpZ5T+2S9WPcisY1/aWhXxCfB1VTq2k/Nlk+jgzUirrLXTwMQvYTEt2hPVZJ8UT8fL0zqfCLLTqjcLls9COrRjVylfN3fXxRJFqUbrNPuPXldd5oXrW8aVYtNJZdbC1YXaTnFb0s11rcQG0sntZ3vuy9jRzKnGTTnGErLfFO/bqUrcSf+srNc8fbHPYpydopt8EbDp0dmyw9CLtqk33sRilFJOy4LJP2WPK8S8+Xs56qNDCSa2p7vu373uL8YqKslkuz5XA9SVskuq2RzVnGCzdvgWqYaYY3KG2Sck6h007KTTSd0m1keLU8p4qpiMNTjKXmQnLYjwTS7/E9RJW/XXcI716Z0g5Q+xP149zMw1OUPsMvXj3MyzN5Hut4fVo8nfZf733IsrUrcnfZv733Is6F3jeitm95c1+aq+pLuMc2Ky/g1PUl3GOVeX7rGD1AAVUwAABc5N+91ruZTLnJusuteJLg/khxk9ZXmex9OPX4HjPV6cfncaeT1lTp7QxAAY6+u8n1rLycnpmurevEuuzSaazzuY0W4yUouzWjNLDYiNSOlnvXDp+dC5xs2o6JV82PfeFh2tbVfPz2FXFYVVPOUrT4vJS/ctKK68rprQWz4Fq+OuTtKCl5pLGqQnTdpxaZybLitOO7VezQ4nQoyXMU11XV/YynbiWieyzGerJOqcJzlaEW2asKFGK+z027au7t7ztJWtotyWSt1aHteJeZ7k56/SrhcJsNTk81wWnxLaSirLRaW3fE8WmSVug9v7S5jxRj7QrXvN5eXS1dinyjUVlCLzlm+rd8fYS4quqayd+F9/7GbKUpScpNtvNsq8nN26IT4ceu8vAAUlhs09GuruOtxzDe+ruPdxs09YZ9/aVPlLmYfmS7olEvcpc1D133IomXm/kldx+sAAInYAABsUeYo/lrvZjmxQ5il+Wu9lnie6HP6u0U+UObl60fEuIp8oeg+uPiW+R/HKDB7KAAMtdauFqqpBS32zXSTNewyKFV0pXWj1RqQqRnFPaurZdOnzY0uPm6q9M+YVMuPU7h3sprNJ31v70+gz8Rg5JuVJXX4b5rq4mhfgGk1ZpM7y4Iyd3FMs1YrTTs1ZnhtShGdtuKmlulnft1Ip4Wk8/JQXU38SnPFv9LEZqsokpUalTNK0eL0NSNGlFLZpQVs7pXfvbOkknfV8X3e86rxbTPeXk54+keFpQpUtlJraV5NvN/DqJXm7ro9oyfUuC0PbqKzvrb28Oku1rGONQr2tN5ct8HZ6J8OnsMrFVPK1W16KVo9RPja+bpweuUrPJdHxZTKHIy9c6jwtYqdMAAKyVp4SqqlKLb870Wunc/ngWHpdGPRqOlPaWa3p70atOrGpC6bae98eHX/5NDjZomOmVXNj1O4dNe33FHEYN7W1RTd89j4cS+7HjzTTs+sky4YyQjx5JqxpJxbUk01uZ4bMoRktmSUkt0lfLhnmRTw1KWapQXQr/ABKk8W/0sRnqyzqEJzdoRbNOGHpRTXkqbb355e8l2I5aZdHRw0Pa8S8+Sc9fpVwuG2Xee9bi0oRvokuo9eeby8ekaJ33a3ysi7TFWldK9rzaXMlFLKN3uRm42alV2Y22Y5XW972WMXiHC8Yy89q3Sv3KBR5OSLT0ws4qdMdwAFZKAAAAAAAAJtO6yZaoYuUbKf8Akl38SqDqtprO4eTET5a9KvGaycZN/hefs1PVKOeaVnbMxyWOIrxVlWmlw2izXlzHmEM4Inw1FKNr7UbdZ6px436tTM+t17W21/ijmeIryVpVZ24XO55kfUOf7f8Ay0qtaNN2laNtU3r2alKti5SVoXX9T17OBVBXyZ737Jq461AAQu3qbTTTs1ofTn+xn6VL6Q/RWnTxNVPG4T+FVvrJbpexHzEWuT+UcfydOU8BjK+GlL0nSqON/YexOmL+u/o1P1bjfFM6mJ3E/h9lqUXeLlG3WZP0w5Hw30g+juM5LxGzJVoWi7rzZfda7bdh8sv6U/SR68u8o/8A9EviF9KvpKtOXeUc/wD9iXxOuqH4/j/0JyOPlrlpnjcTvwzuUsJWwGPr4LER2atGbhJdKIqPPQ9ZHuIrVcRWlWr1JVKk3eUpO7bOE2mmtUcPpNd6jflrUGvIwzW7ed3XFGXHE1oqycV/YvgdLG4hfeh/hH4F6OXERrSvOCZnaXlX06LX8vxZSO61WdaSlUabSsrKxwU726rTKxWNRpsUOah6ke47WpHh+aj6ke4k4mtjn9kKF/aVblF/8LJf+5F+6RBhsU15tSXa/H4knKL/AITX9S7mUDPzWmuWZhbxxE01LZjOLtnZPR8ep6HtjIp1alN+ZJritzLFPGyVtumnb8LcSbHy4/7Qjtg/C/7ugaFJ41N+jNcM18BLHRcbeTlfjt6+4l/uqOPgsvZJXbS6WyOrVjGKcmkmtXv7CjLGVW7xUYdSv3lecpTk5Sk5N72yG/L7arCSmDXlPiMTKd1C6TVm97K4BTtabTuU8REdoAAePV7ktrYrpu11H9SLja4r2mRSqzp32Gs9bq5N9dxP44/4L4FrDnjHXUwhyYptO2nScfLUrNX8pHvRi1edn6zJ/r2J/HH/AAXwK7bbberOM2WMkw6x06IeAAgSAAAEmH53sfcyM9jJxldansTqdjZbi0s17RtKzzV+szVjK60lH/BfAfXcR+KP+C+Bd/u668K3wT+XvKf2uXqx7kVjqpOVSe1N3ZyUpnc7WIjUAAPHq1h8U4+bN9vHrL8KkZQ2lZxWrTuYx1Cc4O8JOL6GT4+RanZHfFFmwmmsmmLXdrmbHF1UvOUZdNrP3EscbG2dKX+ZajlUnygnBP0vJZ/A8eWbaS6Sm8dG3Nyv637EUsZVbvFRi7Wva7955blVjwRgt9r86sYQ2pNJPS+/s1ZnYnESqu12o95FOUpycpycm97ZyVcua2T/AMT0xxVoYCSVBJtLzm/cWdpXWa9plUq1WkvMlbsTJPruJ/mL/BfAlx8mKV6dOL4eqdrePkngpJP78e5mYS1sRVqq1SSa6kiIgyX67bSUr0xpo8nP/h7f1vuRZay/cyKdWdP0Wu1XJFiqy+9H/FE+LkxSvTMI74ptO2lWzo1fy5GMTSxVaUWm42atlFEJDmyRktuHeOnTGgAESQAAAt8nelLrXcyod06k6bvFrtVzvHbptEubRuNNd/OYXpxW+/gZn1uv+KP+KDxVZ/ej/ii1blRMa0grgmJ3tAACksh7GUoyUotprRo8AF/DYtejO0X7v2LW3F2e0s/ntMYkpVqtL0JuPRuLOPk2r2nuivhizWzDM+ONnpOEXx2fNv7CT67FpeZNW/qXwLNeVTXdDOCy4ePQqLHJNtxk+2xxLGys1GnHPfLzmJ5VNdiMFl/ajmtd+TyXWVcRi1HKDjJ77LK/Xv7inVrVanpzbXDcRlbJybW7R2S1wxV1OUpycpO7ZyAVkwAANmHo655dx7u/cyliKq0kv8UdfW6/4o/4ou15URGtK1sEzO9p+Ul/Cg/65dyKJJVrVKqSm1ZZ2SS+dCMq5LdVplPWNRoABw6AAANijzFHpprf0sxyaGIqwioqSsuMUS4cnx224yV6o01FqVOUF/Db6Y//AGK/1uv+KP8AgjirWqVFaTVuiKRNl5MXr06R48U1naMAFROElGrOlK8XlvRGD2J14Gph8TCoktrPLJ5P97E2Tdr53s+Jik0MVXitnb2lwkrlqnKmO1kFsET4athoUYY78VJvqll7w8anpGaV72un4E8crGi+Cy9v19h47J5vUpfXsrbEn/dbwI5Yyq/RUY9Nrv3nluXT6exgn7aFSpGEbytFcX85lDE4ra82ldLTaerK85znJynJyb3tnJVyZ7XT0xxUABAkAAAJKNWdJtxeT1T0ZGANTD4mFRJbXncJPPse8mbV7N2d9GvAxSeniq8I7KqXja1pK695ax8q1Y1KG2GJncNS3SLZFCGOd1t09N0ZNHrxsW7qM49qZYjlU0hnBZdsFZZ7ugpfXV+GftS8COWMqO2zGKa0drsTy6RHZ7GC0+Wg6kVG7dks77iliMUn5tN3ad9q1rdXxK1SpUqO9ScpPpZwVMme1+yemKKjzd2ACBIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANfD83H1I/pRJxI6HNx9SP6STezYp6Qz8nsp8o82/WXcygaHKK/gN/wBa7mZ5m5/eVzF6wAAhSAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANfD81D1I9xIvSIqDSpwV1fYjv6DtSV73Rr4pjojcqF4/dKvyj9nfrx7pGcaPKLToO3449zM4zs87vK3i9IAAQpAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFiljMTSjswquK00R19fxf85/4oqg93LzUJa+IrVklVntW6EiIA8egAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA//2Q=='

html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Regime Monitor</title><link rel="icon" href="data:image/png;base64,{FAVICON}">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{{--bg:#fafaf9;--s:#fff;--b:#e7e5e4;--bl:#f5f5f4;--t:#1c1917;--t2:#57534e;--t3:#a8a29e;--g:#16a34a;--gb:#f0fdf4;--r:#dc2626;--rb:#fef2f2;--x:#78716c;--xb:#f5f5f4;--f:'DM Sans',sans-serif;--m:'JetBrains Mono',monospace}}
*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:var(--f);background:var(--bg);color:var(--t);font-size:13px;line-height:1.5}}
.c{{max-width:1200px;margin:0 auto;padding:16px 14px}}
header{{display:flex;flex-direction:column;align-items:center;padding-bottom:12px;border-bottom:2px solid var(--t);margin-bottom:16px;gap:6px}}
header .logo{{height:44px;margin-bottom:2px}}header .hb{{display:flex;justify-content:space-between;align-items:baseline;width:100%}}header h1{{font-family:var(--m);font-size:15px;font-weight:700;letter-spacing:-0.03em}}header .m{{font-size:11px;color:var(--t3);font-family:var(--m)}}
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
const D={data_str};\nconst LOGO='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';
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
let h='<header><img class="logo" src="data:image/jpeg;base64,'+LOGO+'" alt="alphanonce"><div class="hb"><h1>Regime Monitor</h1><div class="m">'+r.strategic.date+'</div></div></header>';
h+='<div class="tn">';[['global','Global'],['korea','Korea']].forEach(([k,v])=>{{h+='<button class="'+(S.region===k?'on':'')+'" onclick="U(\\'region\\',\\''+k+'\\')">'+v+'</button>'}});h+='</div>';
h+='<div class="sw">';[['regime','Macro Indicators'],['internals','Stock Market Internals'],['highs','52-week Highs']].forEach(([k,v])=>{{h+='<button class="'+(S.page===k?'on':'')+'" onclick="U(\\'page\\',\\''+k+'\\')">'+v+'</button>'}});h+='</div>';
if(S.page==='regime')h+=pgRegime();else if(S.page==='internals')h+=pgInternals();else h+=pgHighs();
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
function pgHighs(){{
const hk=S.region==='korea'?'highs_kr':'highs_us';const hs=D[hk];const isKr=S.region==='korea';
let h='<div class="md">'+(isKr?'KOSPI + KOSDAQ \\u00b7 52\\u00b7\\u00b7\\u00b7 \\u00b7 Naver Finance':'NYSE + NASDAQ + AMEX \\u00b7 52-week New High \\u00b7 Finviz')+' \\u00b7 '+hs.length+' stocks</div>';
if(hs.length===0){{h+='<div style="padding:40px;text-align:center;color:var(--t3);font-family:var(--m)">No 52-week highs found (scraping may have failed)</div>';return h}}
h+='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:5px">';
hs.forEach(s=>{{h+='<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 12px;border-radius:6px;background:var(--s);border:1px solid var(--b);border-left:3px solid var(--g)"><div style="min-width:0;flex:1"><div style="font-family:var(--m);font-size:11px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">'+(isKr?s.n:s.t)+'</div><div style="font-family:var(--m);font-size:9px;color:var(--t3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis">'+(isKr?(s.t||''):s.n)+'</div>'+(s.sector?'<div style="font-family:var(--m);font-size:8px;color:var(--t3)">'+s.sector+'</div>':'')+'</div><div style="text-align:right;flex-shrink:0;margin-left:8px"><div style="font-family:var(--m);font-size:13px;font-weight:800">'+(isKr?s.p.toLocaleString():fP(s.p,s.t))+'</div><div style="font-family:var(--m);font-size:8px;font-weight:700;color:var(--g)">\\u2605 NEW HIGH</div></div></div>'}});
h+='</div>';return h}}
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
