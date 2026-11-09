import type { ShowGame } from '../types';

/**
 * 比赛演出：一块 640×640 的小地图，10 个球按三路/野区走位，
 * 30 秒一局，最后一秒落到已经定好的输赢上。
 * 这里只负责「怎么演」，胜负与比分由 reduce 里的 buildSeries 先算好。
 */

type Team = 'blue' | 'red';
type Lane = 'top' | 'mid' | 'bot';
type Role = 'top' | 'jg' | 'mid' | 'adc' | 'sup';

export interface ShowOptions {
  games: ShowGame[];
  bestOf: 3 | 5;
  myName: string;
  rivalName: string;
  onDone: () => void;
}

const W = 640;
const H = 640;

const LANE_DEF: Record<Lane, [number, number][]> = {
  top: [[0.1, 0.9], [0.1, 0.16], [0.16, 0.1], [0.84, 0.1], [0.9, 0.1]],
  mid: [[0.1, 0.9], [0.3, 0.7], [0.5, 0.5], [0.7, 0.3], [0.9, 0.1]],
  bot: [[0.1, 0.9], [0.16, 0.9], [0.84, 0.9], [0.9, 0.84], [0.9, 0.16], [0.9, 0.1]],
};

interface Vec {
  x: number;
  y: number;
}

interface Path {
  p: Vec[];
  seg: { a: Vec; b: Vec; len: number }[];
  total: number;
}

function toPath(def: [number, number][]): Path {
  const p = def.map((a) => ({ x: a[0] * W, y: a[1] * H }));
  const seg: Path['seg'] = [];
  let total = 0;
  for (let i = 1; i < p.length; i += 1) {
    const a = p[i - 1]!;
    const b = p[i]!;
    const len = Math.hypot(b.x - a.x, b.y - a.y);
    seg.push({ a, b, len });
    total += len;
  }
  return { p, seg, total };
}

const LANES: Record<Lane, Path> = {
  top: toPath(LANE_DEF.top),
  mid: toPath(LANE_DEF.mid),
  bot: toPath(LANE_DEF.bot),
};

function lanePoint(lane: Lane, t: number): Vec {
  const path = LANES[lane];
  const tt = Math.max(0, Math.min(1, t));
  let d = tt * path.total;
  for (let i = 0; i < path.seg.length; i += 1) {
    const s = path.seg[i]!;
    if (d <= s.len || i === path.seg.length - 1) {
      const k = Math.min(1, d / s.len);
      return { x: s.a.x + (s.b.x - s.a.x) * k, y: s.a.y + (s.b.y - s.a.y) * k };
    }
    d -= s.len;
  }
  return path.p[path.p.length - 1]!;
}

const BLUE_BASE = { x: 0.1 * W, y: 0.9 * H };
const RED_BASE = { x: 0.9 * W, y: 0.1 * H };
const OBJ = { dragon: { x: 0.66 * W, y: 0.66 * H }, baron: { x: 0.34 * W, y: 0.34 * H } };

interface Camp {
  n: string;
  x: number;
  y: number;
  big?: 1;
}

/** 每方六片野：蓝/狼/蛙/鸟/红/石，按刷野顺序排。 */
const CAMPS: Record<Team, Camp[]> = {
  blue: [
    { n: '狼', x: 0.17, y: 0.69 },
    { n: '蓝', x: 0.32, y: 0.48, big: 1 },
    { n: '蛙', x: 0.2, y: 0.36 },
    { n: '鸟', x: 0.42, y: 0.7 },
    { n: '红', x: 0.52, y: 0.8, big: 1 },
    { n: '石', x: 0.66, y: 0.8 },
  ],
  red: [
    { n: '狼', x: 0.83, y: 0.31 },
    { n: '蓝', x: 0.67, y: 0.52, big: 1 },
    { n: '蛙', x: 0.8, y: 0.64 },
    { n: '鸟', x: 0.58, y: 0.3 },
    { n: '红', x: 0.48, y: 0.2, big: 1 },
    { n: '石', x: 0.34, y: 0.2 },
  ],
};

interface RouteSeg {
  a: Vec;
  b: Vec;
  dur: number;
  start: number;
}

const ROUTE: Record<Team, { segs: RouteSeg[]; total: number }> = {
  blue: { segs: [], total: 0 },
  red: { segs: [], total: 0 },
};

function buildRoute(team: Team): void {
  const base = team === 'blue' ? BLUE_BASE : RED_BASE;
  const pts: Vec[] = [base];
  for (const c of CAMPS[team]) pts.push({ x: c.x * W, y: c.y * H });
  pts.push({ x: CAMPS[team][0]!.x * W, y: CAMPS[team][0]!.y * H });
  const segs: RouteSeg[] = [];
  let acc = 0;
  for (let j = 1; j < pts.length; j += 1) {
    const a = pts[j - 1]!;
    const b = pts[j]!;
    const len = Math.hypot(b.x - a.x, b.y - a.y);
    const dur = Math.max(0.35, len / 70);
    segs.push({ a, b, dur, start: acc });
    acc += dur + 0.5; // 到点后停半秒刷野
  }
  ROUTE[team] = { segs, total: acc };
}
buildRoute('blue');
buildRoute('red');

function campPoint(team: Team, t: number): Vec {
  const r = ROUTE[team];
  const tt = t % r.total;
  for (let i = 0; i < r.segs.length; i += 1) {
    const s = r.segs[i]!;
    if (tt < s.start + s.dur) {
      const k = (tt - s.start) / s.dur;
      return { x: s.a.x + (s.b.x - s.a.x) * k, y: s.a.y + (s.b.y - s.a.y) * k };
    }
    const next = i + 1 < r.segs.length ? r.segs[i + 1]!.start : r.total;
    if (tt < next) return { x: s.b.x, y: s.b.y };
  }
  return { x: r.segs[0]!.a.x, y: r.segs[0]!.a.y };
}

/* ---------- 选手 ---------- */

const ROLE_ORDER: { role: Role; lane: Lane }[] = [
  { role: 'top', lane: 'top' },
  { role: 'jg', lane: 'mid' },
  { role: 'mid', lane: 'mid' },
  { role: 'adc', lane: 'bot' },
  { role: 'sup', lane: 'bot' },
];

interface Dot {
  team: Team;
  role: Role;
  lane: Lane;
  pathT: number;
  x: number;
  y: number;
  dead: boolean;
  deadUntil: number;
  speed: number;
  seed: number;
  angle: number;
  isYou: boolean;
}

interface Kill {
  t: number;
  team: Team;
  victim?: Dot;
}

interface Popup {
  t: number;
  text: string;
  color: string;
}

interface FloatText {
  x: number;
  y: number;
  text: string;
  life: number;
  color: string;
}

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
  max: number;
  c: string;
}

interface Game {
  win: boolean;
  t: number;
  dots: Dot[];
  kills: Kill[];
  ki: number;
  kc: { blue: number; red: number };
  boom: boolean;
  ended: boolean;
  popups: Popup[];
  popIx: number;
}

function makeDots(): Dot[] {
  const dots: Dot[] = [];
  ROLE_ORDER.forEach((role, r) => {
    (['blue', 'red'] as const).forEach((team, ti) => {
      const homeT = team === 'blue' ? 0.02 : 0.98;
      const p = lanePoint(role.lane, homeT);
      dots.push({
        team,
        role: role.role,
        lane: role.lane,
        pathT: homeT,
        x: p.x,
        y: p.y,
        dead: false,
        deadUntil: 0,
        speed: role.role === 'jg' ? 110 : 140,
        seed: (r + 1) * 1.9 + (team === 'red' ? 2.7 : 0) + ti * 0.01,
        angle: (r * Math.PI * 2) / 5 + (team === 'red' ? 0.55 : 0),
        isYou: team === 'blue' && role.role === 'mid',
      });
    });
  });
  return dots;
}

/** 把「总击杀」摊成一条时间线：败方前期先拿两个，胜方在 17–19 秒团灭，再收尾。 */
function buildKills(win: boolean, dots: Dot[], kills: [number, number]): Kill[] {
  const winner: Team = win ? 'blue' : 'red';
  const loser: Team = win ? 'red' : 'blue';
  const loserKills = kills[win ? 1 : 0];
  const winnerKills = kills[win ? 0 : 1];
  const list: Kill[] = [];

  list.push({ t: 2.8 + Math.random() * 2.0, team: loser });
  list.push({ t: 5.6 + Math.random() * 1.8, team: loser });
  for (let i = 0; i < 4; i += 1) list.push({ t: 17.4 + i * 0.42, team: winner });
  for (let j = 0; j < Math.max(0, loserKills - 2); j += 1) {
    list.push({ t: 10 + Math.random() * 6, team: loser });
  }
  for (let k = 0; k < Math.max(0, winnerKills - 4); k += 1) {
    list.push({ t: 6.2 + Math.random() * 17.6, team: winner });
  }
  list.sort((a, b) => a.t - b.t);

  const pool: Record<Team, Dot[]> = {
    blue: dots.filter((d) => d.team === 'blue'),
    red: dots.filter((d) => d.team === 'red'),
  };
  const aceVictims = pool[loser].slice(0, 4);
  let aceIx = 0;
  for (const k of list) {
    const victims = pool[k.team === 'blue' ? 'red' : 'blue'];
    if (k.team === winner && k.t > 17.3 && k.t < 19.0 && aceVictims.length > 0) {
      k.victim = aceVictims[aceIx % aceVictims.length];
      aceIx += 1;
    } else if (victims.length > 0) {
      k.victim = victims[Math.floor(Math.random() * victims.length)];
    }
  }
  return list;
}

function newGame(win: boolean, kills: [number, number]): Game {
  const dots = makeDots();
  return {
    win,
    t: 0,
    dots,
    kills: buildKills(win, dots, kills),
    ki: 0,
    kc: { blue: 0, red: 0 },
    boom: false,
    ended: false,
    popups: [
      { t: 18.95, text: '团灭', color: win ? '#ff6b6b' : '#6ea8ff' },
      { t: 21.5, text: '大龙', color: win ? '#6ea8ff' : '#ff6b6b' },
    ],
    popIx: 0,
  };
}

/* ---------- 演出主体 ---------- */

export function mountShow(host: HTMLElement, opts: ShowOptions): () => void {
  const stage = document.createElement('div');
  stage.className = 'show-stage';
  const cv = document.createElement('canvas');
  cv.width = W;
  cv.height = H;
  const ctx = cv.getContext('2d');
  if (!ctx) return () => undefined;

  const hud = document.createElement('div');
  hud.className = 'show-hud';
  hud.innerHTML = `
    <div class="show-top">
      <span class="bo">bo${opts.bestOf}</span>
      <span class="game">第 1 局</span>
      <span class="score"><b>0</b><i>:</i><b>0</b></span>
      <span class="kills">击杀 0 : 0</span>
    </div>
    <div class="show-names"><b>${escapeHtml(opts.myName)}</b><span>vs</span><b>${escapeHtml(opts.rivalName)}</b></div>
    <div class="show-timer"><i></i></div>
    <div class="show-phase">对线</div>`;
  const skipBtn = document.createElement('button');
  skipBtn.className = 'show-skip';
  skipBtn.textContent = '跳过本局';
  const banner = document.createElement('div');
  banner.className = 'show-banner';
  const result = document.createElement('div');
  result.className = 'show-result hidden';

  stage.append(cv, hud, skipBtn, banner, result);
  host.append(stage);

  const el = {
    top: hud.querySelector<HTMLElement>('.show-top')!,
    bo: hud.querySelector<HTMLElement>('.bo')!,
    game: hud.querySelector<HTMLElement>('.game')!,
    score: hud.querySelector<HTMLElement>('.score')!,
    kills: hud.querySelector<HTMLElement>('.kills')!,
    timer: hud.querySelector<HTMLElement>('.show-timer i')!,
    phase: hud.querySelector<HTMLElement>('.show-phase')!,
    names: hud.querySelector<HTMLElement>('.show-names')!,
  };

  let gameIx = 0;
  let score = { b: 0, r: 0 };
  let totalKills = { b: 0, r: 0 };
  let game: Game | null = null;
  let mode: 'playing' | 'between' | 'done' = 'playing';
  let bannerTimer: number | null = null;
  let raf = 0;
  let last = 0;
  let destroyed = false;
  let particles: Particle[] = [];
  let floats: FloatText[] = [];

  function setScore(): void {
    el.score.innerHTML = `<b>${score.b}</b><i>:</i><b>${score.r}</b>`;
    el.game.textContent = `第 ${Math.min(gameIx + 1, opts.games.length)} 局`;
    el.bo.textContent = `bo${opts.bestOf}`;
  }

  function updateHud(): void {
    setScore();
    if (!game) return;
    el.kills.textContent = `击杀 ${game.kc.blue} : ${game.kc.red}`;
    el.timer.style.width = `${Math.min(100, (game.t / 30) * 100)}%`;
    el.phase.textContent = game.t < 10 ? '对线' : game.t < 23 ? '团战' : '推家';
  }

  function popup(text: string, color: string): void {
    const node = document.createElement('div');
    node.className = 'show-popup';
    node.textContent = text;
    node.style.color = color;
    stage.append(node);
    window.setTimeout(() => node.remove(), 1400);
  }

  function burst(x: number, y: number, team: Team, n: number): void {
    const col = team === 'blue' ? '#4c8dff' : '#ff5a5a';
    for (let i = 0; i < n; i += 1) {
      const a = Math.random() * Math.PI * 2;
      const s = 40 + Math.random() * 140;
      particles.push({ x, y, vx: Math.cos(a) * s, vy: Math.sin(a) * s, life: 0.5 + Math.random() * 0.4, max: 0.9, c: col });
    }
  }

  /* ---------- 绘制 ---------- */

  function riverPath(): void {
    ctx!.beginPath();
    ctx!.moveTo(0.1 * W, 0.1 * H);
    ctx!.lineTo(0.9 * W, 0.9 * H);
  }

  function drawCamps(): void {
    (Object.keys(CAMPS) as Team[]).forEach((team) => {
      const col = team === 'blue' ? '#4c8dff' : '#ff5a5a';
      for (const c of CAMPS[team]) {
        const x = c.x * W;
        const y = c.y * H;
        let farmed = false;
        if (game && mode === 'playing' && game.t < 10) {
          for (const d of game.dots) {
            if (!d.dead && d.role === 'jg' && d.team === team && Math.hypot(d.x - x, d.y - y) < 15) farmed = true;
          }
        }
        const rr = c.big ? 11 : 8;
        ctx!.globalAlpha = farmed ? 1 : 0.55;
        ctx!.strokeStyle = `${col}aa`;
        ctx!.lineWidth = c.big ? 1.6 : 1.2;
        ctx!.beginPath();
        ctx!.arc(x, y, rr, 0, 7);
        ctx!.stroke();
        ctx!.fillStyle = col + (farmed ? '33' : '12');
        ctx!.fill();
        ctx!.fillStyle = col;
        ctx!.font = '10px "Microsoft YaHei",sans-serif';
        ctx!.textAlign = 'center';
        ctx!.fillText(c.n, x, y + 3);
        ctx!.globalAlpha = 1;
      }
    });
  }

  function drawBase(p: Vec, color: string): void {
    const g = ctx!.createRadialGradient(p.x, p.y, 4, p.x, p.y, 66);
    g.addColorStop(0, `${color}55`);
    g.addColorStop(1, `${color}00`);
    ctx!.fillStyle = g;
    ctx!.beginPath();
    ctx!.arc(p.x, p.y, 66, 0, 7);
    ctx!.fill();
    ctx!.globalAlpha = 0.85;
    ctx!.fillStyle = color;
    ctx!.beginPath();
    ctx!.arc(p.x, p.y, 16, 0, 7);
    ctx!.fill();
    ctx!.globalAlpha = 1;
    ctx!.save();
    ctx!.translate(p.x, p.y);
    ctx!.rotate(Math.PI / 4);
    ctx!.fillStyle = '#e8f1ff';
    ctx!.fillRect(-6, -6, 12, 12);
    ctx!.restore();
  }

  function drawPit(p: Vec, color: string, label: string): void {
    ctx!.strokeStyle = `${color}66`;
    ctx!.lineWidth = 1.5;
    ctx!.beginPath();
    ctx!.arc(p.x, p.y, 16, 0, 7);
    ctx!.stroke();
    ctx!.fillStyle = `${color}14`;
    ctx!.fill();
    ctx!.fillStyle = `${color}aa`;
    ctx!.font = '9px "Microsoft YaHei",sans-serif';
    ctx!.textAlign = 'center';
    ctx!.fillText(label, p.x, p.y + 3);
  }

  function drawMap(): void {
    const bg = ctx!.createLinearGradient(0, 0, W, H);
    bg.addColorStop(0, '#08131a');
    bg.addColorStop(1, '#0a1018');
    ctx!.fillStyle = bg;
    ctx!.fillRect(0, 0, W, H);

    ctx!.strokeStyle = '#07141b';
    ctx!.lineWidth = 42;
    ctx!.lineCap = 'round';
    ctx!.lineJoin = 'round';
    riverPath();
    ctx!.stroke();
    ctx!.strokeStyle = '#3f86bd22';
    ctx!.lineWidth = 34;
    riverPath();
    ctx!.stroke();
    ctx!.strokeStyle = '#7cc4ff16';
    ctx!.lineWidth = 2;
    riverPath();
    ctx!.stroke();

    (Object.keys(LANES) as Lane[]).forEach((k) => {
      const path = LANES[k];
      ctx!.beginPath();
      ctx!.moveTo(path.p[0]!.x, path.p[0]!.y);
      for (let n = 1; n < path.p.length; n += 1) ctx!.lineTo(path.p[n]!.x, path.p[n]!.y);
      ctx!.strokeStyle = '#182536';
      ctx!.lineWidth = 30;
      ctx!.lineJoin = 'round';
      ctx!.lineCap = 'round';
      ctx!.stroke();
      ctx!.strokeStyle = '#2b4059';
      ctx!.lineWidth = 2;
      ctx!.stroke();
    });

    drawBase(BLUE_BASE, '#2f6fed');
    drawBase(RED_BASE, '#e04545');
    drawPit(OBJ.dragon, '#d09a4a', '小龙');
    drawPit(OBJ.baron, '#9a6ce0', '大龙');
    drawCamps();
  }

  function dotTarget(d: Dot, g: Game): Vec {
    const t = g.t;
    if (t < 10) {
      if (d.role === 'jg') return campPoint(d.team, t);
      const p = 0.47 + 0.045 * Math.sin(t * 0.9 + d.seed * 2);
      return lanePoint(d.lane, p);
    }
    if (t < 23) {
      const o = t < 16.5 ? OBJ.dragon : OBJ.baron;
      const rad = 22 + (d.role === 'sup' ? 12 : 0) + Math.sin(t * 2 + d.seed) * 5;
      return { x: o.x + Math.cos(d.angle) * rad, y: o.y + Math.sin(d.angle) * rad };
    }
    const atk = (d.team === 'blue') === g.win;
    const base = atk
      ? g.win
        ? RED_BASE
        : BLUE_BASE
      : d.team === 'blue'
        ? BLUE_BASE
        : RED_BASE;
    const rad = (atk ? 34 : 22) + Math.sin(g.t * 5 + d.seed) * 5;
    const ang = d.angle + Math.sin(g.t * 2.5 + d.seed) * 0.12;
    return { x: base.x + Math.cos(ang) * rad, y: base.y + Math.sin(ang) * rad };
  }

  function update(dt: number): void {
    if (mode !== 'playing' || !game) return;
    const g = game;
    g.t = Math.min(30, g.t + dt);

    while (g.ki < g.kills.length && g.kills[g.ki]!.t <= g.t) {
      const k = g.kills[g.ki]!;
      g.ki += 1;
      if (k.victim) {
        k.victim.dead = true;
        k.victim.deadUntil = g.t + 2.2;
        burst(k.victim.x, k.victim.y, k.victim.team, 14);
        floats.push({
          x: k.victim.x,
          y: k.victim.y - 14,
          text: '+1',
          life: 0.9,
          color: k.team === 'blue' ? '#8fc0ff' : '#ff9a9a',
        });
      }
      g.kc[k.team] += 1;
      if (g.kc.blue + g.kc.red === 1) popup('一血', '#ffd166');
      updateHud();
    }

    while (g.popIx < g.popups.length && g.popups[g.popIx]!.t <= g.t) {
      const pp = g.popups[g.popIx]!;
      g.popIx += 1;
      popup(pp.text, pp.color);
    }

    for (const d of g.dots) {
      if (d.dead) {
        if (g.t >= d.deadUntil) {
          d.dead = false;
          d.pathT = d.team === 'blue' ? 0.02 : 0.98;
          const rp = lanePoint(d.lane, d.pathT);
          d.x = rp.x;
          d.y = rp.y;
        } else {
          continue;
        }
      }
      const tgt = dotTarget(d, g);
      const dx = tgt.x - d.x;
      const dy = tgt.y - d.y;
      const dist = Math.hypot(dx, dy);
      if (dist > 0.5) {
        const step = Math.min(dist, d.speed * dt);
        d.x += (dx / dist) * step;
        d.y += (dy / dist) * step;
      }
    }

    for (const q of particles) {
      q.x += q.vx * dt;
      q.y += q.vy * dt;
      q.vx *= 0.96;
      q.vy *= 0.96;
      q.life -= dt;
    }
    particles = particles.filter((x) => x.life > 0);
    for (const f of floats) {
      f.y -= 26 * dt;
      f.life -= dt;
    }
    floats = floats.filter((x) => x.life > 0);

    if (!g.boom && g.t >= 28.2) {
      g.boom = true;
      const base = g.win ? RED_BASE : BLUE_BASE;
      burst(base.x, base.y, g.win ? 'red' : 'blue', 40);
    }

    updateHud();
    if (g.t >= 30) endGame();
  }

  function drawDots(g: Game): void {
    for (const d of g.dots) {
      if (d.dead) continue;
      const col = d.team === 'blue' ? '#4c8dff' : '#ff5a5a';
      ctx!.save();
      ctx!.shadowColor = col;
      ctx!.shadowBlur = 12;
      ctx!.fillStyle = col;
      ctx!.beginPath();
      ctx!.arc(d.x, d.y, 6, 0, 7);
      ctx!.fill();
      ctx!.strokeStyle = '#060c16';
      ctx!.lineWidth = 2;
      ctx!.stroke();
      ctx!.restore();
      if (d.isYou) {
        ctx!.strokeStyle = '#ffffff';
        ctx!.lineWidth = 2;
        ctx!.beginPath();
        ctx!.arc(d.x, d.y, 12, 0, 7);
        ctx!.stroke();
        ctx!.fillStyle = '#ffffff';
        ctx!.font = 'bold 10px "Microsoft YaHei",sans-serif';
        ctx!.textAlign = 'center';
        ctx!.fillText('你', d.x, d.y - 18);
      }
    }
  }

  function drawParticles(): void {
    for (const p of particles) {
      ctx!.globalAlpha = Math.max(0, p.life / p.max);
      ctx!.fillStyle = p.c;
      ctx!.fillRect(p.x - 2, p.y - 2, 4, 4);
    }
    ctx!.globalAlpha = 1;
  }

  function drawFloats(): void {
    ctx!.textAlign = 'center';
    for (const f of floats) {
      ctx!.globalAlpha = Math.max(0, Math.min(1, f.life));
      ctx!.fillStyle = f.color;
      ctx!.font = 'bold 13px "Microsoft YaHei",sans-serif';
      ctx!.fillText(f.text, f.x, f.y);
    }
    ctx!.globalAlpha = 1;
  }

  function render(): void {
    drawMap();
    if (game && mode === 'playing') {
      drawDots(game);
      drawParticles();
      drawFloats();
    } else if (mode === 'between') {
      drawParticles();
    }
  }

  /* ---------- 系列流程 ---------- */

  function startGame(): void {
    const spec = opts.games[gameIx];
    game = newGame(spec?.win ?? false, spec?.kills ?? [12, 5]);
    particles = [];
    floats = [];
    mode = 'playing';
    banner.classList.remove('show');
    updateHud();
  }

  function startSeries(): void {
    gameIx = 0;
    score = { b: 0, r: 0 };
    totalKills = { b: 0, r: 0 };
    startGame();
  }

  function endGame(): void {
    if (!game || game.ended) return;
    game.ended = true;
    mode = 'between';
    score[game.win ? 'b' : 'r'] += 1;
    totalKills.b += game.kc.blue;
    totalKills.r += game.kc.red;
    updateHud();
    banner.textContent = `第 ${gameIx + 1} 局 · ${game.win ? '胜' : '负'}`;
    banner.style.color = game.win ? '#6ea8ff' : '#ff7a7a';
    banner.classList.add('show');
    bannerTimer = window.setTimeout(() => {
      banner.classList.remove('show');
      nextOrResult();
    }, 1500);
  }

  function nextOrResult(): void {
    if (gameIx >= opts.games.length - 1) showResult();
    else {
      gameIx += 1;
      startGame();
    }
  }

  function showResult(): void {
    mode = 'done';
    const win = score.b > score.r;
    const title = win ? '胜利' : '失败';
    result.innerHTML = `
      <h2 style="color:${win ? '#6ea8ff' : '#ff7a7a'}">${title}</h2>
      <div class="show-big">${score.b} : ${score.r}</div>
      <div class="show-stat">总击杀 ${totalKills.b} : ${totalKills.r} · ${opts.games.length} 局</div>
      <button class="btn primary" type="button" data-act="show-continue">继续</button>`;
    result.classList.remove('hidden');
    skipBtn.classList.add('hidden');
    result.querySelector<HTMLButtonElement>('[data-act="show-continue"]')?.addEventListener('click', () => {
      destroy();
      opts.onDone();
    });
  }

  function loop(ts: number): void {
    if (destroyed) return;
    if (!last) last = ts;
    const dt = Math.min(0.05, (ts - last) / 1000);
    last = ts;
    update(dt);
    render();
    raf = window.requestAnimationFrame(loop);
  }

  function skip(): void {
    if (mode === 'playing' && game) {
      // 跳过也要把剩下的人头算进总击杀，不然结算写着 0:2。
      while (game.ki < game.kills.length) {
        const k = game.kills[game.ki]!;
        game.ki += 1;
        if (k.victim) k.victim.dead = true;
        game.kc[k.team] += 1;
      }
      game.t = 30;
      endGame();
    } else if (mode === 'between') {
      if (bannerTimer !== null) window.clearTimeout(bannerTimer);
      banner.classList.remove('show');
      nextOrResult();
    }
  }

  skipBtn.addEventListener('click', skip);

  function destroy(): void {
    if (destroyed) return;
    destroyed = true;
    window.cancelAnimationFrame(raf);
    if (bannerTimer !== null) window.clearTimeout(bannerTimer);
    stage.remove();
  }

  startSeries();
  raf = window.requestAnimationFrame(loop);
  return destroy;
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
