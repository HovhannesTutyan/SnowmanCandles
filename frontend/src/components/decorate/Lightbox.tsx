import { useEffect, useRef, type TouchEvent } from 'react'
import { createPortal } from 'react-dom'
import { Link } from 'react-router'

import type { GalleryPicture } from '../../api/types'
import { productPath } from '../../lib/items'
import { ArrowRightIcon, CloseIcon } from '../icons'
import styles from './Lightbox.module.css'

interface LightboxProps {
  pictures: GalleryPicture[]
  index: number
  onIndexChange: (index: number) => void
  onClose: () => void
}

function ArrowLeftIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M19 12H5M11 6l-6 6 6 6" />
    </svg>
  )
}

/**
 * Full-screen picture viewer: arrows, swipe, ← → keys, Esc or × to close.
 * Focus stays inside while open and returns to the opening element afterwards.
 */
export function Lightbox({ pictures, index, onIndexChange, onClose }: LightboxProps) {
  const dialogRef = useRef<HTMLDivElement>(null)
  const touchStart = useRef<number | null>(null)
  const count = pictures.length
  const picture = pictures[index]

  const go = (delta: number) => onIndexChange((index + delta + count) % count)

  // Latest handlers for the document listener, without re-subscribing on every change.
  const keyHandler = useRef<(event: KeyboardEvent) => void>(() => {})
  useEffect(() => {
    keyHandler.current = (event) => {
      if (event.key === 'Escape') {
        event.preventDefault()
        onClose()
      } else if (event.key === 'ArrowRight') {
        event.preventDefault()
        go(1)
      } else if (event.key === 'ArrowLeft') {
        event.preventDefault()
        go(-1)
      } else if (event.key === 'Tab' && dialogRef.current) {
        // Keep focus inside the viewer.
        const focusable = dialogRef.current.querySelectorAll<HTMLElement>('button, a[href]')
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
  })

  useEffect(() => {
    const opener = document.activeElement as HTMLElement | null
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    dialogRef.current?.focus()
    const onKeyDown = (event: KeyboardEvent) => keyHandler.current(event)
    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('keydown', onKeyDown)
      document.body.style.overflow = previousOverflow
      opener?.focus?.()
    }
  }, [])

  const onTouchStart = (event: TouchEvent) => {
    touchStart.current = event.touches[0].clientX
  }
  const onTouchEnd = (event: TouchEvent) => {
    if (touchStart.current === null) return
    const dx = event.changedTouches[0].clientX - touchStart.current
    touchStart.current = null
    if (Math.abs(dx) > 50) go(dx < 0 ? 1 : -1)
  }

  if (!picture) return null

  return createPortal(
    <div
      ref={dialogRef}
      className={styles.backdrop}
      role="dialog"
      aria-modal="true"
      aria-label="Picture viewer"
      tabIndex={-1}
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose() // click the dark backdrop
      }}
      onTouchStart={onTouchStart}
      onTouchEnd={onTouchEnd}
    >
      <span className={styles.counter} aria-live="polite">
        {index + 1} / {count}
      </span>
      <button type="button" className={styles.close} aria-label="Close picture viewer" onClick={onClose}>
        <CloseIcon size={22} />
      </button>
      {count > 1 && (
        <>
          <button type="button" className={`${styles.nav} ${styles.prev}`} aria-label="Previous picture" onClick={() => go(-1)}>
            <ArrowLeftIcon />
          </button>
          <button type="button" className={`${styles.nav} ${styles.next}`} aria-label="Next picture" onClick={() => go(1)}>
            <ArrowRightIcon size={22} />
          </button>
        </>
      )}

      {/* Keyed so the entrance animation replays for every picture. */}
      <figure key={picture.id} className={styles.figure}>
        <img className={styles.image} src={picture.image} alt={picture.alt} />
        <figcaption className={styles.caption}>
          {picture.caption}
          {picture.products.length > 0 && (
            <span className={styles.products}>
              <span className={styles.productsLabel}>In this picture:</span>
              {picture.products.map((product) => (
                <Link
                  key={product.slug}
                  to={productPath(product.product_type === 'collection' ? 'collection' : 'candle', product.slug)}
                  className={styles.product}
                  onClick={onClose}
                >
                  {product.title}
                  <ArrowRightIcon size={14} />
                </Link>
              ))}
            </span>
          )}
        </figcaption>
      </figure>
    </div>,
    document.body,
  )
}
