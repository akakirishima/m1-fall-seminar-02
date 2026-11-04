<script setup lang="ts">
defineProps<{ page: number | string, chapter?: string }>()
// もくじの5項目。各ページのfrontmatterのchapterと一致する項目だけ白くする。
const chapters = ['研究背景', '課題', '取り組み', '実験と結果', 'まとめ']
</script>

<template>
  <footer class="seminar-footer">
    <div v-if="$slots.summary" class="seminar-summary"><slot name="summary" /></div>
    <div class="seminar-footer-band">
      <nav class="seminar-footer-chapters" aria-label="章">
        <span v-for="name in chapters" :key="name" :class="{ current: name === chapter }" :aria-current="name === chapter ? 'step' : undefined">{{ name }}</span>
      </nav>
      <div class="seminar-footer-credit"><span>Hiroki Matsumoto,</span><span>University of Miyazaki</span></div>
      <div class="seminar-page" :aria-label="`${page}ページ`">{{ page }}</div>
    </div>
  </footer>
</template>
