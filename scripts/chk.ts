import { rankOf, tierCount } from '../src/core/ladder';
console.log('tiers', tierCount());
for (const [lp, p] of [[2800,6929],[4135,1846],[4515,521],[4830,1]] as [number,number][]) {
  console.log(lp, p, rankOf(lp, p));
}
