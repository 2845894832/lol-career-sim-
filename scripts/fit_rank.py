import math, bisect

TIERS=[("黑铁",0),("青铜",400),("白银",900),("黄金",1500),("铂金",2100),("翡翠",2500),("钻石",2700),("大师",2800),("宗师",3800),("王者",4500)]
N=len(TIERS)-1
POP=10000
SEED=20261101
KING=200; SECOND=600; KEEPR=0.35

def tier_index(lp):
    i=0
    for k,(_,at) in enumerate(TIERS):
        if lp>=at: i=k
    return i

def gain(idx, base, keep=KEEPR):
    f=1-(1-keep)*min(idx,N)/N
    return max(1,round(base*f))

def advance(lp, rate, weeks, keep=KEEPR):
    cur=lp; left=weeks
    while left>0:
        idx=tier_index(cur); g=gain(idx,rate,keep)
        nxt=TIERS[idx+1][1] if idx+1<len(TIERS) else None
        if nxt is None:
            cur+=g*left; break
        need=math.ceil((nxt-cur)/g)
        if need>=left: cur+=g*left; break
        cur=nxt; left-=need
    return cur

def hash01(i,seed):
    h=((i+1)*0x9e3779b1)&0xffffffff
    h^=seed
    h=((h^(h>>15))*0x85ebca6b)&0xffffffff
    h=((h^(h>>13))*0xc2b2ae35)&0xffffffff
    return ((h^(h>>16))&0xffffffff)/4294967296

HA=[hash01(i,SEED) for i in range(POP)]
HB=[hash01(i+50021,SEED) for i in range(POP)]

def build(base,spread,rate,rspread=0.10):
    starts=[max(0,round(base+(a-0.5)*2*spread)) for a in HA]
    rates=[rate*(1+(b-0.5)*2*rspread) for b in HB]
    # scores[w] = 排序后的对手分数（w 周后）
    scores={}
    for w in range(0,9):
        arr=sorted(advance(s,r,w) for s,r in zip(starts,rates))
        scores[w]=arr
    return scores

def place(scores,lp,w):
    arr=scores[w]
    return len(arr)-bisect.bisect_right(arr,lp)+1

def tier_at(lp,pl):
    idx=tier_index(lp)
    if idx>=N and pl>KING: idx=N-1
    elif idx>=N-1 and pl>SECOND: idx=min(idx,N-2)
    return TIERS[max(0,idx)][0]

best=None
for base in range(2600,3401,200):
  for spread in range(400,1001,200):
    for rate in range(100,301,50):
      scores=build(base,spread,rate)
      p0=place(scores,2800,0)
      if not (600<p0<8000): continue
      for start in range(500,1300,100):
        lp=2800; rows=[]
        for w in range(1,9):
            if w<=5: lp+=gain(tier_index(lp),start)
            rows.append((lp,place(scores,lp,w),tier_at(lp,place(scores,lp,w))))
        four,five,eight=rows[3],rows[4],rows[7]
        six,seven=rows[5],rows[6]
        if four[2]=="宗师" and five[2]=="王者" and six[2]=="王者" and seven[2]=="王者" and eight[2]=="宗师":
            cost=abs(four[1]-500)+abs(five[1]-150)+abs(eight[1]-400)
            if best is None or cost<best[0]:
                best=(cost,base,spread,rate,start,p0,rows)
if best:
    c,base,spread,rate,start,p0,rows=best
    print(f"base={base} spread={spread} rate={rate} start={start} 开局第{p0}名 cost={c}")
    for w,(lp,pl,t) in enumerate(rows,1):
        tag="（这周没打）" if w>5 else ""
        print(f"  第{w}周 分{lp} 第{pl}名 {t}{tag}")
else:
    print("无解")
