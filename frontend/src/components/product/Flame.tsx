import styles from './Flame.module.css'

interface FlameProps {
  /** Wick position in % of the image box, from the left and from the bottom. */
  x: number
  y: number
  size?: 'large' | 'small'
  /** The warm halo around a large flame. */
  glow?: boolean
}

/**
 * An animated candle flame (and warm glow) placed over the wick of a product image.
 * Render it inside a `position: relative` box that is exactly the size of the image.
 */
export function Flame({ x, y, size = 'large', glow = true }: FlameProps) {
  return (
    <>
      {size === 'large' && glow && (
        // The glow sits a little below the flame, as in the design.
        <span className={styles.glow} style={{ left: `${x}%`, bottom: `${y - 20.5}%` }} aria-hidden="true" />
      )}
      <span
        className={`${styles.flame} ${size === 'small' ? styles.small : ''}`}
        style={{ left: `${x}%`, bottom: `${y}%` }}
        aria-hidden="true"
      />
    </>
  )
}
