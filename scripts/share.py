"""methodology.md のルールで、読みごと・年ごとの女の子の割合（幅つき）と分類を出す"""
import csv, collections, json
N={int(k):tuple(v) for k,v in json.load(open('data/sample_sizes.json')).items()}
d=collections.defaultdict(dict)
for r in csv.DictReader(open('data/yomi_best50.csv')): d[int(r['year']),r['sex']][r['reading']]=int(r['count'])
YEARS=sorted({y for y,_ in d})
cut={k:min(v.values()) for k,v in d.items()}
def share(m,f,y):
    pm,pf=m/N[y][0],f/N[y][1]; return pf/(pm+pf)
out=[]
for rd in sorted({x for v in d.values() for x in v}):
    for y in YEARS:
        m=d[y,'M'].get(rd); f=d[y,'F'].get(rd)
        if m is None and f is None: out.append(dict(reading=rd,year=y,m=None,f=None,lo=None,hi=None,status='both_out')); continue
        mr=(m,m) if m is not None else (0,cut[y,'M']-1)
        fr=(f,f) if f is not None else (0,cut[y,'F']-1)
        lo=share(mr[1],fr[0],y); hi=share(mr[0],fr[1],y)
        out.append(dict(reading=rd,year=y,m=m,f=f,lo=lo,hi=hi,status='ok' if (hi-lo)*100<=20 else 'too_wide'))
byr=collections.defaultdict(list)
for o in out: byr[o['reading']].append(o)
def side(o):
    if o['status']!='ok': return '?'
    return 'M' if o['hi']<=0.40 else 'F' if o['lo']>=0.60 else '-'
res={}
for rd,v in byr.items():
    s=[side(o) for o in v]
    shared=any(o['status']=='ok' and o['lo']>=0.40 and o['hi']<=0.60 for o in v)
    def first_run(sym,start=0):
        for i in range(start,len(s)-1):
            if s[i]==sym and s[i+1]==sym: return i
        return None
    mv=None
    for a,b in [('M','F'),('F','M')]:
        i=first_run(a)
        if i is not None and first_run(b,i+2) is not None: mv=f'{a}->{b}'
    # 向きの変化：25pt以上動いて、その後反対へ25pt以上戻る。
    # 単年の上下では判定しないルール（3章）に従い、隣り合う2年とも判定可能な年の2年平均で見る
    ok=[(o['year'],(o['lo']+o['hi'])/2) for o in v if o['status']=='ok']
    seq=[((a[1]+b[1])/2) for a,b in zip(ok,ok[1:]) if b[0]==a[0]+1]
    turn=any(abs(seq[j]-seq[i])>=0.25 and (seq[k]-seq[j])*(seq[j]-seq[i])<0 and abs(seq[k]-seq[j])>=0.25
             for i in range(len(seq)) for j in range(i+1,len(seq)) for k in range(j+1,len(seq)))
    res[rd]=dict(shared=shared,move=mv,turn=turn,ok_years=sum(o['status']=='ok' for o in v),both_years=sum(o['m'] is not None and o['f'] is not None for o in v))
json.dump(dict(years=YEARS,cells=out,classes=res),open('data/share.json','w'),ensure_ascii=False)
print('読みの数',len(byr),' 判定可能な年が1年以上:',sum(r['ok_years']>0 for r in res.values()),' 男女両方に出た年がある:',sum(r['both_years']>0 for r in res.values()))
print('男女共通:',[k for k,r in res.items() if r['shared']])
print('移動:',{k:r['move'] for k,r in res.items() if r['move']})
print('向きの変化:',[k for k,r in res.items() if r['turn']])
show=[k for k,r in res.items() if r['both_years']>0]
print('\n男女両方に出た年がある読み（'+str(len(show))+'）')
print('読み    '+' '.join(str(y)[2:] for y in YEARS))
for k in sorted(show,key=lambda k:-res[k]['both_years']):
    cells=[]
    for o in byr[k]:
        cells.append('--' if o['status']=='both_out' else '..' if o['status']=='too_wide' else f"{round((o['lo']+o['hi'])/2*100):02d}"[:2] if (o['lo']+o['hi'])/2<0.995 else '99')
    print(f'{k:<6}'+' '.join(cells))
