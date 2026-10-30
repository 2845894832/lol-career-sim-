import { defineConfig } from 'vitest/config';
import { viteSingleFile } from 'vite-plugin-singlefile';

// 平台要求交付单个 index.html：JS/CSS 全部内联，零外链。
export default defineConfig({
  plugins: [viteSingleFile()],
  build: {
    target: 'es2020',
    cssCodeSplit: false,
    assetsInlineLimit: 100_000_000,
    reportCompressedSize: false,
  },
  test: {
    include: ['tests/**/*.test.ts'],
    environment: 'node',
  },
});
