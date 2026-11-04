async (page) => {
  const slides = []
  await page.goto('http://localhost:3032/1')
  await page.getByRole('button', { name: 'Go to next slide', exact: true }).waitFor({ state: 'visible' })
  const totalMatch = (await page.locator('body').innerText()).match(/\b1\s*\/\s*(\d+)\b/)
  if (!totalMatch) throw new Error('Cannot determine the current deck slide count')
  const total = Number(totalMatch[1])
  for (let number = 1; number <= total; number++) {
    await page.goto(`http://localhost:3032/${number}`)
    const root = page.locator('.slidev-layout:visible').last()
    await root.waitFor({ state: 'visible' })
    await page.evaluate(() => document.fonts.ready)
    const tables = await root.evaluate(layout => {
      const origin = layout.getBoundingClientRect()
      const box = element => {
        const rect = element.getBoundingClientRect()
        return { x: rect.x - origin.x, y: rect.y - origin.y, width: rect.width, height: rect.height }
      }
      const textStyle = element => {
        const style = getComputedStyle(element)
        return { font: style.fontFamily.split(',')[0].replaceAll(/['"]/g, ''), size: parseFloat(style.fontSize),
          bold: Number(style.fontWeight) >= 600, italic: style.fontStyle === 'italic', color: style.color }
      }
      return [...layout.querySelectorAll('table')].map(table => {
        const rows = [...table.rows].map(row => ({ height: row.getBoundingClientRect().height,
          cells: [...row.cells].map(cell => {
            const style = getComputedStyle(cell)
            const runs = []
            function walk(node) {
              if (node.nodeType === Node.TEXT_NODE) {
                const text = node.textContent.replaceAll(/\s+/g, ' ')
                if (text) runs.push({ text, ...textStyle(node.parentElement) })
              } else if (node.nodeType === Node.ELEMENT_NODE) {
                if (node.tagName === 'BR') runs.push({ text: '\n', ...textStyle(node.parentElement) })
                else for (const child of node.childNodes) walk(child)
              }
            }
            for (const child of cell.childNodes) walk(child)
            return { ...box(cell), ...textStyle(cell), text: runs.map(run => run.text).join(''), runs,
              fill: style.backgroundColor, align: style.textAlign,
              margins: ['Top', 'Right', 'Bottom', 'Left'].map(side => parseFloat(style[`padding${side}`])),
              borders: ['Top', 'Left', 'Bottom', 'Right'].map(side => ({ color: style[`border${side}Color`], width: parseFloat(style[`border${side}Width`]) })) }
          }) }))
        if (rows.some(row => row.cells.length !== rows[0].cells.length)) throw new Error('Merged tables require explicit support')
        return { ...box(table), rows, columns: rows[0].cells.map(cell => cell.width),
          emphasisColumn: table.classList.contains('gap-table') ? 3 : null }
      })
    })
    if (tables.length) slides.push({ number, tables })
  }
  return { canvas: { width: 1200, height: 900 }, slides }
}
