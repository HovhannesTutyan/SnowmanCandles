import { useCart } from '../../context/cart'
import { useSite } from '../../context/site'
import type { CartItem } from '../../hooks/useCartDetails'
import { useI18n } from '../../i18n/context'
import { Link } from '../../i18n/Link'
import { productPath } from '../../lib/items'
import styles from './Cart.module.css'

interface CartLineItemProps {
  item: CartItem
  /** Smaller layout for the slide-in panel. */
  compact?: boolean
  /** Called when the product link is followed (e.g. to close the panel). */
  onNavigate?: () => void
}

/** One basket line: picture, name, scent, price, quantity buttons and remove. */
export function CartLineItem({ item, compact = false, onNavigate }: CartLineItemProps) {
  const { t } = useI18n()
  const { formatPrice } = useSite()
  const { setQuantity, removeItem } = useCart()
  const { line, details, problem, maxQuantity } = item
  const title = details?.title ?? ''

  if (details === undefined) {
    return <li className={`${styles.line} ${styles.lineLoading}`} aria-hidden="true" />
  }

  const problemText =
    problem === 'gone'
      ? t.basket.gone
      : problem === 'sold_out'
        ? t.basket.soldOut
        : problem === 'too_many' && details
          ? t.basket.tooMany(details.stock)
          : null

  return (
    <li className={`${styles.line} ${compact ? styles.lineCompact : ''} ${problem ? styles.lineProblem : ''}`}>
      <div className={styles.lineImage} style={{ background: details?.tint }}>
        {details?.image && <img src={details.image} alt="" loading="lazy" />}
      </div>

      <div className={styles.lineBody}>
        <div className={styles.lineTop}>
          <div>
            {details ? (
              <Link to={productPath(details.kind, details.slug)} className={styles.lineTitle} onClick={onNavigate}>
                {title}
              </Link>
            ) : (
              <span className={styles.lineTitle}>—</span>
            )}
            {details?.scent && <div className={styles.lineMeta}>{t.basket.scent(details.scent)}</div>}
            {details && line.quantity > 1 && (
              <div className={styles.lineMeta}>{t.basket.each(formatPrice(details.price))}</div>
            )}
          </div>
          {details && <div className={styles.linePrice}>{formatPrice(item.lineTotal.toFixed(2))}</div>}
        </div>

        {problemText && (
          <p className={styles.lineWarning} role="status">
            {problemText}
          </p>
        )}

        <div className={styles.lineActions}>
          {details && problem !== 'sold_out' && (
            <div className={styles.stepper} role="group" aria-label={t.basket.quantityOf(title)}>
              <button
                type="button"
                aria-label={t.cart.decrease}
                onClick={() => setQuantity(line.key, line.scent, line.quantity - 1)}
                disabled={line.quantity <= 1}
              >
                −
              </button>
              <span aria-live="polite">{line.quantity}</span>
              <button
                type="button"
                aria-label={t.cart.increase}
                onClick={() => setQuantity(line.key, line.scent, line.quantity + 1)}
                disabled={line.quantity >= maxQuantity}
              >
                +
              </button>
            </div>
          )}
          <button
            type="button"
            className={styles.remove}
            aria-label={t.basket.removeItem(title || t.basket.remove)}
            onClick={() => removeItem(line.key, line.scent)}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"
              strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M4 7h16M10 11v6M14 11v6M6 7l1 12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-12M9 7V4h6v3" />
            </svg>
            <span>{t.basket.remove}</span>
          </button>
        </div>
      </div>
    </li>
  )
}
