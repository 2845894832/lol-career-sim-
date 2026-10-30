import './style.css';
import { reduce } from '../core/reduce';
import { getEvent, successRateOf } from '../core/events';
import { ACTION_INFO, canAfford, isActionUnlocked, staminaCost } from '../core/actions';
import { loadSaved, persist } from '../core/save';
import { expProgress } from '../core/growth';
import { ageOf, newGame, phaseOfYear, rankTier } from '../core/state';
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

let state: GameState = loadSaved() ?? newGame(randomSeed());
let sheet: Sheet | null = null;
let outcome: LogEntry[] | null = null;

const esc = (s: string): string =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

const slotLabel = (slot: number): string => `第 ${slot + 1} 格`;

function renderTopbar(): string {
  const phase = phaseOfYear(state.year);
  const tag = state.signed ? '已签约' : state.freeAgent ? '自由人' : '路人期';
  return `<div class="topbar">
    <div>
      <div class="title">第 ${state.year} 年 · 第 ${state.week} 周</div>
      <div class="sub">${PHASE_LABEL[phase]} · ${ageOf(state)} 岁 · ${tag}</div>
    </div>
    <div class="sub">${state.week <= 26 ? '比赛周' : '休赛期'}</div>
  </div>`;
}

function renderAttrs(): string {
  const cells = ATTR_KEYS.map((key) => {
    const prog = expProgress(state, key);
    const pct = Math.round((prog.current / prog.needed) * 100);
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
      <span>体力 <b>${state.stamina}/${state.maxStamina}</b></span>
      <span>段位 <b>${rankTier(state.rankPoints).name}</b></span>
      <span>金钱 <b>${state.money}</b></span>
      <span>伤病 <b>${state.injury}/3</b></span>
      <span>教练信任 <b>${state.coachTrust}</b></span>
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

function renderControls(): string {
  const blocked = state.pendingEvent ? 'disabled' : '';
  return `<div class="panel" style="display:flex;flex-direction:column;gap:8px">
    <button class="btn primary" data-act="end-week" ${blocked}>
      <span>结周</span><span class="hint">${state.pendingEvent ? '先处理事件' : '结算三格并推进'}</span>
    </button>
    <button class="btn" data-act="retire"><span>退役</span><span class="hint">立刻看结局</span></button>
    <button class="btn" data-act="skip-year"><span>跳到下一年</span><span class="hint">调试用</span></button>
  </div>`;
}

function renderLog(): string {
  const lines = state.log.slice(-6);
  return `<div class="panel"><div class="log">${lines
    .map((e) => `<div class="${e.tone}">${esc(e.text)}</div>`)
    .join('')}</div></div>`;
}

function renderSheet(): string {
  if (!sheet) return '';
  if (sheet.kind === 'actions') {
    const rows = ACTION_IDS.map((id) => {
      const unlocked = isActionUnlocked(state, id);
      const afford = canAfford(state, sheet!.slot, id);
      const disabled = !unlocked || !afford;
      const hint = !unlocked ? '签约后解锁' : `${staminaCost(id)} 体力 · ${ACTION_INFO[id].hint}`;
      return `<button class="btn" data-act="pick-action" data-id="${id}" ${disabled ? 'disabled' : ''}>
        <span>${ACTION_INFO[id].label}</span><span class="hint">${hint}</span>
      </button>`;
    }).join('');
    return `<div class="overlay" data-act="close-sheet"><div class="sheet" data-stop="1">
      <h2>${slotLabel(sheet.slot)}排什么</h2>
      <div class="options">${rows}</div>
    </div></div>`;
  }

  const rows = ATTR_KEYS.filter((key) => key !== 'popularity')
    .map(
      (key) =>
        `<button class="btn" data-act="pick-target" data-key="${key}"><span>${ATTR_LABEL[key]}</span><span class="hint">集中提升</span></button>`,
    )
    .join('');
  return `<div class="overlay" data-act="close-sheet"><div class="sheet" data-stop="1">
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
      const rate =
        option.risk === 'roll'
          ? `${Math.round(successRateOf(state, option) * 100)}%`
          : option.risk === 'success'
            ? '必成'
            : '必败';
      return `<button class="btn" data-act="choose" data-i="${i}">
        <span>${esc(option.label)}</span><span class="rate">${rate}</span>
      </button>`;
    })
    .join('');
  return `<div class="overlay"><div class="sheet">
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
  return `<div class="overlay"><div class="sheet">
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

function render(): void {
  if (state.ended) {
    app.innerHTML = renderTopbar() + renderEnding();
    return;
  }
  app.innerHTML =
    renderTopbar() +
    renderAttrs() +
    renderMeta() +
    renderSlots() +
    renderControls() +
    renderLog() +
    renderSheet() +
    renderEvent() +
    renderOutcome();
}

function apply(action: Action): void {
  const result = reduce(state, action);
  state = result.state;
  persist(state);
  sheet = null;
  render();
}

app.addEventListener('click', (ev) => {
  const target = ev.target as HTMLElement;
  const node = target.closest<HTMLElement>('[data-act]');
  if (!node) return;
  const act = node.dataset.act;

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
      apply({ kind: 'selectAction', slot, action: id });
      break;
    }
    case 'pick-target': {
      const key = node.dataset.key as AttrKey | undefined;
      if (!key) return;
      const slot = sheet?.kind === 'targets' ? sheet.slot : 0;
      apply({ kind: 'selectAction', slot, action: 'train', target: key });
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
      outcome = state.log.slice(-6);
      render();
      break;
    }
    case 'continue':
      outcome = null;
      render();
      break;
    case 'restart':
      state = newGame(randomSeed());
      persist(state);
      outcome = null;
      sheet = null;
      render();
      break;
  }
});

render();
