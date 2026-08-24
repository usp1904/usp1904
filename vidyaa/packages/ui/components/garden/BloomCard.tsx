export function BloomCard({ stage, subjectColor }: { stage:'Seed'|'Sprout'|'Bud'|'Bloom'|'Full Bloom', subjectColor:string }){
  return <div style={{ borderColor: subjectColor }}>{stage}</div>;
}
