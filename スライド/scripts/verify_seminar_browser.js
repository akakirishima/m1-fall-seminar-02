async (page) => {
  const results = []
  const errors = []
  page.on('pageerror', error => errors.push(error.message))
  await page.setViewportSize({ width: 1200, height: 900 })
  for (let number = 1; number <= 37; number++) {
    await page.goto(`http://localhost:3032/${number}`)
    const slide = page.locator('.slidev-layout:visible').last()
    await slide.waitFor({ state: 'visible' })
    await page.evaluate(() => document.fonts.ready)
    await slide.locator('img').evaluateAll(images => Promise.all(images.map(image => image.decode().catch(() => {}))))
    const inspection = await slide.evaluate(root => {
      const rect = root.getBoundingClientRect()
      const content = root.querySelector('.seminar-content')
      const bounds = content?.getBoundingClientRect()
      const overflow = []
      for (const item of root.querySelectorAll('.reference-purpose-content > *, .seminar-title h1, .seminar-cover-title, .seminar-cover-subtitle, .seminar-cover-logo, .chapter-divider-title, .seminar-source, .seminar-summary')) {
        const box = item.getBoundingClientRect()
        if (box.bottom > rect.bottom + 3 || box.right > rect.right + 3 || box.left < rect.left - 3 || box.top < rect.top - 3) {
          overflow.push({ text: (item.textContent || item.tagName).trim().slice(0, 70), bottom: Math.round(box.bottom-rect.bottom), right: Math.round(box.right-rect.right) })
        }
      }
      if (content && bounds) {
        for (const item of content.querySelectorAll('p,li,table,svg,text')) {
          const box = item.getBoundingClientRect()
          if (box.bottom > bounds.bottom + 3 || box.right > bounds.right + 3 || box.left < bounds.left - 3) {
            overflow.push({ text: (item.textContent || '').trim().slice(0, 70), bottom: Math.round(box.bottom-bounds.bottom), right: Math.round(box.right-bounds.right) })
          }
        }
      }
      const imageFailures = [...root.querySelectorAll('img')].filter(image => !image.complete || !image.naturalWidth).map(image => image.getAttribute('src'))
      return { title: root.querySelector('h1')?.textContent, width: rect.width, height: rect.height, overflow, imageFailures }
    })
    await slide.screenshot({ path: `D:/研究M1/第2回ゼミ発表/output/playwright/seminar02-emphasis-20261104/slide-${String(number).padStart(2, '0')}.png` })
    results.push({ number, ...inspection })
  }
  await page.goto('http://localhost:3032/1')
  await page.getByRole('heading', { level: 1 }).waitFor({ state: 'visible' })
  await page.getByRole('button', { name: 'Go to next slide', exact: true }).click()
  await page.waitForURL('**/2', { timeout: 10000 })
  const navigation = new URL(page.url()).pathname === '/2'
  await page.goto('http://localhost:3032/1')
  const overflow = results.filter(item => item.overflow.length)
  const imageFailures = results.filter(item => item.imageFailures.length)
  return { slides: results.length, navigation, errors, overflow, imageFailures }
}
