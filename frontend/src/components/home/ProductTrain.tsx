import { Link } from 'react-router'

import type { ShopItem } from '../../api/types'
import { itemKey, itemPath } from '../../lib/items'
import { repeatToLength } from '../../lib/repeat'
import styles from './ProductTrain.module.css'

interface ProductTrainProps {
  items: ShopItem[]
}

/** The endless row of product chips along the bottom of the hero. */
export function ProductTrain({ items }: ProductTrainProps) {
  if (items.length === 0) return null

  const row = repeatToLength(items, 8)

  return (
    <div className={styles.train}>
      <ul className={styles.track} aria-label="Pieces in the collection">
        {/* Two identical halves so the -50% slide loops seamlessly; only the first is announced. */}
        {[0, 1].map((half) =>
          row.map((item, index) => {
            const hidden = half === 1 || index >= items.length
            return (
              <li key={`${half}-${index}-${itemKey(item)}`} aria-hidden={hidden || undefined}>
                <Link to={itemPath(item)} className={styles.chip} tabIndex={hidden ? -1 : undefined}>
                  <span className={styles.chipImage}>
                    <img src={item.image} alt="" loading="lazy" />
                  </span>
                  <span className={styles.chipName}>{item.title}</span>
                </Link>
              </li>
            )
          }),
        )}
      </ul>
    </div>
  )
}
