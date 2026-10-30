# 使用OSSと出典

更新日：2026年10月30日

## 採用状況の読み方

「運用の参考採用」は、公開物の構成や原則を参考に、この研究用の文書へ反映したことを表す。
「実験用の採用方針」は、使用を予定するが、実環境への導入と動作確認はまだという意味である。
「候補」は、採用判断や対応確認が残っている。
この一覧を作ったことは、外部ソフトをインストールしたことやモデルを動かしたことを意味しない。

外部の文書やコードの転載はしていない。
AGENTS.mdと管理文書は、この研究向けに新しく記述した。

## 今回の研究運用に取り入れた公開物

| 公開物 | 採用状況と用途 | ライセンスのメタデータ | 確認した版 |
|---|---|---|---|
| [planning-with-files](https://github.com/OthmanAdi/planning-with-files) | 運用の参考採用。計画、知見、経緯をファイルで残し、再開時に読み直す方式 | MIT | `5d29800bf8b919ca9a88ee7885b90050b5cb64ed` |
| [The-Agentic-Researcher](https://github.com/ZIB-IOL/The-Agentic-Researcher)の[INSTRUCTIONS.md](https://github.com/ZIB-IOL/The-Agentic-Researcher/blob/82d1e3fec5f78863c70c015d2090b9823966e97b/INSTRUCTIONS.md) | 運用の参考採用。引用の照合、評価条件の固定、変更条件の識別、段階的な動作確認 | MIT | `82d1e3fec5f78863c70c015d2090b9823966e97b` |

planning-with-filesの3ファイル方式は、そのまま複製せず、研究全体像、共通規則、ステップ別README、日報へ役割を割り当てた。
外部のスキルパッケージ、フック、コンテナ、常駐ループは導入していない。
このプロジェクトでは[AGENTS.md](../AGENTS.md)に読み方と更新の規則を定める。
AGENTS.mdの扱いは[OpenAI公式ドキュメント](https://learn.chatgpt.com/docs/agent-configuration/agents-md)も参照した。

## 実験に使うソフトの採用方針

すべてこの研究の新しい実験環境には未導入、動作未確認である。
他の既存環境にインストール済みかどうかは、今回調べていない。
以下のSHAは公式リポジトリの調査時点の版であり、その開発版を実験へ採用する指定ではない。
対応する安定版などを確認してから環境を作り、実際に使ったパッケージの版を固定する。

| 公開物 | 状態 | 予定する用途 | ライセンスのメタデータ |
|---|---|---|---|
| [PyTorch](https://github.com/pytorch/pytorch) | 採用方針 | 共通の学習と推論の基盤 | APIはNOASSERTION。使用版の原文確認が必要 |
| [Transformers](https://github.com/huggingface/transformers) | 採用方針 | Qwenのモデルとプロセッサの読み込み、推論 | Apache-2.0 |
| [PEFT](https://github.com/huggingface/peft) | 追加学習の第一候補 | LoRAによる追加学習。選ぶモデルとの対応は個別確認 | Apache-2.0 |
| [Accelerate](https://github.com/huggingface/accelerate) | 候補 | 推論時の配置や学習実行を支援。必要な経路で採用 | Apache-2.0 |
| [torchvision](https://github.com/pytorch/vision) | 分類法の候補 | VGGなどの構成と初期重み。原論文の特定後に実装を判断 | BSD-3-Clause |
| [Qwen3-VL公式コード](https://github.com/QwenLM/Qwen3-VL) | Qwen3-VLを使う場合の実装参考 | 画像質問回答の形式と追加学習コードの確認 | Apache-2.0 |
| [bitsandbytes](https://github.com/bitsandbytes-foundation/bitsandbytes) | 必要時に検討 | 量子化とQLoRA。最初から導入を必須にしない | MIT |

Qwen3-VL用のコードがあることだけで、Qwen3.5の学習にも同じコードが使えるとは判断しない。
推論と追加学習の両方を確認し、M1とM2を同じ基盤モデルで比較できる経路を選ぶ。
分類法の原著実装と介入検知用の重みは未特定であり、公開済みとも非公開とも断定しない。
ラベル付けツールは未選定なので、現時点の使用OSSには含めない。

## モデル重み

モデル重みはソフトウェアのコードと分けて登録する。
両モデルとも公式カードのライセンスメタデータはApache-2.0。
重みは取得しておらず、推論と学習も未実施である。

| モデル | 位置づけ | 確認したrevision |
|---|---|---|
| [Qwen/Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B) | 最初に推論を試す第一候補。主比較への採用は追加学習の成立確認後 | `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a` |
| [Qwen/Qwen3-VL-4B-Instruct](https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct) | 公式学習コードも含めて検討する候補。主比較モデルはまだ固定していない | `ebb281ec70b05090aa6165b016eac8ec08e71b17` |

9B級や別系列は追加比較の候補として既存調査に残すが、最初の実験で必須とはしない。
最終的に取得する重みのrevisionと形式は、実行環境と各実行へ記録する。

## 調査したが今回導入していない公開物

| 公開物 | 今回の扱い |
|---|---|
| [karpathy/autoresearch](https://github.com/karpathy/autoresearch) | 変更可能範囲と固定評価を分ける設計の参考。実験コードや無期限の実行ループは未採用。APIではライセンス情報なしのため、OSS採用済みとは扱わない |
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | 文献調査と批判的検討の候補集。MITメタデータを確認。本体と個別SKILLは未導入 |
| [Orchestra-Research/AI-Research-SKILLs](https://github.com/Orchestra-Research/AI-Research-SKILLs) | 学習と評価の実装手順の候補集。MITメタデータを確認。本体と個別SKILLは未導入 |

## 出典確認と再確認

公式GitHub APIのリポジトリ情報とコミット情報、Hugging Face公式APIのモデル情報を取得した。
確認した全SHA、URL、ライセンスのメタデータ、取得時刻は[出典確認JSON](../step01_文献調査と実験設計/runs/20261030_oss_sources_01/sources.json)に保存した。
手順と結果は[実行結果](../step01_文献調査と実験設計/runs/20261030_oss_sources_01/実行結果.md)に記録する。
メタデータ確認は、ライセンス原文や依存関係全体の確認、コード品質の検証、動作保証の代わりにはならない。

コードや文書を実際に取り込む場合は、使用版のライセンスと著作権表示を保持し、取得元と変更点を記録する。
今後の採用、変更、撤回はこの一覧と方針変更履歴へ反映する。
