import { Link } from 'react-router'

import type { ShopItem } from '../../api/types'
import { useSite } from '../../context/site'
import { itemKey, itemPath } from '../../lib/items'
import { ArrowRightIcon } from '../icons'
import styles from './RelatedProducts.module.css'

export function RelatedProducts({ items }: { items: ShopItem[] }) {
  const { formatPrice } = useSite()
  if (items.length === 0) return null

  return (
    <section className={styles.related} aria-labelledby="related-title">
      <div className={styles.inner}>
        <div className={`${styles.head} reveal`}>
          <h2 id="related-title" className={styles.title}>You might also love</h2>
          <Link to="/#winter" className={styles.back}>
            Back to the collection
            <ArrowRightIcon />
          </Link>
        </div>
        <ul className={styles.cards}>
          {items.map((item) => (
            <li key={itemKey(item)}>
              <Link to={itemPath(item)} className={`${styles.card} lift reveal`}>
                <div className={styles.cardImage} style={{ background: item.tint }}>
                  <img className="pimg" src={item.image} alt="" loading="lazy" />
                </div>
                <div className={styles.cardBody}>
                  <div className={styles.cardTitle}>{item.title}</div>
                  <div className={styles.cardMeta}>
                    {item.product_type_label} · {formatPrice(item.price)}
                  </div>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
