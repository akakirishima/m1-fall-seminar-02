# データ登録CSVの仕様

状態：準備用スキーマ v0.1。ラベル規則と評価条件の確定を意味しない。
[空のひな型](templates/)にはヘッダのみを入れ、実患者や仮の実験件数は登録していない。

## ファイルと列

CSVはUTF-8（BOM付きも可）を使い、1行目の列名と順序をひな型に合わせる。
カンマを含む文字列はCSVの引用規則で囲む。
先頭末尾の空白は検査時に取り除く。

| ファイル | 列 | 記録する内容 |
|---|---|---|
| videos.csv | video_id, patient_id, duration_s, source_ref, sha256 | 匿名動画ID、匿名患者ID、動画長の秒、保存先へのローカル参照、元ファイルのSHA-256 |
| splits.csv | patient_id, split, split_version | 患者ごとに1行。pilot/train/dev/testのいずれかと単一の分割版 |
| coverage.csv | video_id, patient_id, start_s, end_s, annotator, annotation_version | その作業者がその規則版で全時間の注釈を終えた範囲 |
| labels.csv | video_id, patient_id, start_s, end_s, adult_hand_arm, contact_evidence, annotator, annotation_version, note | 範囲内の区間ラベル。note以外は必須 |

時刻は元動画の開始を0とする秒の有限小数で、`0 <= start_s < end_s <= duration_s`とする。
区間は開始を含み終了を含まない。
動画に複数のタイムベースや可変フレームレートがある場合、フレーム番号との変換規則を別途記録する。

adult_hand_armはpresent/absent/uncertain、contact_evidenceはvisible/not_visible/uncertainを使う。
主対象がuncertainならnoteに理由を入れる。
動画ID、作業者、規則版ごとに区間を独立に検査するので、別の作業者の独立注釈は上書きせず追加できる。
同じ範囲を繰り返し注釈する場合は、別のannotation_versionで区別する。

## coverageの意味

coverageは「ここに手が映っている」という陽性区間一覧ではなく、すべての時間を見て注釈した範囲を指す。
同じ動画、作業者、規則版のlabelsがcoverageを隙間なく覆う必要がある。
離れた注釈範囲は複数行に分け、間の時間は未注釈のまま保つ。
ラベル行同士、coverage行同士の重複は同じ組の中では許可しない。

## ローカルで使う方法

リポジトリのルートで次のように実行する。
`data/local/`は実データ登録用としてGitから除外している。
患者対応表や元動画自体は、研究室の決めた保存先に置く。

```sh
mkdir -p data/local/pilot-v01
cp step02_正解データ作成/templates/*.csv data/local/pilot-v01/
# 上の4ファイルへ、確認した実データの情報を入力する。
python3 step02_正解データ作成/scripts/validate_dataset.py \
  --input-dir data/local/pilot-v01 \
  --output data/local/checks/自分で付けた新しい実行ID.json
```

ヘッダのみのひな型はエラーになる。
検査の終了コードは成功0、データ不整合1、コマンド指定の誤り2。
既存の出力ファイルへは上書きしない。
出力には各CSVのSHA-256、行数、患者数、分割ごとの人数、検出した誤りが入る。
検査失敗の入力情報もローカルに保持し、修正後は新しい実行IDで再検査する。

## 検査できる範囲

未知の動画、患者IDの不一致、同一患者の複数分割、分割版の混在、時刻範囲、重複、注釈の隙間、ラベル名を検査する。
元動画を開かないため、source_refの実在、sha256と動画本体の一致、ラベルの映像上の正しさは確認しない。
過去に開発で見た患者のtestへの変更や、別IDを振った同一患者の混入は、履歴と患者対応表で確認する。
患者数の十分性や、本評価に必要な全分割の存在を自動で認定する機能もない。

[合成データのテスト](tests/test_validate_dataset.py)は、実患者やモデルの実験と区別する。

```sh
python3 -m unittest discover -s step02_正解データ作成/tests -v
```
