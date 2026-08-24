import { colors } from '../../tokens/colors';
export function Button({ children, variant='primary', ...props }: any){
  const bg = variant==='primary' ? colors.chakraBlue900 : variant==='leaf' ? colors.leaf500 : 'white';
  const color = variant==='ghost' ? colors.chakraBlue900 : 'white';
  return <button style={{ background: bg, color, borderRadius: 999, padding: '10px 18px', fontWeight: 700, border: variant==='ghost' ? `1.5px solid ${colors.chakraBlue900}` : 'none' }} {...props}>{children}</button>
}
