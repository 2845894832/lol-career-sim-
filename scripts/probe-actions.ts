import { CONFIG } from '../src/config';
import { expNeeded } from '../src/core/growth';
import { weeklyGain } from '../src/core/ladder';

const at = 55;
const need = expNeeded(at);
const mult = 1 + (2800 / CONFIG.rank.max) * 0.5;
console.log('expNeeded(55)', need);
console.log('weeklyGain(2800)', weeklyGain(2800));
console.log('rankExpMultiplier', mult.toFixed(2), 'rank 单维', Math.round(6 * mult), '合计', Math.round(6 * mult) * 4);
console.log('train', CONFIG.actions.train.exp, (CONFIG.actions.train.exp / need).toFixed(2));
console.log('review', 10, (10 / need).toFixed(2));
console.log('scrim', 16, (16 / need).toFixed(2));
