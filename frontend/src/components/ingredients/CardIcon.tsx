import type { ReactNode } from 'react'

import type { CardIcon as CardIconName } from '../../api/types'

const PATHS: Record<CardIconName, ReactNode> = {
  braid: (
    <>
      <path d="M14 8c4 2 4 6 0 8s-4 6 0 8 4 6 0 8" />
      <path d="M22 8c-4 2-4 6 0 8s4 6 0 8-4 6 0 8" />
    </>
  ),
  wood: (
    <>
      <rect x="12" y="6" width="12" height="26" rx="2" />
      <path d="M15 10v18M19 12v16" />
    </>
  ),
  clock: (
    <>
      <circle cx="18" cy="18" r="12" />
      <path d="M18 11v7l5 3" />
    </>
  ),
  scissors: (
    <>
      <path d="M8 28 26 10" />
      <circle cx="10" cy="10" r="4" />
      <circle cx="10" cy="26" r="4" />
      <path d="M13 13l15 15" />
    </>
  ),
  leaf: (
    <>
      <path d="M8 28C8 14 16 8 30 6c-1 14-8 22-22 22Z" />
      <path d="M8 28 22 14" />
    </>
  ),
  drop: <path d="M18 5c5 7 9 11 9 16a9 9 0 0 1-18 0c0-5 4-9 9-16Z" />,
}

/** Line icons for the chapter cards, chosen in the admin. */
export function CardIcon({ name }: { name: CardIconName }) {
  return (
    <svg width="36" height="36" viewBox="0 0 36 36" fill="none" stroke="#2F6B4F" strokeWidth="1.6"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {PATHS[name] ?? PATHS.leaf}
    </svg>
  )
}
