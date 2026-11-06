import { useState } from 'react'

import type { ProductDetail } from '../../api/types'
import { useI18n } from '../../i18n/context'
import type { Messages } from '../../i18n/messages/en'
import { Snowfall, type Flake } from '../home/Snowfall'
import { Flame } from './Flame'
import styles from './ProductGallery.module.css'

// From the product page design.
const LIT_FLAKES: Flake[] = [
  [10, 5, 10, -3], [24, 3, 8, -6], [41, 6, 12, -1], [58, 4, 9, -4], [73, 5, 11, -8], [88, 3, 10, -2],
]

type View =
  | { kind: 'main'; label: string }
  | { kind: 'lit'; label: string }
  | { kind: 'photo'; label: string; image: string }

function buildViews(product: ProductDetail, t: Messages): View[] {
  return [
    { kind: 'main', label: t.product.mainView },
    ...(product.flame ? [{ kind: 'lit', label: t.product.lit } as const] : []),
    ...product.gallery.map((photo) => ({ kind: 'photo', label: photo.label, image: photo.image }) as const),
  ]
}

interface ProductGalleryProps {
  product: ProductDetail
}

/**
 * The stage and its thumbnails: the main cut-out, an optional "Lit" view with an
 * animated flame on the wick, and any extra photos uploaded in the admin.
 */
export function ProductGallery({ product }: ProductGalleryProps) {
  const { t } = useI18n()
  const views = buildViews(product, t)
  const [active, setActive] = useState(0)
  const view = views[active] ?? views[0]
  const lit = view.kind === 'lit'

  return (
    <div className={styles.gallery}>
      <div
        className={`${styles.stage} ${lit ? styles.stageLit : ''}`}
        style={{ backgroundColor: lit ? undefined : product.tint }}
      >
        {lit && <Snowfall flakes={LIT_FLAKES} />}
        <span className={`${styles.chip} ${styles.chipTopLeft}`}>{t.product.uniqueChip}</span>

        {/* Keyed so the entrance animation replays on every switch. */}
        <div key={active} className={styles.view}>
          {view.kind === 'photo' ? (
            <img className={styles.photo} src={view.image} alt={t.product.photoAlt(product.title, view.label)} />
          ) : (
            <>
              <div className={`${styles.floor} ${lit ? styles.floorDark : ''}`} />
              <div className="bob">
                <div className={`${styles.piece} ${lit ? styles.pieceLit : styles.zoomable}`}>
                  <img
                    src={product.image}
                    alt={lit ? t.product.litAlt(product.title) : product.title}
                  />
                  {lit && product.flame && <Flame x={product.flame.x} y={product.flame.y} />}
                </div>
              </div>
            </>
          )}
        </div>

        <span className={`${styles.chip} ${styles.chipBottomRight}`} aria-live="polite">
          {view.label}
        </span>
      </div>

      {views.length > 1 && (
        <div className={styles.thumbs} role="group" aria-label={t.product.views}>
          {views.map((v, index) => (
            <button
              key={`${v.kind}-${index}`}
              type="button"
              className={`${styles.thumb} ${v.kind === 'lit' ? styles.thumbLit : ''}`}
              style={{ backgroundColor: v.kind === 'lit' ? undefined : product.tint }}
              aria-label={v.label}
              aria-pressed={index === active}
              onClick={() => setActive(index)}
            >
              {v.kind === 'photo' ? (
                <img className={styles.thumbPhoto} src={v.image} alt="" loading="lazy" />
              ) : (
                <span className={styles.thumbPiece}>
                  <img src={product.image} alt="" />
                  {v.kind === 'lit' && product.flame && (
                    <Flame x={product.flame.x} y={product.flame.y} size="small" />
                  )}
                </span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
