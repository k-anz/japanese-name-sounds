"""明治安田PDFのテキスト（pdftotext -layout）から読み方ベスト50を抽出する。
usage: python3 -I parse_yomi.py <txt>... > out.csv
出力の検証は check_yomi.py（順位＝人数がそれより多い読みの数＋1）で行う。
"""
import re, sys, csv
HDR = re.compile(r'(?:^|[．.\s])(\d{4}|[０-９]{4})年生まれの名前の読み方ベスト *(５０|50)（(男|女)の子）')
STOP = re.compile(r'年生まれの名前の読み方(ベスト|トップ)３')
RANK = r'(第\s*\d+\s*位|〃)'
PREV_TOP = r'(?:[(（]\s*(?:第\s*\d+\s*位|ランク外|初[^)）]*)\s*[)）]|〃(?=\s+[ァ-ヴ])|第\s*\d+\s*位(?=\s+[ァ-ヴ]))?'
TAIL = r'\s*([ァ-ヴー]{1,8})\s*(?:[（(][^）)\d]*[）)]?)?[^\dァ-ヴ人〃第]*(\d+\s*人|〃)?'
ENT_TOP = re.compile(RANK + r'\s*' + PREV_TOP + TAIL)   # 上位10位（前年順位の欄あり）
ENT = re.compile(RANK + TAIL)                            # 下段2列
KANA_ONLY = re.compile(r'^\s*([ァ-ヴー]+)\s*$')
def z2h(s): return s.translate(str.maketrans('０１２３４５６７８９','0123456789'))
def is_top(ln):
    return re.search(r'[(（]\s*第|[(（]\s*ランク外|[(（]\s*初|^\s*第\s*\d+\s*位\s+(〃|第\s*\d+\s*位)\s|^\s*〃\s+第\s*\d+\s*位\s+[ァ-ヴ]', ln)
w = csv.writer(sys.stdout); w.writerow(['year','sex','rank','reading','count','source'])
for path in sys.argv[1:]:
    lines = open(path, encoding='utf-8').read().split('\n')
    i = 0
    while i < len(lines):
        m = HDR.search(lines[i])
        if not m or re.search(r'（P|\(P|・・|Ｐ\s*[0-9０-９]', lines[i]):
            i += 1; continue
        year = int(z2h(m.group(1))); sex = 'M' if m.group(3)=='男' else 'F'
        j = i+1; block=[]
        while j < len(lines) and not HDR.search(lines[j]) and not STOP.search(lines[j]):
            block.append(lines[j]); j += 1
        # 下段2列の境界：見出し行の2つ目の「順位」の位置
        bound = None
        for ln in block:
            ps = [mm.start() for mm in re.finditer('順位', ln)]
            if len(ps) == 2: bound = ps[1] - 3; break
        top, left, right = [], [], []
        for k, ln in enumerate(block):
            ms = list((ENT_TOP if is_top(ln) else ENT).finditer(ln))
            # 読みが2行に割れている行（例：ショウ／[順位行]／タ）
            if not ms and is_top(ln) and k > 0 and k+1 < len(block):
                a, b = KANA_ONLY.match(block[k-1]), KANA_ONLY.match(block[k+1])
                if a and b:
                    r = re.match(r'\s*' + RANK, ln); c = re.search(r'(\d+)\s*人', ln)
                    top.append([r.group(1), a.group(1)+b.group(1), c.group(0) if c else None]); continue
            for mm in ms:
                cnt = mm.group(3)
                if cnt is None:  # 人数が折り返し行にある
                    for ln2 in block[k+1:k+4]:
                        c2 = re.search(r'(\d+)\s*人', ln2)
                        if c2: cnt = c2.group(0); break
                rec = [mm.group(1), mm.group(2), cnt]
                if len(ms) == 1 and is_top(ln) and mm.start() < 15:
                    top.append(rec)
                elif bound is not None and mm.start() >= bound:
                    right.append(rec)
                else:
                    left.append(rec)
        prev_rank = prev_cnt = None
        for rk, rd, ct in top + left + right:
            if ct is None:
                sys.stderr.write(f'NO COUNT {path} {year} {sex} {rk} {rd}\n'); continue
            rank = prev_rank if rk == '〃' else int(re.sub(r'\D','',z2h(rk)))
            cnt = prev_cnt if ct == '〃' else int(re.sub(r'\D','',z2h(ct)))
            w.writerow([year, sex, rank, rd, cnt, path.split('/')[-1]])
            prev_rank, prev_cnt = rank, cnt
        i = j
