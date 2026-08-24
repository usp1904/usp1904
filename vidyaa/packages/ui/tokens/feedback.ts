export const correctFeedback = [
  "You didn't just get this right — you understood it. That's different.",
  "Beautiful. The way you skipped the hint? Confidence.",
  "Watch out. You're becoming dangerous. In a good way.",
  "If this were cricket, that was a cover drive for four.",
  "Your garden just grew another petal.",
  "Einstein probably also struggled with this once. You figured it out faster.",
] as const;

export function pickFeedback(){ return correctFeedback[Math.floor(Math.random()*correctFeedback.length)]; }
