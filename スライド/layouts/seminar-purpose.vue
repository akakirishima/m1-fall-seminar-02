<script setup lang="ts">
import { useSlideContext } from '@slidev/client'
const { $page, $frontmatter } = useSlideContext()
</script>

<template>
  <div class="slidev-layout seminar seminar-purpose">
    <header class="seminar-title"><slot /></header>
    <div class="seminar-rule" aria-hidden="true" />
    <ReferencePurpose />
    <SeminarFooter :page="$page" :chapter="$frontmatter.chapter" />
  </div>
</template>
