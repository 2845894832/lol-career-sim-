import type { GameEvent, GameState } from '../types';

/**
 * 春决 / 夏决：每年写死的两场决赛。
 *
 * 为什么不写进 EVENTS 常量里：决赛每年都要打一次，而 triggeredEvents 是整局去重，
 * 静态事件只会触发一次。这里按年份生成 id（SPR-1、SPR-2…），去重就自然按年生效。
 *
 * 周次：春 1–8、MSI 9–12、夏 13–20、S 赛 21–26、休赛 27–30。
 * 只有签约之后（职业选手）才打联赛。
 */

const SPRING_WEEK = 8;
const SUMMER_WEEK = 20;

export function springFinal(year: number): GameEvent {
  return {
    id: `SPR-${year}`,
    kind: 'match',
    phase: 'any',
    year,
    week: SPRING_WEEK,
    opponent: 65,
    tags: ['#春决', '#联赛', '#决赛'],
    text: '春季赛决赛。对面是常规赛第一，你们输过一次。BP 还没开始，场馆已经满了。',
    once: true,
    weight: 1,
    requires: (s) => s.signed,
    options: [
      {
        label: '让中单先拿绝活',
        risk: 'roll',
        bonus: 0.15,
        success: { honor: 'lpl-champion', attrs: { mentality: 3, popularity: 4 } },
        successText: '对面三 ban 中单，你的绝活放出来了。团战第一秒你就知道能赢。',
        fail: { attrs: { mentality: -4, popularity: -2 } },
        failText: '绝活被针对了。你在水晶爆炸前就摘了耳机。',
      },
      {
        label: '抢版本最强阵容',
        risk: 'roll',
        bonus: 0.3,
        success: { honor: 'lpl-champion', attrs: { popularity: 5 } },
        successText: '版本答案就是版本答案。三局两胜，第三局二十三分钟结束。',
        fail: { attrs: { mentality: -3 } },
        failText: '对面用你最熟的阵容赢了你。',
      },
      {
        label: '打自己这套',
        risk: 'roll',
        bonus: 0.0,
        success: { honor: 'lpl-champion', attrs: { teamfight: 2, popularity: 3 } },
        successText: '你们打了一整年的东西，今天终于对上了。',
        fail: { attrs: { mentality: -2, teamfight: 1 } },
        failText: '差一点。你在回来的车上把这场看了三遍。',
      },
    ],
  };
}

export function summerFinal(year: number): GameEvent {
  return {
    id: `SUM-${year}`,
    kind: 'match',
    phase: 'any',
    year,
    week: SUMMER_WEEK,
    opponent: 70,
    tags: ['#夏决', '#联赛', '#决赛'],
    text: '夏季赛决赛，赢了就是一号种子。有人在你耳边说「打完这局就放假」。',
    once: true,
    weight: 1,
    requires: (s) => s.signed,
    options: [
      {
        label: '第一局就压死对面',
        risk: 'roll',
        bonus: 0.25,
        success: { honor: 'lpl-champion', attrs: { popularity: 5, mentality: 2 } },
        successText: '三比零。你举起奖杯的时候，弹幕全是那个你听了八年的名字。',
        fail: { attrs: { mentality: -4 } },
        failText: '你赌早了。对面缓过来之后连下三局。',
      },
      {
        label: '稳着打，后手赢',
        risk: 'roll',
        bonus: 0.1,
        success: { honor: 'lpl-champion', attrs: { awareness: 2, popularity: 3 } },
        successText: '决胜局你叫停了两次，两次都改对了。',
        fail: { attrs: { mentality: -3, awareness: 1 } },
        failText: '你稳过头了，对面先动手。',
      },
      {
        label: '放开了打',
        risk: 'roll',
        bonus: 0.2,
        success: { honor: 'lpl-champion', attrs: { operation: 2, popularity: 4 } },
        successText: '那一波你自己都觉得离谱，但它成了。',
        fail: { attrs: { mentality: -2, popularity: -2 } },
        failText: '你打出了最漂亮的一波，也输掉了最后一波。',
      },
    ],
  };
}

/** 本周是不是决赛周，是就返回那场。 */
export function finalFor(state: GameState): GameEvent | null {
  if (state.week === SPRING_WEEK) return springFinal(state.year);
  if (state.week === SUMMER_WEEK) return summerFinal(state.year);
  return null;
}

/** 从 id 还原（SPR-3 = 第 3 年春决）。结算事件时用。 */
export function finalById(id: string): GameEvent | null {
  const m = /^(SPR|SUM)-(\d+)$/.exec(id);
  if (!m) return null;
  const year = Number(m[2]);
  return m[1] === 'SPR' ? springFinal(year) : summerFinal(year);
}
