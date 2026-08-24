export const typography = {
  fonts: {
    display: 'Fraunces, serif', // warm storybook 700
    heading: '"Inter Tight", sans-serif', // 600
    body: 'Inter, sans-serif', // 400/500
    mono: '"JetBrains Mono", monospace', // math/code
    hindi: '"Noto Sans Devanagari", sans-serif',
    microcopy: 'Caveat, cursive', // handwritten 600
  },
  scale: {
    displayXl: '56px', // streak
    displayLg: '44px',
    h1: '36px',
    h2: '28px',
    h3: '22px',
    bodyLg: '18px',
    body: '16px',
    caption: '14px',
    microcopy: '18px',
  },
  lineHeight: {
    displayXl: 1.05, displayLg: 1.1, h1: 1.2, h2: 1.25, h3: 1.3, body: 1.6,
  },
} as const;
