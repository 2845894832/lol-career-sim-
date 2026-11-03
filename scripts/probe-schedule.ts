import { newGame } from '../src/core/state';
import { scheduleFor, nextFixture, standings, myPlace, mySquad } from '../src/core/league';
import { CONFIG } from '../src/config';

const s = newGame(12345);
s.signed = true;
s.teamId = 'RNG';
s.coachTrust = 65;
s.week = 13;
const fx = scheduleFor(s);
console.log('regularWeeks', CONFIG.league.regularWeeks.join(','));
console.log('fixtures', fx.map((f) => `${f.week}:${f.rivalId}`).join(' '));
console.log('next', nextFixture(s));
console.log('standing', standings(s).slice(0, 3).map((r) => `${r.name} ${r.wins}-${r.losses}`).join(' | '), 'place', myPlace(s));
console.log('squad', mySquad(s).map((p) => `${p.pos} ${p.name} ${p.ovr}`).join(' | '));
