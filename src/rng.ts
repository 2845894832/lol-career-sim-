/**
 * 种子化随机：不自己取随机数，随机状态存在 GameState 里。
 * 同状态 + 同动作 → 同结果，这是可复现的基础。
 */

export interface Rng {
  /** [0, 1) */
  next(): number;
  /** [0, n) 的整数 */
  int(n: number): number;
  /** 按权重取一项的下标 */
  weighted(weights: readonly number[]): number;
}

/** mulberry32：小、快、够均匀。 */
export function createRng(state: number): { rng: Rng; state: () => number } {
  let s = state | 0;

  const next = (): number => {
    s = (s + 0x6d2b79f5) | 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };

  const rng: Rng = {
    next,
    int: (n: number) => Math.floor(next() * n),
    weighted(weights: readonly number[]): number {
      const total = weights.reduce((a, b) => a + b, 0);
      if (total <= 0) return 0;
      let roll = next() * total;
      for (let i = 0; i < weights.length; i++) {
        roll -= weights[i] ?? 0;
        if (roll < 0) return i;
      }
      return weights.length - 1;
    },
  };

  return { rng, state: () => s };
}

export function randomSeed(): number {
  return (Math.random() * 0x100000000) >>> 0;
}
