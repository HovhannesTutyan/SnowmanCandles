import { useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'
import { useLocation } from 'react-router'

import { useCart } from '../../context/cart'
import { useCartDetails } from '../../hooks/useCartDetails'
import { useI18n } from '../../i18n/context'
import { Link } from '../../i18n/Link'
import { CloseIcon } from '../icons'
import styles from './Cart.module.css'
import { CartLineItem } from './CartLineItem'
import { CartTotals } from './CartTotals'

/** The basket sliding in from the side (after "Add to basket", or the bag icon). */
export function CartPanel() {
  const { panelOpen, closePanel } = useCart()
  const { pathname } = useLocation()

  // Moving to another page closes it.
  useEffect(() => {
    closePanel()
  }, [pathname, closePanel])

  if (!panelOpen) return null
  return createPortal(<PanelContent onClose={closePanel} />, document.body)
}

function PanelContent({ onClose }: { onClose: () => void }) {
  const { t } = useI18n()
  const { count } = useCart()
  const { items, subtotal, error, retry, canCheckout } = useCartDetails()
  const panelRef = useRef<HTMLDivElement>(null)

  // Focus moves into the panel, stays there, and goes back to the opener on close.
  useEffect(() => {
    const opener = document.activeElement as HTMLElement | null
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    panelRef.current?.querySelector<HTMLElement>('button')?.focus()

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault()
        onClose()
      } else if (event.key === 'Tab' && panelRef.current) {
        const focusable = panelRef.current.querySelectorAll<HTMLElement>('button:not(:disabled), a[href]')
        const first = focusable[0]
        const last = focusable[focusable.length - 1]
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault()
          last.focus()
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault()
          first.focus()
        }
      }
    }
    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('keydown', onKeyDown)
      document.body.style.overflow = previousOverflow
      opener?.focus?.()
    }
  }, [onClose])

  return (
    <div
      className={styles.overlay}
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose()
      }}
    >
      <div ref={panelRef} className={styles.panel} role="dialog" aria-modal="true" aria-labelledby="cart-panel-title">
        <div className={styles.panelHead}>
          <h2 id="cart-panel-title" className={styles.panelTitle}>
            {t.basket.title}
            {count > 0 && <span className={styles.panelCount}>{t.basket.count(count)}</span>}
          </h2>
          <button type="button" className={styles.close} aria-label={t.basket.close} onClick={onClose}>
            <CloseIcon size={20} />
          </button>
        </div>

        {items.length === 0 ? (
          <div className={styles.empty}>
            <p className={styles.emptyTitle}>{t.basket.empty}</p>
            <p className={styles.emptyText}>{t.basket.emptyHint}</p>
            <Link to="/#winter" className={styles.primaryButton} onClick={onClose}>
              {t.basket.continueShopping}
            </Link>
          </div>
        ) : (
          <>
            <ul className={styles.panelLines}>
              {items.map((item) => (
                <CartLineItem key={`${item.line.key}|${item.line.scent ?? ''}`} item={item} compact onNavigate={onClose} />
              ))}
            </ul>
            <div className={styles.panelFoot}>
              {error && (
                <p className={styles.lineWarning} role="alert">
                  {t.basket.loadFailed}{' '}
                  <button type="button" className={styles.textButton} onClick={retry}>
                    {t.basket.retry}
                  </button>
                </p>
              )}
              <CartTotals subtotal={subtotal} />
              <div className={styles.panelButtons}>
                <Link to="/basket" className={styles.secondaryButton}>
                  {t.basket.viewBasket}
                </Link>
                {canCheckout ? (
                  <Link to="/checkout" className={styles.primaryButton}>
                    {t.basket.checkout}
                  </Link>
                ) : (
                  <span className={`${styles.primaryButton} ${styles.buttonDisabled}`} aria-disabled="true">
                    {t.basket.checkout}
                  </span>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
