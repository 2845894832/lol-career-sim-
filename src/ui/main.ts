import './style.css';
import { reduce } from '../core/reduce';
import { getEvent, successRateOf } from '../core/events';
import { ACTION_INFO, canAfford, isActionUnlocked, staminaCost } from '../core/actions';
import { loadSaved, persist } from '../core/save';
import { ageOf, isMatchWeek, newGame, phaseOfYear } from '../core/state';
import { rankOf } from '../core/ladder';
import { myPlace, myOvr, mySquad, nextFixture, startRequirement, upcomingFixtures, standings, isStarting } from '../core/league';
import { randomSeed } from '../rng';
import {
  ACTION_IDS,
  ATTR_KEYS,
  ATTR_LABEL,
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
  state.coachTrust = devMode === 'bench' ? 55 : 65;
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
let tab: 'week' | 'schedule' = 'week';

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
      const extra = id === 'train' && target ? ATTR_LABEL[target] : id ? `${staminaCost(id)} 体力` : '点一下安排';
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
      const pts = staminaCost(id);
      const cost = unlocked && pts > 0 ? `<b class="opt-num">${pts}</b><span class="opt-unit">体力</span>` : '';
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
      ${phaseOfYear(state.year) === 'growth' ? '<div class="cap">成长阶段：每次练习多涨 1 点。</div>' : ''}
      <div class="options">${rows}${clearRow}</div>
    </div></div>`;
  }

  const rows = ATTR_KEYS.filter((key) => key !== 'popularity')
    .map(
      (key) =>
        `<button class="btn" data-act="pick-target" data-key="${key}"><span>${ATTR_LABEL[key]}</span><span class="hint">集中提升</span></button>`,
    )
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
  const item = (id: 'week' | 'schedule', label: string) =>
    `<button class="tab${tab === id ? ' on' : ''}" data-act="tab" data-tab="${id}">${label}</button>`;
  return `<nav class="tabs">${item('week', '本周')}${item('schedule', '赛程')}</nav>`;
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
  if (tab === 'schedule') {
    app.innerHTML = renderTopbar() + renderSchedule() + renderTabs() + renderSheet() + renderEvent() + renderOutcome();
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
    tab = (node.dataset.tab as 'week' | 'schedule') ?? 'week';
    render();
    return;
  }

  // 点浮层空白处关闭，点内容不关。
  if (act === 'close-sheet' && target.closest('[data-stop]')) return;

  switch (act) {
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
      outcome = result.log;
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
