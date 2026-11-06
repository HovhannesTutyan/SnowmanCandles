
import type { ShopItem } from '../../api/types'
import { useSite } from '../../context/site'
import { useI18n } from '../../i18n/context'
import { Link } from '../../i18n/Link'
import { itemKey, itemPath } from '../../lib/items'
import { ArrowRightIcon } from '../icons'
import styles from './RelatedProducts.module.css'

export function RelatedProducts({ items }: { items: ShopItem[] }) {
  const { formatPrice } = useSite()
  const { t } = useI18n()
  if (items.length === 0) return null

  return (
    <section className={styles.related} aria-labelledby="related-title">
      <div className={styles.inner}>
        <div className={`${styles.head} reveal`}>
          <h2 id="related-title" className={styles.title}>{t.product.related}</h2>
          <Link to="/#winter" className={styles.back}>
            {t.product.backToCollection}
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
                    {t.productType[item.product_type]} · {formatPrice(item.price)}
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
