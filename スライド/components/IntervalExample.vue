<script setup lang="ts">
const labels = ['無', '有', '有', '無', '有', '有', '無', '?', '無']
const x = (i: number) => 250 + i * 95
</script>

<template>
  <svg class="interval-diagram" viewBox="0 0 1096 470" role="img" aria-label="時刻付きの判定を区間候補へ変換する説明用の例">
    <text class="diagram-label" x="0" y="48">時刻［秒］</text>
    <g v-for="(_, i) in labels" :key="i">
      <text class="diagram-label" :x="x(i)" y="48" text-anchor="middle">{{ i }}</text>
      <path :d="`M${x(i)} 66V377`" stroke="#ddd" stroke-width="1.5" />
    </g>
    <text class="diagram-label" x="0" y="123">画像ごとの判定</text>
    <g v-for="(label, i) in labels" :key="`prediction-${i}`">
      <rect :x="x(i)-25" y="87" width="50" height="50" :fill="label==='有' ? '#d9d9d9' : '#f4f4f4'" stroke="#777" :stroke-dasharray="label==='?' ? '5 4' : undefined" />
      <text class="diagram-label" :x="x(i)" y="123" text-anchor="middle">{{ label }}</text>
    </g>
    <text class="diagram-label" x="0" y="229">区間候補</text>
    <rect :x="x(1)" y="190" :width="x(3)-x(1)" height="58" fill="#d9d9d9" stroke="#666" stroke-width="2" />
    <rect :x="x(4)" y="190" :width="x(6)-x(4)" height="58" fill="#d9d9d9" stroke="#666" stroke-width="2" />
    <text class="diagram-label" :x="x(2)" y="229" text-anchor="middle">有</text>
    <text class="diagram-label" :x="x(5)" y="229" text-anchor="middle">有</text>
    <rect :x="x(7)" y="190" width="95" height="58" fill="#f4f4f4" stroke="#666" stroke-dasharray="5 4" stroke-width="2" />
    <text class="diagram-label" :x="x(7)+47" y="229" text-anchor="middle">?</text>
    <text class="diagram-label" x="0" y="345">隙間をつなぐ例</text>
    <rect :x="x(1)" y="306" :width="x(6)-x(1)" height="58" fill="#d9d9d9" stroke="#666" stroke-width="2" />
    <text class="diagram-label" :x="x(1)+18" y="345" text-anchor="start">同じ区間としてまとめる</text>
    <rect :x="x(7)" y="306" width="95" height="58" fill="#f4f4f4" stroke="#666" stroke-dasharray="5 4" stroke-width="2" />
    <text class="diagram-label" :x="x(7)+47" y="345" text-anchor="middle">?</text>
    <text class="diagram-note" x="0" y="429">各判定を次の時刻まで適用した仮の例／「?」は判定不能</text>
  </svg>
</template>
