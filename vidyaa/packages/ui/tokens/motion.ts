export const motion = {
  easeSoft: 'cubic-bezier(0.4, 0.0, 0.2, 1)',
  durations: { micro: '200ms', page: '400ms', celebration: '2000ms' },
  animations: {
    streakFlame: '1.5s ease-soft',
    chapterUnlock: '1s ease-soft',
    bloomPetals: '2s ease-soft',
    badge: '700ms bounce-soft',
    hoverLift: '200ms ease-soft',
    pageTransition: '300ms ease-soft',
  },
  respectReducedMotion: true, // @media (prefers-reduced-motion: reduce) -> instant
} as const;
