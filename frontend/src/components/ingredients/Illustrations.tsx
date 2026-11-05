import { useId } from 'react'

import type { ChapterIllustration } from '../../api/types'
import plasterBauble from '../../assets/design/plaster-bauble.webp'
import { Flame } from '../product/Flame'
import styles from './Illustrations.module.css'

/** Fine grain drawn with an SVG noise filter (linen, plaster). */
export function Grain({ frequency, seed, tint, opacity }: {
  frequency: string
  seed: number
  tint: string
  opacity: number
}) {
  const id = useId()
  return (
    <svg className={styles.grain} style={{ opacity }} width="100%" height="100%" aria-hidden="true">
      <filter id={id}>
        <feTurbulence type="fractalNoise" baseFrequency={frequency} numOctaves={3} seed={seed} />
        <feColorMatrix values={tint} />
      </filter>
      <rect width="100%" height="100%" filter={`url(#${id})`} />
    </svg>
  )
}

function Soy() {
  return (
    <div className={`${styles.art} ${styles.soy}`}>
      <div className={styles.soyPool} />
      <div className={styles.soyShine} />
      <span className={styles.flake} style={{ left: '14%', bottom: '20%', width: 22, height: 16, background: '#D8BC86' }} />
      <span className={styles.flake} style={{ left: '17%', bottom: '25%', width: 20, height: 15, background: '#CFAF74' }} />
      <span className={styles.flake} style={{ left: '20%', bottom: '19%', width: 22, height: 16, background: '#DCC28E' }} />
    </div>
  )
}

function Plaster() {
  return (
    <div className={`${styles.art} ${styles.plaster}`}>
      <Grain frequency="0.7" seed={9} tint="0 0 0 0 .5  0 0 0 0 .47  0 0 0 0 .42  0 0 0 .45 0" opacity={0.55} />
      <span className={styles.pore} style={{ left: '62%', top: '40%', width: 7, height: 7 }} />
      <span className={styles.pore} style={{ left: '71%', top: '58%', width: 5, height: 5 }} />
      <span className={styles.pore} style={{ left: '54%', top: '66%', width: 9, height: 9 }} />
      <img className={styles.vessel} src={plasterBauble} alt="" />
    </div>
  )
}

function Wick() {
  return (
    <div className={`${styles.art} ${styles.wick}`}>
      <div className={styles.wickGlow} />
      <div className={styles.candle} />
      <div className={styles.wickStem}>
        <Flame x={50} y={90} glow={false} />
      </div>
      <span className={styles.wisp} />
    </div>
  )
}

function Fragrance() {
  return (
    <div className={`${styles.art} ${styles.fragrance}`}>
      <svg className={styles.sprigs} viewBox="0 0 800 460" preserveAspectRatio="xMaxYMid slice">
        <g fill="none" stroke="#C9D2B4" strokeWidth="2" strokeLinecap="round">
          <path d="M640 470 C 630 380, 650 300, 610 200" />
          <path d="M630 380 c -30 -10 -50 -30 -56 -56 M628 330 c 28 -8 46 -26 52 -52 M622 280 c -26 -10 -42 -28 -46 -52 M616 236 c 22 -8 36 -24 40 -44" />
          <path d="M720 470 C 720 400, 700 330, 730 250" />
          <path d="M716 410 c 24 -12 38 -30 40 -54 M712 360 c -22 -10 -34 -28 -36 -50 M718 310 c 20 -10 30 -26 32 -46" />
        </g>
        <g fill="#E6D9B8" opacity=".75">
          <circle cx="606" cy="196" r="6" />
          <circle cx="732" cy="246" r="5" />
          <circle cx="574" cy="270" r="4" />
        </g>
      </svg>
    </div>
  )
}

function Colour({ colors }: { colors: string[] }) {
  return (
    <div
      className={`${styles.art} ${styles.colour}`}
      style={{ gridTemplateColumns: `repeat(${Math.max(colors.length, 1)}, minmax(0, 1fr))` }}
    >
      {colors.map((color, index) => (
        <span key={`${index}-${color}`} style={{ background: color }} />
      ))}
    </div>
  )
}

interface ChapterArtProps {
  kind: ChapterIllustration
  /** For the colour stripes: the chapter's swatch colours. */
  colors: string[]
}

/** The drawn banner pictures from the design (placeholders for real photos). */
export function ChapterArt({ kind, colors }: ChapterArtProps) {
  switch (kind) {
    case 'soy':
      return <Soy />
    case 'plaster':
      return <Plaster />
    case 'wick':
      return <Wick />
    case 'fragrance':
      return <Fragrance />
    case 'colour':
      return <Colour colors={colors} />
    default:
      return <div className={styles.art} />
  }
}
