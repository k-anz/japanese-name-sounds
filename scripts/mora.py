"""探索的分析（methodology.md 8章）：末尾の拍と拍数"""
import csv, json, collections, re
N={int(k):tuple(v) for k,v in json.load(open('data/sample_sizes.json')).items()}
SMALL=set('ャュョァィゥェォヮ')
def morae(s):
    out=[]
    for ch in s:
        if ch in SMALL and out: out[-1]+=ch
        else: out.append(ch)
    return out
rows=list(csv.DictReader(open('data/yomi_best50.csv')))
fin=collections.defaultdict(collections.Counter); cnt=collections.defaultdict(collections.Counter); tot=collections.Counter()
for r in rows:
    y,s,n=int(r['year']),r['sex'],int(r['count']); m=morae(r['reading'])
    fin[y,s][m[-1]]+=n; cnt[y,s][len(m)]+=n; tot[y,s]+=n
years=sorted({y for y,_ in fin})
def dist(c,t): return {k:v/t for k,v in c.items()}
res=dict(years=years,coverage={},overlap={},final={},count={})
for y in years:
    for s in 'MF':
        res['coverage'][f'{y}{s}']=round(tot[y,s]/N[y][0 if s=='M' else 1],4)
        res['final'][f'{y}{s}']={k:round(v,4) for k,v in dist(fin[y,s],tot[y,s]).items()}
        res['count'][f'{y}{s}']={str(k):round(v,4) for k,v in dist(cnt[y,s],tot[y,s]).items()}
    pm,pf=dist(fin[y,'M'],tot[y,'M']),dist(fin[y,'F'],tot[y,'F'])
    res['overlap'][y]=round(sum(min(pm.get(k,0),pf.get(k,0)) for k in set(pm)|set(pf)),4)
json.dump(res,open('data/mora.json','w'),ensure_ascii=False)
print('カバー率 男',min(res['coverage'][f'{y}M'] for y in years),'-',max(res['coverage'][f'{y}M'] for y in years),' 女',min(res['coverage'][f'{y}F'] for y in years),'-',max(res['coverage'][f'{y}F'] for y in years))
print('男女の重なり（末尾の拍）'); print(' '.join(f"{y}:{res['overlap'][y]:.2f}" for y in years))
# 5年ずつの期間で比較
P={'2007-11':range(2007,2012),'2021-25':range(2021,2026)}
def pool(sex,yrs,which):
    c=collections.Counter(); t=0
    for y in yrs:
        c.update(fin[y,sex] if which=='f' else cnt[y,sex]); t+=tot[y,sex]
    return {k:v/t for k,v in c.items()}
for sex in 'MF':
    for which,label in [('f','末尾の拍'),('c','拍数')]:
        a,b=pool(sex,P['2007-11'],which),pool(sex,P['2021-25'],which)
        keys=sorted(set(a)|set(b),key=lambda k:-(a.get(k,0)+b.get(k,0)))[:10]
        print(f"\n{'男' if sex=='M' else '女'}・{label}  2007-11 → 2021-25")
        print('  '+'  '.join(f"{k}:{a.get(k,0)*100:.0f}→{b.get(k,0)*100:.0f}" for k in keys))
for lbl,yrs in P.items():
    pm,pf=pool('M',yrs,'f'),pool('F',yrs,'f'); print(lbl,'期間の重なり',round(sum(min(pm.get(k,0),pf.get(k,0)) for k in set(pm)|set(pf)),3))
