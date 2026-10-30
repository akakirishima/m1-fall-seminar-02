<template>
  <div class="slidev-layout title-cover">
    <div class="cover-heading"><slot /></div>
    <div class="cover-english"><slot name="english" /></div>
    <div class="cover-rule" aria-hidden="true" />
    <div class="cover-advisor"><slot name="advisor" /></div>
    <div class="cover-bottom">
      <div class="cover-author"><slot name="author" /></div>
      <div class="cover-logo"><img src="/images/university-of-miyazaki-logo.png" alt="宮崎大学" /></div>
      <div class="cover-affiliation"><slot name="affiliation" /></div>
    </div>
  </div>
</template>
