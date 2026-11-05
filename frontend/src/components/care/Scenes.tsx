import type { CSSProperties, ReactNode } from 'react'

import carouselCandle from '../../assets/design/carousel-candle.webp'
import hollyBaubleCandle from '../../assets/design/holly-bauble-candle.webp'
import pineGarlandBauble from '../../assets/design/pine-garland-bauble.webp'
import vintageRoadsterCandle from '../../assets/design/vintage-roadster-candle.webp'
import { Flame } from '../product/Flame'
import styles from './Scenes.module.css'

// The roadster's wick, as on its product page.
const ROADSTER_WICK = { x: 47.6, y: 86.5 }

function Bokeh({ style }: { style: CSSProperties }) {
  return <span className={styles.bokeh} style={style} aria-hidden="true" />
}

interface SceneProps {
  /** A photo uploaded in the admin replaces the illustrated scene. */
  photo: string | null
  label: string
  children?: ReactNode
}

/** Hero: painted candles glowing on a table in a dark, warm room. */
export function CandlelitScene({ photo, label }: SceneProps) {
  if (photo) {
    return <img className={`${styles.hero} ${styles.photo}`} src={photo} alt={label} />
  }
  return (
    <div className={`${styles.hero} ${styles.heroScene}`} role="img" aria-label={label}>
      <Bokeh style={{ left: '8%', top: '14%', width: 46, height: 46 }} />
      <Bokeh style={{ left: '20%', top: '30%', width: 22, height: 22, animationDelay: '-4s' }} />
      <Bokeh style={{ left: '78%', top: '12%', width: 60, height: 60, animationDelay: '-7s' }} />
      <Bokeh style={{ left: '88%', top: '38%', width: 26, height: 26, animationDelay: '-2s' }} />
      <Bokeh style={{ left: '64%', top: '8%', width: 18, height: 18, animationDelay: '-10s' }} />
      <div className={styles.table} />
      <div className={styles.warm} />
      <img className={styles.carousel} src={carouselCandle} alt="" />
      <div className={styles.roadster}>
        <img src={vintageRoadsterCandle} alt="" />
        <Flame x={ROADSTER_WICK.x} y={ROADSTER_WICK.y} glow={false} />
      </div>
      <img className={styles.holly} src={hollyBaubleCandle} alt="" />
    </div>
  )
}

/** Fragrance section: painted bauble candles on a warm wooden shelf. */
export function ShelfScene({ photo, label, children }: SceneProps) {
  return (
    <div className={`${styles.shelf} reveal`}>
      {photo ? (
        <img className={styles.photo} src={photo} alt={label} />
      ) : (
        <div className={styles.shelfScene} role="img" aria-label={label}>
          <Bokeh style={{ left: '12%', top: '10%', width: 70, height: 70, background: 'rgba(255,240,210,.5)' }} />
          <Bokeh
            style={{ left: '70%', top: '18%', width: 40, height: 40, background: 'rgba(255,240,210,.45)', animationDelay: '-6s' }}
          />
          <div className={styles.shelfBoard} />
          <div className={styles.shelfEdge} />
          <img className={styles.pine} src={pineGarlandBauble} alt="" />
          <img className={styles.hollyOnShelf} src={hollyBaubleCandle} alt="" />
        </div>
      )}
      {children}
    </div>
  )
}
