---
theme: default
title: 第2回ゼミ研究報告
info: 固定ROI内の成人の手や腕の区間指定支援／実験結果は未測定
lang: ja
colorSchema: light
aspectRatio: 4/3
canvasWidth: 1200
transition: none
mdc: true
drawings:
  persist: false
fonts:
  provider: none
  sans: 'Meiryo, メイリオ, sans-serif'
  mono: 'Meiryo, メイリオ, sans-serif'
defaults:
  layout: seminar
layout: seminar-cover
id: cover
---

# 映像データを用いた新生児の<br>運動特徴量抽出と時系列的評価に関する研究

<!--
根拠：前回ゼミ資料の表紙、研究全体像.md、research_state.json 方針v1.9
表紙の配置と書式：中間発表/スライド/layouts/title-cover.vue、style.cssを参考
今回の対象は本編で説明し、表紙は研究の大目的を示す題名にまとめる
発表日と持ち時間は未確定のため記載していない
この版はゼミ本編の準備版であり、研究モデルの推論と学習は未実施
-->

---
id: agenda
chapter: 研究背景
class: reference-agenda
---

# もくじ

::content::

<ol class="agenda">
  <li>研究背景</li>
  <li>課題</li>
  <li>取り組み</li>
  <li>実験と結果</li>
  <li>まとめ</li>
</ol>

<!-- 2026/11/03本人採用の5項目。提案手法は取り組みに統合。実験結果のページは実測がそろってから追加する -->

---
layout: chapter-divider
id: chapter-background
---

# 研究背景

<!-- もくじの章の扉 -->

---
id: background-births
chapter: 研究背景
class: background
sourceVisible: true
source: '出典：厚生労働省「人口動態調査 人口動態統計 確定数 出生（上巻）表4-25 性・年次別にみた出生時の体重（500g階級）別出生数及び百分率並びに出生時の平均体重」e-Stat, https://www.e-stat.go.jp/dbview?sid=0003411614'
---

# 研究背景

::content::

<p class="background-heading">低出生体重児の出生数と割合</p>

<div class="birth-chart-wrap">
  <BackgroundBirthChart />
  <figure class="lbw-photo">
    <img src="/local-reference/slide-004-lbw-photo-covered.png" alt="NICUの低出生体重児（顔は被覆済み）">
    <figcaption>実際の低出生体重児</figcaption>
  </figure>
</div>

::summary::

出生数減少の中で低出生体重児の割合は増加

<!--
前回正式版4ページを継承。数値は2026-11-03にe-Statの表4-25を男女別に表示し、合計して照合した（記録：local_data/presentation_reference_20261103/estat-table4-25.json）
低出生体重児の出生数9年分は前回の値と全て一致。割合は前回が体重不詳を含む全出生数で割っていたため、表の注（体重不詳を除いた出生数に対する百分率）に合わせ、1951年7.35→7.38%、1960年7.08→7.11%、1970年5.67→5.68%に直した
全出生数（同表の男女合計）：1951年2,137,689人、2023年727,288人
前回の凡例「出生数」は誤りで、棒は2,500g未満の出生数（例：2023年 約72.7万人×9.65%≈70,151人）。今回「低出生体重児の出生数」に訂正した
前回は左軸を40,000から始めていたが、棒の高さの比較が誇張されるため0からにした
全出生数の減少はグラフでは示していない
写真は前回発表版のページ画像から切り出した。顔の被覆は前回の発表のまま保持。Git対象外のpublic/local-referenceに置く
-->

---
id: background-nicu
chapter: 研究背景
class: background
sourceVisible: true
source: '出典：厚生労働省保険局医療課長通知「基本診療料の施設基準等及びその届出に関する手続きの取扱いについて」保医発0305第5号, 2024年3月5日, 新生児特定集中治療室管理料の施設基準'
---

# 研究背景

::content::

<div class="nicu-top">
  <div>
    <p class="nicu-terms"><span>NICU</span>：Neonatal Intensive Care Unit<br><span>GCU</span>：Growing Care Unit</p>
    <p class="background-body">低出生体重児などの観察や処置を必要とする<br>新生児はNICU/GCUに入院対象</p>
  </div>
  <div class="nicu-photo"><img src="/local-reference/slide-005-picture-01.jpeg" alt="NICUの病室の様子"></div>
</div>

<p class="background-heading">課題</p>

<div class="nicu-problem">
  <div class="nicu-left">
    <p class="background-body">各新生児には<strong>多くのケア</strong>が必要</p>
    <div class="nicu-plus">＋</div>
    <div class="nicu-ratio">
      <img src="/local-reference/slide-005-picture-03.svg" alt=""><img src="/local-reference/slide-005-picture-02.svg" alt=""><img src="/local-reference/slide-005-picture-05.svg" alt="">
      <span class="ratio-colon">：</span>
      <img src="/local-reference/slide-005-picture-04.svg" alt="">
    </div>
    <p class="background-body">NICUでは看護師1人が同時に<br>最大<strong>3名の新生児</strong>を担当</p>
  </div>
  <div class="nicu-arrow" aria-hidden="true">➡</div>
  <img class="nicu-illust" src="/local-reference/slide-005-picture-06.png" alt="複数の新生児を見守る看護師のイラスト">
</div>

::summary::

医療者が新生児一人一人を継続的に観察するのは困難

<!--
前回正式版5ページを継承。前回の「看護師1人が同時に最大3名」は、出典の新生児特定集中治療室管理料（NICU）の常時3対1以上の看護配置に当たるため「NICUでは」と明記した
GCU（新生児治療回復室入院医療管理料）の配置基準は今回の出典ページでは確認していない
出典PDF：https://www.mhlw.go.jp/content/12404000/001293317.pdf（2026-11-03に題名、発出番号、日付、3対1の記載を確認）
-->

---
id: background-observation
chapter: 研究背景
class: background
---

# 研究背景

::content::

<p class="background-heading">新生児は主に<strong>バイタル</strong>と<strong>身体運動</strong>を観察する</p>

<div class="observe-grid">
  <div class="observe-head">バイタル</div>
  <div class="observe-head span2">身体運動</div>
  <div class="observe-desc">生命状態を示す基本的な指標<ul><li>心拍数</li><li>呼吸数</li><li>血中酸素飽和度　など</li></ul></div>
  <div class="observe-desc span2">神経発達を反映する重要な行動情報<ul><li>四肢の動き</li><li>姿勢変化</li></ul></div>
  <div class="observe-method">専用機械</div>
  <div class="observe-method focus-top">目視観察</div>
  <div class="observe-method">センサー等</div>
  <div class="observe-cell"><img src="/local-reference/slide-006-picture-03.png" alt="保育器とモニターのイラスト"></div>
  <div class="observe-cell focus-bottom"><img src="/local-reference/slide-006-picture-01.png" alt="保育器を観察する看護師のイラスト"><p>継続的な観察は困難</p></div>
  <div class="observe-cell"><img src="/local-reference/slide-006-picture-02.png" alt="センサーを付けた新生児のイラスト"><p>新生児に負担</p></div>
</div>

::summary::

センサーでは新生児に負担が大きい<br>目視観察は客観性に欠け、人的負担も大きい

<!-- 前回正式版6ページを継承。前回の赤枠は今回の配色指定に合わせてオレンジ枠へ変更。前回のページに出典の記載はない。イラストは前回作成の説明用画像 -->

---
id: overall-goal
chapter: 研究背景
layout: seminar-purpose
source: '研究全体の目的：第1回研究報告（2026/10/19）7枚目を継承'
---

# 研究目的

<!--
前回7枚目の目的ページを、文字と画像の位置、画像のトリミングと顔の被覆を保って再構成
期待される効果は元資料の将来目標であり、今回の実測結果ではない
研究の大目的と今回の目的は別のページで示す
-->

---
layout: chapter-divider
id: chapter-problem
---

# 課題

<!-- もくじの章の扉 -->

---
id: continuity
chapter: 課題
source: '参照：第1回研究報告・正式版13・15〜18・47・48ページ／英論①（2026/06/08）4・5・49枚目'
---

# 前回の検討から今回へ

::content::

<table class="wide-first">
  <thead><tr><th>位置づけ</th><th>検討したこと・残ること</th></tr></thead>
  <tbody>
    <tr><td>前回の検討</td><td>白黒画像での身体部位抽出を比較<br>研究室映像では欠落や取り違えが残る</td></tr>
    <tr><td>前回の展望</td><td>身体部位解析の前段に、<br>医療者が映る区間の検出を組み込む構想</td></tr>
    <tr><td><strong>今回の対象</strong></td><td>運動解析へ進む前に、<br><strong>入力映像の区間指定</strong>を支援する</td></tr>
  </tbody>
</table>

<p class="note">身体部位抽出の改善と、解析に使う区間の指定は別の課題</p>

::summary::

前回の全体構想の入口に、今回の取り組みを位置づける

<!--
前回正式版13・15〜18ページの「課題→今回の対象→確かめること」という説明順を参考にした
前回の研究室映像での課題は正式版46・47ページ、介入検出の構想は48ページ
今回の優先対象は方針v1.9に基づく。身体部位抽出やMSIの課題が解決したとは扱わない
-->

---
id: selection-problem
chapter: 課題
class: selection-problem
sourceVisible: true
source: '参照：2026/06/08 英論① 4・5・49枚目／手作業の時間と今回の削減効果は未測定'
---

# 現状の課題：入力映像の選別

::content::

<p class="lead">身体運動を解析する前に、<br><strong>解析に使う区間を選ぶ作業</strong>がある</p>

<h2>これまでの方法</h2>

<div class="flow-row selection-flow">
  <div class="flow-node">撮影した映像</div><span class="flow-arrow">→</span>
  <div class="flow-node focus">人が映像を確認し<br>除外する区間を指定</div><span class="flow-arrow">→</span>
  <div class="flow-node">解析に使う映像</div>
</div>

<ul class="selection-points">
  <li>医療者が映るデータを、手作業で除外してきた</li>
  <li>動画の中で、除外する区間の<strong>開始・終了</strong>を決める必要がある</li>
</ul>

<p class="note">今回は、成人の手や腕が映る区間を候補として提示する</p>

::summary::

区間を一から指定する作業を支援し、人の負担を減らしたい

<!--
6月8日英論①の4・5・49枚目：運動解析前に医療者の介入がある入力データを手作業で除外し、自動判定の導入を検討していた
図はその作業を今回の区間指定へ整理した模式図であり、実測結果ではない
当時の「介入中や直後は自発運動とはいえない」という断定は引き継がない
今回検出するのは固定ROI内の成人の手や腕の映り込み。接触、臨床的な介入、自発運動とは別
手作業の所要時間と、人の確認修正でどこまで削減できるかは未測定
-->

---
id: prior-study-gap
chapter: 課題
class: prior-study-gap
sourceVisible: true
source: 'Souley Dosso et al., RGB-D scene analysis in the NICU, Comput. Biol. Med. 138, 104873, 2021, doi:10.1016/j.compbiomed.2021.104873'
---

# 先行研究を踏まえた今回の検討

::content::

<p>6月の英論発表では、NICU画像からの<strong>介入分類</strong>を紹介した</p>
<p class="paper-description">先行研究では、RGB・深度画像を用い、VGG-16に基づく分類を検討</p>

<div class="gap-table-wrap">
<table class="gap-table">
  <thead><tr><th scope="col">観点</th><th scope="col">先行研究</th><th scope="col">今回</th></tr></thead>
  <tbody>
    <tr><th scope="row">入力</th><td>RGB・深度画像</td><td>研究室の<strong>IR映像</strong></td></tr>
    <tr><th scope="row">判定の単位</th><td>画像ごとの分類</td><td>画像の判定から<br><strong>開始・終了を持つ区間</strong>へ</td></tr>
    <tr><th scope="row">支援する作業</th><td>NICUの看護記録</td><td>運動解析の前段での<br><strong>区間指定</strong></td></tr>
  </tbody>
</table>
</div>

<p class="note">IR映像での判定と、確認修正を含む作業時間は今回確かめる</p>

::summary::

先行研究を基準に、IR映像での区間指定支援を検討する

<!--
原典：Yasmina Souley Dosso, Kim Greenwood, JoAnn Harrold, James R. Green.
RGB-D scene analysis in the NICU. Computers in Biology and Medicine 138 (2021), 104873.
DOI:10.1016/j.compbiomed.2021.104873、PMID:34600329。2026-11-03にPubMedの書誌と原著抄録を照合
原著抄録は29新生児、RGB・深度、単一画像のシーン認識、VGG-16による分類と看護記録文生成を記載
本人の英論①10・12・28・29・49枚目も参照。原著Table 2の陽性は看護師（または成人）の手や腕がシーンに伸びている画像（2026/11/04に全文で確認）。今回はROI内に限定するため、同一の検出対象とは主張しない
入力・判定単位・用途の差を今回への適用上の確認点として整理した。原著が区間処理や作業時間を一切扱わないという主張ではない
今回の比較ではM3を原著に基づくIR向け分類法として扱い、完全再現とは呼ばない
前回正式版17ページの「先行研究の条件→自分の対象→今回の問い」という接続を参考にした
-->

---
id: overview
chapter: 課題
source: '全体図：前回正式版15・47・48ページを参考に、今回の対象を追加／後段は将来構想'
---

# 研究全体の構想と今回の対象

::content::

<p>研究室映像から身体運動を捉え、将来の評価へつなげる</p>

<SeminarOverview />

::summary::

今回は、身体部位を解析する前の区間指定支援を扱う

<!--
参照：研究全体像.md、研究全体の推奨構成_20261102.md、前回15・47枚目
領域とKPの2経路とCPリスク評価は将来構想
ROI内の手が見えないことは自発運動の保証ではない
人物領域検出とROI設定は別の処理
-->

---
layout: chapter-divider
id: chapter-approach
---

# 取り組み

<!-- もくじの章の扉 -->

---
id: support-purpose
chapter: 取り組み
class: problem-response
source: '今回の目的と比較の構成：研究方針v1.9（2026/11/02）'
---

# 今回の目的

::content::

<div class="objective secondary">
  固定ROI内に<strong>成人の手や腕が映る区間</strong>の<br>
  指定を支援し、<strong>必要な完成品質</strong>を保ちながら<br>
  人の作業負担をどこまで減らせるか調べる
</div>

<table class="wide-first response-table">
  <thead><tr><th>課題</th><th>今回どうするか</th></tr></thead>
  <tbody>
    <tr><td>手作業での区間指定</td><td>モデルが候補を提示し、人が確認修正する</td></tr>
    <tr><td>IR映像での判定</td><td>学習なし・ありVLMと、論文に基づく分類法を比べる</td></tr>
    <tr><td>作業負担の改善</td><td>手作業と、完成品質・人の作業時間を比べる</td></tr>
  </tbody>
</table>

::summary::

区間の検出から、人が確定する作業まで評価する

<!--
方針v1.9の説明を「課題→今回どうするか」の対応で記述。研究方針の変更ではない
品質の許容値は少数試行と用途を踏まえて最終評価前に固定する
学習ありVLMの改善、論文手法に対する優位、人の負担削減は未検証
-->

---
id: target-definition
chapter: 取り組み
source: 'ラベル規則は試行段階／詳細な境界と判定例は実動画で確定する'
---

# 判定する対象

::content::

<p class="lead">ROI内に、成人の手や腕が<strong>見えるか</strong>を判定する</p>

<table class="wide-first">
  <thead><tr><th>ラベル</th><th>判断の出発点</th></tr></thead>
  <tbody>
    <tr><td><strong>あり</strong></td><td>成人の手や腕と識別できる部分が<br>ROI内に見える</td></tr>
    <tr><td>なし</td><td>確認できる範囲で、ROI内に<br>成人の手や腕が見えない</td></tr>
    <tr><td>判定不能</td><td>乳児の手、反射、遮蔽、境界などにより<br>有無を決められない</td></tr>
  </tbody>
</table>

::summary::

映り込みと接触、臨床的な介入は区別する

<!-- ROI外だけの手を全画面ラベルと混同しない。なしは非接触や自発運動の証明ではない -->

---
id: fixed-roi
chapter: 取り組み
source: '採用した運用／環境別の保存と実動画での確認はこれから行う'
---

# 撮影環境ごとの固定ROI

::content::

<p class="lead">同じ撮影環境の動画では、<strong>一度設定したROIを共有する</strong></p>

<table>
  <thead><tr><th>設定する単位</th><th>動画ごとの確認</th><th>再設定する場合</th></tr></thead>
  <tbody>
    <tr><td>カメラと寝床の<br>配置が同じ範囲</td><td>基準画像と<br>位置を照合する</td><td>カメラ位置、画角、<br>寝床配置などの変化</td></tr>
  </tbody>
</table>

<ul style="margin-top:38px">
  <li>乳児の動きや手の出入りに合わせてROIを動かさない</li>
  <li>動画途中の環境変化は、その時刻から適用範囲を分ける</li>
  <li>ROIの設定と、各動画での照合にかかる時間も記録する</li>
</ul>

::summary::

対象範囲をそろえ、繰り返し囲む作業を減らす

<!-- 共通ROIの運用方針であり、機能完成や負担削減の実測を主張しない -->

---
id: processing-flow
chapter: 取り組み
class: proposed-method
source: '採用した構成：研究方針v1.9（2026/11/02）／実装と実行はこれから'
---

# 提案手法：区間指定支援の流れ

::content::

<p class="lead">モデルの判定から区間候補を作り、<strong>人が確認修正して確定</strong>する</p>

<div class="flow-row">
  <div class="flow-node">① 固定ROIの照合</div><span class="flow-arrow">→</span>
  <div class="flow-node">② 時刻付き<br>画像の抽出</div><span class="flow-arrow">→</span>
  <div class="flow-node focus">③ モデルによる判定</div>
</div>
<div class="flow-bridge">↓</div>
<div class="flow-row">
  <div class="flow-node">確定した区間を保存</div><span class="flow-arrow">←</span>
  <div class="flow-node">⑤ 人が確認修正</div><span class="flow-arrow">←</span>
  <div class="flow-node">④ 区間候補へ変換</div>
</div>

<table class="wide-first method-parts">
  <tbody>
    <tr><td><strong>入れ替える部分</strong></td><td><strong>③の判定</strong>：学習なしVLM、学習ありVLM、<br>論文に基づく分類器</td></tr>
    <tr><td>共通にする部分</td><td>①②④⑤：ROI、時刻、区間化、確認修正の画面</td></tr>
  </tbody>
</table>

<p class="note">流れの構成は採用済み。実装と実行はこれから</p>

::summary::

判定部分だけを入れ替え、区間の確定まで比較する

<!--
提案手法は①〜⑤の処理全体を指し、③の判定部分を比較する。この呼び方は2026/11/04に本人が採用した説明上の整理で、研究方針の変更ではない
共通条件の根拠：研究全体の推奨構成_20261102.md「共通の処理で3手法を比較する」
実装と実行済みの図ではない。推論と区間化は別実行として原予測を保持する
未確定：ROIのモデルへの渡し方、抽出間隔（1fpsは試行の初期値）、基盤モデル、質問文、区間の結合条件と前後の余裕、陰性区間の確認範囲
判定不能、推論失敗、未推論は陰性へ変換しない。負担の削減は未検証で、「減らせる」とは主張しない
-->

---
id: intervalization
chapter: 取り組み
source: '説明用の仮例：実測結果ではない／適用範囲と結合条件は未確定'
---

# 時刻付きの判定から区間へ

::content::

<p>連続した判定をまとめ、人が確認する区間候補を作る</p>

<IntervalExample />

<p class="note">短い映り込みの見逃し、細切れ、境界のずれを確認する</p>

::summary::

区間をまとめる条件と、前後の余裕は試行で決める

<!--
1秒間隔の仮図であり本実験の1fps採用やイベントの実測ではない
開始を含み終了を含まない仮例。各予測を次の時刻まで適用
判定不能、推論失敗、未推論を陰性へ変換しない。動画やROIの適用範囲を越えて結合しない
-->

---
id: methods
chapter: 取り組み
sourceVisible: true
source: 'M3の基準：Souley Dosso et al., RGB-D scene analysis in the NICU, 2021, doi:10.1016/j.compbiomed.2021.104873'
---

# 比較する方法と役割

::content::

<p>提案手法の判定部分（M1〜M3）を比べ、M0を基準にする<br>VLM：画像と文章を入力して回答を得るモデル</p>

<table class="method-table">
  <thead><tr><th>ID</th><th>方法</th><th>比較で確かめること</th></tr></thead>
  <tbody>
    <tr><td>M0</td><td>手作業の区間指定</td><td>完成品質と作業時間の基準</td></tr>
    <tr><td>M1</td><td>追加学習なしVLM</td><td>専用の重み更新なしで<br>判定できる範囲</td></tr>
    <tr><td>M2</td><td>追加学習ありVLM</td><td>同じ基盤モデルへの<br>追加学習の効果</td></tr>
    <tr><td>M3</td><td>論文に基づく分類器</td><td>共通の学習対象を使った<br>分類法とVLMの違い</td></tr>
  </tbody>
</table>

::summary::

同じ対象と評価条件で、精度と作業負担を比較する

<!--
M1/M2基盤モデルは同一環境で推論と学習の成立を確認して固定する
M3基準：Yasmina Souley Dosso, Kim Greenwood, JoAnn Harrold, James R. Green,
RGB-D scene analysis in the NICU, 2021, DOI:10.1016/j.compbiomed.2021.104873
原著の条件は2026/11/04に全文で確認。IRへの変更は未確定で、原著の完全再現とは呼ばない
-->

---
id: method-m0
chapter: 取り組み
class: method-detail
source: '注釈ツールは合成データで操作を確認した段階／手作業の時間は未測定'
---

# M0：手作業の区間指定

::content::

<p class="lead">人が動画を見て、手や腕が映る区間を<strong>一から指定</strong>する</p>

<div class="flow-row">
  <div class="flow-node">映像を確認</div><span class="flow-arrow">→</span>
  <div class="flow-node">開始と終了、<br>ラベルを指定</div><span class="flow-arrow">→</span>
  <div class="flow-node">再確認</div>
</div>

<table class="wide-first detail-table">
  <tbody>
    <tr><td>使うもの</td><td>自作の区間注釈ツール（固定ROIを表示）</td></tr>
    <tr><td>出力</td><td>あり／なし／判定不能の区間</td></tr>
    <tr><td>役割</td><td><strong>正解の作成</strong>と<strong>作業時間の基準</strong></td></tr>
    <tr><td>注意点</td><td>自身の正解では精度を算出しない<br>時間は未視聴の動画で測る</td></tr>
  </tbody>
</table>

::summary::

手作業は、正解の作成と作業時間の基準を担う

<!--
ツール：step02_正解データ作成/annotation-app。動画の区間入力と集計を合成データで確認した段階で、実動画の注釈は未実施
本人のラベルをそのまま正解にした状態で、M0自身の精度は算出しない（研究全体像）
同じ動画を直後に繰り返して時間を比べない。一人の場合は未視聴の別セットと順序を決め、慣れを制約として示す
過去に手作業で除外した区間の記録は残っていないため、手作業の時間は新しく測る
-->

---
id: vlm-intro
chapter: 取り組み
class: vlm-intro
source: '質問文は開発用の案（v0.1）で未確定／VLMの判定性能は未測定'
---

# VLM（Vision-Language Model）とは

::content::

<p class="lead"><strong>画像と質問文</strong>を入力し、<strong>回答の文章</strong>を返すモデル</p>

<div class="flow-row">
  <div class="flow-node">画像</div><span class="flow-arrow">＋</span>
  <div class="flow-node question">質問文（案）<br>成人の手または腕が<br>見えますか</div><span class="flow-arrow">→</span>
  <div class="flow-node focus">VLM</div><span class="flow-arrow">→</span>
  <div class="flow-node">回答<br>あり／なし／<br>判定不能</div>
</div>

<table class="wide-first vlm-compare">
  <thead><tr><th>観点</th><th>分類器（M3）</th><th>VLM（M1、M2）</th></tr></thead>
  <tbody>
    <tr><td>入力</td><td>画像</td><td>画像と質問文</td></tr>
    <tr><td>出力</td><td>学習時に決めたクラス</td><td>文章（回答の形式を指定する）</td></tr>
    <tr><td>専用の学習</td><td>必要</td><td><strong>なしでも回答を得られる</strong><br>追加学習もできる</td></tr>
  </tbody>
</table>

::summary::

学習なしで使えれば、準備の負担を抑えられる可能性がある

<!--
VLMを使う理由の中心は、専用の学習なしで試せること。実際に判定できるかは研究室のIR映像で未確認で、優位は仮説として扱う
質問文の案：step03_各手法の実装と実験/configs/prompt_draft.txt（v0.1）。回答はpresent、absent、uncertainの1語。接触の有無や職種は推測させない。本文は日本語で要約した
案の質問は「画像内」を尋ねており、ROIの渡し方（クロップかマスクか）は未確定
1画像ずつ同じ質問を渡す。複数画像や動画の入力は別の条件として扱う
-->

---
id: vlm-selection
chapter: 取り組み
class: vlm-selection
sourceVisible: true
source: '重み容量とスコア：各モデルの公式Hugging Faceカード（2026/10/30確認）／選定案で、モデルは未実行'
---

# VLMの選定：どのモデルを使うか

::content::

<p class="lead">公開されたVLMの中から、<strong>3つの基準</strong>で候補を絞る</p>

<div class="criteria-row">
  <div class="flow-node">① 研究室のGPU<br>（24 GiB）で動く規模</div>
  <div class="flow-node">② 同じモデルで<br>追加学習できる見込み</div>
  <div class="flow-node">③ 画像理解の<br>公開スコア（参考）</div>
</div>

<table class="selection-table">
  <thead><tr><th>候補</th><th>重み容量</th><th>スコア※</th><th>判断</th></tr></thead>
  <tbody>
    <tr><td>Qwen3.5-2B</td><td>約4.6 GB</td><td>71.7</td><td>軽量側の比較候補</td></tr>
    <tr class="picked"><td><strong>Qwen3.5-4B</strong></td><td>約9.3 GB</td><td>78.3</td><td><strong>最初に試す</strong></td></tr>
    <tr><td>Qwen3-VL-4B-Instruct</td><td>約8.9 GB</td><td>69.8</td><td>比較候補：公式の学習コードあり</td></tr>
    <tr><td>Qwen3.5-9B</td><td>約19.3 GB</td><td>79.7</td><td>4Bの確認後に追加を検討</td></tr>
    <tr><td>InternVL3.5-4B</td><td>約9.5 GB</td><td>－</td><td>別系列の比較が必要な場合</td></tr>
    <tr><td>SmolVLM2-2.2B</td><td>－</td><td>－</td><td>軽量だが最初の比較に入れない</td></tr>
    <tr><td>Qwen3.6、Qwen3.8</td><td>27B級以上</td><td>－</td><td>大きいため最初の候補にしない</td></tr>
  </tbody>
</table>

<p class="note">※MMStar（開発元の報告値）。条件は異なり、研究室のIR映像の成績ではない</p>

::summary::

Qwen3.5-4Bから試し、追加学習まで動いてからモデルを固定する

<!--
選定の順序：4B級は重み以外の処理にもGPUメモリを残せるため、最初の候補にした。9B級は約19.3 GBで余裕が小さく、動作前に24 GBで確実に動くとは扱わない
重み容量は実行に必要なGPUメモリの総量ではない。GPUはRTX 3090（24 GiB）。別のPCを使う場合は選定を見直す
②は未確認：Qwen3.5の追加学習の経路は公開ガイドの記載を確認しただけで、このPCでは試していない。Qwen3-VLのコードがQwen3.5へそのまま使えるとは扱わない。成立しなければ候補を再検討する
スコアは異なる報告の値を並べたもので、そろえた比較ではない。2BはThinkingの値。4Bと9Bは公式表のモード設定に依存し、Non-Thinkingで同じ点数が出る証拠にはしない。InternVLの値は調査メモに転記していないため空欄
表に載せていない候補：Qwen3-VL-8B-Instruct（サイズ差の比較候補。重み容量は約17.5 GB）
Qwen3.6と3.8は確認した案内が27B級以上中心で、27Bはモデル規模の目安。新しい世代という理由だけでは選ばない。SmolVLM2-2.2BはQwen優先の希望により最初の比較に入れない。空欄は調査メモに値を転記していないもの
調査範囲：本人のQwen優先の希望と24 GiBの条件に合わせ、2Bから9B級を中心に調べた。全VLMの網羅的な比較ではなく、研究室IR映像で候補を比べた報告も確認できていない
Qwen3.5-4BとQwen3-VL-4B-Instructの公式カードのライセンスはApache-2.0
参照：調査/VLM候補比較と研究室PCでの選定_20261030.md、共通/使用OSSと出典.md
-->

---
id: method-m1
chapter: 取り組み
class: method-detail method-dense
sourceVisible: true
source: 'Qwen Team, Qwen3-VL Technical Report, arXiv:2511.21631, 2025／Qwen3.5-4B公式モデルカード（2026/11/04確認）／質問文は案で未実行'
---

# M1：追加学習なしVLM

::content::

<p class="lead">公開モデルの<strong>重みを更新せず</strong>、質問文だけで判定する</p>

<div class="flow-row">
  <div class="flow-node">時刻付き画像<br>と質問文</div><span class="flow-arrow">→</span>
  <div class="flow-node focus">画像エンコーダ → 言語モデル<br>（重みは固定）</div><span class="flow-arrow">→</span>
  <div class="flow-node">回答の<br>文字列</div><span class="flow-arrow">→</span>
  <div class="flow-node">ラベルへ<br>読み取り</div>
</div>

<table class="wide-first detail-table">
  <tbody>
    <tr><td>質問文（案）</td><td>成人の手または腕が見えますか<br>present、absent、uncertainの1語で回答</td></tr>
    <tr><td>推論の設定</td><td>1画像ずつ、思考を省いた直接回答から試す</td></tr>
    <tr><td>結果の保存</td><td>回答の原文、ラベル、状態（正常、判定不能、<br>形式違反、推論失敗）を画像ごとに残す</td></tr>
    <tr><td>必要な準備</td><td>調整用の患者で、質問文と推論条件を選ぶ</td></tr>
    <tr><td>測るもの</td><td>判定の成績、1画像の時間、最大GPUメモリ</td></tr>
  </tbody>
</table>

::summary::

専用の学習なしで、どこまで判定できるかを確かめる

<!--
構成：Qwen3-VLは画像エンコーダ（SigLIP-2）、MLPのマージャ、言語モデルからなる（技術報告2章）。Qwen3.5-4Bもカードでは画像エンコーダを持つ言語モデルと説明されている。図は両候補に共通する説明
候補の順序は前のページ。主比較のモデルは推論と追加学習の両方が同じ環境で成立してから固定する
直接回答：Qwen3.5はカードに enable_thinking を False にする例がある。Thinkingを加える場合は別の条件として記録する。Qwen3-VL-4B-Instructは別の設定になるため実機で確認する
質問文：step03_各手法の実装と実験/configs/prompt_draft.txt（v0.1）。接触の有無や職種は推測させない。原文は日本語で「画像内に」を尋ねており、ROIの渡し方（クロップかマスクか）は未確定
判定不能、形式違反、推論失敗は陰性へ変換しない。正常回答だけの成績を全対象の成績と混同しない
手順：環境の保存、一般画像1枚での読込と直接回答の確認、開発患者の少数画像での推論（P05）。いずれも未実施。速度、メモリ、判定精度は未測定
最終評価の患者では質問文を調整しない。M1の「学習なし」は重みを更新しない意味で、質問の選定に使ったラベルの作業量は報告する
-->

---
id: method-m2
chapter: 取り組み
class: method-detail method-dense
source: '計画：研究計画_詳細、評価条件固定票／追加学習は未実施'
---

# M2：追加学習ありVLM

::content::

<p class="lead">M1と同じモデルを、研究室映像のラベルで<strong>追加学習</strong>する</p>

<div class="flow-row">
  <div class="flow-node">共通の<br>区間ラベル</div><span class="flow-arrow">→</span>
  <div class="flow-node">学習データ<br>を生成</div><span class="flow-arrow">→</span>
  <div class="flow-node focus">LoRAで<br>追加学習</div><span class="flow-arrow">→</span>
  <div class="flow-node">M1と同じ<br>条件で推論</div>
</div>

<table class="wide-first detail-table">
  <tbody>
    <tr><td>学習データ</td><td>画像、質問文、正解の1語を組にする</td></tr>
    <tr><td>そろえる条件</td><td>基盤モデルと版、質問文、解像度、推論条件、区間化</td></tr>
    <tr><td>学習と選択</td><td>学習用の患者で更新し、調整用の患者で重みを選ぶ</td></tr>
    <tr><td>M3との関係</td><td>同じ患者、動画、ラベル、抽出対象で学習する</td></tr>
    <tr><td>クラスの偏り</td><td>元の比率と1：1の2条件を候補に、調整用で比べる</td></tr>
    <tr><td>最初の確認</td><td>少数データで更新、保存、再読込、同条件での推論</td></tr>
  </tbody>
</table>

::summary::

M1との差から、追加学習の効果を確かめる

<!--
質問をM2だけ変えない。共通質問の見直しが必要ならP08へ戻り、M1とM2を両方測り直す
異なる基盤モデルのM1とM2を学習前後として比較しない
1：1は候補で、最適と断定しない。学習側だけで調整し、評価データの自然な比率は保つ。参照：step02_正解データ作成/区間注釈とクラス比率.md
M1より良くなることは完了条件に含めず、悪化や判定不能も保存する。改善しなかった場合に「学習が足りない」で終えず、対象の曖昧さ、抽出、入力、実装、画像条件を調べる
少数画像の暗記や損失の低下を、未知の患者への精度の証拠にしない
参照：step03_各手法の実装と実験/M2_追加学習Qwen/README.md、環境確認と少数実験.md
-->

---
id: method-m2-lora
chapter: 取り組み
class: m2-lora
sourceVisible: true
source: 'LoRA：Hu et al., arXiv:2106.09685, 2021／Unsloth学習ガイド、Qwen3-VL公式README（2026/11/04確認）'
---

# M2：LoRAと学習の経路

::content::

<div class="flow-row">
  <div class="flow-node">元の重み <strong>W</strong><br>（固定）</div><span class="flow-arrow">＋</span>
  <div class="flow-node focus">小さな行列の積 <strong>BA</strong><br>（ここだけ学習）</div><span class="flow-arrow">→</span>
  <div class="flow-node">推論に使う重み<br><strong>W＋BA</strong></div>
</div>

<p class="note">全層を更新する学習より、更新する数と必要なメモリを減らせる</p>

<table class="route-table">
  <thead><tr><th>観点</th><th>Qwen3.5-4B</th><th>Qwen3-VL-4B-Instruct</th></tr></thead>
  <tbody>
    <tr><td>学習の資料</td><td>Unslothのガイド</td><td>開発元の公式コード</td></tr>
    <tr><td>学習の形式</td><td>BF16のLoRAを推奨<br>4-bit QLoRAは非推奨</td><td>LoRAの設定あり</td></tr>
    <tr><td>更新対象</td><td>画像側と言語側を切替</td><td>画像、MLP、言語を切替</td></tr>
    <tr><td>メモリの目安</td><td>約10 GB（資料の記載）</td><td>資料からは未確認</td></tr>
  </tbody>
</table>

::summary::

同じモデルで推論と追加学習が動く経路を、先に確かめる

<!--
LoRA原典：Edward J. Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, Weizhu Chen. arXiv:2106.09685, 2021。事前学習の重みを固定し、低ランクの行列を学習する。原典の報告（GPT-3 175Bで学習パラメータ約1万分の1、GPUメモリ約3分の1）は言語モデルの結果で、今回のVLMの値ではない
Unslothガイド：Transformers v5が必要。ガイドの例は r=16、lora_alpha=16、全線形層。推論は学習時と同じチャットテンプレートを使う。9Bは約22 GBと記載されており、24 GiBのGPUでは余裕が小さい
公式README：会話形式のJSONで画像を指定する。lora_enable、lora_r、lora_alpha の設定があり、例は r=8、lora_alpha=16。tune_mm_vision、tune_mm_mlp、tune_mm_llm で更新対象を切り替える
どの設定も資料の例で、今回の採用条件ではない。資料の値は実測ではなく、研究室PCでは未確認。どの部分を更新するかは未決
Qwen3-VLのコードがQwen3.5へそのまま使えるとは扱わない。Qwen3.5の組が成立しなければQwen3-VL-4B-Instructを次の候補にし、変更履歴へ残す
Windowsネイティブ、WSL2、Linuxのどれで動かすかは依存関係の確認後に決める
-->

---
id: method-m3
chapter: 取り組み
class: method-detail method-dense
sourceVisible: true
source: 'Souley Dosso et al., RGB-D scene analysis in the NICU, Comput. Biol. Med. 138, 2021, doi:10.1016/j.compbiomed.2021.104873'
---

# M3：基準論文の介入分類

::content::

<p class="lead"><strong>成人の手や腕が映っているか</strong>を、VGG-16で画像ごとに分類する</p>

<div class="flow-row">
  <div class="flow-node">RGB画像と<br>Depth画像</div><span class="flow-arrow">→</span>
  <div class="flow-node">4チャンネルに<br>結合</div><span class="flow-arrow">→</span>
  <div class="flow-node focus">VGG-16<br>畳み込み13層、全結合3層</div><span class="flow-arrow">→</span>
  <div class="flow-node">介入あり／<br>なし</div>
</div>

<table class="wide-first detail-table">
  <tbody>
    <tr><td>陽性の定義</td><td>看護師（または成人）の<strong>手や腕</strong>がシーンに伸びている</td></tr>
    <tr><td>データ</td><td>27人、14,892枚（介入1,260枚、なし13,632枚）<br>30秒に1枚を抽出</td></tr>
    <tr><td>学習</td><td>事前学習の重みから全層を更新<br>SGD、学習率1e-5、バッチ32、最大20エポック</td></tr>
    <tr><td>偏りへの対策</td><td>少ない介入クラスを重み付き交差エントロピーで強調</td></tr>
    <tr><td>評価</td><td>患者が重ならない5分割交差検証</td></tr>
  </tbody>
</table>

::summary::

対象の定義が近く、学習条件も明記された比較の基準

<!--
原著全文で確認（2026/11/04）。論文の3.2節、3.6節、Table 2
VGG-16はImageNet事前学習（事前学習の記載は2024年のHajj-Aliらの2.3節でも確認）。fine-tuningは全層の重みを更新する
追加の条件：SGDのmomentum 0.9。学習パラメータは4患者の部分集合で調整。拡張はX軸Y軸の反転と0〜360度の回転で、平行移動と拡大縮小は対象を失うため行わない
論文全体は5つの文脈を分類して看護記録の文を生成する研究で、ここで使うのは介入分類の部分だけ
RGBD4は第4チャンネルの重みに、入力層の赤チャンネルの重みをコピーする。介入分類ではRGBD4が最良のRGB-D融合だった
画像全体の評価で、胴体が手と患者を隠す複雑な場面はデータから除外している
本研究のROI内という定義とは同一ではない
-->

---
id: method-m3-application
chapter: 取り組み
class: m3-application
sourceVisible: true
source: '報告値：Souley Dosso et al., 2021, Table 4（研究室映像の結果ではない）／今回の条件は未確定で未実施'
---

# M3：論文の結果と今回の適用

::content::

<table class="m3-result-table">
  <thead><tr><th>論文の報告値（%）</th><th>再現率</th><th>適合率</th><th>F1</th><th>MCC</th></tr></thead>
  <tbody>
    <tr><td>肌色検出（基準法）</td><td>18.20</td><td>59.01</td><td>16.63</td><td>20.52</td></tr>
    <tr><td>RGB</td><td>83.44</td><td>64.55</td><td>72.79</td><td>70.63</td></tr>
    <tr><td>Depthのみ</td><td>66.11</td><td>36.24</td><td>46.82</td><td>42.64</td></tr>
    <tr class="picked"><td><strong>RGB-D（4チャンネル）</strong></td><td>84.25</td><td>64.54</td><td><strong>73.06</strong></td><td><strong>70.98</strong></td></tr>
  </tbody>
</table>

<table class="m3-change-table">
  <thead><tr><th>観点</th><th>論文</th><th>今回</th></tr></thead>
  <tbody>
    <tr><td>入力</td><td>RGB-D（近赤外は分析に使わず）</td><td><strong>IR映像のみ</strong></td></tr>
    <tr><td>入力層</td><td>Depthのみでは1チャンネルへ変更</td><td>同じ変更を候補に検討</td></tr>
    <tr><td>範囲</td><td>画像全体</td><td>固定ROI内</td></tr>
    <tr><td>抽出間隔</td><td>30秒に1枚</td><td>試行で決める（1秒から）</td></tr>
  </tbody>
</table>

::summary::

報告値はIRへそのまま当てはまらないため、同じ評価データで測る

<!--
±はRGB 83.44±0.07、RGB-D 84.25±1.03など。原著Table 4を参照。MCCはクラスの偏りに強い指標で、適合率が低いのは介入が少ないことも影響する
読み方：RGBとRGB-Dの差は小さく、Depthのみは大きく下がる。IRは色も深度も持たないので、どの行の値も期待値にはならない
著者の考察：手袋を含むデータで、肌の色ではなく手の形と文脈を学習したと述べている。色のないIRでも使える可能性を示すが、検証はされていない
介入の約98%は明るい環境で起きていた。低照度は少なく、IRの暗所映像に近い条件の評価は限られる
論文のDepthモデルは入力層の重みを1チャンネルだけ残している。IRへの適用はこの方法を候補とするが、3チャンネルへの複製など他の案と合わせて未決
1fpsは試行の初期値で本採用ではない。ROIの渡し方も未確定
論文の報告値と研究室映像の実測は比較しない。実装、学習、性能測定は未実施
-->

---
layout: chapter-divider
id: chapter-experiment
---

# 実験と結果

<!-- もくじの章の扉 -->

---
id: patient-split
chapter: 実験と結果
source: '患者数と患者単位の分割は未確定'
---

# データの分割と共通条件

::content::

<p class="lead"><strong>患者単位</strong>で用途を分け、画像抽出より先に割り当てる</p>

<table class="wide-first">
  <thead><tr><th>用途</th><th>使用する目的</th></tr></thead>
  <tbody>
    <tr><td>学習用</td><td>M2とM3の専用学習に使う</td></tr>
    <tr><td>調整用</td><td>質問、閾値、区間化、学習条件を選ぶ</td></tr>
    <tr><td>最終評価用</td><td>固定した条件で、未使用患者の結果を比較する</td></tr>
  </tbody>
</table>

<p class="note">少数試行で見た患者を、手つかずの最終評価へ戻さない</p>

::summary::

最終評価の結果を見ながら条件を調整しない

<!-- 患者数不足時は評価設計を再検討し、フレーム数で患者数を代用しない -->

---
id: before-after
chapter: 実験と結果
source: '基盤モデルと使用する版は、推論と追加学習の動作確認後に固定する'
---

# VLMの学習前後でそろえる条件

::content::

<table class="wide-first">
  <thead><tr><th>比較条件</th><th>M1とM2でそろえるもの</th></tr></thead>
  <tbody>
    <tr><td>基盤モデル</td><td>同じモデルと同じ版</td></tr>
    <tr><td>入力と質問</td><td>画像、ROI、解像度、質問と回答形式</td></tr>
    <tr><td>推論</td><td>量子化、生成条件、出力の読み取り方</td></tr>
    <tr><td>区間化</td><td>予測の適用範囲、結合、前後の余裕</td></tr>
  </tbody>
</table>

<p class="note">M2とM3には、共通の専用学習対象を使う</p>

::summary::

条件をそろえ、追加学習による変化を確かめる

<!-- 避けられない条件差は明示し、追加学習だけの効果と断定しない -->

---
id: evaluation
chapter: 実験と結果
class: reference-evaluation
source: '評価方法は試行段階／完成品質の許容値は最終評価前に固定する'
---

# 今回確かめること

::content::

<table class="wide-first three-layer">
  <thead><tr><th>観点</th><th>確かめること</th></tr></thead>
  <tbody>
    <tr><td>1　画像判定</td><td>手や腕を見逃さず、<br>乳児の手や寝具と区別できるか</td></tr>
    <tr><td>2　区間候補</td><td>完全見逃し、余計な除外、<br>開始終了のずれがどれだけあるか</td></tr>
    <tr><td>3　人の作業</td><td>必要な完成品質を満たすまでの<br>確認修正時間を減らせるか</td></tr>
  </tbody>
</table>

::summary::

画像、区間、人の作業の3段階で評価する

<!--
前回18枚目の「観点／確かめること」を継承
画像：再現率・適合率・F1。区間：残留陽性時間・過剰除外時間・完全見逃し・境界ずれ
患者別の分母と成績、形式違反、推論失敗、判定不能も残す
-->

---
id: human-workload
chapter: 実験と結果
source: '作業者と対象の割当は、本測定前に固定する'
---

# 完成品質をそろえた作業時間の比較

::content::

<p class="lead">同じ品質基準を満たすまでの、<strong>人の作業時間</strong>を比べる</p>

<div class="support-compare">
  <div class="support-row"><div class="label">手作業</div><div class="steps">映像を確認 → 区間を指定 → 再確認</div></div>
  <div class="support-row"><div class="label">モデル支援</div><div class="steps">候補を提示 → 確認修正 → 再確認</div></div>
</div>

<ul style="margin-top:35px">
  <li>候補に出なかった区間の確認も、作業時間に含める</li>
  <li>同じ動画を見た記憶や、作業順序の影響を考慮する</li>
  <li>初期の注釈と学習、人の操作、計算時間を分ける</li>
</ul>

::summary::

短い作業時間と、修正後に残る誤りを一緒に確認する

<!-- 品質条件未達の方式も不成立として記録する。M0のラベル自身を正解にしてM0の精度を計算しない -->

---
id: result-data
chapter: 実験と結果
class: result-shell
sourceVisible: true
source: '枠のみで未測定／実行IDは未登録／項目は評価方法のドラフトで、本評価前に固定する'
---

# 結果：データの内訳

::content::

<p class="shell-status">未測定（表の枠のみ）</p>

<p class="shell-lead">用途ごとの患者、動画、注釈時間を示す</p>

<table class="shell-table">
  <thead><tr><th>用途</th><th>患者数</th><th>動画数</th><th>注釈時間</th><th>陽性の割合</th><th>判定不能の割合</th></tr></thead>
  <tbody>
    <tr><td>学習用</td><td>－</td><td>－</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>調整用</td><td>－</td><td>－</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>最終評価用</td><td>－</td><td>－</td><td>－</td><td>－</td><td>－</td></tr>
  </tbody>
</table>

<p class="note">画像の枚数を患者数の代わりにしない</p>

::summary::

用途ごとの内訳と、陽性の少なさを確認する

<!--
数値は空欄で、実験の結果ではない。実測後に保存した集計から入れ、実行IDを発表根拠の対応表へ登録する
患者数と動画は未確認（Q002）。陽性の割合は二値判定できる時間を分母にする。患者が足りない場合は分割の設計を見直す
-->

---
id: result-image
chapter: 実験と結果
class: result-shell
sourceVisible: true
source: '枠のみで未測定／実行IDは未登録／項目は評価方法のドラフトで、本評価前に固定する'
---

# 結果①：画像判定

::content::

<p class="shell-status">未測定（表の枠のみ）</p>

<p class="shell-lead">最終評価の患者で、手法ごとの画像判定を比べる</p>

<table class="shell-table">
  <thead><tr><th>手法</th><th>再現率</th><th>適合率</th><th>F1</th><th>陰性の誤検知率</th><th>回答率</th></tr></thead>
  <tbody>
    <tr><td>M1：学習なしVLM</td><td>－</td><td>－</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M2：学習ありVLM</td><td>－</td><td>－</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M3：分類器</td><td>－</td><td>－</td><td>－</td><td>－</td><td>－</td></tr>
  </tbody>
</table>

<p class="note">判定不能、形式違反、推論失敗の件数も全対象を分母に示す</p>

::summary::

手や腕を見逃さず判定できたかを比べる

<!--
数値は空欄で、実験の結果ではない。実測後に保存した集計から入れ、実行IDを発表根拠の対応表へ登録する
M0は自身の正解で精度を算出しない。正常回答だけの指標には回答率を添える。論文の報告値とは比較しない
-->

---
id: result-patient
chapter: 実験と結果
class: result-shell
sourceVisible: true
source: '枠のみで未測定／実行IDは未登録／項目は評価方法のドラフトで、本評価前に固定する'
---

# 結果①：患者別の判定

::content::

<p class="shell-status">未測定（表の枠のみ）</p>

<p class="shell-lead">全体の平均に隠れる失敗を、患者ごとに見る</p>

<table class="shell-table">
  <thead><tr><th>患者</th><th>画像数</th><th>M1のF1</th><th>M2のF1</th><th>M3のF1</th><th>M2－M1</th></tr></thead>
  <tbody>
    <tr><td>患者A</td><td>－</td><td>－</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>患者B</td><td>－</td><td>－</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>患者C</td><td>－</td><td>－</td><td>－</td><td>－</td><td>－</td></tr>
  </tbody>
</table>

<p class="note">患者の行数は仮。分母が0の場合はNAとし、0点にしない</p>

::summary::

平均に隠れる失敗を、患者ごとに確認する

<!--
数値は空欄で、実験の結果ではない。実測後に保存した集計から入れ、実行IDを発表根拠の対応表へ登録する
10月19日の「全体の値だけで判断しない」という指摘への対応。差は同じ患者同士で計算する。連続フレームを独立標本として有意差を主張しない。患者名はIDで示す
-->

---
id: result-time
chapter: 実験と結果
class: result-shell
sourceVisible: true
source: '枠のみで未測定／実行IDは未登録／項目は評価方法のドラフトで、本評価前に固定する'
---

# 結果①：推論時間

::content::

<p class="shell-status">未測定（表の枠のみ）</p>

<p class="shell-lead">同じ画像を1枚ずつ処理し、モデルごとの時間を比べる</p>

<table class="shell-table">
  <thead><tr><th>手法</th><th>処理した<br>枚数</th><th>全体の<br>時間</th><th>1枚あたりの<br>平均</th><th>モデルの<br>読み込み</th><th>最大GPU<br>メモリ</th></tr></thead>
  <tbody>
    <tr><td>M1：学習なしVLM</td><td>－</td><td>－</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M2：学習ありVLM</td><td>－</td><td>－</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M3：分類器</td><td>－</td><td>－</td><td>－</td><td>－</td><td>－</td></tr>
  </tbody>
</table>

<p class="note">1枚あたりの平均＝全体の時間÷処理した枚数。読み込みは全体の時間に含めない</p>

::summary::

全体の時間と1枚あたりの平均で、モデルの速さを比べる

<!--
数値は空欄で、実験の結果ではない。実測後に保存した集計から入れ、実行IDを発表根拠の対応表へ登録する
全体の時間は、モデルの読み込み後から全画像の回答を読み取り終えるまで。GPU処理は完了を待って測る。失敗した画像も処理した枚数に含め、件数を別に示す
同じPC、同じ画像で測り、他の重い処理を同時に動かさない。バッチサイズは全モデル1にそろえる。まとめて処理すると速くなるモデルとの不公平を避けるためで、まとめて処理した場合の速さはこの比較では分からない。VLMは出力の長さでも時間が変わるので生成長も記録する
1枚ごとの時間も保存し、最初の数枚の遅さや外れ値を確認できるようにする
M0は人の作業で推論時間がないため、結果③で扱う。1枚あたりの平均に抽出枚数を掛けると、動画の処理時間を見積もれる（1秒に1枚なら動画1時間で3,600枚）。フレーム抽出の時間は別に測る
学習時間は初期費用で、推論時間に含めない
-->

---
id: result-interval
chapter: 実験と結果
class: result-shell
sourceVisible: true
source: '枠のみで未測定／実行IDは未登録／項目は評価方法のドラフトで、本評価前に固定する'
---

# 結果②：区間候補

::content::

<p class="shell-status">未測定（表の枠のみ）</p>

<p class="shell-lead">画像の判定をまとめた区間を、正解の区間と比べる</p>

<table class="shell-table">
  <thead><tr><th>手法</th><th>残った陽性（秒）</th><th>余計な除外（秒）</th><th>完全見逃し（件）</th><th>開始終了のずれ</th></tr></thead>
  <tbody>
    <tr><td>M1：学習なしVLM</td><td>－</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M2：学習ありVLM</td><td>－</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M3：分類器</td><td>－</td><td>－</td><td>－</td><td>－</td></tr>
  </tbody>
</table>

<p class="note">各正解区間をどれだけ覆えたかも示す。区間化の条件は未確定</p>

::summary::

区間の指定に使えるかを比べる

<!--
数値は空欄で、実験の結果ではない。実測後に保存した集計から入れ、実行IDを発表根拠の対応表へ登録する
1秒でも重なれば検出とはしない。M1対M2では区間化の設定をそろえた比較を残す。抽出間隔による取りこぼしと、モデルの誤判定を分ける
-->

---
id: result-work
chapter: 実験と結果
class: result-shell
sourceVisible: true
source: '枠のみで未測定／実行IDは未登録／項目は評価方法のドラフトで、本評価前に固定する'
---

# 結果③：人の作業

::content::

<p class="shell-status">未測定（表の枠のみ）</p>

<p class="shell-lead">同じ品質基準で、人の作業時間を比べる</p>

<table class="shell-table">
  <thead><tr><th>手法</th><th>品質基準</th><th>確認修正の時間</th><th>残った誤り</th><th>計算時間</th><th>初期費用</th></tr></thead>
  <tbody>
    <tr><td>M0：手作業</td><td>－</td><td>－</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M1：学習なしVLM</td><td>－</td><td>－</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M2：学習ありVLM</td><td>－</td><td>－</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M3：分類器</td><td>－</td><td>－</td><td>－</td><td>－</td><td>－</td></tr>
  </tbody>
</table>

<p class="note">品質基準の許容値と、M0の品質の確認方法は未確定</p>

::summary::

品質を満たす条件で、人の時間がどれだけ変わるかを確かめる

<!--
数値は空欄で、実験の結果ではない。実測後に保存した集計から入れ、実行IDを発表根拠の対応表へ登録する
品質基準を満たさない方法も不成立として記録する。陰性区間の確認時間も含める。実作業、計算の経過時間、初期の注釈と学習の費用を分ける。作業者の数と対象の割当は未確定
-->

---
id: result-errors
chapter: 実験と結果
class: result-shell
sourceVisible: true
source: '枠のみで未測定／実行IDは未登録／項目は評価方法のドラフトで、本評価前に固定する'
---

# 結果：誤りの分析

::content::

<p class="shell-status">未測定（表の枠のみ）</p>

<p class="shell-lead">どの場面で失敗するかを、手法ごとに整理する</p>

<table class="shell-table">
  <thead><tr><th>場面（候補）</th><th>区間数</th><th>M1の誤り</th><th>M2の誤り</th><th>M3の誤り</th></tr></thead>
  <tbody>
    <tr><td>指先だけ、手袋</td><td>－</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>反射、遮蔽</td><td>－</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>乳児の手</td><td>－</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>ROIの境界</td><td>－</td><td>－</td><td>－</td><td>－</td></tr>
  </tbody>
</table>

<p class="note">場面は開発用の患者で実在を確認してから決める。代表例の図は実測後に追加</p>

::summary::

失敗の条件を確かめ、手法を選ぶ判断につなげる

<!--
数値は空欄で、実験の結果ではない。実測後に保存した集計から入れ、実行IDを発表根拠の対応表へ登録する
10月19日の「動画や場面ごとに中身を見る」という指摘への対応。最終評価で新しく見つかった失敗は探索的な所見として区別する。見逃しと誤検知は実測後に分けて書く
-->

---
id: discussion-image-good
chapter: 実験と結果
class: result-shell discussion-shell
sourceVisible: true
source: '枠のみで未記入／実測後に保存した結果から書く／理由は確かめるまで仮説として扱う'
---

# 考察①：画像判定でうまくいった点

::content::

<p class="shell-status">未記入（枠のみ）</p>

<p class="shell-lead">うまく判定できた手法と場面の理由を考える</p>

<table class="shell-table">
  <thead><tr><th>手法</th><th>何が起きたか</th><th>多分こうだから</th><th>どう確かめるか</th></tr></thead>
  <tbody>
    <tr><td>M1：学習なしVLM</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M2：学習ありVLM</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M3：分類器</td><td>－</td><td>－</td><td>－</td></tr>
  </tbody>
</table>

<p class="note">見る観点：M1とM2の差、M3との差、患者、場面</p>

::summary::

うまくいった理由を、確かめられる形で書く

<!--
枠のみで、考察の内容ではない。実測後に、保存した結果を見て書く
理由の候補（未検証）：追加学習で研究室映像の手や腕の見え方に合った、質問と回答形式が合っていた。M1とM2の差は追加学習以外の条件をそろえた比較でだけ、学習の効果として述べる
最終評価を見て条件を変えない。変える場合は、その評価データを開発に使ったものとして扱い、手つかずの患者での評価を考える
-->

---
id: discussion-image-bad
chapter: 実験と結果
class: result-shell discussion-shell
sourceVisible: true
source: '枠のみで未記入／実測後に保存した結果から書く／理由は確かめるまで仮説として扱う'
---

# 考察①：画像判定でうまくいかなかった点

::content::

<p class="shell-status">未記入（枠のみ）</p>

<p class="shell-lead">判定を誤った手法と場面の理由を考える</p>

<table class="shell-table">
  <thead><tr><th>手法</th><th>何が起きたか</th><th>多分こうだから</th><th>どう確かめるか</th></tr></thead>
  <tbody>
    <tr><td>M1：学習なしVLM</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M2：学習ありVLM</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M3：分類器</td><td>－</td><td>－</td><td>－</td></tr>
  </tbody>
</table>

<p class="note">見る観点：見逃しと誤検知、判定不能、誤りの多い場面</p>

::summary::

失敗の理由を、次に何を変えるかにつなげる

<!--
枠のみで、考察の内容ではない。実測後に、保存した結果を見て書く
理由の候補（未検証）：指先だけ、手袋、反射、遮蔽、乳児の手、ROIの境界。IRには色がない。学習データの量や偏り。認識の誤りと回答形式の誤りを分ける
最終評価を見て条件を変えない。変える場合は、その評価データを開発に使ったものとして扱い、手つかずの患者での評価を考える
-->

---
id: discussion-time-good
chapter: 実験と結果
class: result-shell discussion-shell
sourceVisible: true
source: '枠のみで未記入／実測後に保存した結果から書く／理由は確かめるまで仮説として扱う'
---

# 考察①：推論時間でうまくいった点

::content::

<p class="shell-status">未記入（枠のみ）</p>

<p class="shell-lead">速く処理できたモデルの理由を考える</p>

<table class="shell-table">
  <thead><tr><th>手法</th><th>何が起きたか</th><th>多分こうだから</th><th>どう確かめるか</th></tr></thead>
  <tbody>
    <tr><td>M1：学習なしVLM</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M2：学習ありVLM</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M3：分類器</td><td>－</td><td>－</td><td>－</td></tr>
  </tbody>
</table>

<p class="note">見る観点：1枚あたりの平均、全体の時間、読み込み、メモリ</p>

::summary::

速かった理由と、使える動画の量を結びつける

<!--
枠のみで、考察の内容ではない。実測後に、保存した結果を見て書く
理由の候補（未検証）：モデルの大きさ、入力画像の大きさ、VLMの出力の短さ。比較は1枚ずつの条件で、まとめて処理した場合の速さは分からない
最終評価を見て条件を変えない。変える場合は、その評価データを開発に使ったものとして扱い、手つかずの患者での評価を考える
-->

---
id: discussion-time-bad
chapter: 実験と結果
class: result-shell discussion-shell
sourceVisible: true
source: '枠のみで未記入／実測後に保存した結果から書く／理由は確かめるまで仮説として扱う'
---

# 考察①：推論時間でうまくいかなかった点

::content::

<p class="shell-status">未記入（枠のみ）</p>

<p class="shell-lead">遅かったモデルと、時間のかかる処理の理由を考える</p>

<table class="shell-table">
  <thead><tr><th>手法</th><th>何が起きたか</th><th>多分こうだから</th><th>どう確かめるか</th></tr></thead>
  <tbody>
    <tr><td>M1：学習なしVLM</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M2：学習ありVLM</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M3：分類器</td><td>－</td><td>－</td><td>－</td></tr>
  </tbody>
</table>

<p class="note">見る観点：1枚ごとのばらつき、出力の長さ、メモリの不足</p>

::summary::

遅さの原因と、許容できるかを確かめる

<!--
枠のみで、考察の内容ではない。実測後に、保存した結果を見て書く
理由の候補（未検証）：生成が長い、GPUメモリの不足、前処理や回答の読み取りに時間がかかる。動画の量に対して現実的な時間かを、1枚あたりの平均と抽出枚数から見積もる
最終評価を見て条件を変えない。変える場合は、その評価データを開発に使ったものとして扱い、手つかずの患者での評価を考える
-->

---
id: discussion-interval-good
chapter: 実験と結果
class: result-shell discussion-shell
sourceVisible: true
source: '枠のみで未記入／実測後に保存した結果から書く／理由は確かめるまで仮説として扱う'
---

# 考察②：区間候補でうまくいった点

::content::

<p class="shell-status">未記入（枠のみ）</p>

<p class="shell-lead">区間の指定に使えた手法の理由を考える</p>

<table class="shell-table">
  <thead><tr><th>手法</th><th>何が起きたか</th><th>多分こうだから</th><th>どう確かめるか</th></tr></thead>
  <tbody>
    <tr><td>M1：学習なしVLM</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M2：学習ありVLM</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M3：分類器</td><td>－</td><td>－</td><td>－</td></tr>
  </tbody>
</table>

<p class="note">見る観点：正解区間を覆えた割合、開始終了のずれ</p>

::summary::

画像の判定が区間で役立った理由を書く

<!--
枠のみで、考察の内容ではない。実測後に、保存した結果を見て書く
理由の候補（未検証）：映り込みが長く続く区間は、1枚ごとの誤りを区間化で吸収できる。区間化の設定をそろえた比較でM1とM2を述べる
最終評価を見て条件を変えない。変える場合は、その評価データを開発に使ったものとして扱い、手つかずの患者での評価を考える
-->

---
id: discussion-interval-bad
chapter: 実験と結果
class: result-shell discussion-shell
sourceVisible: true
source: '枠のみで未記入／実測後に保存した結果から書く／理由は確かめるまで仮説として扱う'
---

# 考察②：区間候補でうまくいかなかった点

::content::

<p class="shell-status">未記入（枠のみ）</p>

<p class="shell-lead">見逃しや余計な除外が起きた理由を考える</p>

<table class="shell-table">
  <thead><tr><th>手法</th><th>何が起きたか</th><th>多分こうだから</th><th>どう確かめるか</th></tr></thead>
  <tbody>
    <tr><td>M1：学習なしVLM</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M2：学習ありVLM</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M3：分類器</td><td>－</td><td>－</td><td>－</td></tr>
  </tbody>
</table>

<p class="note">見る観点：完全見逃し、余計な除外、短い区間</p>

::summary::

取りこぼしの原因が、抽出かモデルかを分ける

<!--
枠のみで、考察の内容ではない。実測後に、保存した結果を見て書く
理由の候補（未検証）：抽出間隔より短い映り込み、モデルの誤判定、区間の結合や余裕時間の設定。抽出による取りこぼしとモデルの誤判定を分ける
最終評価を見て条件を変えない。変える場合は、その評価データを開発に使ったものとして扱い、手つかずの患者での評価を考える
-->

---
id: discussion-work-good
chapter: 実験と結果
class: result-shell discussion-shell
sourceVisible: true
source: '枠のみで未記入／実測後に保存した結果から書く／理由は確かめるまで仮説として扱う'
---

# 考察③：人の作業でうまくいった点

::content::

<p class="shell-status">未記入（枠のみ）</p>

<p class="shell-lead">手作業より作業が減った手法の理由を考える</p>

<table class="shell-table">
  <thead><tr><th>手法</th><th>何が起きたか</th><th>多分こうだから</th><th>どう確かめるか</th></tr></thead>
  <tbody>
    <tr><td>M1：学習なしVLM</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M2：学習ありVLM</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M3：分類器</td><td>－</td><td>－</td><td>－</td></tr>
  </tbody>
</table>

<p class="note">見る観点：M0との差、確認修正の時間、残った誤り</p>

::summary::

品質を保って時間が減った理由を書く

<!--
枠のみで、考察の内容ではない。実測後に、保存した結果を見て書く
理由の候補（未検証）：入力の手間が減った、確認する範囲を絞れた。品質基準を満たす条件でだけ、時間の短縮として述べる。初期の注釈と学習の費用も合わせて見る
最終評価を見て条件を変えない。変える場合は、その評価データを開発に使ったものとして扱い、手つかずの患者での評価を考える
-->

---
id: discussion-work-bad
chapter: 実験と結果
class: result-shell discussion-shell
sourceVisible: true
source: '枠のみで未記入／実測後に保存した結果から書く／理由は確かめるまで仮説として扱う'
---

# 考察③：人の作業でうまくいかなかった点

::content::

<p class="shell-status">未記入（枠のみ）</p>

<p class="shell-lead">作業が減らなかった手法の理由を考える</p>

<table class="shell-table">
  <thead><tr><th>手法</th><th>何が起きたか</th><th>多分こうだから</th><th>どう確かめるか</th></tr></thead>
  <tbody>
    <tr><td>M1：学習なしVLM</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M2：学習ありVLM</td><td>－</td><td>－</td><td>－</td></tr>
    <tr><td>M3：分類器</td><td>－</td><td>－</td><td>－</td></tr>
  </tbody>
</table>

<p class="note">見る観点：候補の修正量、陰性区間の確認、作業の順序</p>

::summary::

時間が減らない原因と、運用の限界を確かめる

<!--
枠のみで、考察の内容ではない。実測後に、保存した結果を見て書く
理由の候補（未検証）：全範囲の確認が残ると視聴時間が減らない、候補の誤りの修正に時間がかかる、既視聴の慣れで差が見えにくい。品質基準を満たさない方法は不成立として記録する
最終評価を見て条件を変えない。変える場合は、その評価データを開発に使ったものとして扱い、手つかずの患者での評価を考える
-->

---
layout: chapter-divider
id: chapter-summary
---

# まとめ

<!-- もくじの章の扉 -->

---
id: current-status
chapter: まとめ
source: '研究の進捗：2026年11月2日時点'
---

# 現在地

::content::

<table class="status-table">
  <thead><tr><th>状況</th><th>確認できている範囲</th></tr></thead>
  <tbody>
    <tr><td>整理したこと</td><td>研究目的、固定ROIの運用、<br>比較する方法と評価の構成</td></tr>
    <tr><td>準備したもの</td><td>画像と動画区間の注釈UI<br>合成データで主要操作を確認</td></tr>
    <tr><td><strong>未実施</strong></td><td><strong>実動画の注釈、モデルの推論と学習、<br>精度と作業時間の測定</strong></td></tr>
  </tbody>
</table>

::summary::

次は、実動画で少数試行を一周する

<!--
UI根拠：20261102_video_ui_02（合成動画、旧形式manifest、partial）
管理ツールの成功をモデル実験の成功とは扱わない
環境別ROI共有、共通ラベル変換、画像抽出、予測区間読込は実装確認が残る
-->

---
id: next-steps
chapter: まとめ
source: '対象患者、実施日程、品質の許容値は少数試行を踏まえて具体化する'
---

# 次の取り組み

::content::

<table class="wide-first">
  <thead><tr><th>進める段階</th><th>確認すること</th></tr></thead>
  <tbody>
    <tr><td>動画と患者の確認</td><td>利用できる動画と患者を登録し、<br>開発に使う患者を先に割り当てる</td></tr>
    <tr><td>少数の連続注釈</td><td>固定ROI、迷う場面、境界、<br>画像との時刻対応と作業時間を確かめる</td></tr>
    <tr><td>推論から確認修正</td><td>区間候補を作って元動画と照合し、<br>見逃し、細切れ、修正の負担を確認する</td></tr>
  </tbody>
</table>

::summary::

少数試行の結果を踏まえ、本注釈と3手法比較へ進む

<!-- P02→P03→P05をP04の本注釈前に確認。並行して原論文条件とモデル環境、同基盤の追加学習を確認 -->

---
id: recap
chapter: まとめ
source: '研究方針v1.9／この版は実験結果がそろう前のゼミ本編'
---

# まとめと今後の展望

::content::

<div class="recap">
  <h2>今回整理したこと</h2>
  <p>運動解析の前段として、<br><strong>手や腕の映り込み区間の指定支援</strong>を位置づけた</p>
  <p>固定ROI、区間化、人の確認修正をつなぎ、<br><strong>完成品質と作業時間</strong>を比較する構成を定めた</p>
  <h2 style="margin-top:35px">今後確かめること</h2>
  <p>少数の実動画で処理を一周し、<br>学習前後のVLMと分類器の比較へ進む</p>
</div>

::summary::

必要な品質を保ち、区間指定の負担を減らせるか確かめる

<!-- 性能改善、負担削減、臨床的有用性は未検証。実験後は画像と区間の比較、患者別指標、完成品質と時間、失敗分析を追加する -->

---
layout: chapter-divider
id: appendix
---

# 付録

<!-- 前回（第1回研究報告 2026/10/19）正式版の付録54〜57、59〜62を、本人の指定で今回の書式へ移した -->

---
id: appendix-gms
class: appendix
sourceVisible: true
source: '出典：UCLA Health, General Movements Assessment（説明資料PDF, 2020）／Aizawa et al., The general movement checklist, J Pediatr (Rio J), 97(4), 2021, doi:10.1016/j.jped.2020.09.006／イラスト：AI生成'
---

# General Movements（GMs）とは

::content::

<p class="appendix-lead">胎児期から乳児期早期に見られる、全身の自発的な運動</p>

<div class="appendix-two">
  <figure class="appendix-figure">
    <img src="/images/appendix/gms-infant-a.png" alt="仰向けの乳児の説明用イラスト">
    <figcaption>首・腕・体幹・脚が組み合わさって動く</figcaption>
  </figure>
  <div class="gms-points">
    <h2>動きの質に注目する</h2>
    <p class="point-label">複雑性</p><p>複数の部位・方向が組み合わさる</p>
    <p class="point-label">多様性</p><p>速度・強さ・動く順序が変わる</p>
    <p class="point-label">滑らかさ</p><p>始まり・終わりが滑らかにつながる</p>
  </div>
</div>

<p class="appendix-center">GMs ＝ 動きそのもの　　GMA ＝ 動きを観察する評価方法</p>

::summary::

GMsでは、全身の動きの組み合わせや変化に注目する

<!--
前回正式版59ページを継承。前回の青い強調は今回のオレンジへ変更
イラストは前回作成のImageGen画像（gma-teaching-illustrations-v1.png）の左上を切り出したもの。実在の児、症例、測定された運動ではない
出典は2026-11-03に原典を照合。UCLA資料はhttps://www.uclahealth.org/sites/default/files/documents/GMA-Flyer.pdf（題名General Movements Assessment: For Early Detection of Movement Disorders、PDF作成2020-02）。Aizawa et al.はCrossrefで題名・著者5名・巻号頁を確認
-->

---
id: appendix-gms-development
class: appendix
sourceVisible: true
source: '出典：UCLA Health, General Movements Assessment（説明資料PDF, 2020）／Child and Adolescent Health Service（西オーストラリア州）, General movement assessment／イラスト：AI生成'
---

# 発達に伴うGMsの変化

::content::

<p class="appendix-lead">予定日前からの動きが、予定日後6〜9週頃に徐々に移行する</p>

<svg class="gms-timeline" viewBox="0 0 1096 110" role="img" aria-label="予定日から20週までの時期の目安">
  <text x="40" y="26" class="start">予定日</text><text x="340" y="26">6週</text><text x="490" y="26">9週</text><text x="640" y="26">12週</text><text x="1040" y="26">20週</text>
  <line x1="40" y1="45" x2="1040" y2="45" class="axis" />
  <path d="M40 37 V53 M340 37 V53 M490 37 V53 M640 37 V53 M1040 37 V53" class="axis" />
  <rect x="40" y="62" width="300" height="44" class="phase" /><rect x="340" y="62" width="150" height="44" class="phase transition" /><rect x="490" y="62" width="550" height="44" class="phase" />
  <text x="190" y="93" class="phase-label">Writhing</text><text x="415" y="93" class="phase-label minor">移行期</text><text x="765" y="93" class="phase-label">Fidgety</text>
</svg>

<div class="gms-stages">
  <div class="gms-stage">
    <img src="/images/appendix/gms-infant-a.png" alt="Writhingの時期の説明用イラスト">
    <div><p class="point-label">Writhing movements</p><p>全身がうねるような動き</p><p>速度・強さ・範囲が変化する</p></div>
  </div>
  <div class="gms-stage">
    <img src="/images/appendix/gms-infant-b.png" alt="Fidgetyの時期の説明用イラスト">
    <div><p class="point-label">Fidgety movements</p><p>首・体幹・四肢の小さな細かい動き</p><p>方向や加速度が変化</p></div>
  </div>
</div>

<p class="appendix-small">静止画は実際の運動パターンを示すものではない<br>早産児は修正月齢で整理：生後の月齢から、予定日より早く生まれた期間を引く</p>

::summary::

同じ動きでも、発達時期に応じて観察・評価する

<!--
前回正式版60ページを継承。時間軸は説明用の目安。Writhingは予定日前から存在し、6〜9週頃にFidgetyへ移行。Fidgetyの目安は予定日後約9〜20週
前回の静止画に重ねた動きの矢印は、今回は省いた
出典は2026-11-03に原典を照合。UCLA資料はWrithingが予定日後5週頃まで、Fidgetyが6〜9週頃から20週頃までと記載。CAHSのページは約9〜20週のFidgetyを記載
-->

---
id: appendix-gma
class: appendix
sourceVisible: true
source: '出典：Child and Adolescent Health Service（西オーストラリア州）, General movement assessment／UCLA Health, General Movements Assessment（説明資料PDF, 2020）／イラスト：AI生成'
---

# General Movements Assessment（GMA）とは

::content::

<p class="appendix-lead">自然な自発運動を撮影し、訓練を受けた評価者が観察する</p>

<div class="gma-steps">
  <figure><img src="/images/appendix/gma-recording.png" alt="全身を撮影するカメラとマットの説明用イラスト"><figcaption>① 全身が見えるように撮影</figcaption></figure>
  <div class="flow-arrow" aria-hidden="true">→</div>
  <figure><img src="/images/appendix/gma-observer.png" alt="動画を観察する評価者の説明用イラスト"><figcaption>② 動画で動きの質を評価</figcaption></figure>
</div>

<p class="point-label">撮影の基本</p>
<p class="appendix-body">仰向け・落ち着いて覚醒 ／ 手足を隠さない服装 ／ 声かけや玩具の刺激を避ける<br>評価する内容：複雑性・多様性・滑らかさ、月齢に応じた運動パターン</p>

::summary::

撮影した自発運動を、訓練を受けた評価者が観察する

<!--
前回正式版61ページを継承。主にPrechtl法の基本的な説明。撮影条件や時間は年齢・施設の手順で異なり、一律の撮影時間は指定しない
「声かけや玩具の刺激を避ける」は、成人の手や腕の映り込みや介入と自発運動を区別する今回の研究背景の補足になる
出典は2026-11-03に原典を照合。CAHS（https://www.cahs.health.wa.gov.au/Our-services/Neonatology/Resources/Library/General-movement-assessment）は仰向け・落ち着いて覚醒・薄着、訓練を受けた職員の動画確認を記載。UCLA資料は覚醒、仰向け、手足を服で覆わない、撮影中の気をそらすものなしを記載
-->

---
id: appendix-gma-patterns
class: appendix
sourceVisible: true
source: '出典：Aizawa et al., The general movement checklist, J Pediatr (Rio J), 97(4), 2021, doi:10.1016/j.jped.2020.09.006／AACPDM, Care Pathways: Early Detection of Cerebral Palsy'
---

# GMAで観察する主なパターン

::content::

<p class="appendix-heading">Writhingの時期：動き方の特徴を見分ける<span>概念図（測定波形・判定基準ではない）</span></p>

<div class="gma-patterns">
  <div class="pattern-name">正常なGMs</div>
  <svg viewBox="0 0 200 40" aria-hidden="true"><path d="M2 26 C17 -6 32 52 50 19 S82 -3 97 21 S127 41 147 12 S177 31 198 18" /></svg>
  <div>多様で複雑、滑らかに変化する</div>
  <div class="pattern-name">Poor repertoire</div>
  <svg viewBox="0 0 200 40" aria-hidden="true"><path d="M2 22 Q14 2 26 22 T50 22 T74 22 T98 22 T122 22 T146 22 T170 22 T194 22" /></svg>
  <div>種類や変化が乏しく、単調</div>
  <div class="pattern-name">Cramped-synchronized</div>
  <svg viewBox="0 0 200 40" aria-hidden="true"><path d="M2 14 L27 14 L42 3 L60 14 L102 14 L117 3 L135 14 L198 14" /><path class="second" d="M2 34 L27 34 L42 23 L60 34 L102 34 L117 23 L135 34 L198 34" /></svg>
  <div>体幹や四肢が硬く、同時に動く</div>
  <div class="pattern-name">Chaotic</div>
  <svg viewBox="0 0 200 40" aria-hidden="true"><path d="M2 22 L17 4 L24 37 L42 8 L56 38 L64 2 L82 33 L101 4 L117 38 L128 16 L147 38 L160 6 L177 30 L198 2" /></svg>
  <div>大きく急な動きが、まとまりなく現れる</div>
</div>

<p class="appendix-heading accent">Fidgetyの時期：細かい動きの有無と、その質を観察する</p>

<div class="appendix-callout">適切な時期にFidgety movementsが見られないことは、<br>脳性麻痺リスクを評価する重要な所見</div>
<p class="appendix-body">脳画像や神経学的診察などの情報も組み合わせて判断する</p>

::summary::

GMAの異常所見だけで、脳性麻痺が確定するわけではない

<!--
前回正式版62ページを継承。各パターンの記述は初心者向けの要約であり診断基準の代用ではない
Fidgetyの欠如は修正月齢に応じた適切な観察時期の所見。GMA単独の一律の診断精度は提示しない
前回の赤枠は、今回の配色指定に合わせてオレンジ枠へ変更
出典は2026-11-03に原典を照合。Aizawa et al.はWrithingの時期の正常と異常（Poor repertoire、Cramped-synchronizedなど）を評価するチェックリストの論文。AACPDMのページはFidgetyの欠如、MRI、HINEを組み合わせた早期発見の経路を示し、脳性麻痺は複数の臨床所見に基づく臨床診断と記載（Novak et al., JAMA Pediatr, 2017に基づくとページに記載）。「GMAの異常所見だけで確定しない」は、この記載に基づく要約
-->

---
id: appendix-oks
class: appendix
sourceVisible: true
source: '前回のキーポイント推定の評価で使用した指標（前回付録54ページを継承）。今回の評価指標ではない'
---

# 指標：OKS

::content::

<p class="appendix-heading">OKS（Object Keypoint Similarity）とは<br>キーポイント検出において、<strong>正解と推論の類似度</strong>を表す尺度</p>

<div class="oks-row">
  <svg class="oks-figure" viewBox="0 0 380 270" role="img" aria-label="正解キーポイントと推論キーポイントの距離の模式図">
    <path d="M40 255 V12 M28 245 H370" class="axis" />
    <text x="48" y="22" class="axis-label">縦px</text><text x="330" y="268" class="axis-label">横px</text>
    <path d="M110 105 L100 170 L88 230" class="truth" /><path d="M200 50 L205 140 L195 215" class="pred" />
    <path d="M118 102 L190 54 M108 168 L195 141 M96 228 L185 216" class="dist" />
    <circle cx="110" cy="105" r="9" class="truth-dot" /><circle cx="100" cy="170" r="9" class="truth-dot" /><circle cx="88" cy="230" r="9" class="truth-dot" />
    <circle cx="200" cy="50" r="9" class="pred-dot" /><circle cx="205" cy="140" r="9" class="pred-dot" /><circle cx="195" cy="215" r="9" class="pred-dot" />
    <text x="72" y="104">A₁</text><text x="62" y="172">A₂</text><text x="50" y="238">A₃</text>
    <text x="214" y="48">P₁</text><text x="218" y="144">P₂</text><text x="208" y="222">P₃</text>
    <text x="148" y="68">d₁</text><text x="140" y="148">d₂</text><text x="135" y="212">d₃</text>
    <circle cx="282" cy="22" r="7" class="truth-dot" /><text x="296" y="29" class="legend">正解</text>
    <circle cx="282" cy="50" r="7" class="pred-dot" /><text x="296" y="57" class="legend">推論</text>
  </svg>
  <div class="appendix-equation">

$$
\mathrm{OKS}=\frac{\sum_i \exp\left(\dfrac{-d_i^2}{2s^2k_i^2}\right)\delta(v_i>0)}{\sum_i \delta(v_i>0)}
$$

  </div>
</div>

<table class="symbol-table">
  <tbody>
    <tr><td><i>d<sub>i</sub></i></td><td>i番目のキーポイントに対応する推論キーポイントと正解キーポイントのユークリッド距離</td></tr>
    <tr><td><i>s</i></td><td>正解BBoxで定められた物体の矩形領域面積</td></tr>
    <tr><td><i>k<sub>i</sub></i></td><td>キーポイントごとに設定される定数</td></tr>
    <tr><td><i>v<sub>i</sub></i></td><td>キーポイントのvisibilityラベル（0, 1, 2）</td></tr>
    <tr><td><i>δ</i>(<i>v<sub>i</sub></i>&gt;0)</td><td><i>v<sub>i</sub></i> &gt; 0ならば1、それ以外なら0となる関数</td></tr>
  </tbody>
</table>

<!--
前回正式版54ページを継承。距離の模式図は前回の画像を今回の配色（正解：灰色、推論：オレンジ）でSVGに描き直した
前回の旧研究（キーポイント推定）の評価指標。今回の手や腕の区間判定の評価では使わない
-->

---
id: appendix-oks-reading
class: appendix
sourceVisible: true
source: '前回のキーポイント推定の評価で使用した指標（前回付録55ページを継承）。今回の評価指標ではない'
---

# Ki と OKS の見方

::content::

<p class="appendix-body"><i>K<sub>i</sub></i>：キーポイント毎に設定される定数で、<strong>キーポイント検出の難易度を表す</strong>値<br>1つのデータセットに対して複数人でアノテーションを行い、その座標情報の標準偏差</p>

<table class="oks-reading">
  <thead><tr><th>OKSが大きい（1に近い）</th><th>OKSが小さい（0に近い）</th></tr></thead>
  <tbody>
    <tr><td>推定キーポイントが正解に近い</td><td>推定キーポイントが正解から遠い</td></tr>
    <tr><td>多くの点で一致していて、<br><strong>姿勢推定が良い</strong></td><td>ずれている点が多く、<br><strong>姿勢推定が悪い</strong></td></tr>
    <tr><td>極端に言えば、全点ぴったりなら<br><strong>OKS＝1</strong></td><td>ずれが大きい点は指数項が<br>ほぼ0になりOKSが下がる</td></tr>
  </tbody>
</table>

<!-- 前回正式版55ページを継承。前回のオレンジ表は今回の灰色の表へ変更 -->

---
id: appendix-ap
class: appendix
sourceVisible: true
source: '前回のキーポイント推定の評価で使用した指標（前回付録56ページを継承）。今回の評価指標ではない'
---

# 指標：AP50とmAP50-95

::content::

<div class="metric-block">
  <h2>AP50</h2>
  <p>ポーズが正解かどうかを判定する基準として<br>「<strong>OKSスコアが0.5以上なら正解</strong>」もしくは「IoUスコアが0.5以上なら正解」<br>という、単一基準を用いたときのモデルの総合的な性能スコア</p>
</div>

<div class="metric-block">
  <h2>mAP50-95</h2>
  <p>AP50からAP95まで、閾値を0.05刻みで設定したAPの平均をとったもの</p>
</div>

<div class="appendix-equation wide">

$$
\mathrm{mAP}_{50\text{-}95}=\text{平均}\left(\mathrm{AP}_{\mathrm{OKS}=0.50},\ \mathrm{AP}_{\mathrm{OKS}=0.55},\ \dots,\ \mathrm{AP}_{\mathrm{OKS}=0.95}\right)
$$

</div>

<!-- 前回正式版56ページを継承。前回の「5刻み」は、閾値0.05刻み（AP50, AP55, ... AP95）の意味で書き直した -->

---
id: appendix-iou
class: appendix
sourceVisible: true
source: '前回のキーポイント推定・領域検出の評価で使用した指標（前回付録57ページを継承）'
---

# 指標：IoU

::content::

<p class="appendix-heading">IoU（Intersection over Union）とは<br>予測したバウンディングボックスと正解のバウンディングボックスの<br>「<strong>重なり具合</strong>」を評価する指標</p>

<div class="iou-row">
  <div>
    <div class="appendix-equation">

$$
\mathrm{IoU}=\frac{\text{重なった領域の面積}}{\text{予測領域と正解領域を合わせた面積}}
$$

  </div>
    <p class="point-label">例</p>
    <ul class="appendix-list">
      <li>完全に重なっている場合：<strong>IoU＝1</strong></li>
      <li>重なりが全くない場合：<strong>IoU＝0</strong></li>
    </ul>
  </div>
  <svg class="iou-figure" viewBox="0 0 400 380" role="img" aria-label="正解と予測の矩形が重なる模式図">
    <rect x="110" y="110" width="170" height="160" class="overlap" />
    <rect x="10" y="10" width="270" height="260" class="truth-box" />
    <rect x="110" y="110" width="280" height="260" class="pred-box" />
    <text x="20" y="42" class="legend">正解</text><text x="300" y="356" class="legend">予測</text><text x="195" y="198" class="legend center">重なり</text>
  </svg>
</div>

<!--
前回正式版57ページを継承。前回の「予測領域と正解領域の合計面積」は、重なりを二重に数えない和集合の意味のため「合わせた面積」とした
今回の評価指標は本編「今回確かめること」のノートに従う。ここで今回の区間評価の指標を決定扱いしない
-->
