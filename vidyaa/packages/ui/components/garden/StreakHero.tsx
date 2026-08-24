/** 4.3 StreakHero — Sun + flame 23 + embers */
export function StreakHero({ name, streak }: { name:string, streak:number }){
  return <div className="streak-hero">{name} — {streak} day streak</div>;
}
