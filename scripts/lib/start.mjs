/** 统一的「进入第 1 周」流程：清存档 → 走开局屏（选分路/摇数值/取名）→ 落到本周页。 */
export async function startCareer(page) {
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: 'networkidle0' });
  const role = await page.$('.role');
  if (role) {
    await role.click();
    await page.type('.name-input', '阿呆');
    await page.click('[data-act="start"]');
  }
  await page.waitForSelector('.slot', { timeout: 5000 });
}
