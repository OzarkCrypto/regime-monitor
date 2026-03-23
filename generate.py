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

# ═══ TICKER DISPLAY NAMES (en, kr) ═══
TICKER_DISPLAY = {
    '005930.KS':('Samsung','삼성전자'),'000660.KS':('SK Hynix','SK하이닉스'),
    '042700.KQ':('Hanmi Semi','한미반도체'),'058470.KS':('LEENO','리노공업'),
    '373220.KS':('LG Energy','LG에너지솔루션'),'006400.KS':('Samsung SDI','삼성SDI'),
    '247540.KQ':('Ecopro BM','에코프로비엠'),'003670.KS':('POSCO Future M','포스코퓨처엠'),
    '329180.KS':('HD HHI','HD현대중공업'),'010140.KS':('Samsung Heavy','삼성중공업'),
    '042660.KS':('Hanwha Ocean','한화오션'),'012450.KS':('Hanwha Aero','한화에어로스페이스'),
    '079550.KS':('LIG Nex1','LIG넥스원'),'047810.KS':('KAI','한국항공우주'),
    '005380.KS':('Hyundai Motor','현대차'),'000270.KS':('Kia','기아'),
    '012330.KS':('Hyundai Mobis','현대모비스'),'051910.KS':('LG Chem','LG화학'),
    '011170.KS':('Lotte Chem','롯데케미칼'),'011780.KS':('Kumho Petro','금호석유화학'),
    '005490.KS':('POSCO Hldgs','POSCO홀딩스'),'004020.KS':('Hyundai Steel','현대제철'),
    '028260.KS':('Samsung C&T','삼성물산'),'000720.KS':('Hyundai E&C','현대건설'),
    '105560.KS':('KB Financial','KB금융'),'055550.KS':('Shinhan','신한지주'),
    '086790.KS':('Hana Financial','하나금융지주'),'316140.KS':('Woori Financial','우리금융지주'),
    '207940.KS':('Samsung Bio','삼성바이오로직스'),'068270.KS':('Celltrion','셀트리온'),
    '352820.KS':('HYBE','하이브'),'041510.KS':('SM Ent','SM'),
    '035900.KS':('JYP Ent','JYP'),'004170.KS':('Shinsegae','신세계'),
    '139480.KS':('E-Mart','이마트'),'097950.KS':('CJ CheilJedang','CJ제일제당'),
    '017670.KS':('SK Telecom','SK텔레콤'),'030200.KS':('KT','KT'),
    '015760.KS':('KEPCO','한국전력'),'036460.KS':('Korea Gas','한국가스공사'),
    '034020.KS':('Doosan Enerbility','두산에너빌리티'),'052690.KS':('KEPCO E&C','한전기술'),
    '035420.KS':('NAVER','네이버'),'035720.KS':('Kakao','카카오'),
    '259960.KS':('Krafton','크래프톤'),'251270.KS':('Netmarble','넷마블'),
    '454910.KS':('Doosan Robotics','두산로보틱스'),'277810.KQ':('Rainbow Robotics','레인보우로보틱스'),
    '006800.KS':('Mirae Asset','미래에셋증권'),'071050.KS':('Korea Invest','한국금융지주'),
    '005940.KS':('NH Invest','NH투자증권'),'000810.KS':('Samsung Fire','삼성화재'),
    '005830.KS':('DB Insurance','DB손해보험'),'088350.KS':('Hanwha Life','한화생명'),
    '003230.KS':('Samyang Foods','삼양식품'),'007310.KS':('Ottogi','오뚜기'),
    '004370.KS':('Nongshim','농심'),'090430.KS':('Amorepacific','아모레퍼시픽'),
    '051900.KS':('LG H&H','LG생활건강'),'192820.KQ':('Cosmax','코스맥스'),
    '000120.KS':('CJ Logistics','CJ대한통운'),'086280.KS':('Hyundai Glovis','현대글로비스'),
    '003490.KS':('Korean Air','대한항공'),'089590.KS':('Jeju Air','제주항공'),
    '008770.KS':('Hotel Shilla','호텔신라'),'034230.KS':('Paradise','파라다이스'),
    '035250.KS':('Kangwon Land','강원랜드'),'036930.KQ':('Jusung Eng','주성엔지니어링'),
    '240810.KS':('Wonik IPS','원익IPS'),'066970.KS':('L&F','엘앤에프'),
    '278280.KQ':('Chunbo','천보'),'^KS11':('KOSPI','코스피'),'^KQ11':('KOSDAQ','코스닥'),
}

def ticker_name(t):
    """Get display name tuple (en, kr) for a ticker."""
    if t in TICKER_DISPLAY: return TICKER_DISPLAY[t]
    return (t, '')

# Build code -> english name map from TICKER_DISPLAY (for 52w highs)
CODE_TO_EN = {}
for _t, (_en, _kr) in TICKER_DISPLAY.items():
    if '.' in _t and not _t.startswith('^'):
        _c = _t.split('.')[0].zfill(6)
        CODE_TO_EN[_c] = _en

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

KRX_API_KEY = '31C1A64E11714282BD3C0A3D1E17FC00D5965CA1'
KRX_API_BASE = 'https://data-dbg.krx.co.kr/svc/apis'

def krx_api_fetch(endpoint, params):
    """Call KRX Open API and return JSON data."""
    import requests
    headers = {'AUTH_KEY': KRX_API_KEY}
    r = requests.get(f'{KRX_API_BASE}/{endpoint}', params=params, headers=headers, timeout=15)
    d = r.json()
    if 'OutBlock_1' in d: return d['OutBlock_1']
    return None

def krx_api_52w_highs():
    """Get KOSPI+KOSDAQ 52-week highs via KRX Open API (full universe ~3000 stocks)."""
    import time
    from datetime import timedelta
    print("  KR: trying KRX Open API...")
    # Step 1: Find latest trading date
    today_data = None
    for delta in range(0, 10):
        dt = (datetime.now() - timedelta(days=delta)).strftime('%Y%m%d')
        data = krx_api_fetch('sto/stk_bydd_trd', {'basDd': dt})
        if data and len(data) > 100:
            today_data = data; today_str = dt; break
        time.sleep(0.3)
    if not today_data:
        print("  KRX API: no trading data found")
        return None
    print(f"  KRX API: {len(today_data)} stocks on {today_str}")
    # Build today's price map: ticker -> (close, name)
    today_map = {}
    for row in today_data:
        code = str(row.get('ISU_SRT_CD', '')).strip()
        name = str(row.get('ISU_ABBRV', '')).strip()
        close = row.get('TDD_CLSPRC', '')
        high = row.get('TDD_HGPRC', '')
        if not code or not name: continue
        try:
            close = float(str(close).replace(',', ''))
            high = float(str(high).replace(',', ''))
            if close > 0: today_map[code] = {'n': name, 'p': close, 'h': high}
        except: pass
    # Step 2: Sample ~50 dates over past year for max highs
    max_highs = {}
    year_ago = datetime.now() - timedelta(days=365)
    sample_dates = pd.bdate_range(year_ago.strftime('%Y%m%d'), today_str, freq='5D')
    sampled = 0
    for sd in sample_dates:
        try:
            data = krx_api_fetch('sto/stk_bydd_trd', {'basDd': sd.strftime('%Y%m%d')})
            if not data: continue
            sampled += 1
            for row in data:
                code = str(row.get('ISU_SRT_CD', '')).strip()
                high = row.get('TDD_HGPRC', '')
                try:
                    high = float(str(high).replace(',', ''))
                    if high > max_highs.get(code, 0): max_highs[code] = high
                except: pass
            time.sleep(0.2)
        except: pass
    # Also include today's highs
    for code, info in today_map.items():
        if info['h'] > max_highs.get(code, 0): max_highs[code] = info['h']
    print(f"  KRX API: sampled {sampled} dates, tracked {len(max_highs)} stocks")
    # Step 3: Find stocks at/near 52-week high
    highs = []
    for code, info in today_map.items():
        h52 = max_highs.get(code, 0)
        if h52 <= 0: continue
        pct = (info['p'] / h52 - 1) * 100
        if pct >= -0.5:
            highs.append({'t': code, 'n': info['n'], 'en': CODE_TO_EN.get(code, ''), 'p': round(info['p'], 0), 'pct': round(pct, 1)})
    highs.sort(key=lambda x: -x['pct'])
    print(f"  KRX API: {len(highs)} stocks at 52-week high")
    return highs if highs else None

def scrape_kr_52w_highs():
    """Get Korean stocks at 52-week high via KRX API -> pykrx -> Naver fallback."""
    # Method 0: KRX Open API (full KOSPI+KOSDAQ ~3000 stocks)
    try:
        result = krx_api_52w_highs()
        if result: return result
    except Exception as e:
        print(f"  KRX API failed: {e}")
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
                    highs.append({'t': ticker, 'n': name, 'en': CODE_TO_EN.get(ticker, ''), 'p': round(cur, 0), 'pct': round(pct, 1)})
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
                        highs.append({'t': '', 'n': name, 'en': '', 'p': round(price, 0), 'pct': 0.0})
                except: pass
            print(f"  Naver: {len(highs)} KR stocks")
            if highs: return highs
    except Exception as e:
        print(f"  Naver failed: {e}")
    return None

def fallback_kr_52w_highs(kr_csv):
    """Compute 52-week highs from KR CSV data as fallback"""
    # Load full name map from ticker list
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tl_path = os.path.join(base_dir, 'data', 'kr_ticker_list.csv')
    kr_name_map = {}
    if os.path.exists(tl_path):
        tl = pd.read_csv(tl_path)
        for _, r in tl.iterrows():
            c = str(r['code']).zfill(6)
            kr_name_map[c] = str(r['name'])
    highs = []
    for code, s in kr_csv.items():
        try:
            if not isinstance(s, pd.Series) or s.notna().sum() < 200: continue
            s = s.dropna()
            cur = float(s.iloc[-1])
            lb = min(252, len(s)-1)
            h252 = float(s.iloc[-lb:].max())
            if h252 <= 0: continue
            pct = (cur/h252-1)*100
            if pct >= -2.0:
                kr_name = kr_name_map.get(code, KR_NAMES_FALLBACK.get(code, code))
                en_name = CODE_TO_EN.get(code, '')
                highs.append({'t':code,'n':kr_name,'en':en_name,'p':round(cur,0),'pct':round(pct,1)})
        except: pass
    highs.sort(key=lambda x: -x['pct'])
    return highs

# ═══ KR CSV DATA + KRX API DAILY APPEND ═══
import os, time as _time

def kr_code(t):
    """Extract 6-digit code from KR ticker: '005930.KS' → '005930'. None for non-KR."""
    if '.' in t and t.split('.')[-1] in ('KS','KQ') and not t.startswith('^'):
        return t.split('.')[0].zfill(6)
    return None

def load_and_update_kr_csv():
    """Load KR stock CSV, update from KRX API if stale, return {code: Series}."""
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'kr_full_daily.csv')
    if not os.path.exists(csv_path):
        print("  KR CSV not found, falling back to yfinance for KR stocks")
        return {}
    df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    last_date = df.index.max()
    today = pd.Timestamp.now().normalize()
    # Fetch missing trading days from KRX API (KOSPI + KOSDAQ)
    if last_date < today - pd.Timedelta(days=1):
        print(f"  KR CSV last: {last_date.strftime('%Y-%m-%d')}, fetching from KRX API...")
        dt = last_date + pd.Timedelta(days=1)
        new_rows = []
        while dt <= today:
            dt_str = dt.strftime('%Y%m%d')
            all_data = []
            for ep in ['sto/stk_bydd_trd', 'sto/ksq_bydd_trd']:
                try:
                    data = krx_api_fetch(ep, {'basDd': dt_str})
                    if data: all_data.extend(data)
                except: pass
            if all_data and len(all_data) > 100:
                row = {}
                for r in all_data:
                    code = r['ISU_CD']
                    if len(code) == 6 and code.isdigit():
                        try:
                            close = float(r['TDD_CLSPRC'].replace(',',''))
                            if close > 0: row[code] = close
                        except: pass
                if row:
                    new_rows.append((dt, row))
                    print(f"    {dt_str}: {len(row)} stocks")
            dt += pd.Timedelta(days=1)
            _time.sleep(0.3)
        if new_rows:
            new_df = pd.DataFrame([r for _, r in new_rows], index=[d for d, _ in new_rows])
            df = pd.concat([df, new_df]).sort_index()
            df = df[~df.index.duplicated(keep='last')]
            df.to_csv(csv_path)
            print(f"  KR CSV updated: +{len(new_rows)} trading days (total {len(df)})")
    else:
        print(f"  KR CSV up to date (last: {last_date.strftime('%Y-%m-%d')})")
    result = {}
    for col in df.columns:
        s = df[col].dropna()
        if len(s) > 50:
            result[col] = s
    print(f"  KR CSV loaded: {len(result)} stocks, {len(df)} trading days")
    return result

# ═══ 1. DOWNLOAD ═══
print(f"Regime Monitor v2: {START} -> {END}")

# Phase 0: Load KR stock data from CSV + KRX API append
KR_CSV = load_and_update_kr_csv()

# Phase 0.5: Compute KR broad market breadth from full CSV (2000+ stocks)
def compute_kr_breadth(kr_csv):
    """Compute market breadth indicators from full KR stock universe."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tl_path = os.path.join(base_dir, 'data', 'kr_ticker_list.csv')
    if not os.path.exists(tl_path) or not kr_csv:
        print("  KR breadth: ticker list or CSV not available, skipping")
        return None
    tl = pd.read_csv(tl_path)
    # Filter to common stocks (exclude ETF/ETN/preferred/REIT/SPAC)
    ETF_PFX = ['KODEX','TIGER','KBSTAR','ARIRANG','SOL ','HANARO','KOSEF',
        'ACE ','TIMEFOLIO','PLUS ','히어로','파워 ','마이다스',
        'TRUE','RISE ','FOCUS','WOORI','1Q ','TREX','KINDEX','QV ']
    ETF_CTN = ['ETN','레버리지','인버스','선물','합성)','액티브','패시브',
        'S&P','나스닥100','MSCI','블룸버그']
    def is_common(name):
        n = str(name)
        for p in ETF_PFX:
            if n.startswith(p): return False
        for c in ETF_CTN:
            if c in n: return False
        if n.endswith('우') or n.endswith('우B') or n.endswith('우C') or n.endswith('우D'): return False
        if n.endswith('리츠'): return False
        if '스팩' in n or 'SPAC' in n: return False
        return True
    common = tl[tl['name'].apply(is_common)]
    kospi_codes = set(str(c).zfill(6) for c in common[common['market']=='KOSPI']['code'])
    kosdaq_codes = set(str(c).zfill(6) for c in common[common['market']=='KOSDAQ']['code'])
    all_codes = kospi_codes | kosdaq_codes
    # Build DataFrame from CSV dict
    frames = {}
    for code, s in kr_csv.items():
        if code in all_codes and len(s) > 100:
            frames[code] = s
    if not frames:
        print("  KR breadth: no valid stocks, skipping")
        return None
    df = pd.DataFrame(frames)
    print(f"  KR breadth: computing from {len(df.columns)} common stocks ({len([c for c in df.columns if c in kospi_codes])} KOSPI + {len([c for c in df.columns if c in kosdaq_codes])} KOSDAQ)")
    # Moving averages
    ma200 = df.rolling(200, min_periods=150).mean()
    ma50 = df.rolling(50, min_periods=30).mean()
    # % above 200d MA (all)
    v200 = df.notna() & ma200.notna()
    pct_200 = ((df[v200] > ma200[v200]).sum(axis=1) / v200.sum(axis=1) * 100).round(1)
    # % above 50d MA (all)
    v50 = df.notna() & ma50.notna()
    pct_50 = ((df[v50] > ma50[v50]).sum(axis=1) / v50.sum(axis=1) * 100).round(1)
    # KOSPI only breadth
    ki_cols = [c for c in df.columns if c in kospi_codes]
    ki_v200 = df[ki_cols].notna() & ma200[ki_cols].notna()
    pct_200_kospi = ((df[ki_cols][ki_v200] > ma200[ki_cols][ki_v200]).sum(axis=1) / ki_v200.sum(axis=1) * 100).round(1)
    # KOSDAQ only breadth
    kq_cols = [c for c in df.columns if c in kosdaq_codes]
    kq_v200 = df[kq_cols].notna() & ma200[kq_cols].notna()
    pct_200_kosdaq = ((df[kq_cols][kq_v200] > ma200[kq_cols][kq_v200]).sum(axis=1) / kq_v200.sum(axis=1) * 100).round(1)
    # Advance / Decline
    daily_ret = df.pct_change()
    advances = (daily_ret > 0).sum(axis=1)
    declines = (daily_ret < 0).sum(axis=1)
    ad_ratio = (advances / declines.replace(0, 1)).round(2)
    ad_net = advances - declines
    ad_line = ad_net.cumsum()
    # Net new 52w highs
    hi252 = df.rolling(252, min_periods=200).max()
    lo252 = df.rolling(252, min_periods=200).min()
    v52 = df.notna() & hi252.notna()
    n_hi = ((df[v52] / hi252[v52] - 1).abs() < 0.02).sum(axis=1)
    n_lo = ((df[v52] / lo252[v52] - 1).abs() < 0.02).sum(axis=1)
    net_52w = n_hi - n_lo
    result = pd.DataFrame({
        'KR_Pct200': pct_200,
        'KR_Pct50': pct_50,
        'KR_Pct200_KOSPI': pct_200_kospi,
        'KR_Pct200_KOSDAQ': pct_200_kosdaq,
        'KR_AD_Ratio': ad_ratio,
        'KR_AD_Net': ad_net,
        'KR_AD_Line': ad_line,
        'KR_Net52w': net_52w,
    })
    result.attrs['n_stocks'] = len(df.columns)
    last = result.iloc[-1]
    print(f"  KR breadth latest: 200d={last['KR_Pct200']:.1f}% | 50d={last['KR_Pct50']:.1f}% | A/D={last['KR_AD_Ratio']:.2f} | net52w={last['KR_Net52w']:.0f}")
    return result

KR_BREADTH = compute_kr_breadth(KR_CSV)

# Phase 0.6: Compute US broad market breadth from Russell 3000
def compute_us_breadth():
    """Download Russell 3000 proxy (top 3000 by mcap) and compute breadth + 52w highs."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tl_path = os.path.join(base_dir, 'data', 'us_ticker_list.csv')
    if not os.path.exists(tl_path):
        print("  US breadth: us_ticker_list.csv not found, skipping")
        return None, []
    tl = pd.read_csv(tl_path)
    tickers = list(tl['symbol'])
    name_map = dict(zip(tl['symbol'], tl['name']))
    sector_map = dict(zip(tl['symbol'], tl['sector'].fillna('')))
    print(f"  US breadth: downloading {len(tickers)} tickers (1y) in batches...")
    # Batch download to avoid rate limits
    BATCH = 500
    frames = {}
    import time as _t2
    for i in range(0, len(tickers), BATCH):
        batch = tickers[i:i+BATCH]
        if i > 0: _t2.sleep(3)  # Pause between batches
        batch = tickers[i:i+BATCH]
        try:
            raw = yf.download(batch, period='1y', progress=False, group_by='ticker', threads=True)
            if raw is None or raw.empty: continue
            for t in batch:
                try:
                    if len(batch) == 1:
                        s = raw['Close'].squeeze()
                    else:
                        if t not in raw.columns.get_level_values(0): continue
                        s = raw[t]['Close'].squeeze()
                    if isinstance(s, pd.Series) and s.notna().sum() > 50:
                        frames[t] = s
                except: pass
            print(f"    batch {i//BATCH+1}/{(len(tickers)-1)//BATCH+1}: {len(frames)} stocks so far")
        except Exception as e:
            print(f"    batch {i//BATCH+1} failed: {e}")
            continue
    if not frames:
        print("  US breadth: no valid data")
        return None, []
    df = pd.DataFrame(frames)
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df = df.sort_index().ffill()
    print(f"  US breadth: {len(df.columns)} stocks loaded, {len(df)} trading days")
    # Moving averages
    ma200 = df.rolling(200, min_periods=150).mean()
    ma50 = df.rolling(50, min_periods=30).mean()
    # % above 200d MA
    v200 = df.notna() & ma200.notna()
    pct_200 = ((df[v200] > ma200[v200]).sum(axis=1) / v200.sum(axis=1) * 100).round(1)
    # % above 50d MA
    v50 = df.notna() & ma50.notna()
    pct_50 = ((df[v50] > ma50[v50]).sum(axis=1) / v50.sum(axis=1) * 100).round(1)
    # Advance / Decline
    daily_ret = df.pct_change()
    advances = (daily_ret > 0).sum(axis=1)
    declines = (daily_ret < 0).sum(axis=1)
    ad_ratio = (advances / declines.replace(0, 1)).round(2)
    ad_net = advances - declines
    # Net new 52w highs
    hi252 = df.rolling(252, min_periods=200).max()
    lo252 = df.rolling(252, min_periods=200).min()
    v52 = df.notna() & hi252.notna()
    n_hi = ((df[v52] / hi252[v52] - 1).abs() < 0.02).sum(axis=1)
    n_lo = ((df[v52] / lo252[v52] - 1).abs() < 0.02).sum(axis=1)
    net_52w = n_hi - n_lo
    result = pd.DataFrame({
        'US_Pct200': pct_200, 'US_Pct50': pct_50,
        'US_AD_Ratio': ad_ratio, 'US_AD_Net': ad_net, 'US_Net52w': net_52w,
    })
    result.attrs['n_stocks'] = len(df.columns)
    # 52-week highs list
    us_highs = []
    if hi252 is not None and len(hi252) > 0:
        for t in df.columns:
            try:
                cur = float(df[t].iloc[-1])
                if pd.isna(cur) or cur <= 0: continue
                h52 = float(hi252[t].iloc[-1]) if pd.notna(hi252[t].iloc[-1]) else 0
                if h52 <= 0: continue
                pct = (cur / h52 - 1) * 100
                if pct >= -0.5:
                    us_highs.append({
                        't': t, 'n': name_map.get(t, t),
                        'p': round(cur, 2), 'pct': round(pct, 1),
                        'sector': sector_map.get(t, '')
                    })
            except: pass
        us_highs.sort(key=lambda x: -x['pct'])
    last = result.iloc[-1]
    print(f"  US breadth latest: 200d={last['US_Pct200']:.1f}% | 50d={last['US_Pct50']:.1f}% | A/D={last['US_AD_Ratio']:.2f} | net52w={last['US_Net52w']:.0f}")
    print(f"  US 52w highs: {len(us_highs)} stocks")
    return result, us_highs

US_BREADTH, US_52W_HIGHS = compute_us_breadth()

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

# Separate: KR stocks from CSV, everything else from yfinance
yf_tickers = set()
kr_from_csv = 0
for t in all_tickers:
    code = kr_code(t)
    if code and code in KR_CSV:
        kr_from_csv += 1  # skip yfinance, use CSV
    else:
        yf_tickers.add(t)

print(f"Downloading {len(yf_tickers)} tickers via yfinance + {kr_from_csv} KR stocks from CSV...")
raw = yf.download(list(yf_tickers), start=START, end=END, progress=False, group_by='ticker')

def parse_tickers(ticker_map):
    df = pd.DataFrame()
    ok = []
    for t, n in ticker_map.items():
        try:
            code = kr_code(t)
            if code and code in KR_CSV:
                s = KR_CSV[code].copy(); s.name = n
                if s.notna().sum() > 100:
                    df = pd.concat([df, s], axis=1); ok.append(n)
            elif t in raw.columns.get_level_values(0):
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
            code = kr_code(t)
            if code and code in KR_CSV:
                s = KR_CSV[code].copy(); s.name = t
                if s.notna().sum() > 100:
                    df = pd.concat([df, s], axis=1); ok.append(t)
            elif t in raw.columns.get_level_values(0):
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
# Inject US broad market breadth into Global regime
if US_BREADTH is not None:
    for col in ['US_Pct200','US_Pct50','US_AD_Ratio','US_Net52w']:
        if col in US_BREADTH.columns:
            daily_g[col] = US_BREADTH[col].reindex(daily_g.index).ffill().bfill()
            g_ok.append(col)
    us_br_cols = [c for c in ['US_Pct200','US_Pct50','US_AD_Ratio','US_Net52w'] if c in daily_g.columns]
    if us_br_cols:
        G_CAT_A['US Breadth'] = us_br_cols
        if 'US Breadth' not in CAT_ORD: CAT_ORD.append('US Breadth')

# Korea regime data
df_kr, kr_ok = parse_tickers(kr_regime_map)
daily_kr = df_kr.dropna(how='all')
# Inject broad market breadth into KR regime
if KR_BREADTH is not None:
    for col in ['KR_Pct200','KR_Pct50','KR_AD_Ratio','KR_Net52w']:
        if col in KR_BREADTH.columns:
            daily_kr[col] = KR_BREADTH[col].reindex(daily_kr.index).ffill().bfill()
            kr_ok.append(col)
KR_CAT_A = {}
for cat, tks in KR_UNI.items():
    assets = [n for n in tks.values() if n in daily_kr.columns]
    if assets: KR_CAT_A[cat] = assets
# Add breadth category
kr_breadth_cols = [c for c in ['KR_Pct200','KR_Pct50','KR_AD_Ratio','KR_Net52w'] if c in daily_kr.columns]
if kr_breadth_cols:
    KR_CAT_A['KR Breadth'] = kr_breadth_cols
    if 'KR Breadth' not in KR_CAT_ORD: KR_CAT_ORD.append('KR Breadth')

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
                dn = ticker_name(t)
                stocks.append({'t':t,'en':dn[0],'kr':dn[1],'z':round(z,2),'rz':round(z-bench_z,2),'p':round(p,2) if p else None,'a200':above200})
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

# ═══ 52-WEEK HIGHS ═══
print("52-week highs...")
# US: use pre-computed from Russell 3000 universe, fallback to Finviz
if US_52W_HIGHS:
    us_highs = US_52W_HIGHS
    print(f"  US: {len(us_highs)} stocks from Russell 3000 universe")
else:
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
    kr_highs = fallback_kr_52w_highs(KR_CSV)
    print(f"  KR fallback: {len(kr_highs)} stocks from CSV universe")

print(f"  Final: US={len(us_highs)} | KR={len(kr_highs)}")

data = {
    'global':{'strategic':g_strat,'tactical':g_tact,'int_strategic':gi_strat,'int_tactical':gi_tact},
    'korea':{'strategic':kr_strat,'tactical':kr_tact,'int_strategic':ki_strat,'int_tactical':ki_tact},
    'highs_us': us_highs[:300],
    'highs_kr': kr_highs[:300],
}
# Add US breadth snapshot
if US_BREADTH is not None and len(US_BREADTH) > 0:
    last = US_BREADTH.iloc[-1]
    data['us_breadth'] = {
        'pct200': round(float(last.get('US_Pct200', 0)), 1),
        'pct50': round(float(last.get('US_Pct50', 0)), 1),
        'ad_ratio': round(float(last.get('US_AD_Ratio', 0)), 2),
        'ad_net': int(last.get('US_AD_Net', 0)),
        'net_52w': int(last.get('US_Net52w', 0)),
        'n_stocks': US_BREADTH.attrs.get('n_stocks', 0),
        'hist_pct200': [round(float(x), 1) for x in US_BREADTH['US_Pct200'].dropna().tail(60).values],
        'hist_pct50': [round(float(x), 1) for x in US_BREADTH['US_Pct50'].dropna().tail(60).values],
        'hist_net52w': [int(x) for x in US_BREADTH['US_Net52w'].dropna().tail(60).values],
        'hist_ad_net': [int(x) for x in US_BREADTH['US_AD_Net'].dropna().tail(60).values],
    }
# Add KR breadth snapshot
if KR_BREADTH is not None and len(KR_BREADTH) > 0:
    last = KR_BREADTH.iloc[-1]
    data['kr_breadth'] = {
        'pct200': round(float(last.get('KR_Pct200', 0)), 1),
        'pct50': round(float(last.get('KR_Pct50', 0)), 1),
        'pct200_kospi': round(float(last.get('KR_Pct200_KOSPI', 0)), 1),
        'pct200_kosdaq': round(float(last.get('KR_Pct200_KOSDAQ', 0)), 1),
        'ad_ratio': round(float(last.get('KR_AD_Ratio', 0)), 2),
        'ad_net': int(last.get('KR_AD_Net', 0)),
        'net_52w': int(last.get('KR_Net52w', 0)),
        'n_stocks': KR_BREADTH.attrs.get('n_stocks', 0),
        # Historical for sparkline (last 60 trading days)
        'hist_pct200': [round(float(x), 1) for x in KR_BREADTH['KR_Pct200'].dropna().tail(60).values],
        'hist_pct50': [round(float(x), 1) for x in KR_BREADTH['KR_Pct50'].dropna().tail(60).values],
        'hist_net52w': [int(x) for x in KR_BREADTH['KR_Net52w'].dropna().tail(60).values],
        'hist_ad_net': [int(x) for x in KR_BREADTH['KR_AD_Net'].dropna().tail(60).values],
    }
data_str = json.dumps(data, separators=(',',':'))
print(f"Data JSON: {len(data_str)/1024:.0f} KB")

# ═══ 5. HTML ═══
FAVICON = 'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAABdmlDQ1BJQ0MgUHJvZmlsZQAAeJylkLFLw0AYxV9bRdFKBx0cHDIUB2lB6uKodShIKaVWsOqSpEkrJG1IUkQcHVw7dFFxsYr/gW7iPyAIgjq56OygIIKU+K4pxKGd/MLd9+PdvcvdA8JNQzWdoXnArLl2IZOWNkqbEv6UrDrWcj6fxcD6ekRI9IekOGvwvr41XtYcFQiNkhdVy3bJS+TcrmsJbpKn1KpcJp+TEzYvSL4XuuLzm+CKz9+C7WJhBQhHyVLF54RgxWfxFkmt2ibZIMdNo6H27iNeEtVq62vsM93hoIAM0pCgoIEdGHCRZK8xs/6+VNeXQ50elbOFPdh0VFClN0G1wVM1dp26xs/gDlaQfZCpoy+k/D9EV4HhV8/7nANGToDOoef9nHlepw1EnoHbVuCvtxjnO/VmoMVPgdgBcHUTaMoFcM2Mp18s2Za7UoQjrOvAxyUwUQImmfXY1n/X/bx762g/AcV9IHsHHB0Ds9wf2/4F9IxzaxM+sS0AAAsQSURBVHicdZd7jF5HecZ/M2fO+c533/vFu96N17d1YmIbjG1wNtDUToIDknGpECF1UGMiUENrwl9FlEsFcqoGVUrEpRWqKNDWqNCkCW3AwY5yceLEwXc7dm1s732/z7v7Xc93O2dm+scmqiq7jzTz36tn5n2fmfd5hfj7ldYaENayBPHuirDWkK5twA/uIFnZSrbwMbAet4LAEklBR7PMH46/zIogz6nGWXb83WfYsHELtaCKlPKmOOWPh0RpifUEBrAYrI6QIsvyxa/Snt+FiNoQAoywNzO/BwtWCDbOv8Oa4jWaXpyVeoijP36BNX+7HiluJgdQ9wVriKIIETc4cUGtZGkuRrQil8XZEeRAG9YxGAzY97IjbsUPQGdjgVAKWkaTzXQw+fYsZ9/+HVs/PEZQvTkLKpl2UFLhOj7SGETKoSEVbb0tzoknmMrtx0lvwXETOOrdmxp900GMlIwWr9Ib5IiEQgJCW5RU+J6PNebWGdi46i4m81eYW5jG9Vy8mKJar2KLkjs+JOkaP0BuZpBadS2V6P1IdxtuPIWQYLRGWIEUlo9OvcHGG6cRVhAJgRKS2eYcAw+uY93GDTTq9Vtr4Mzhq+zd+xAlk+flU78mX71BttMlaliaJYe+FSn6VuQJmzPUii8yNzXM5MRmTOyT+NleqhJGqjnef+M0xgoiIRHCQmTJtS/y2Qc/h9SC6JaFAxlUyjzzi2fZc8+D7P/019k0tJVWEBE1LdUcVGYNpTlJoxzH9xOsXjfHh7YfpC+1n6jwFneUcoxNH8VYixYSgcVg8JSHqilqpWBJOv8P5NjYGCdPnySXn2NkeBV/9umvsHv7XnzHx5qQsGLRFQhLIdV8SGEWomaW1bcXGO75BmsvfZeRcp5IOIh3pegJl6nyNGJ1gs6ubrTRWGGxAqwVGPO/r0kA9r6d9/PsfzyD53tIJFh46ehvOXj0aVpOExE5iFCCgJa12NCBCJxURPlKgy0nPsKg20/TtIgJxTv6Gl27V/Gphx/EdRRBrUYinkSbEOE2ESpBrRYipEW9b/2dPPalx/DjPlpHaKNxXMXoyDrWXvwgg8OD9Lb1E1NxTlw4zYWLF6hHZbQbENYgNiQ5v3iCnmv34sUVQdngbzvJzj/N891Xz3N8bpxqWKIrkyK2uIX2xft5+IE4WzaNEDQFYvz3k3ZoZPD/1KUJTEyO05lppyOTAQHHXn+Lxx9/nD2f/COeee7fuVGe4/NffJhSmOPc9dMMvL6ascZHOF48w+7vHePIsgW++ZscZOKAAgp0TnyLrokvk3XPMTZaZee2DOrFk8/RcbmdZLqTfhmn8/p1GtMzZG4bpv0P7sGKDPV6nSf+5gBXfn+ZN4+/wd1jY8zN5ChO19n/5a/xyyP/ym/sCxz63fPcs2+OsY+neOblOjLWjpIOWkuMW8dJ5EjHoS7X8+zZJofPXkEdPv0sxlNsmI944FQOm2qnZ+e9BP/yj4w/9ST9Xz/A3MhaXnvlVbp7e5iZmWF4aJhkOsHZM+fo7upl765HCWqW/KpDPPRYiqffnuOnF0qImCQyFitrxKsb6czvJbIWaQyZVIxUYwVKeXG6y5pPHJ+mPVeg1a0pXbxINDdPcOkc1/bvI/btp9mweQtHfvsCAK+/cRSAr331rzDGEE/67NvzKK++KagVnycRd1loWoRnEUZhVI14bR3Jyu2ESgMSozV3Tx1BOVnJuqsFGJ9lQVmYmsIpVQhrdSLlEk7O0vjnH3L3zs2MT1xkZjxHKpXigV27ePTRfUgpMVaTzST5wPoxQnuIfFDAkQKsRDsBjs6SLn0U7URLfzkSgUBZi4onLapQIVcJcHwJUpGIZ6m3NM2oTCglxev/TWGbx91/cieL1wv0d4zwxw98BscRLM7P4/sxikXDQukCT01P8KPzFYh5IOq41XWsmHiaZDCKESAFNBxYVbjGYGUaZYAFXxKPNLYZ4hBhLp/HSkUkLZGGasLFpi1+xjLc104YLvLzE98ndqodjyxu5LNmqMSn7p8gkRfQEGSFw4DN0JMfoZqPMO55lLSEUQLrDDK6OIevayiD5cbKLOlMGhOUMBisBWMimtYicZnvyxI0BdKAUYJE5CCUJlnP0zN/ibW6wtBojJdOZmm73MuusI1O4iTdOGL5NSrtf47ERTqCWtWlUe4nMduHiYYRX/jBx61wBP2HZkkffodWq0ZowGCxSLhzBTOfWENdQMPChquWh1+cJLxLc6gvxg0vRmA0eSeDM9CLKyEes8yXc9RqTTJtbSTiPsZERK0IL+6ibY3CfIPut1eihBVgLLl7+gi6FLGTM7BYQ8dc9NoeatuX4aQVmRBcT5CaCDAzs7wY9PDaymXEVJINg1t4aP19/PyfDvL8c//Ftu1b2fu5vVyeusipK69wI8gjIofORA/njl2nv2eATZs/wHjqMuKLP9htJRYjDNaVOC2NU9dYJdEJB6MNQlsQLsIB0zC0xuuI1XFE1GDAX8s3H3mKiSsTbPzgJkZW3kahUOStY8fp7O7g6JljHD3xK8Y27+AfvneQN196lVpQ49vf+Wt279mNtKGDdRQCgWhGaAHNlCL0BLZlEBoQAtBYbRCeQHelcRqGmOcx3bjEdw7u5/j1lxlaMcC1qxN8eNt22tvaqLVaLJvM86VSG6uf/CHur56nhWFyZpxfHzpEKpVGfOMLO+1Cj0/UrcDXSGNAWywCIeVSw7RLigAQUtBckBALiaUEGEkjbICBjNeOrcUYHRml0qwRzuXY9ZNDZFSS8swUZSP5VqKTUkcnTz5xgGRPDPFv+3bYktZMxySLHT6tDg+TNAjHInEQVmCJsNaCBeEImgWBVQY/ZbEGBJJmI8TIEOlIGkGDJoLlRc2eH5+i1TIUPJdcucLc53dSuL2PelDCRA7qRk2TiEnWRtDM1ZmfbzHvK4KUopXSWN9BOAorBdbROJFAh6BigNUAWGFwPQcZCKQQpIRLy2rCAY9ja7pJvXmNYgWi/g5oRfiXczg0SAdpVDYGlVZE2Vh816HbGvqqLaJKg4oQBI6kJQSh4xA5Fs8YGqGktMqFuEBYiwaGrwh6ix4NE6GsRCMoOiHNwTXIVjsyikgv78at+ISzAfGuZXSNbkJp6dGXsGhCqs2IoAaRFHhKkHU8ui1IYZG6BS2JYw1zWnKmuTQmCEBrgzASHAgcTYQhcjRWCGRSUR4boBVXBCqgFWp2rNzHqjvvomPZctQbXZLOkmEodOmISdrilqY2VCJJ0LIUjcEI8KSEmKQY88hnHUyHQFoLYmksuzwQMq0M2pNYITCOBPme7xM4MsCzMe5f9Rhb199Lo1GnFVRRdiTGbEOTX4xoW4TehqVHOnT4FvwQbQShhiASvFZejd40SaqtgrU+YUshhURJiUpD+J6lsiAiwFoEEYoqFy6tZXXXI2zc8T7CepkwAkdKlAOohEUnHBZ6BDdKEd6cpqfksjyWIW4DYiqirpdzvvQIcyeqbFr9S7o6r+LJCogIY9SSxZYstTthEMYSaUlQb+PSxC5OX/ssR05meeXiFD/5yyS9nT7N0KJs4GGth8IlIRMksh109N/GcOc6Bnt6Ofb6GX7xQox5uZGrZoDGgmJqYTPZ5CSdmatkk9O0p2eIxZsIYxDCEmmHYnkZ+cIqcsVRgsYQjgI/bXnnaj8HfjbL978So9kC9bH1f4Gw4HlxUn6aZCpNOplBKpdM0vCj/yzwSnkrMisBi1IaiFOsraFYXQMGljaDEEvTNThgnSV9KFDuUoeNIpAZl8NnfCZmG/R1J/gfTgJMIx6CvrsAAAAASUVORK5CYII='

LOGO = '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'

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
if(S.region==='korea'&&D.kr_breadth){{const B=D.kr_breadth;
h+='<div style="margin-bottom:14px;padding:16px;border-radius:10px;background:var(--s);border:2px solid var(--b)">';
h+='<div style="font-family:var(--m);font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.08em;color:var(--t);margin-bottom:10px">Broad Market Breadth \\u00b7 '+B.n_stocks+' Stocks</div>';
h+='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px;margin-bottom:10px">';
const bc=v=>v>=60?'var(--g)':v<=40?'var(--r)':'var(--x)';
const ac=v=>v>1.5?'var(--g)':v<0.7?'var(--r)':'var(--x)';
const nc=v=>v>20?'var(--g)':v<-20?'var(--r)':'var(--x)';
h+='<div style="padding:8px;border-radius:6px;background:var(--bl)"><div style="font-family:var(--m);font-size:8px;color:var(--t3)">% above 200d MA</div><div style="font-family:var(--m);font-size:22px;font-weight:800;color:'+bc(B.pct200)+'">'+B.pct200+'%</div><div style="font-family:var(--m);font-size:8px;color:var(--t3)">KOSPI '+B.pct200_kospi+'% \\u00b7 KOSDAQ '+B.pct200_kosdaq+'%</div></div>';
h+='<div style="padding:8px;border-radius:6px;background:var(--bl)"><div style="font-family:var(--m);font-size:8px;color:var(--t3)">% above 50d MA</div><div style="font-family:var(--m);font-size:22px;font-weight:800;color:'+bc(B.pct50)+'">'+B.pct50+'%</div></div>';
h+='<div style="padding:8px;border-radius:6px;background:var(--bl)"><div style="font-family:var(--m);font-size:8px;color:var(--t3)">Advance / Decline</div><div style="font-family:var(--m);font-size:22px;font-weight:800;color:'+ac(B.ad_ratio)+'">'+B.ad_ratio+'</div><div style="font-family:var(--m);font-size:8px;color:var(--t3)">net '+(B.ad_net>=0?'+':'')+B.ad_net+'</div></div>';
h+='<div style="padding:8px;border-radius:6px;background:var(--bl)"><div style="font-family:var(--m);font-size:8px;color:var(--t3)">Net 52w Highs</div><div style="font-family:var(--m);font-size:22px;font-weight:800;color:'+nc(B.net_52w)+'">'+(B.net_52w>=0?'+':'')+B.net_52w+'</div></div>';
h+='</div>';
const spk=(arr,w,ht,col)=>{{if(!arr||!arr.length)return'';const mn=Math.min(...arr),mx=Math.max(...arr),rg=mx-mn||1;let pts=arr.map((v,i)=>[i/(arr.length-1)*w,(1-(v-mn)/rg)*ht]);let d2="M"+pts.map(p2=>p2[0]+","+p2[1]).join("L");return'<svg width="'+w+'" height="'+ht+'" style="display:block"><path d="'+d2+'" fill="none" stroke="'+col+'" stroke-width="1.5"/><circle cx="'+pts[pts.length-1][0]+'" cy="'+pts[pts.length-1][1]+'" r="2" fill="'+col+'"/></svg>'}};
h+='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px">';
h+='<div style="padding:6px"><div style="font-family:var(--m);font-size:8px;color:var(--t3);margin-bottom:3px">% above 200d (60d)</div>'+spk(B.hist_pct200,200,40,bc(B.pct200))+'</div>';
h+='<div style="padding:6px"><div style="font-family:var(--m);font-size:8px;color:var(--t3);margin-bottom:3px">% above 50d (60d)</div>'+spk(B.hist_pct50,200,40,bc(B.pct50))+'</div>';
h+='<div style="padding:6px"><div style="font-family:var(--m);font-size:8px;color:var(--t3);margin-bottom:3px">Net 52w Highs (60d)</div>'+spk(B.hist_net52w,200,40,nc(B.net_52w))+'</div>';
h+='<div style="padding:6px"><div style="font-family:var(--m);font-size:8px;color:var(--t3);margin-bottom:3px">A/D Net (60d)</div>'+spk(B.hist_ad_net,200,40,'var(--t2)')+'</div>';
h+='</div></div>';
}}
if(S.region==='global'&&D.us_breadth){{const B=D.us_breadth;
h+='<div style="margin-bottom:14px;padding:16px;border-radius:10px;background:var(--s);border:2px solid var(--b)">';
h+='<div style="font-family:var(--m);font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.08em;color:var(--t);margin-bottom:10px">Broad Market Breadth \\u00b7 Russell 3000 \\u00b7 '+B.n_stocks+' Stocks</div>';
h+='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px;margin-bottom:10px">';
const bc=v=>v>=60?'var(--g)':v<=40?'var(--r)':'var(--x)';
const ac=v=>v>1.5?'var(--g)':v<0.7?'var(--r)':'var(--x)';
const nc=v=>v>20?'var(--g)':v<-20?'var(--r)':'var(--x)';
h+='<div style="padding:8px;border-radius:6px;background:var(--bl)"><div style="font-family:var(--m);font-size:8px;color:var(--t3)">% above 200d MA</div><div style="font-family:var(--m);font-size:22px;font-weight:800;color:'+bc(B.pct200)+'">'+B.pct200+'%</div></div>';
h+='<div style="padding:8px;border-radius:6px;background:var(--bl)"><div style="font-family:var(--m);font-size:8px;color:var(--t3)">% above 50d MA</div><div style="font-family:var(--m);font-size:22px;font-weight:800;color:'+bc(B.pct50)+'">'+B.pct50+'%</div></div>';
h+='<div style="padding:8px;border-radius:6px;background:var(--bl)"><div style="font-family:var(--m);font-size:8px;color:var(--t3)">Advance / Decline</div><div style="font-family:var(--m);font-size:22px;font-weight:800;color:'+ac(B.ad_ratio)+'">'+B.ad_ratio+'</div><div style="font-family:var(--m);font-size:8px;color:var(--t3)">net '+(B.ad_net>=0?'+':'')+B.ad_net+'</div></div>';
h+='<div style="padding:8px;border-radius:6px;background:var(--bl)"><div style="font-family:var(--m);font-size:8px;color:var(--t3)">Net 52w Highs</div><div style="font-family:var(--m);font-size:22px;font-weight:800;color:'+nc(B.net_52w)+'">'+(B.net_52w>=0?'+':'')+B.net_52w+'</div></div>';
h+='</div>';
const spk=(arr,w,ht,col)=>{{if(!arr||!arr.length)return'';const mn=Math.min(...arr),mx=Math.max(...arr),rg=mx-mn||1;let pts=arr.map((v,i)=>[i/(arr.length-1)*w,(1-(v-mn)/rg)*ht]);let d2="M"+pts.map(p2=>p2[0]+","+p2[1]).join("L");return'<svg width="'+w+'" height="'+ht+'" style="display:block"><path d="'+d2+'" fill="none" stroke="'+col+'" stroke-width="1.5"/><circle cx="'+pts[pts.length-1][0]+'" cy="'+pts[pts.length-1][1]+'" r="2" fill="'+col+'"/></svg>'}};
h+='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px">';
h+='<div style="padding:6px"><div style="font-family:var(--m);font-size:8px;color:var(--t3);margin-bottom:3px">% above 200d (60d)</div>'+spk(B.hist_pct200,200,40,bc(B.pct200))+'</div>';
h+='<div style="padding:6px"><div style="font-family:var(--m);font-size:8px;color:var(--t3);margin-bottom:3px">% above 50d (60d)</div>'+spk(B.hist_pct50,200,40,bc(B.pct50))+'</div>';
h+='<div style="padding:6px"><div style="font-family:var(--m);font-size:8px;color:var(--t3);margin-bottom:3px">Net 52w Highs (60d)</div>'+spk(B.hist_net52w,200,40,nc(B.net_52w))+'</div>';
h+='<div style="padding:6px"><div style="font-family:var(--m);font-size:8px;color:var(--t3);margin-bottom:3px">A/D Net (60d)</div>'+spk(B.hist_ad_net,200,40,'var(--t2)')+'</div>';
h+='</div></div>';
}}


const cp=I.catchphrase;
h+='<div class="sig"><div><div class="sh">Cycle Assessment</div><div class="sl">'+cp.cycle.join('<br>')+'</div></div><div><div class="sh">Thematic Rotation</div><div class="sl">'+cp.themes.join('<br>')+'</div></div></div>';
h+='<div class="sc">Sort: <button class="'+(S.sort==='rel'||S.sort==='default'?'on':'')+'" onclick="U(\\'sort\\',\\'rel\\')">Rel \\u2193</button><button class="'+(S.sort==='abs'?'on':'')+'" onclick="U(\\'sort\\',\\'abs\\')">Abs \\u2193</button><button class="'+(S.sort==='cat'?'on':'')+'" onclick="U(\\'sort\\',\\'cat\\')">Category</button></div>';
if(S.sort==='cat'){{co.forEach(cat=>{{const cbs=bs.filter(b=>b.cat===cat);if(!cbs.length)return;h+='<div class="bcat"><h3>'+cat+' ('+cbs.length+')</h3><div class="bgrid">';cbs.sort((a,b)=>b.rel-a.rel);cbs.forEach(b=>{{h+=mkBC(b)}});h+='</div></div>'}})}}
else{{const sorted=S.sort==='abs'?[...bs].sort((a,b)=>Math.abs(b.z)-Math.abs(a.z)):[...bs].sort((a,b)=>b.rel-a.rel);h+='<div class="bgrid">';sorted.forEach(b=>{{h+=mkBC(b)}});h+='</div>'}}
return h}}
function mkBC(b){{const zc=b.rel>0.5?'pos':b.rel<-0.5?'neg':'neu';let h='<div class="bc" onclick="this.classList.toggle(\\'open\\')"><div class="bn"><span>'+b.name+'</span><span class="al '+(b.rel>0.3?'bu':b.rel<-0.3?'be':'si')+'">'+( b.rel>0?'OUT':'UNDER')+'</span></div><div class="bz '+zc+'">'+(b.rel>=0?'+':'')+b.rel.toFixed(2)+'</div><div class="bsub">'+b.cat+(b.pct200!=null?' \\u00b7 '+b.pct200+'% >200d':'')+'</div><div class="bst">';b.stocks.forEach(s=>{{const sc=s.rz>0.3?'var(--g)':s.rz<-0.3?'var(--r)':'var(--x)';const a2=s.a200===true?'\\u25b2':s.a200===false?'\\u25bc':'';h+='<div class="bs"><span class="st">'+(s.en||s.t)+(s.kr?' <span style="opacity:.5">'+s.kr+'</span>':'')+'</span><span>'+a2+(s.p?fP(s.p,s.t):'')+'</span><span class="sz" style="color:'+sc+'">'+(s.rz>=0?'+':'')+s.rz.toFixed(2)+'</span></div>'}});h+='</div></div>';return h}}
function pgHighs(){{
const hk=S.region==='korea'?'highs_kr':'highs_us';const hs=D[hk];const isKr=S.region==='korea';
const brd=isKr?D.kr_breadth:D.us_breadth;
let h='<div class="md">'+(isKr?'KOSPI + KOSDAQ \\u00b7 52-Week High \\u00b7 ':'Russell 3000 \\u00b7 52-Week High \\u00b7 ')+hs.length+' stocks'+(brd?' \\u00b7 from '+brd.n_stocks+' universe':'')+'</div>';
if(hs.length===0){{h+='<div style="padding:40px;text-align:center;color:var(--t3);font-family:var(--m)">No 52-week highs found</div>';return h}}
h+='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:5px">';
hs.forEach(s=>{{
let main,sub,sub2='';
if(isKr){{main=s.n||s.t;sub=(s.en?s.en+' \\u00b7 ':'')+s.t}}
else{{main=s.t;sub=s.n||'';sub2=s.sector||''}}
h+='<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 12px;border-radius:6px;background:var(--s);border:1px solid var(--b);border-left:3px solid var(--g)"><div style="min-width:0;flex:1"><div style="font-family:var(--m);font-size:11px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">'+main+'</div><div style="font-family:var(--m);font-size:9px;color:var(--t3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis">'+sub+'</div>'+(sub2?'<div style="font-family:var(--m);font-size:8px;color:var(--t3)">'+sub2+'</div>':'')+'</div><div style="text-align:right;flex-shrink:0;margin-left:8px"><div style="font-family:var(--m);font-size:13px;font-weight:800">'+(isKr?s.p.toLocaleString():'$'+s.p.toLocaleString())+'</div><div style="font-family:var(--m);font-size:8px;font-weight:700;color:var(--g)">\\u2605 '+(s.pct>=0?'NEW HIGH':s.pct.toFixed(1)+'%')+'</div></div></div>'}});
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
