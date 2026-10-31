import { CONFIG } from '../config';
import type { GameEvent } from '../types';

/**
 * 事件库第一轮：3 个（P1 表）+ 1 个无条件填充事件。
 * 正文硬上限 50 字；后果只能落在状态字段或标记上。
 */
export const EVENTS: readonly GameEvent[] = [
  {
    id: 'E01',
    kind: 'match',
    phase: 'growth',
    opponent: 60,
    tags: ['#比赛', '#河道', '#大龙', '#下路'],
    text: '你和队友被卡在河道，超级兵正推我方高地。你是 AD，手里还有闪现和大招。',
    once: false,
    weight: 10,
    options: [
      {
        label: '闪现进场开大',
        risk: 'roll',
        bonus: 0.15,
        success: {
          attrs: { mentality: 3 },
        },
        successText: '五个人的位置，正好是你想要的。',
        fail: {
          attrs: { mentality: -3 },
          coachTrust: -5,
        },
        failText: '你进场了，但队友没跟上。高地丢了。',
      },
      {
        label: '拉扯等超级兵回推',
        risk: 'roll',
        bonus: 0.05,
        success: {
          attrs: { awareness: 2 },
        },
        successText: '你们把时间拖回了自己这边。',
        fail: {
          attrs: { popularity: -2 },
        },
        failText: '你被抓单了，弹幕开始刷「就这」。',
      },
      {
        label: '回守高地',
        risk: 'roll',
        bonus: -0.15,
        success: {
          attrs: { popularity: -1 },
        },
        successText: '高地守住了，但这局已经没了。',
        fail: {
          attrs: { popularity: -3 },
          coachTrust: -3,
        },
        failText: '你回去了，可正面已经崩了。',
      },
    ],
  },
  {
    id: 'E02',
    kind: 'life',
    phase: 'growth',
    tags: ['#直播', '#弹幕', '#路人期'],
    text: '正在服务器大杀四方的你，看见弹幕飘过一句「不去打职业扬名立万，窝在这里当个小主播」。',
    once: true,
    weight: 10,
    requires: (s) => !s.signed,
    options: [
      {
        label: '去试训',
        risk: 'roll',
        attrs: ['laning', 'popularity'],
        success: {
          attrs: { mentality: 3 },
          flag: '试训通过',
        },
        successText: '第三局你 3-0，对方教练合上本子，「什么时候能来？」',
        fail: {
          attrs: { mentality: -4 },
        },
        failText: '你打出了两波节奏，但手已经不听使唤了。',
      },
      {
        label: '回怼弹幕',
        risk: 'fail',
        fail: {
          attrs: { laning: -2, teamfight: -2 },
          flag: '嘴碎',
        },
        failText: '你回了两句，第二天剪辑就上了热门。',
      },
      {
        label: '继续播',
        risk: 'success',
        success: {
          attrs: { mentality: 2 },
          flag: '想得开',
        },
        successText: '你把心态放得很好：水到渠成，急不得。',
      },
    ],
  },
  {
    id: 'E03',
    kind: 'special',
    phase: 'peak',
    year: CONFIG.career.finalYear,
    week: CONFIG.career.finalWeek,
    opponent: CONFIG.match.opponentFinal,
    tags: ['#S赛', '#决赛', '#特殊', '#请神'],
    text: '第 3 年，决赛。这一场决定你以后的历史地位。',
    once: true,
    weight: 1,
    options: [
      {
        label: '闭上双眼请神',
        risk: 'roll',
        bonus: 0.25,
        success: {
          attrs: { mentality: 3 },
          flag: '请神',
        },
        successText: '请神成功，你化身神秘瓜皮头男。',
        fail: {
          attrs: { mentality: -4 },
        },
        failText: '你睁开眼，屏幕已经灰了。',
      },
      {
        label: '不想这些，专注游戏',
        risk: 'roll',
        bonus: 0.0,
        successText: '你把耳机音量调大了一格，世界安静了。',
      },
      {
        label: '向队友说些话',
        risk: 'roll',
        bonus: 0.05,
        success: {
          attrs: { mentality: 2 },
        },
        fail: {
          attrs: { mentality: -2 },
        },
        successText: '你说「打完这把去吃火锅」，语音里有人笑出了声。',
      },
    ],
  },
  {
    id: 'E04',
    kind: 'life',
    phase: 'any',
    tags: ['#队内', '#矛盾', '#特殊'],
    text: '训练室里，中单把耳机摔了。他说你昨天那句「下路自己打」，全队都听见了。',
    once: true,
    weight: 1,
    options: [
      {
        label: '道歉',
        risk: 'success',
        success: {
          coachTrust: 4,
          attrs: { mentality: 2 },
          flag: '道过歉',
        },
        successText: '你把话收回去，训练室安静下来。',
      },
      {
        label: '怼回去',
        risk: 'fail',
        fail: {
          coachTrust: -8,
          attrs: { mentality: -2 },
        },
        failText: '你们打了一架，第二天上了热搜。',
      },
      {
        label: '不说话',
        risk: 'success',
        success: {
          attrs: { mentality: -1 },
        },
        successText: '你没说话，他也没再说。',
      },
    ],
  },
];

/** 无条件填充池：连常规事件都抽不到时兜底，各用一次。 */
export const FILLER_EVENTS: readonly GameEvent[] = [
  {
    id: 'F01',
    kind: 'life',
    phase: 'any',
    tags: ['#训练', '#深夜'],
    text: '凌晨四点，训练室只剩你一个人。屏幕上还是那波没打好的团。',
    once: true,
    weight: 10,
    filler: true,
    options: [
      {
        label: '再打一把',
        risk: 'success',
        success: { attrs: { mentality: 1 } },
        successText: '你赢了一把，然后天亮了。',
      },
      {
        label: '回去睡觉',
        risk: 'success',
        success: { stamina: 8 },
        successText: '你睡了个好觉，梦里还在补刀。',
      },
    ],
  },
  {
    id: 'F02',
    kind: 'life',
    phase: 'any',
    tags: ['#采访', '#嘴'],
    text: '赛后采访，记者问你：「今天下路被压成这样，你怎么看？」',
    once: true,
    weight: 10,
    filler: true,
    options: [
      {
        label: '实话实说',
        risk: 'success',
        success: { attrs: { mentality: 2 } },
        successText: '你说「我打得不好」，评论区反而安静了。',
      },
      {
        label: '甩锅打野',
        risk: 'fail',
        fail: { attrs: { popularity: -3 }, coachTrust: -3 },
        failText: '这句话第二天挂在了所有平台的首页。',
      },
    ],
  },
];

export function findEvent(id: string): GameEvent | undefined {
  return [...EVENTS, ...FILLER_EVENTS].find((e) => e.id === id);
}
