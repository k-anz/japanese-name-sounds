import csv,collections,sys
rows=list(csv.DictReader(open(sys.argv[1])))
g=collections.defaultdict(list)
for r in rows: g[r['year'],r['sex']].append(r)
for k,v in sorted(g.items()):
    cs=[int(r['count']) for r in v]
    bad=[(r['reading'],r['rank'],1+sum(c>int(r['count']) for c in cs)) for r in v if 1+sum(c>int(r['count']) for c in cs)!=int(r['rank'])]
    dup=[x for x,c in collections.Counter(r['reading'] for r in v).items() if c>1]
    print(k,len(v),'max rank',max(int(r['rank']) for r in v),'mono',cs==sorted(cs,reverse=True),'rankbad',bad[:4],'dup',dup)
