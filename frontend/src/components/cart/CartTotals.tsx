import { useSite } from '../../context/site'
import { useI18n } from '../../i18n/context'
import styles from './Cart.module.css'

/** Subtotal, free delivery and total. */
export function CartTotals({ subtotal }: { subtotal: number }) {
  const { t } = useI18n()
  const { content, formatPrice } = useSite()
  const amount = formatPrice(subtotal.toFixed(2))

  return (
    <dl className={styles.totals}>
      <div className={styles.totalsRow}>
        <dt>{t.basket.subtotal}</dt>
        <dd>{amount}</dd>
      </div>
      <div className={styles.totalsRow}>
        <dt>{t.basket.delivery}</dt>
        <dd className={styles.free}>{t.basket.free}</dd>
      </div>
      {content.delivery_text && <div className={styles.deliveryNote}>{content.delivery_text}</div>}
      <div className={`${styles.totalsRow} ${styles.totalsGrand}`}>
        <dt>{t.basket.total}</dt>
        <dd>{amount}</dd>
      </div>
    </dl>
  )
}
