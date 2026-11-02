# 中間発表 Slidev 作業フォルダ

Slidev 53 / Node.js 24.22.0。実行環境と色・文字の基本は、本人所有のプライベートリポジトリ `akakirishima/fujitsu-internship-slides` の現在の GitHub `main` を基準にしています。研究発表向けに、4:3、白背景、メイリオ、オレンジ見出し線、青太字、赤枠のルールを反映しています。

## 起動・書き出し

```powershell
npm ci
npm run dev
npm run export
```

`npm run export` は編集可能な PowerPoint (`exports/midterm-editable.pptx`) を作成する。PDFは `npm run export:pdf` で出力できる。本文、目次、章扉は文字・図形で構成し、現在のスライドには画像オブジェクトを使っていない。

## ファイル

- `slides.md`: 発表のたたき台。文章、図、発表時間の目安を更新する
- `発表日程と確認事項.md`: Gmailで確認した中間報告の日程、未確認事項、参照メール
- `style.css`: Slidev 共通スタイル
- [references/README.md](references/README.md): 参照資料の入口。本人の過去資料、他の発表参考、共通ルールを分けて管理
- `public/`: スライドへ載せる図・画像・動画
- `layouts/lecture.vue`: 富士通資料の本文ページに合わせた共通レイアウト
- `layouts/title-cover.vue`, `layouts/chapter-divider.vue`: 表紙と章扉のレイアウト
- `exports/`: PowerPointなどの書き出し先

## 引き継いだ制作ルール

数値、画像、結論は保存結果と条件を照合する。論文の報告、自分の実装、追加した変更、保存済み結果、未実施を区別する。研究室映像の予測を正解なしに精度と呼ばない。編集可能な本文は句点「。」を避ける。結果画像は元の縦横比を保ち、同じ条件で比較する。表示できたことをもって、結果や画面の正確さを確認済みとはしない。

詳細は[参照資料の入口](references/README.md)から共通ルールを確認する。
`references/過去の本人資料/`にある当時のAI指示書は制作履歴として扱い、現在の研究条件やスライド構成へ自動適用しない。

## 今回の結果の根拠

[発表根拠の対応表](発表根拠の対応表.md)から、各主張と図表の実行ID、集計結果、条件、確認状況をたどる。
現時点では実験結果の登録はなく、保存先の準備を行った段階。
コード、実行、検証、考察がそろった結果からPowerPointへ反映する。

## やることの入口

- [やることと進め方](やること.md)
- [チェックリスト](やることリスト.md)
