/* Optional asset regeneration; the committed PNG is ready to publish. */
const path = require('node:path');
const sharp = require(process.env.BIFROST_SHARP_MODULE || 'sharp');
const ROOT = path.resolve(__dirname, '..');
(async () => {
  if (process.env.BIFROST_KOREAN_FONT) {
    await sharp({ text: { text: '학습', font: 'Malgun Gothic 16', fontfile: process.env.BIFROST_KOREAN_FONT, rgba: true } }).png().toBuffer();
  }
  await sharp(path.join(ROOT, 'assets/og-image.svg')).png().toFile(path.join(ROOT, 'og-image.png'));
  console.log('Generated 1200 × 630 og-image.png.');
})().catch(error => { console.error(error); process.exitCode = 1; });
