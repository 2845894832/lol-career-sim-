import { ATTR_KEYS, ATTR_LABEL, HONOR_LABEL, type Ending, type GameState } from '../types';
import { ageOf, rankTier } from './state';

export type EndReason = 'expired' | 'retired' | 'no-team';

/** 标记 → 尾注。尾注必须点出「当年那个选择」。 */
const MARK_NOTES: Record<string, string> = {
  试训通过: '当年那条弹幕飘过去，你选了去试训。',
  请神: '第 3 年决赛前，你闭上了眼睛——那一下，值不值，只有你知道。',
};

function bestAndWorst(state: GameState): { best: string; worst: string } {
  const sorted = [...ATTR_KEYS].sort((a, b) => state.attrs[b] - state.attrs[a]);
  const best = sorted[0] ?? 'operation';
  const worst = sorted[sorted.length - 1] ?? 'operation';
  return { best: ATTR_LABEL[best], worst: ATTR_LABEL[worst] };
}

function honorLine(state: GameState): string {
  if (state.honors.length === 0) return '你的荣誉柜是空的。';
  return `荣誉：${state.honors.map((h) => HONOR_LABEL[h]).join('、')}。`;
}

function noteFor(state: GameState): string {
  const marks = state.flags.filter((f) => MARK_NOTES[f]);
  const first = marks[0];
  if (first) return MARK_NOTES[first] ?? '';
  return '没有哪个选择特别响，但它们都算数。';
}

export function normalEnding(state: GameState, reason: EndReason): Ending {
  const { best, worst } = bestAndWorst(state);
  const tier = rankTier(state.rankPoints).name;
  const age = ageOf(state);

  const title = reason === 'retired' ? `第 ${state.year} 年，你主动退役了` : '八年，结束了';
  const body = [
    `你 18 岁进这行，${age} 岁离开，最后停在${tier}。`,
    `六维里最强的是${best}，最弱的是${worst}。`,
    honorLine(state),
  ].join(' ');

  return { kind: 'normal', title, body, note: noteFor(state) };
}

export function specialEnding(state: GameState): Ending {
  const { best } = bestAndWorst(state);
  return {
    kind: 'special',
    title: '无人可签',
    body: [
      `连续两个签约窗口，没有一支队伍回你消息。`,
      `你最强的是${best}，但这行不看这个。`,
      honorLine(state),
    ].join(' '),
    note: noteFor(state),
  };
}
