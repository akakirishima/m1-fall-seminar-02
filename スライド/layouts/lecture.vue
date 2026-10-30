<script setup lang="ts">
import { useSlideContext } from '@slidev/client'
const { $page, $frontmatter, $slidev } = useSlideContext()
</script>

<template>
  <div class="slidev-layout lecture" :class="$frontmatter.class">
    <header class="lecture-title"><slot /></header>
    <div class="lecture-rule" aria-hidden="true" />
    <main class="lecture-content"><slot name="content" /></main>
    <footer class="lecture-footer">
      <span class="lecture-attribution">{{ $frontmatter.sectionTitle ?? $slidev.configs.themeConfig.footerText }}</span>
      <span class="lecture-page">{{ $frontmatter.slideId ?? $page }}</span>
    </footer>
  </div>
</template>
