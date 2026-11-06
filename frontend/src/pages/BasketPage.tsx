import cartStyles from '../components/cart/Cart.module.css'
import { CartLineItem } from '../components/cart/CartLineItem'
import { CartTotals } from '../components/cart/CartTotals'
import { ArrowRightIcon } from '../components/icons'
import { useCart } from '../context/cart'
import { useSite } from '../context/site'
import { useCartDetails } from '../hooks/useCartDetails'
import { useI18n } from '../i18n/context'
import { Link } from '../i18n/Link'
import styles from './BasketPage.module.css'

/** /basket: every line with quantity buttons, totals and "Proceed to checkout". */
export function BasketPage() {
  const { t } = useI18n()
  const { content } = useSite()
  const { count } = useCart()
  const { items, subtotal, error, retry, canCheckout, loading } = useCartDetails()
  const hasProblems = items.some((item) => item.problem)

  return (
    <div className={styles.page}>
      <title>{`${t.basket.pageTitle} — ${content.studio_name}`}</title>
      <div className={styles.inner}>
        <header className={styles.head}>
          <h1 className={styles.title}>{t.basket.title}</h1>
          {count > 0 && <span className={styles.count}>{t.basket.count(count)}</span>}
        </header>

        {items.length === 0 ? (
          <div className={styles.card}>
            <div className={cartStyles.empty}>
              <p className={cartStyles.emptyTitle}>{t.basket.empty}</p>
              <p className={cartStyles.emptyText}>{t.basket.emptyHint}</p>
              <Link to="/#winter" className={cartStyles.primaryButton}>
                {t.basket.continueShopping}
              </Link>
            </div>
          </div>
        ) : (
          <div className={styles.grid}>
            <section className={styles.card} aria-label={t.basket.title} aria-busy={loading}>
              <ul className={styles.lines}>
                {items.map((item) => (
                  <CartLineItem key={`${item.line.key}|${item.line.scent ?? ''}`} item={item} />
                ))}
              </ul>
              <Link to="/#winter" className={styles.back}>
                ← {t.basket.continueShopping}
              </Link>
            </section>

            <aside className={`${styles.card} ${styles.summary}`}>
              {error && (
                <p className={cartStyles.lineWarning} role="alert">
                  {t.basket.loadFailed}{' '}
                  <button type="button" className={cartStyles.textButton} onClick={retry}>
                    {t.basket.retry}
                  </button>
                </p>
              )}
              <CartTotals subtotal={subtotal} />
              {hasProblems && (
                <p className={cartStyles.lineWarning} role="status">
                  {t.basket.fixProblems}
                </p>
              )}
              {canCheckout ? (
                <Link to="/checkout" className={`${cartStyles.primaryButton} ${styles.checkout}`}>
                  {t.basket.proceed}
                  <ArrowRightIcon />
                </Link>
              ) : (
                <span className={`${cartStyles.primaryButton} ${cartStyles.buttonDisabled} ${styles.checkout}`}
                  aria-disabled="true">
                  {t.basket.proceed}
                </span>
              )}
            </aside>
          </div>
        )}
      </div>
    </div>
  )
}
