import type { ShopItem } from '../../api/types'
import type { PriceFormatter } from '../../lib/format'
import { useI18n } from '../../i18n/context'
import { itemKey } from '../../lib/items'
import { ArrowRightIcon } from '../icons'
import styles from './CollectionGrid.module.css'
import { ProductCard } from './ProductCard'

interface CollectionGridProps {
  eyebrow: string
  title: string
  items: ShopItem[]
  formatPrice: PriceFormatter
}

/** The featured products ("The winter collection" in the design). */
export function CollectionGrid({ eyebrow, title, items, formatPrice }: CollectionGridProps) {
  const { t } = useI18n()
  return (
    <section id="winter" className={styles.section} aria-labelledby="winter-title">
      <div className={styles.inner}>
        <div className={`${styles.header} reveal`}>
          <div>
            <p className={styles.eyebrow}>{eyebrow}</p>
            <h2 id="winter-title" className={styles.title}>{title}</h2>
          </div>
          <a href="#shop" className={styles.viewAll}>
            {t.home.viewAll}
            <ArrowRightIcon />
          </a>
        </div>

        {items.length > 0 ? (
          <div className={styles.grid}>
            {items.map((item) => (
              <ProductCard key={itemKey(item)} item={item} formatPrice={formatPrice} />
            ))}
          </div>
        ) : (
          <p className={styles.empty}>{t.home.empty}</p>
        )}
      </div>
    </section>
  )
}
