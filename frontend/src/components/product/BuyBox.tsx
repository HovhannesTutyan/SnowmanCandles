import { useId, useState, type ReactNode } from 'react'
import { Link } from 'react-router'

import type { CollectionDetail, ProductDetail } from '../../api/types'
import { useCart } from '../../context/cart'
import { useSite } from '../../context/site'
import { useFlash } from '../../hooks/useFlash'
import { itemKey, productPath } from '../../lib/items'
import { Accordion, type AccordionItem } from './Accordion'
import styles from './BuyBox.module.css'

const LOW_STOCK = 5
const MAX_QUANTITY = 20

interface BuyBoxProps {
  product: ProductDetail
  /** Full page width (under the showcase): facts and accordion go in a second column. */
  wide?: boolean
}

function isCollection(product: ProductDetail): product is CollectionDetail {
  return product.product_type === 'collection'
}

export function BuyBox({ product, wide = false }: BuyBoxProps) {
  const { content, formatPrice } = useSite()
  const { addItem } = useCart()
  const [scent, setScent] = useState<string | null>(product.scents[0] ?? null)
  const [quantity, setQuantity] = useState(1)
  const [added, flashAdded] = useFlash(2200)
  const [addCount, setAddCount] = useState(0)
  const scentLabelId = useId()

  const maxQuantity = Math.max(1, Math.min(product.stock, MAX_QUANTITY))
  const soldOut = !product.is_available

  const handleAdd = () => {
    addItem({ key: itemKey(product), scent, quantity })
    setAddCount((n) => n + 1)
    flashAdded()
  }

  const kicker = product.is_featured
    ? `${product.product_type_label} · ${content.collection_eyebrow}`
    : product.product_type_label

  const facts: { label: string; value: string; icon: ReactNode }[] = [
    { label: 'Burn time', value: product.burn_time, icon: <BurnIcon /> },
    { label: 'Size', value: product.size, icon: <SizeIcon /> },
    { label: 'Ships in', value: content.ships_in, icon: <TruckIcon /> },
  ].filter((fact) => fact.value)

  // Panels with no text are left out.
  const accordion: AccordionItem[] = []
  if (product.details) accordion.push({ title: 'Details', content: product.details })
  if (content.care_text) {
    accordion.push({
      title: 'Candle care',
      content: (
        <>
          {content.care_text}{' '}
          <Link to="/candle-care" className={styles.inlineLink}>
            Read the full care guide
          </Link>
        </>
      ),
    })
  }
  if (content.shipping_text) {
    accordion.push({ title: 'Shipping & returns', content: content.shipping_text })
  }

  return (
    <div className={`${styles.buybox} ${wide ? styles.wide : ''}`}>
      <div className={styles.column}>
        <div>
          <p className={styles.kicker}>{kicker}</p>
          <h1 className={styles.title}>{product.title}</h1>
          <svg className={styles.stroke} viewBox="0 0 300 16" width="240" height="14" aria-hidden="true">
            <path d="M4 10c40-6 90-8 140-4s100 4 152-2" fill="none" stroke="var(--accent)"
              strokeWidth="5" strokeLinecap="round" />
          </svg>
          <div className={styles.priceRow}>
            <span className={styles.price}>{formatPrice(product.price)}</span>
            {content.price_note && <span className={styles.muted}>{content.price_note}</span>}
          </div>
          {soldOut ? (
            <p className={`${styles.stock} ${styles.stockOut}`}>Sold out — back soon</p>
          ) : (
            product.stock <= LOW_STOCK && (
              <p className={styles.stock}>Only {product.stock} left</p>
            )
          )}
        </div>

        <p className={styles.lede}>{product.description}</p>

        {product.scents.length > 0 && (
          <div className={styles.scents} role="group" aria-labelledby={scentLabelId}>
            <p id={scentLabelId} className={styles.legend}>
              Scent: <span>{scent}</span>
            </p>
            <div className={styles.pills}>
              {product.scents.map((name) => (
                <button
                  key={name}
                  type="button"
                  className={styles.pill}
                  aria-pressed={name === scent}
                  onClick={() => setScent(name)}
                >
                  {name}
                </button>
              ))}
            </div>
          </div>
        )}

        {isCollection(product) && product.candles.length > 0 && (
          <div>
            <p className={styles.legend}>Includes</p>
            <ul className={styles.included}>
              {product.candles.map((candle) => (
                <li key={candle.slug}>
                  <Link to={productPath('candle', candle.slug)} className={styles.includedItem}>
                    <span className={styles.includedImage} style={{ background: candle.tint }}>
                      <img src={candle.image} alt="" loading="lazy" />
                    </span>
                    {candle.title}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className={styles.buyRow}>
          <div className={styles.stepper}>
            <button
              type="button"
              aria-label="Decrease quantity"
              onClick={() => setQuantity((q) => Math.max(1, q - 1))}
              disabled={soldOut || quantity <= 1}
            >
              −
            </button>
            <span aria-live="polite" aria-label={`Quantity ${quantity}`}>{quantity}</span>
            <button
              type="button"
              aria-label="Increase quantity"
              onClick={() => setQuantity((q) => Math.min(maxQuantity, q + 1))}
              disabled={soldOut || quantity >= maxQuantity}
            >
              +
            </button>
          </div>
          <button
            type="button"
            className={`${styles.addButton} ${added ? styles.addButtonAdded : ''}`}
            onClick={handleAdd}
            disabled={soldOut}
          >
            {soldOut ? (
              'Sold out'
            ) : added ? (
              // Keyed so the pop-in and tick animations replay on every add.
              <span key={addCount} className={styles.addedLabel}>
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <circle cx="12" cy="12" r="11" fill="rgba(255,255,255,.2)" />
                  <path className={styles.check} d="M7 12.5l3.2 3.2L17 9" stroke="#FFFFFF"
                    strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                Added to cart
              </span>
            ) : (
              'Add to cart'
            )}
          </button>
        </div>
      </div>

      <div className={styles.column}>
        {facts.length > 0 && (
          <dl className={styles.facts} style={{ gridTemplateColumns: `repeat(${facts.length}, minmax(0, 1fr))` }}>
            {facts.map((fact) => (
              <div key={fact.label} className={styles.fact}>
                {fact.icon}
                <dt className={styles.factLabel}>{fact.label}</dt>
                <dd className={styles.factValue}>{fact.value}</dd>
              </div>
            ))}
          </dl>
        )}

        {accordion.length > 0 && <Accordion items={accordion} />}
      </div>
    </div>
  )
}

const iconProps = {
  width: 24,
  height: 24,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: '#2F6B4F',
  strokeWidth: 1.6,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
  'aria-hidden': true,
}

function BurnIcon() {
  return (
    <svg {...iconProps}>
      <path d="M12 3c2.5 3.2 4 5.2 4 7.5a4 4 0 0 1-8 0C8 8.2 9.5 6.2 12 3Z" />
      <path d="M6 21h12" />
    </svg>
  )
}

function SizeIcon() {
  return (
    <svg {...iconProps}>
      <path d="M3 9h18M3 15h18M9 3v18" />
    </svg>
  )
}

function TruckIcon() {
  return (
    <svg {...iconProps}>
      <path d="M3 7h11v9H3zM14 10h4l3 3v3h-7" />
      <circle cx="7" cy="18" r="2" />
      <circle cx="17" cy="18" r="2" />
    </svg>
  )
}
