import type { CSSProperties } from 'react'

import styles from './Snowfall.module.css'

/** [left %, size px, duration s, delay s] */
export type Flake = [number, number, number, number]

// From the homepage design.
const HERO_FLAKES: Flake[] = [
  [52, 6, 11, -2], [58, 4, 9, -6], [63, 7, 13, -1], [69, 3, 8, -4], [74, 5, 12, -8],
  [79, 4, 10, -3], [84, 6, 14, -10], [89, 3, 9, -7], [94, 5, 12, -5], [8, 4, 13, -9],
  [22, 3, 10, -1], [38, 5, 15, -12], [46, 3, 9, -6], [66, 4, 11, -9],
]

export function Snowfall({ flakes = HERO_FLAKES }: { flakes?: Flake[] }) {
  return (
    <div className={styles.snow} aria-hidden="true">
      {flakes.map(([left, size, duration, delay], index) => {
        const style: CSSProperties = {
          left: `${left}%`,
          width: size,
          height: size,
          animationDuration: `${duration}s`,
          animationDelay: `${delay}s`,
        }
        return <span key={index} className={styles.flake} style={style} />
      })}
    </div>
  )
}
