import { defineConfig } from 'vitest/config';
import { viteSingleFile } from 'vite-plugin-singlefile';

// 平台要求交付单个 index.html：JS/CSS 全部内联，零外链。
// SLICE=1 出切片副本（打到第 8 周就收尾），产物在 dist-slice/。
const SLICE = process.env.SLICE === '1';
const SLICE_AT_WEEK = 8;

export default defineConfig({
  plugins: [viteSingleFile()],
  define: {
    __SLICE_AT__: JSON.stringify(SLICE ? SLICE_AT_WEEK : 0),
  },
  build: {
    target: 'es2020',
    outDir: SLICE ? 'dist-slice' : 'dist',
    cssCodeSplit: false,
    assetsInlineLimit: 100_000_000,
    reportCompressedSize: false,
  },
  test: {
    include: ['tests/**/*.test.ts'],
    environment: 'node',
  },
});
