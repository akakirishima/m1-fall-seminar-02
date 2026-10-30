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
- `references/`: 第1回資料、発表後の記録、書式・内容ルール
- `public/`: スライドへ載せる図・画像・動画
- `layouts/lecture.vue`: 富士通資料の本文ページに合わせた共通レイアウト
- `layouts/title-cover.vue`, `layouts/chapter-divider.vue`: 表紙と章扉のレイアウト
- `exports/`: PowerPointなどの書き出し先

## 引き継いだ制作ルール

数値、画像、結論は保存結果と条件を照合する。論文の報告、自分の実装、追加した変更、保存済み結果、未実施を区別する。研究室映像の予測を正解なしに精度と呼ばない。編集可能な本文は句点「。」を避ける。結果画像は元の縦横比を保ち、同じ条件で比較する。表示できたことをもって、結果や画面の正確さを確認済みとはしない。

詳細は `references/` 内の共通ルールおよびAI指示書を参照。
