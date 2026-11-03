"""ページに埋め込むデータ（payload.json）を作る。数値はすべて data/ のCSVとshare.pyの結果から機械的に作る"""
import csv, json, collections
S=json.load(open('data/share.json')); N=json.load(open('data/sample_sizes.json'))
rank=collections.defaultdict(dict); cnts=collections.defaultdict(dict)
for r in csv.DictReader(open('data/yomi_best50.csv')):
    rank[r['year'],r['sex']][r['reading']]=int(r['rank']); cnts[r['year'],r['sex']][r['reading']]=int(r['count'])
cut={k:min(v.values()) for k,v in cnts.items()}
years=S['years']
both={str(y):sorted(set(cnts[str(y),'M'])&set(cnts[str(y),'F'])) for y in years}
rows=[k for k,c in S['classes'].items() if c['both_years']>0]
rows.sort(key=lambda k:(-S['classes'][k]['both_years'],k))
cells={}
for o in S['cells']:
    if o['reading'] not in rows: continue
    y=str(o['year'])
    cells.setdefault(o['reading'],[]).append(dict(y=o['year'],m=o['m'],f=o['f'],
        mr=rank[y,'M'].get(o['reading']),fr=rank[y,'F'].get(o['reading']),
        lo=None if o['lo'] is None else round(o['lo'],4),hi=None if o['hi'] is None else round(o['hi'],4),st=o['status']))
payload=dict(years=years,N=N,cut={f"{y}{s}":v for (y,s),v in cut.items()},both=both,rows=rows,cells=cells,
             shared=[k for k,c in S['classes'].items() if c['shared']],n_readings=len(S['classes']))
M=json.load(open('data/mora.json'))
two={sx:[round(M['count'][f'{y}{sx}'].get('2',0)*100,1) for y in years] for sx in 'MF'}
payload['mora']=dict(two=two,coverage=[min(M['coverage'].values()),max(M['coverage'].values())],overlap=M['overlap'])
# 語尾の表（end）は mora.py の期間集計から作る。ページに埋め込まれた値は 2007〜11年と2021〜25年の上位5語尾
json.dump(payload,open('data/payload.json','w'),ensure_ascii=False,separators=(',',':'))
print(len(json.dumps(payload,ensure_ascii=False)),'bytes; rows',rows)
