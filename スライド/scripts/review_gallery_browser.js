async (page) => {
  await page.setViewportSize({ width: 1200, height: 1350 })
  for (let group = 0; group < 3; group++) {
    await page.goto(`file:///D:/研究M1/第2回ゼミ発表/output/playwright/seminar02/gallery-${group}.html`)
    await page.waitForFunction(() => [...document.images].every(image => image.complete && image.naturalWidth > 0))
    await page.screenshot({ path: `D:/研究M1/第2回ゼミ発表/output/playwright/seminar02/gallery-${group}.png`, fullPage: true })
  }
  await page.setViewportSize({ width: 1200, height: 900 })
  await page.goto('http://localhost:3032/1')
  console.log('Three galleries rendered; browser returned to the first slide')
}
