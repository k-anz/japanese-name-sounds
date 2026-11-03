# 名前の音は男女を越えるか

明治安田生命「生まれ年別の名前調査」2007〜2025年の読み方ベスト50から、男女両方で使われる名前の読みを調べたページです。

- `index.html` … ページ本体（集計済みデータを埋め込み済み。そのままGitHub Pagesで公開できます）
- `docs/methodology.md` … データを見る前に決めた分析ルールと、その後の変更履歴
- `data/sample_sizes.json` … 各年・男女別の調査人数
- `data/mora.json` … 探索的な集計（拍数・語尾）の結果
- `scripts/` … 抽出・検証・集計のスクリプト

## 再集計の手順

元データ（明治安田生命のニュースリリースPDFと、そこから書き起こした読み方ベスト50の表）は、同社サイトの利用規定に配慮してこのリポジトリには含めていません。各年のPDFは同社サイトのニュースリリースから入手できます。

1. PDFを `pdftotext -layout` でテキスト化する（2010年分は文字コード情報がないため、資料編の読み方ベスト50のページを目視で書き起こす）
2. 以下を順に実行する

```
python3 scripts/parse_yomi.py <txtファイル>... > data/yomi_best50.csv   # 読み方ベスト50の抽出
python3 scripts/check_yomi.py data/yomi_best50.csv                       # 順位と人数の整合性検査
python3 scripts/share.py                                                 # 女の子の割合と分類
python3 scripts/mora.py                                                  # 拍数・語尾の集計
python3 scripts/build_payload.py                                         # ページ用データ（data/payload.json）。index.html の const D = の値を差し替える
```

## 出典

- 明治安田生命保険相互会社「生まれ年別の名前調査」
- Ogihara, Y. (2020). Baby names in Japan, 2004–2018: common writings and their readings. *BMC Research Notes*, 13, 553. データセット：OSF, DOI 10.17605/OSF.IO/2WURJ（CC0）
