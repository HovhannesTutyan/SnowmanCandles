
import type { ShopItem } from '../../api/types'
import { useCart } from '../../context/cart'
import { useFlash } from '../../hooks/useFlash'
import { useI18n } from '../../i18n/context'
import { Link } from '../../i18n/Link'
import type { PriceFormatter } from '../../lib/format'
import { itemKey, itemPath } from '../../lib/items'
import styles from './ProductCard.module.css'

interface ProductCardProps {
  item: ShopItem
  formatPrice: PriceFormatter
}

export function ProductCard({ item, formatPrice }: ProductCardProps) {
  const { addItem } = useCart()
  const [added, flashAdded] = useFlash(2000)
  const { t } = useI18n()

  const handleAdd = () => {
    addItem({ key: itemKey(item), scent: null, quantity: 1 })
    flashAdded()
  }

  return (
    <article className={`${styles.card} lift reveal`}>
      <div className={styles.media} style={{ background: item.tint }}>
        <span className={styles.badge}>{t.productType[item.product_type]}</span>
        <img
          className={`${styles.image} pimg`}
          src={item.image}
          alt={item.title}
          loading="lazy"
          decoding="async"
        />
      </div>
      <div className={styles.body}>
        <h3 className={styles.title}>
          {/* Stretched over the whole card, so the card opens the product page. */}
          <Link to={itemPath(item)} className={styles.titleLink}>
            {item.title}
          </Link>
        </h3>
        <p className={styles.description}>{item.description}</p>
        <div className={styles.footer}>
          <span className={styles.price}>{formatPrice(item.price)}</span>
          <button
            type="button"
            className={`${styles.button} ${added ? styles.buttonAdded : ''}`}
            onClick={handleAdd}
          >
            {added ? t.cart.added : t.cart.add}
            <span className="visually-hidden">: {item.title}</span>
          </button>
        </div>
      </div>
    </article>
  )
}
