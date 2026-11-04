<script setup lang="ts">
import { useSlideContext } from '@slidev/client'
const { $page, $frontmatter } = useSlideContext()
</script>

<template>
  <div class="slidev-layout seminar" :class="$frontmatter.class">
    <header class="seminar-title"><slot /></header>
    <div class="seminar-rule" aria-hidden="true" />
    <main class="seminar-content"><slot name="content" /></main>
    <div v-if="$frontmatter.sourceVisible" class="seminar-source">{{ $frontmatter.source }}</div>
    <SeminarFooter :page="$page" :chapter="$frontmatter.chapter">
      <template v-if="$slots.summary" #summary><slot name="summary" /></template>
    </SeminarFooter>
  </div>
</template>
