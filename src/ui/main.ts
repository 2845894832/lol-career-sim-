import './style.css';
import { reduce } from '../core/reduce';
import { getEvent, matchOptionRate, successRateOf } from '../core/events';
import { ACTION_INFO, canAfford, isActionUnlocked, staminaCost } from '../core/actions';
import { loadSaved, persist } from '../core/save';
import { ageOf, isMatchWeek, newGame, phaseOfYear } from '../core/state';
import { rankOf } from '../core/ladder';
import { myPlace, myOvr, mySquad, nextFixture, startRequirement, upcomingFixtures, standings, isStarting } from '../core/league';
import {
  SHOP,
  buy,
  buyBlocker,
  hasOnce,
  subActive,
  subUntil,
} from '../core/shop';
import { randomSeed } from '../rng';
import { rosterOf } from '../data/rosters';
import { mountShow } from './show';
import {
  ACTION_IDS,
  ATTR_KEYS,
  ATTR_LABEL,
  HONOR_LABEL,
  PHASE_LABEL,
  type Action,
  type ActionId,
  type AttrKey,
  type GameState,
  type LogEntry,
} from '../types';

const root = document.querySelector<HTMLDivElement>('#app');
if (!root) throw new Error('#app 不存在');
const app = root;

type Sheet = { kind: 'actions'; slot: number } | { kind: 'targets'; slot: number };

type RoleId = GameState['role'];

const ROLES: { id: RoleId; label: string; note: string }[] = [
  { id: 'TOP', label: '上单', note: '一条线，抗压' },
  { id: 'JUNGLE', label: '打野', note: '满地图跑' },
  { id: 'MID', label: '中单', note: '中线，最容易被打野抓' },
  { id: 'ADC', label: '射手', note: '要靠人保' },
  { id: 'SUP', label: '辅助', note: '不补刀，给视野' },
];

let state: GameState = loadSaved() ?? newGame(randomSeed());



// 调试用：?dev=signed 直接在签约状态下开局，方便看赛程屏。正式流程不会走到这里。
const devMode = new URLSearchParams(location.search).get('dev');
if (devMode === 'signed' || devMode === 'bench') {
  state = newGame(randomSeed());
  state.signed = true;
  state.teamId = 'RNG';
  state.coachTrust = devMode === 'bench' ? 55 : 100;
  // signed 调试档要真的能首发（信任 > 60、对位差 ≤ 10），否则看不到比赛流程。
  if (devMode === 'signed') {
    state.attrs.operation = 85;
    state.attrs.laning = 85;
    state.attrs.teamfight = 85;
    state.attrs.awareness = 85;
    state.attrs.mentality = 85;
  }
  state.week = 13;
  state.seasonResults = [
    { week: 2, rivalId: 'WE', won: true, kind: 'regular' },
    { week: 4, rivalId: 'IG', won: true, kind: 'regular' },
    { week: 6, rivalId: 'BLG', won: false, kind: 'regular' },
    { week: 8, rivalId: 'EDG', won: true, kind: 'regular' },
    { week: 10, rivalId: 'SS', won: true, kind: 'regular' },
    { week: 12, rivalId: 'JDG', won: false, kind: 'regular' },
  ];
}
let sheet: Sheet | null = null;
let outcome: LogEntry[] | null = null;
/** 底部页签：本周 / 赛程。 */
let tab: 'week' | 'schedule' | 'career' | 'money' = 'week';

/** 比赛演出只挂一次：key 不变就不重建，免得每次 render 都从头播。 */
let showKey = '';
let showDestroy: (() => void) | null = null;
/** 比赛事件选项的结果，演出开头飘一下。 */
let matchNote: LogEntry[] | null = null;

const esc = (s: string): string =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

const slotLabel = (slot: number): string => `行动 ${slot + 1}`;

/** 开局屏：还没开始生涯时先在这里摇人。 */
const starter = {
  open: !loadSaved(),
  role: null as RoleId | null,
  name: '',
  attrs: rollAttrs(),
};

function rollAttrs(): Record<string, number> {
  const out: Record<string, number> = {};
  for (const key of ATTR_KEYS) {
    if (key === 'popularity') {
      out[key] = 20;
      continue;
    }
    out[key] = 40 + Math.floor(Math.random() * 31); // 40–70
  }
  return out;
}

function renderStarter(): void {
  const roleBtns = ROLES.map(
    (r) => `<button class="role${starter.role === r.id ? ' on' : ''}" data-act="role" data-role="${r.id}">
      <b>${r.label}</b><span>${r.note}</span></button>`,
  ).join('');

  const attrRows = ATTR_KEYS.map((key) => {
    const v = starter.attrs[key] ?? 0;
    const muted = key === 'popularity' ? ' muted' : '';
    const note = key === 'popularity' ? '<span class="cap">不摇，靠打出来</span>' : '';
    return `<li class="roll-row${muted}">
      <span class="nm">${ATTR_LABEL[key]}</span>
      <span class="val">${v}</span>
      <span class="bar"><i style="width:${v}%"></i></span>${note}
    </li>`;
  }).join('');

  const nameLen = [...starter.name].length;
  const canStart = Boolean(starter.role) && nameLen >= 2 && nameLen <= 8;

  app.innerHTML = `<div class="starter">
    <h1 class="s-title">开始生涯</h1>
    <div class="cap">一共三步：选分路、摇数值、取名字。</div>

    <div class="s-block">
      <div class="s-cap">1 · 你打哪个位置</div>
      <div class="roles">${roleBtns}</div>
    </div>

    <div class="s-block">
      <div class="s-cap">2 · 你的数值</div>
      <ul class="rolls">${attrRows}</ul>
      <button class="btn" data-act="reroll">重摇一次</button>
      <div class="cap">五项 40–70 随机；不满意就再摇，不限次数。</div>
    </div>

    <div class="s-block">
      <div class="s-cap">3 · 你叫什么</div>
      <input class="name-input" id="nameInput" maxlength="8" placeholder="2–8 个字，不能留空" value="${esc(starter.name)}" />
      <div class="cap">${nameLen}/8</div>
    </div>

    <button class="btn primary start${canStart ? '' : ' disabled'}" data-act="start"${canStart ? '' : ' disabled'}>
      开始生涯
    </button>
    <div class="cap s-note">${canStart ? '' : '选一个分路、填上名字才能开始。'}</div>
  </div>`;
}

function renderTopbar(): string {
  const phase = phaseOfYear(state.year);
  const tag = state.signed ? '已签约' : state.freeAgent ? '自由人' : '路人期';
  return `<div class="topbar">
    <div>
      <div class="title">第 ${state.year} 年 · 第 ${state.week} 周</div>
      <div class="sub">${PHASE_LABEL[phase]} · ${ageOf(state)} 岁 · ${tag}</div>
    </div>
    <div class="sub">${isMatchWeek(state.week) ? '比赛周' : '休赛期'}</div>
  </div>`;
}

function renderAttrs(): string {
  const cells = ATTR_KEYS.map((key) => {
    // 条形 = 属性值 / 100（0–100 满分），不是经验进度：玩家看的是“我有多强”
    const pct = Math.max(0, Math.min(100, Math.round(state.attrs[key])));
    return `<div class="attr">
      <div class="row"><span class="name">${ATTR_LABEL[key]}</span><span class="val">${state.attrs[key]}</span></div>
      <div class="bar"><i style="width:${pct}%"></i></div>
    </div>`;
  }).join('');
  return `<div class="panel"><div class="attrs">${cells}</div></div>`;
}

function renderMeta(): string {
  const staminaPct = Math.round((state.stamina / state.maxStamina) * 100);
  return `<div class="panel">
    <div class="meta">
      <span class="grp"><span>段位 <b>${rankOf(state.rankPoints, state.placement).name}</b> <span class="mini">第 ${state.placement} 名</span></span></span>
      <span class="grp"><span>教练信任 <b>${state.coachTrust}</b></span><span>伤病 <b>${state.injury}/3</b></span></span>
      <span class="grp"><span>体力 <b>${state.stamina}/${state.maxStamina}</b></span></span>
      <span class="grp"><span>金钱 <b>${state.money}</b></span></span>
    </div>
    <div class="bar" style="margin-top:8px"><i style="width:${staminaPct}%"></i></div>
  </div>`;
}

function renderSlots(): string {
  const cells = state.actionGrid
    .map((id, slot) => {
      const label = id ? ACTION_INFO[id].label : '空';
      const target = state.actionTargets[slot];
      const extra = id === 'train' && target ? ATTR_LABEL[target] : id ? `${staminaCost(state, id, target)} 体力` : '点一下安排';
      return `<button class="slot ${id ? 'filled' : ''}" data-act="slot" data-slot="${slot}">
        <span class="k">${slotLabel(slot)}</span>
        <span class="v">${label}</span>
        <span class="t">${extra}</span>
      </button>`;
    })
    .join('');
  return `<div class="panel"><div class="slots">${cells}</div></div>`;
}

/**
 * 结周为什么点不了：一句里要有「为什么」和「怎么做」。
 * 体力不够是另一种处境——说成「点上面补上」会误导。
 */
function blockedWhy(empty: number): string {
  if (state.pendingEvent) return '这个事件还没选完，先在上面选一个';
  if (state.pendingMatch) return '这周的比赛还没打完，先把比赛走完';
  const slot = state.actionGrid.indexOf(null);
  const canDoSomething = ACTION_IDS.some(
    (id) => id !== 'rest' && isActionUnlocked(state, id) && canAfford(state, slot, id),
  );
  if (!canDoSomething) return `还剩 ${empty} 格，但体力只够排休息`;
  return `还差 ${empty} 格没排，点上面补上`;
}

function renderControls(): string {
  const empty = state.actionGrid.filter((id) => id === null).length;
  const incomplete = empty > 0;
  const blocked = state.pendingEvent || incomplete ? 'disabled' : '';
  return `<div class="panel" style="display:flex;flex-direction:column;gap:8px">
    <button class="btn primary" data-act="end-week" ${blocked}>
      <span>结周</span><span class="hint">${blocked ? '' : '结算三个行动并推进'}</span>
    </button>
    ${blocked ? `<p class="why">${blockedWhy(empty)}</p>` : ''}
    <button class="btn" data-act="retire"><span>退役</span><span class="hint">立刻看结局</span></button>
    <button class="btn" data-act="skip-year"><span>跳到下一年</span><span class="hint">调试用</span></button>
  </div>`;
}

function renderLog(): string {
  const lines = state.log.slice(-6);
  const mark = { good: '＋', bad: '－', plain: '' } as const;
  return `<div class="panel"><div class="log">${lines
    .map((e) => `<div class="${e.tone}">${mark[e.tone]}${mark[e.tone] ? ' ' : ''}${esc(e.text)}</div>`)
    .join('')}</div></div>`;
}

function renderSheet(): string {
  if (!sheet) return '';
  if (sheet.kind === 'actions') {
    const rows = ACTION_IDS.map((id) => {
      const unlocked = isActionUnlocked(state, id);
      const afford = canAfford(state, sheet!.slot, id);
      const disabled = !unlocked || !afford;
      // 体力一律放右边、右对齐、等宽数字；描述降一行说「换来什么」
      const pts = staminaCost(state, id, null);
      const at = id === 'train' ? ' 起' : '';
      const cost =
        unlocked && pts > 0
          ? `<b class="opt-num">${pts}</b><span class="opt-unit">体力${at}</span>`
          : '';
      const sub = !unlocked
        ? '签约后解锁'
        : !afford
          ? '体力不够，这周排不上'
          : ACTION_INFO[id].hint;
      return `<button class="btn opt" data-act="pick-action" data-id="${id}" ${disabled ? 'disabled' : ''}>
        <span class="opt-top"><span class="opt-name">${ACTION_INFO[id].label}</span><span class="opt-cost">${cost}</span></span>
        <span class="opt-sub">${sub}</span>
      </button>`;
    }).join('');
    const filled = state.actionGrid[sheet.slot] !== null;
    const clearRow = filled
      ? `<button class="btn" data-act="clear-slot"><span>清空这一格</span><span class="hint">恢复成空，重新排</span></button>`
      : '';
    return `<div class="overlay" data-act="close-sheet"><div class="sheet" data-kind="pick" data-stop="1">
      <h2>${slotLabel(sheet.slot)}排什么</h2>
      <div class="options">${rows}${clearRow}</div>
    </div></div>`;
  }

  const rows = ATTR_KEYS.filter((key) => key !== 'popularity')
    .map((key) => {
      const price = staminaCost(state, 'train', key);
      const afford = canAfford(state, sheet!.slot, 'train');
      return `<button class="btn" data-act="pick-target" data-key="${key}" ${afford ? '' : 'disabled'}>
        <span>${ATTR_LABEL[key]}</span>
        <span class="hint">现在 ${state.attrs[key]} · ${price} 体力</span>
      </button>`;
    })
    .join('');
  return `<div class="overlay" data-act="close-sheet"><div class="sheet" data-kind="pick" data-stop="1">
    <h2>专项训练练哪一项</h2>
    <div class="options">${rows}</div>
  </div></div>`;
}

function renderEvent(): string {
  if (!state.pendingEvent) return '';
  const event = getEvent(state.pendingEvent.eventId);
  if (!event) return '';
  const rows = event.options
    .map((option, i) => {
      // 只有掷骰的选项才写概率；必成/必败不写出来（右列只放数字，才能竖着扫）
      const rate =
        option.risk === 'roll'
          ? `${Math.round(successRateOf(state, event, option) * 100)}%`
          : '';
      return `<button class="btn" data-act="choose" data-i="${i}">
        <span>${esc(option.label)}</span><span class="rate">${rate}</span>
      </button>`;
    })
    .join('');
  return `<div class="overlay"><div class="sheet" data-kind="result">
    <h2>本周事件</h2>
    <p class="event-text">${esc(event.text)}</p>
    <div class="options">${rows}</div>
  </div></div>`;
}

/** 我的队名（签约后用队名，没签约写「我的队」）。 */
function myTeamName(): string {
  const team = state.teamId ? rosterOf(state.year).find((t) => t.id === state.teamId) : undefined;
  return team?.name ?? '我的队';
}

/** 开赛卡 / 比赛事件卡：演出之前的两步。 */
function renderMatch(): string {
  const pm = state.pendingMatch;
  if (!pm) return '';
  if (pm.phase === 'kickoff') {
    return `<div class="overlay"><div class="sheet" data-kind="result">
      <h2>开赛</h2>
      <p class="event-text">${esc(myTeamName())} vs ${esc(pm.rivalName)}</p>
      <div class="cap">bo${pm.bestOf} · 每局 30 秒，可随时跳过本局</div>
      <div style="height:12px"></div>
      <div class="options"><button class="btn primary" data-act="kickoff">开赛</button></div>
    </div></div>`;
  }
  if (pm.phase === 'event' && pm.eventId) {
    const event = getEvent(pm.eventId);
    if (!event) return '';
    const rows = event.options
      .map((option, i) => {
        const rate = option.risk === 'roll' ? `${Math.round(matchOptionRate(state, option) * 100)}%` : '';
        return `<button class="btn" data-act="match-choose" data-i="${i}">
          <span>${esc(option.label)}</span><span class="rate">${rate}</span>
        </button>`;
      })
      .join('');
    return `<div class="overlay"><div class="sheet" data-kind="result">
      <h2>赛前 · 比赛事件</h2>
      <p class="event-text">${esc(event.text)}</p>
      <div class="options">${rows}</div>
      <div class="cap" style="margin-top:8px">这一次只决定心态/信任等后果；成了才把加成带进比赛。</div>
    </div></div>`;
  }
  return '';
}

/** 演出层：canvas 由 show.ts 挂进去。 */
function renderShow(): string {
  if (state.pendingMatch?.phase !== 'show') return '';
  const note = matchNote?.length
    ? `<div class="show-note">${matchNote.map((e) => esc(e.text)).join(' · ')}</div>`
    : '';
  return `<div class="show-overlay"><div id="show-host"></div>${note}</div>`;
}

function renderOutcome(): string {
  if (!outcome) return '';
  const rows = outcome
    .map((e) => `<div class="${e.tone}">${esc(e.text)}</div>`)
    .join('');
  return `<div class="overlay"><div class="sheet" data-kind="result">
    <h2>结果</h2>
    <div class="log">${rows}</div>
    <div style="height:12px"></div>
    <button class="btn primary" data-act="continue">继续</button>
  </div></div>`;
}

function renderEnding(): string {
  const ending = state.ended;
  if (!ending) return '';
  return `<div class="panel ending">
    <h2>${esc(ending.title)}</h2>
    <p>${esc(ending.body)}</p>
    <p class="note">${esc(ending.note)}</p>
    <div style="height:12px"></div>
    <button class="btn primary" data-act="restart">再来一局</button>
  </div>`;
}

function renderTabs(): string {
  const item = (id: 'week' | 'schedule' | 'career' | 'money', label: string) =>
    `<button class="tab${tab === id ? ' on' : ''}" data-act="tab" data-tab="${id}">${label}</button>`;
  return `<nav class="tabs">${item('week', '本周')}${item('schedule', '赛程')}${item('career', '生涯')}${item('money', '收支')}</nav>`;
}

/** 生涯屏：上面是六维（含人气），下面是荣誉。 */
function renderCareer(): string {
  const rows = ATTR_KEYS.map((key) => {
    const v = state.attrs[key];
    return `<li class="squad-row">
        <span class="pos">${ATTR_LABEL[key]}</span>
        <span class="nm"></span>
        <span class="ovr">${v}</span>
        <span class="bar"><i style="width:${v}%"></i></span>
      </li>`;
  }).join('');

  const byYear = new Map<number, string[]>();
  for (const h of state.honors) {
    const list = byYear.get(h.year) ?? [];
    const label = HONOR_LABEL[h.id];
    const at = list.indexOf(label);
    if (at >= 0) {
      const cur = list[at] ?? '';
      const m = cur.match(/×(\d+)$/);
      list[at] = m ? cur.replace(/×\d+$/, `×${Number(m[1]) + 1}`) : `${cur} ×2`;
    } else {
      list.push(label);
    }
    byYear.set(h.year, list);
  }
  const years = [...byYear.keys()].sort((a, b) => a - b);
  const honorBlock = years.length
    ? years
        .map(
          (y) => `<div class="honor-year">
        <div class="cap">第 ${y} 年</div>
        <ul class="honors">${byYear.get(y)!.map((t) => `<li>${t}</li>`).join('')}</ul>
      </div>`,
        )
        .join('')
    : '<div class="sub">荣誉柜是空的。打完一个赛季再看。</div>';

  return `<div class="panel">
      <div class="cap">能力</div>
      <ul class="squad">${rows}</ul>
    </div>
    <div class="panel">
      <div class="cap">荣誉</div>
      ${honorBlock}
    </div>`;
}

/** 收支屏：上面本周流水（为空时显示上周），下面是商店。 */
function renderMoney(): string {
  const useLast = state.ledger.length === 0 && state.lastLedger.length > 0;
  const entries = useLast ? state.lastLedger : state.ledger;
  const rows = entries
    .map((e) => {
      const sign = e.amount > 0 ? '+' : '−';
      const cls = e.amount > 0 ? 'in' : 'out';
      return `<li class="ledger-row"><span class="lb">${esc(e.label)}</span>
        <span class="amt ${cls}">${sign}${Math.abs(e.amount)}</span></li>`;
    })
    .join('');
  const income = entries.filter((e) => e.amount > 0).reduce((a, b) => a + b.amount, 0);
  const spent = entries.filter((e) => e.amount < 0).reduce((a, b) => a + b.amount, 0);
  const list = rows || '<li class="ledger-row"><span class="lb">还没有任何进出账</span><span class="amt"></span></li>';

  const cart = SHOP.map((item) => {
    const blocked = buyBlocker(state, item);
    const owned =
      item.shape === 'once' && hasOnce(state, item.id)
        ? '已拥有'
        : item.shape === 'year' && subActive(state, item.id)
          ? `买到第 ${subUntil(state, item.id)} 年`
          : '';
    const right = owned
      ? `<span class="mini owned">${owned}</span>`
      : `<button class="btn buy" data-act="buy" data-id="${item.id}"${blocked ? ' disabled' : ''}>买 · ${item.price}</button>`;
    const note = blocked && !owned ? `<span class="mini why">${esc(blocked)}</span>` : '';
    return `<li class="shop-row">
        <span class="nm">${item.label}<span class="mini">${esc(item.effect)}</span>${note}</span>
        ${right}
      </li>`;
  }).join('');

  return `
    <section class="panel">
      <div class="cap">${useLast ? '上周收支' : '本周收支'}</div>
      <ul class="ledger">${list}</ul>
      <div class="totals"><span>收入 ${income}</span><span>支出 ${Math.abs(spent)}</span>
        <b>余额 ${state.money}</b></div>
    </section>
    <section class="panel">
      <div class="cap">商店</div>
      <ul class="shop">${cart}</ul>
      <div class="cap" style="margin-top:10px">年费一次付清，管到明年底；买断的永久有效。</div>
    </section>`;
}

function renderSchedule(): string {
  if (!state.signed) {
    return `<div class="panel"><div class="sub">还没签约，没有赛程。上王者之后会收到邀请。</div></div>`;
  }
  const rows = standings(state);
  const place = myPlace(state);
  const me = rows.find((r) => r.isMe);
  const next = nextFixture(state);
  const upcoming = upcomingFixtures(state, 4);

  const rankLine = `<div class="rank-big"><b>第 ${place} 名</b><span class="mini">/ ${rows.length} 支</span>
    <span class="rec">${me?.wins ?? 0} 胜 ${me?.losses ?? 0} 负</span></div>`;

  const nextLine = next
    ? `<div class="next"><span>下一场</span><b>${esc(next.rivalName)}</b><span class="mini">第 ${next.week} 周</span></div>`
    : '<div class="next"><span>本季常规赛打完了</span></div>';

  const list = upcoming
    .map((f) => `<li><span class="w">W${f.week}</span><span class="t">${esc(f.rivalName)}</span></li>`)
    .join('');

  const squadRows = mySquad(state);
  const benched = state.signed && !isStarting(state);
  const squad = squadRows
    .map((p) => {
      const meRow = p.me ? ' me' : '';
      const sub = p.me && !isStarting(state) ? '<span class="mini">替补</span>' : '';
      return `<li class="squad-row${meRow}">
        <span class="pos">${p.pos}</span>
        <span class="nm">${esc(p.name)}${sub}</span>
        <span class="ovr">${p.ovr}</span>
        <span class="bar"><i style="width:${p.ovr}%"></i></span>
      </li>`;
    })
    .join('');

  const req = startRequirement(state);
  const mine = myOvr(state);
  const why = (() => {
    if (req.gap > 10) return `差 ${req.gap} 点，超过 10 点上不了场`;
    if (state.coachTrust <= req.needTrust) return `信任 ${state.coachTrust}/${req.needTrust}，还差 ${req.needTrust - state.coachTrust + 1}`;
    return '可以首发';
  })();
  const meRow = benched
    ? `<li class="squad-row me sub-row">
        <span class="pos">替补</span>
        <span class="nm">${esc(state.playerName)}<span class="mini">${why}</span></span>
        <span class="ovr">${mine}</span>
        <span class="bar"><i style="width:${mine}%"></i></span>
      </li>`
    : '';

  return `<div class="panel">
      <div class="cap">赛季排名</div>
      ${rankLine}
      ${nextLine}
      <ul class="weeks">${list}</ul>
    </div>
    <div class="panel">
      <div class="cap">当前阵容 · ${esc(state.teamId ?? '')}</div>
      <ul class="squad">${squad}${meRow}</ul>
      <div class="cap" style=" margin-top:10px">首发两关：信任 > ${req.needTrust}，且差距 ≤ 10（现在差 ${req.gap}）。</div>
    </div>`;
}

function wireStarter(): void {
  const input = document.getElementById('nameInput') as HTMLInputElement | null;
  if (!input) return;
  input.addEventListener('input', () => {
    starter.name = input.value;
    const len = [...starter.name].length;
    const ok = Boolean(starter.role) && len >= 2 && len <= 8;
    const btn = document.querySelector<HTMLButtonElement>('[data-act="start"]');
    if (btn) {
      btn.disabled = !ok;
      btn.classList.toggle('disabled', !ok);
    }
    const note = document.querySelector('.s-note');
    if (note) note.textContent = ok ? '' : '选一个分路、填上名字才能开始。';
    const counter = input.parentElement?.querySelector('.cap:last-child');
    if (counter) counter.textContent = `${len}/8`;
  });
  input.focus();
}

function render(): void {
  if (starter.open && !devMode) {
    renderStarter();
    wireStarter();
    return;
  }
  if (state.ended) {
    app.innerHTML = renderTopbar() + renderEnding();
    return;
  }
  // 演出进行中：不重建 DOM，等 show.ts 回调。
  const pm = state.pendingMatch;
  if (pm && pm.phase === 'show') {
    const key = `${pm.rivalId}-${pm.bestOf}-${pm.score?.join(':') ?? ''}-${pm.win ? 1 : 0}`;
    if (showKey === key) return;
    showKey = key;
    showDestroy?.();
    app.innerHTML = renderShow();
    const host = document.getElementById('show-host');
    if (host) {
      showDestroy = mountShow(host, {
        games: pm.games ?? [],
        bestOf: pm.bestOf ?? 3,
        myName: myTeamName(),
        rivalName: pm.rivalName,
        onDone: () => {
          showDestroy = null;
          showKey = '';
          matchNote = null;
          apply({ kind: 'finishMatch' });
        },
      });
    }
    return;
  }
  showKey = '';
  if (tab === 'schedule') {
    app.innerHTML = renderTopbar() + renderSchedule() + renderTabs() + renderSheet() + renderEvent() + renderMatch() + renderOutcome();
    return;
  }
  if (tab === 'career') {
    app.innerHTML = renderTopbar() + renderCareer() + renderTabs() + renderSheet() + renderEvent() + renderMatch() + renderOutcome();
    return;
  }
  if (tab === 'money') {
    app.innerHTML = renderTopbar() + renderMoney() + renderTabs() + renderSheet() + renderEvent() + renderMatch() + renderOutcome();
    return;
  }
  app.innerHTML =
    renderTopbar() +
    renderAttrs() +
    renderMeta() +
    renderSlots() +
    renderControls() +
    renderLog() +
    renderTabs() +
    renderSheet() +
    renderEvent() +
    renderMatch() +
    renderOutcome();
}

function apply(action: Action, persistNow = true): void {
  const result = reduce(state, action);
  state = result.state;
  // 存档以比赛周为界：排行动点不落盘，结周才写。
  if (persistNow) persist(state);
  sheet = null;
  render();
}

app.addEventListener('click', (ev) => {
  const target = ev.target as HTMLElement;
  const node = target.closest<HTMLElement>('[data-act]');
  if (!node) return;
  const act = node.dataset.act;
  if (act === 'role') {
    starter.role = (node.dataset.role as RoleId) ?? null;
    render();
    return;
  }
  if (act === 'reroll') {
    starter.attrs = rollAttrs();
    render();
    return;
  }
  if (act === 'start') {
    if (!starter.role) return;
    const name = starter.name.trim();
    if ([...name].length < 2 || [...name].length > 8) return;
    state = newGame(randomSeed(), name, starter.role, starter.attrs as GameState['attrs']);
    starter.open = false;
    persist(state);
    render();
    return;
  }
  if (act === 'tab') {
    tab = (node.dataset.tab as 'week' | 'schedule' | 'career' | 'money') ?? 'week';
    render();
    return;
  }

  // 点浮层空白处关闭，点内容不关。
  if (act === 'close-sheet' && target.closest('[data-stop]')) return;

  switch (act) {
    case 'buy': {
      const id = node.dataset.id;
      if (!id) return;
      const item = SHOP.find((i) => i.id === id);
      if (!item || buyBlocker(state, item)) return;
      for (const line of buy(state, id)) state.log.push({ text: line, tone: 'good' });
      persist(state);
      render();
      break;
    }
    case 'slot': {
      const slot = Number(node.dataset.slot);
      sheet = { kind: 'actions', slot };
      render();
      break;
    }
    case 'pick-action': {
      const id = node.dataset.id as ActionId | undefined;
      if (!id) return;
      if (id === 'train') {
        const slot = sheet?.kind === 'actions' ? sheet.slot : 0;
        sheet = { kind: 'targets', slot };
        render();
        return;
      }
      const slot = sheet?.kind === 'actions' ? sheet.slot : 0;
      apply({ kind: 'selectAction', slot, action: id }, false);
      break;
    }
    case 'pick-target': {
      const key = node.dataset.key as AttrKey | undefined;
      if (!key) return;
      const slot = sheet?.kind === 'targets' ? sheet.slot : 0;
      apply({ kind: 'selectAction', slot, action: 'train', target: key }, false);
      break;
    }
    case 'clear-slot': {
      const slot = sheet?.kind === 'actions' ? sheet.slot : 0;
      apply({ kind: 'clearSlot', slot }, false);
      break;
    }
    case 'close-sheet':
      sheet = null;
      render();
      break;
    case 'end-week':
      apply({ kind: 'endWeek' });
      break;
    case 'retire':
      apply({ kind: 'retire' });
      break;
    case 'skip-year':
      apply({ kind: 'skipYear' });
      break;
    case 'choose': {
      const index = Number(node.dataset.i);
      const result = reduce(state, { kind: 'chooseOption', option: index });
      state = result.state;
      persist(state);
      // 决赛：选项结算完直接进演出，把结果飘在演出开头。
      if (state.pendingMatch?.phase === 'show') {
        matchNote = result.log.filter((e) => e.tone !== 'plain').slice(0, 3);
        outcome = null;
      } else {
        outcome = result.log;
      }
      render();
      break;
    }
    case 'kickoff':
      apply({ kind: 'kickoffMatch' });
      break;
    case 'match-choose': {
      const index = Number(node.dataset.i);
      const result = reduce(state, { kind: 'chooseMatchOption', option: index });
      state = result.state;
      matchNote = result.log.filter((e) => e.tone !== 'plain').slice(0, 3);
      persist(state);
      render();
      break;
    }
    case 'continue':
      outcome = null;
      render();
      break;
    case 'restart':
      // 再来一局 = 回到开局屏，重新选人。
      state = newGame(randomSeed());
      starter.open = true;
      starter.role = null;
      starter.name = '';
      starter.attrs = rollAttrs();
      outcome = null;
      sheet = null;
      render();
      break;
  }
});

render();
