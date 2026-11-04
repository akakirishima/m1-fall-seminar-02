<script setup lang="ts">
const pictures = [
  { file: 'slide-007-picture-01.png', x: 60.333, y: 466.667, w: 250, h: 187.5 },
  { file: 'slide-007-picture-02.jpeg', x: 393.184, y: 466.667, w: 208.57, h: 187.5, crop: [31752, 45259, 38554, 19145] },
  { file: 'slide-007-picture-03.png', x: 169.441, y: 552.178, w: 38.924, h: 33.543, crop: [17288, 17842, 14450, 23323], rotation: 156.6861 },
  { file: 'slide-007-picture-04.png', x: 488.197, y: 545.433, w: 27.192, h: 23.438, crop: [17288, 17842, 14450, 23323], rotation: 32.46165 },
  { file: 'slide-007-picture-05.png', x: 703.066, y: 720, w: 73.202, h: 80, crop: [13258, 15317, 14298, 10312] },
  { file: 'slide-007-picture-06.png', x: 702.678, y: 473.333, w: 73.976, h: 80 },
  { file: 'slide-007-picture-07.png', x: 699.667, y: 596.667, w: 80, h: 80 },
]
function cropStyle(crop?: number[]) {
  if (!crop) return { width: '100%', height: '100%', left: '0', top: '0' }
  const [l, t, r, b] = crop
  return { width: `${10000000/(100000-l-r)}%`, height: `${10000000/(100000-t-b)}%`, left: `${-100*l/(100000-l-r)}%`, top: `${-100*t/(100000-t-b)}%` }
}
</script>

<template>
  <div class="reference-purpose-content">
    <div class="reference-purpose-main"><strong>NICU/GCU 環境</strong>において<br>新生児の身体運動を<strong>目視観察に依存せず</strong><br><strong>連続的・客観的</strong>に扱うためのシステムの構築</div>
    <div class="reference-purpose-heading advantage-heading">優位性</div>
    <div class="reference-purpose-heading benefits-heading">期待される効果</div>
    <div class="reference-purpose-panel advantage-panel" />
    <div class="reference-purpose-panel benefits-panel" />
    <div v-for="picture in pictures" :key="picture.file" class="reference-picture" :style="{left:`${picture.x}px`,top:`${picture.y}px`,width:`${picture.w}px`,height:`${picture.h}px`,transform:`rotate(${picture.rotation || 0}deg)`}">
      <img :src="`/local-reference/${picture.file}`" :style="cropStyle(picture.crop)" alt="前回の研究目的ページから引き継いだ画像" />
    </div>
    <div class="reference-purpose-caption grayscale-caption"><strong>グレースケール</strong><br>映像を用いる</div>
    <div class="reference-purpose-caption clinical-caption">撮影環境が厳しい<br>NICU/GCUにて撮影した<br><strong>リアルデータ</strong>を使用</div>
    <div class="reference-purpose-benefit benefit-monitoring">24時間での見守り</div>
    <div class="reference-purpose-benefit benefit-workload">負担軽減・業務効率化</div>
    <div class="reference-purpose-benefit benefit-diagnosis">診断の補助</div>
  </div>
</template>
