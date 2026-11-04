<script setup lang="ts">
// e-Stat 人口動態統計 表4-25（2026-11-03取得）の男女の値を合計。
// 棒は全出生数ではなく、2,500g未満の出生数。割合は表の注に合わせ、体重不詳を除いた出生数に対する値。
const years = ['1951', '1960', '1970', '1980', '1990', '2000', '2010', '2020', '2023']
const lowWeightBirths = [157048, 113641, 109726, 81659, 77332, 102888, 103049, 77539, 70151]
const lowWeightRate = [0.0738, 0.0711, 0.0568, 0.0518, 0.0633, 0.0864, 0.0962, 0.0922, 0.0965]
const plot = { left: 120, right: 960, top: 24, bottom: 430 }
const step = (plot.right - plot.left) / years.length
const x = (i: number) => plot.left + step * (i + 0.5)
const yCount = (v: number) => plot.bottom - (plot.bottom - plot.top) * v / 180000
const yRate = (v: number) => plot.bottom - (plot.bottom - plot.top) * v / 0.12
const countTicks = [0, 30000, 60000, 90000, 120000, 150000, 180000]
const rateTicks = [0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12]
const line = lowWeightRate.map((v, i) => `${i ? 'L' : 'M'}${x(i)} ${yRate(v)}`).join(' ')
</script>

<template>
  <svg class="birth-chart" viewBox="0 0 1096 500" role="img" aria-label="低出生体重児の出生数と割合の推移（1951〜2023年）">
    <g class="grid">
      <line v-for="t in countTicks" :key="t" :x1="plot.left" :x2="plot.right" :y1="yCount(t)" :y2="yCount(t)" />
    </g>
    <g class="tick left">
      <text v-for="t in countTicks" :key="t" :x="plot.left - 12" :y="yCount(t) + 8">{{ t.toLocaleString() }}</text>
      <text :x="plot.left + 8" :y="plot.top - 6" class="unit">（人）</text>
    </g>
    <g class="tick right">
      <text v-for="t in rateTicks" :key="t" :x="plot.right + 12" :y="yRate(t) + 8" :class="{ accent: t === 0.10 }">{{ (t * 100).toFixed(0) }}%</text>
    </g>
    <rect v-for="(v, i) in lowWeightBirths" :key="years[i]" class="bar" :x="x(i) - 20" :y="yCount(v)" width="40" :height="plot.bottom - yCount(v)" />
    <path :d="line" class="rate" />
    <circle v-for="(v, i) in lowWeightRate" :key="years[i]" :cx="x(i)" :cy="yRate(v)" r="5" class="rate-dot" />
    <text v-for="(year, i) in years" :key="year" :x="x(i)" :y="plot.bottom + 34" class="year">{{ year }}</text>
    <g class="legend" transform="translate(190 492)">
      <rect x="0" y="-20" width="26" height="22" class="bar" /><text x="36" y="0">低出生体重児の出生数</text>
      <path d="M330 -9 H370" class="rate" /><text x="380" y="0">低出生体重児の割合（2,500g未満）</text>
    </g>
  </svg>
</template>

<style scoped>
.birth-chart { width:100%; height:auto; overflow:visible; }
text { font-family:Meiryo,'メイリオ',sans-serif; font-size:24px; fill:#151515; }
.grid line { stroke:#ddd; stroke-width:1.5; }
.tick.left text { text-anchor:end; }
.tick.right text { text-anchor:start; }
.tick text.accent { fill:var(--text-accent); font-weight:700; }
.tick text.unit { font-size:22px; text-anchor:start; }
.bar { fill:#bfbfbf; }
.rate { fill:none; stroke:var(--text-accent); stroke-width:4; }
.rate-dot { fill:var(--text-accent); }
.year { text-anchor:middle; }
.legend text { font-size:24px; }
</style>
