# AI向け記録形式

更新日：2026年10月30日
本人が毎回記録を読む前提から、AIが必要な記録を選んで確認し、説明する運用へ変更する。

## AIの入口

1. [research_state.json](../research_state.json)で現在地、未決事項、次の作業、必要な文書の参照先を読む。
2. [experiment_index.json](../experiment_index.json)から必要な実行IDを選ぶ。
3. その実行のmanifest.json、設定、保存コード、結果を必要な範囲だけ読む。
4. 判断の理由は研究全体像、変更履歴、日報へたどる。

現在地、ID、状態、データの登録、参照先の正本はresearch_state.jsonとする。
実行の正本は各実行のmanifest.json、個別の測定値はその実行の出力とする。
experiment_index.jsonは派生した索引なので、直接編集しない。
Markdownは目的、仮説、判断の理由、考察、経緯を記述する。
同じ数値や長い入力一覧を複数のMarkdownへ手作業で転記しない。

## 固定項目

[実験記録テンプレート](../templates/experiment_manifest.json)を新しい実行のmanifest.jsonの出発点にする。
実際の実行ではis_templateをfalseへ変更し、項目を実測情報で埋める。
テンプレートは実験として登録しない。

| 項目 | 内容 |
|---|---|
| run_id / step_id / method_id | 実行、ステップ、比較方式のID |
| operation / purpose | 処理名と目的 |
| status | planned、running、completed、failed、interrupted |
| plan_version / protocol_versions | 研究方針とラベル、評価規則の版 |
| parent_run_ids | 利用した前段の実行ID |
| command_argv / working_directory | 引数を分けた起動コマンドと作業場所 |
| code | コードID、実行時コピーの相対参照、SHA-256 |
| inputs / outputs | データID、役割、版、SHA-256、保存区分 |
| config / environment | 既定値を反映した設定と、実際の実行環境 |
| metrics / validation | 測定値と確認結果 |
| reproduction | 再実行コマンド、未確認事項、再現確認の状態 |
| failure | 失敗や中断の理由。成功時はnull |

nullは未確定、配列の空は登録対象なしを表す。
未実施を0点や0秒に置き換えない。
status=completedは処理の終了を示し、科学的な結論の正しさや再現確認の完了を示さない。
validationとreproductionは別の状態として記録する。

## 入出力の参照

codeの各項目はid、snapshot_ref、sha256を持ち、snapshot_refは実行フォルダからの相対パスとする。
inputsとoutputsの各項目はid、role、version、sha256、storageを持つ。
storageはrepositoryまたはlocal_only。
repositoryの場合は必要に応じてプロジェクトからの相対パスをrefへ記載する。
sha256が未取得ならnullとし、fingerprint_missing_reasonに理由を記載する。再現確認済みとは扱わない。
local_onlyの場合は共有記録のrefに実パスを書かず、[ローカル対応表の規則](データ一覧と分割/README.md)に従う。
動画、画像、正解ラベル、患者対応表、モデル重みの本体はGitHubに置かない。
設定やログに元データの実パスが含まれる場合も、ローカル保存先へ分ける。
識別情報自体に機微な内容がある場合は、その情報もローカル側へ置く。

## 操作

プロジェクトのルートで、保存したPythonコードを起動する。

```powershell
python research_tools/ai_records.py context
python research_tools/ai_records.py index
python research_tools/ai_records.py check
python research_tools/ai_records.py validate-manifest --manifest <実行フォルダ>/manifest.json
```

contextはAIが最初に必要とする状態と索引をJSONで返す。
indexは各ステップの既存runsと、状態JSONにruns_dirを登録したP工程のruns直下を調べ、索引を再生成する。
工程の実行には索引上でwork_package_idを付け、保存先の準備だけでは実験に数えない。
checkは文書参照、索引の更新漏れ、ID、親の参照と循環、記録の必須項目、コードコピーとリポジトリ内の入出力の整合性を確認する。
この検査は、実データに対するモデル性能や入力全体の再現性を保証しない。
今後のモデル実行で、既存の記録コードとの接続と実データの識別検査を追加する必要がある。

過去のsources.jsonとverification.jsonは元のまま保持し、索引ではlegacy、partialとして登録する。
旧記録から開始終了、コマンド、環境を推測して完全なmanifestを作らない。
それらの出典確認と記録検査を、介入検知モデルの実験と数えない。

## 更新するタイミング

作業開始時にcontextを読み、必要な規則と該当実験へたどる。
研究方針や現在地が変わったらresearch_state.jsonを更新し、理由を変更履歴または日報へ追記する。
実験の開始、終了、失敗時にその実行のmanifestを更新する。
完了後の記録は保持し、再実行は新しいIDとする。
実行記録の追加後にindex、checkを順に実行する。
日報には変更したIDと確認結果を残す。

索引生成と検査は実装したが、モデルの実行開始終了を自動捕捉するランナーは未統合。
今回モデルや研究データは動かしていない。

## 工程別の保存先と旧形式

新規実行は状態JSONのwork_packagesに登録したruns_dirへ保存する。
完了済みの旧実行は移動せず、旧runsと工程別runsを同じ索引から参照する。
固定形式導入前のmanifestは、legacy_manifestsへ個別登録したものだけをlegacy_manifest、partialとして扱う。
新しい不完全なmanifestの検査は引き続き失敗させる。
発表への接続は[作業と発表根拠の運用](作業フォルダと発表根拠の運用.md)を参照する。
