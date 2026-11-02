import { CONFIG } from '../config';
import { ATTR_KEYS, ATTR_LABEL, HONOR_LABEL, type Ending, type GameState } from '../types';
import { ageOf, rankTier } from './state';

export type EndReason = 'expired' | 'retired';

/** 标记 → 尾注。尾注必须点出「当年那个选择」。 */
const MARK_NOTES: Record<string, string> = {
  试训通过: '当年那条弹幕飘过去，你选了去试训。',
  嘴碎: '当年你回怼了那条弹幕，之后每一年都在还。',
  想得开: '当年你选择继续播，没把那条弹幕当回事。',
  请神: '第 3 年决赛前，你闭上了眼睛——那一下值不值，只有你知道。',
  道过歉: '那年训练室里你低了头，队伍没散。',
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
  // 取最后一个能对上模板的标记：越晚发生，越接近「这一局的我」。
  const marks = state.flags.filter((f) => MARK_NOTES[f]);
  const last = marks[marks.length - 1];
  if (last) return MARK_NOTES[last] ?? '';
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

/**
 * 切片版收尾：不是结局，是「到此为止」。
 * 说清三件事——你打到了哪、这一周发生了什么、完整版还差什么。
 */
export function sliceEnding(state: GameState): Ending {
  const { best } = bestAndWorst(state);
  const tier = rankTier(state.rankPoints).name;
  const startTier = rankTier(CONFIG.start.rankPoints).name;
  const wonSpring = state.honors.includes('lpl-champion');
  const spring = wonSpring ? '春决你赢了，奖杯现在还在休息室的柜子里。' : '春决你输了，场馆灯灭得比想象中快。';

  const title = '切片到此为止';
  const body = [
    `这 ${CONFIG.career.sliceAtWeek} 周，你从${startTier}打到${tier}，现在第 ${state.placement} 名。六维最强的是${best}。`,
    spring,
    '完整版是八年：春决之后还有 MSI、夏季赛、世界赛，和七次同样的春天。',
  ].join('');

  return {
    kind: 'normal',
    title,
    body,
    note: '这一页不是结局，是这道菜的试吃装——好吃不好吃，你说。',
  };
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
