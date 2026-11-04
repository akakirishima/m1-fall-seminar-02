<template>
  <svg class="overview-diagram" viewBox="0 0 1096 560" role="img" aria-label="研究全体の構想と今回の区間指定支援の位置">
    <defs><marker id="overview-arrow" markerWidth="9" markerHeight="9" refX="8" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="#666" /></marker></defs>
    <g class="diagram-links" marker-end="url(#overview-arrow)">
      <path d="M170 102H218" /><path d="M535 102H582" /><path d="M775 102H823" /><path d="M1035 102H1052" />
      <path d="M55 287H146" /><path d="M410 287H462" />
      <path d="M103 287V438H462" /><path d="M717 287H765V354H805" /><path d="M717 438H765V391H805" />
      <path d="M933 414V472" />
    </g>
    <path class="diagram-node" d="M25 57H190L169 147H4Z" />
    <text class="diagram-label" x="96" y="97" text-anchor="middle"><tspan x="96">研究室の</tspan><tspan x="96" dy="36">IR映像</tspan></text>
    <text class="diagram-callout" x="220" y="25">今回の対象</text>
    <rect class="diagram-node focus" x="220" y="57" width="315" height="90" />
    <text class="diagram-label focus" x="377" y="94" text-anchor="middle"><tspan x="377">手や腕の区間検出</tspan><tspan x="377" dy="36">＋ 人が確認修正</tspan></text>
    <rect class="diagram-node" x="584" y="57" width="191" height="90" />
    <text class="diagram-label" x="679" y="94" text-anchor="middle"><tspan x="679">人物領域</tspan><tspan x="679" dy="36">検出</tspan></text>
    <rect class="diagram-node" x="825" y="57" width="210" height="90" />
    <text class="diagram-label" x="930" y="94" text-anchor="middle"><tspan x="930">身体部位</tspan><tspan x="930" dy="36">分割</tspan></text>
    <circle class="diagram-node" cx="1071" cy="102" r="18" /><text class="connector-label" x="1071" y="112" text-anchor="middle">A</text>
    <circle class="diagram-node" cx="36" cy="287" r="18" /><text class="connector-label" x="36" y="297" text-anchor="middle">A</text>
    <rect class="diagram-node" x="148" y="242" width="262" height="90" />
    <text class="diagram-label" x="279" y="280" text-anchor="middle"><tspan x="279">キーポイント推定</tspan><tspan x="279" dy="36">領域を利用</tspan></text>
    <rect class="diagram-node" x="464" y="242" width="253" height="90" />
    <text class="diagram-label" x="590" y="280" text-anchor="middle"><tspan x="590">KP由来の特徴量</tspan><tspan x="590" dy="36">角度や座標の変化</tspan></text>
    <rect class="diagram-node" x="464" y="393" width="253" height="90" />
    <text class="diagram-label" x="590" y="431" text-anchor="middle"><tspan x="590">領域由来の特徴量</tspan><tspan x="590" dy="36">面積や重心の変化</tspan></text>
    <rect class="diagram-node" x="807" y="329" width="252" height="85" />
    <text class="diagram-label" x="933" y="365" text-anchor="middle"><tspan x="933">2種類の特徴量</tspan><tspan x="933" dy="36">を統合</tspan></text>
    <rect class="diagram-node" x="807" y="474" width="252" height="76" rx="38" />
    <text class="diagram-label" x="933" y="520" text-anchor="middle">CPリスク評価</text>
    <text class="diagram-note" x="148" y="204">後段は将来構想：今回の実験で効果を検証する範囲とは分ける</text>
  </svg>
</template>
