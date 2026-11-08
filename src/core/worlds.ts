import { createRng } from '../rng';
import type { GameState, LogEntry } from '../types';
import { myTeamStrength, seasonAverageStrength, isStarting, myPlace } from './league';
import { canPlay } from './match';
import { winProbability } from './odds';
import { addFlag } from './state';

/**
 * 第 27 周：S 赛小组赛自动模拟。
 * 16 队、LPL 前 4 参加；玩家所在组打 3 场，2 胜出线。
 * 对手用当季 LPL 平均强度当代理——名单里没有其他赛区的队。
 */
export function resolveWorldsGroup(state: GameState, out: LogEntry[]): void {
  if (!state.signed || !canPlay(state) || !isStarting(state) || myPlace(state) > 4) return;

  const opponent = seasonAverageStrength(state.year);
  const rate = winProbability(myTeamStrength(state), opponent, 0, state.coachTrust);
  const ctx = createRng(state.rngState);
  let wins = 0;
  for (let i = 0; i < 3; i += 1) {
    if (ctx.rng.next() < rate) wins += 1;
  }
  state.rngState = ctx.state();

  if (wins >= 2) {
    addFlag(state, `#S八强-${state.year}`);
    out.push({ text: `S 赛小组赛 ${wins} 胜，出线。`, tone: 'good' });
  } else {
    out.push({ text: `S 赛小组赛 ${wins} 胜，出局。`, tone: 'bad' });
  }
}
