export const streakMessages: Record<string,string> = {
  '1': "Your garden has its first seed. Tomorrow, plant another.",
  '3': "Three days in. The soil is warming up.",
  '7': "A whole week of tending. Your garden is starting to show.",
  '14': "Half a moon of consistency. Beautiful.",
  '30': "A month. You're not just learning — you're growing.",
  '50': "Fifty days. You've outlasted most resolutions in history.",
  '100': "Triple digits. Your garden is unrecognizable from where it began.",
  '365': "A whole year. You are the garden.",
  'broken': "The garden never judges. Pick up where you left off.",
  'atRisk': "Your streak is one tap away from continuing. Just one small seed today.",
};

export function getStreakMessage(day: number, opts?: { broken?: boolean, atRisk?: boolean }){
  if(opts?.broken) return streakMessages['broken'];
  if(opts?.atRisk) return streakMessages['atRisk'];
  const keys = [1,3,7,14,30,50,100,365].filter(k=>k<=day).sort((a,b)=>b-a);
  const nearest = keys[0] ?? 1;
  return streakMessages[String(nearest)];
}
