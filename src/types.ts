/** 全局类型定义。所有规则都围绕这里的结构，界面只管画。 */

/** 六维：操作 / 对线 / 团战 / 意识 / 心态 / 人气（人气也在六维内，共六项）。 */
export type AttrKey = 'operation' | 'laning' | 'teamfight' | 'awareness' | 'mentality' | 'popularity';

export const ATTR_KEYS: readonly AttrKey[] = ['operation', 'laning', 'teamfight', 'awareness', 'mentality', 'popularity'];

/** 除人气之外的五个维度；人气只在场外生效。 */
export type CoreAttr = 'operation' | 'laning' | 'teamfight' | 'awareness' | 'mentality';

/** 会随年龄衰退的四个维度。 */
export type TrainableAttr = 'operation' | 'laning' | 'teamfight' | 'awareness';

/** 进入比赛结算的五个维度。 */
export const MATCH_ATTRS: readonly CoreAttr[] = ['operation', 'laning', 'teamfight', 'awareness', 'mentality'];

/** 衰退期会跌的四个维度；心态与人气不降。 */
export const DECLINE_ATTRS: readonly TrainableAttr[] = ['operation', 'laning', 'teamfight', 'awareness'];

export const ATTR_LABEL: Record<AttrKey, string> = {
  operation: '操作',
  laning: '对线',
  teamfight: '团战',
  awareness: '意识',
  mentality: '心态',
  popularity: '人气',
};

export type Stats = Record<AttrKey, number>;

/** 生涯三段：成长期 1–2 年、巅峰期 3–6 年、衰退期 7–8 年。 */
export type Phase = 'growth' | 'peak' | 'decline';

export const PHASE_LABEL: Record<Phase, string> = {
  growth: '成长期',
  peak: '巅峰期',
  decline: '衰退期',
};

/** 八种行动。 */
export type ActionId = 'rank' | 'train' | 'review' | 'scrim' | 'fitness' | 'stream' | 'business' | 'rest';

export const ACTION_IDS: readonly ActionId[] = [
  'rank',
  'train',
  'review',
  'scrim',
  'fitness',
  'stream',
  'business',
  'rest',
];

export type HonorId =
  | 'lpl-champion'
  | 'msi-champion'
  | 'worlds-champion'
  | 'season-mvp'
  | 'all-pro'
  | 'rookie-of-year'
  | 'hall-of-fame';

export const HONOR_LABEL: Record<HonorId, string> = {
  'lpl-champion': '联赛冠军',
  'msi-champion': 'MSI 冠军',
  'worlds-champion': 'S 赛冠军',
  'season-mvp': '常规赛 MVP',
  'all-pro': '最佳阵容',
  'rookie-of-year': '最佳新秀',
  'hall-of-fame': '名人堂',
};

/** 后果：只能落在状态字段或标记上。 */
export interface Consequence {
  attrs?: Partial<Record<AttrKey, number>>;
  /** 临时加减，只在本场比赛内有效，结周清零，不进存档。 */
  temp?: Partial<Record<AttrKey, number>>;
  stamina?: number;
  maxStamina?: number;
  money?: number;
  injury?: number;
  coachTrust?: number;
  honor?: HonorId;
  flag?: string;
  /** 收到邀请函并接受：直接转成职业选手。 */
  signed?: boolean;
  teamId?: string;
}

export type RiskKind = 'roll' | 'success' | 'fail';

export interface EventOption {
  label: string;
  risk: RiskKind;
  /** 非比赛事件：掷骰时读取的属性；成功率 = 这些属性的平均 / 100。 */
  attrs?: readonly AttrKey[];
  /** 比赛事件：这个选项对胜率的加成（±小数，如 0.3 = +30%）。 */
  bonus?: number;
  /** 命中成功分支的后果；必败选项只写 fail。 */
  success?: Consequence;
  fail?: Consequence;
  /** 成功时的高光文本（「场面」）。 */
  successText?: string;
  /** 失败时的带梗文本。 */
  failText?: string;
  /** 比赛事件专用：这个分支算赢还是输。省略则按成败判定。 */
  matchResult?: 'win' | 'loss';
}

export type EventKind = 'match' | 'life' | 'special';

export interface GameEvent {
  id: string;
  kind: EventKind;
  /** 比赛事件：对手强度。有它就走统一胜负公式。 */
  opponent?: number;
  phase: Phase | 'any';
  /** 写死年份的必触发事件，如第 3 年决赛。 */
  year?: number;
  /** 必触发事件只在指定周出现；省略表示该年任意周。 */
  week?: number;
  tags: string[];
  /** 正文，硬上限 50 字。 */
  text: string;
  options: EventOption[];
  /** true = 抽完即止；false = 可重复进池。 */
  once: boolean;
  /** 进入随机池时的权重：特殊 1，常规 10。 */
  weight: number;
  /** 附加出现条件。 */
  requires?: (s: GameState) => boolean;
  /** 能否作为空池兜底。 */
  filler?: boolean;
  /** 没有写死年份/周次、只靠 requires 触发的必触发事件（如邀请函）。 */
  auto?: boolean;
}

export interface PendingEvent {
  eventId: string;
}

export interface Ending {
  kind: 'normal' | 'special';
  title: string;
  body: string;
  /** 尾注：点出「当年那个选择」。 */
  note: string;
}

export interface LogEntry {
  text: string;
  tone: 'good' | 'bad' | 'plain';
}

export interface SeasonResult {
  week: number;
  rivalId: string;
  won: boolean;
  kind: 'regular' | 'spring' | 'summer';
}

export interface GameState {
  version: number;
  /** 本局种子，用于复现。 */
  seed: number;
  /** 当前随机状态；每次抽随机数后推进。 */
  rngState: number;
  year: number;
  week: number;
  attrs: Stats;
  /** 当前属性累积的经验（未满阈值）。 */
  exp: Stats;
  /** 本年已涨的点数，用来卡年龄涨幅上限。 */
  yearGain: Stats;
  stamina: number;
  maxStamina: number;
  rankPoints: number;
  /** 全服名次（1 起）。由分数与已走周数算出，不手改。 */
  placement: number;
  money: number;
  injury: number;
  coachTrust: number;
  honors: HonorId[];
  flags: string[];
  triggeredEvents: string[];
  signed: boolean;
  /** 玩家自建角色的名字与分路。 */
  playerName: string;
  role: 'TOP' | 'JUNGLE' | 'MID' | 'ADC' | 'SUP';
  /** 签约之后的队伍 id；未签约为 null。 */
  teamId: string | null;
  /** 今年打过的比赛。 */
  seasonResults: SeasonResult[];
  freeAgent: boolean;
  /** 连续无人可签的签约窗口数。 */
  failedWindows: number;
  /** 本周三格：null = 未排。 */
  actionGrid: (ActionId | null)[];
  /** 专项训练指定哪一维（记录在格子上）。 */
  actionTargets: (AttrKey | null)[];
  pendingEvent: PendingEvent | null;
  /** 本周事件是否已结算。 */
  eventDone: boolean;
  /** 临场加减，不进存档。 */
  temp: Partial<Stats>;
  log: LogEntry[];
  ended: Ending | null;
  /** 玩家主动退役。 */
  retired: boolean;
  /** 巅峰年份，用来做批量统计。 */
  peakYear: number;
  /** 巅峰时的六维总和，用于判断巅峰年份。 */
  peakScore: number;
}

export type Action =
  | { kind: 'selectAction'; slot: number; action: ActionId; target?: AttrKey }
  | { kind: 'clearSlot'; slot: number }
  | { kind: 'chooseOption'; option: number }
  | { kind: 'endWeek' }
  | { kind: 'retire' }
  | { kind: 'skipYear' };

export interface ReduceResult {
  state: GameState;
  log: LogEntry[];
}
