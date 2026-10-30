import { CONFIG } from '../config';
import type { GameState } from '../types';

export interface SaveEnvelope {
  version: number;
  state: GameState;
}

/** 临场状态不进存档。 */
export function toSaveJson(state: GameState): string {
  const copy: GameState = { ...state, temp: {} };
  return JSON.stringify({ version: CONFIG.version, state: copy });
}

/** 版本不符或损坏时返回 null，调用方安全重开。 */
export function fromSaveJson(raw: string | null): GameState | null {
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as SaveEnvelope;
    if (!parsed || parsed.version !== CONFIG.version) return null;
    const state = parsed.state;
    if (!state || typeof state.year !== 'number' || !state.attrs) return null;
    state.temp = {};
    return state;
  } catch {
    return null;
  }
}

const STORAGE_KEY = `${CONFIG.storageKey}:v${CONFIG.version}`;

export function loadSaved(): GameState | null {
  try {
    return fromSaveJson(globalThis.localStorage?.getItem(STORAGE_KEY) ?? null);
  } catch {
    return null;
  }
}

export function persist(state: GameState): void {
  try {
    globalThis.localStorage?.setItem(STORAGE_KEY, toSaveJson(state));
  } catch {
    // 隐私模式下写不进去，不影响玩。
  }
}

export function clearSaved(): void {
  try {
    globalThis.localStorage?.removeItem(STORAGE_KEY);
  } catch {
    // 忽略。
  }
}
