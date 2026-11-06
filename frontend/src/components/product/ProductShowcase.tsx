import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type CSSProperties,
  type KeyboardEvent,
  type PointerEvent,
} from 'react'

import type { ShowcaseView } from '../../api/types'
import { useMediaQuery } from '../../hooks/useMediaQuery'
import { usePrefersReducedMotion } from '../../hooks/usePrefersReducedMotion'
import { useI18n } from '../../i18n/context'
import styles from './ProductShowcase.module.css'

/*
 * React port of the product-showcase "glow pedestal" viewer. The selected view slides
 * onto a glowing ring and the scene takes its colours.
 *   Drag / swipe left-right ... turn to the next view (keep dragging to keep turning)
 *   Drag down / up ............ jump to the view from above / underneath
 *   Click the product ......... zoom in (move the mouse or drag to look around)
 *   Click a side product ...... bring it to the centre
 *   Pills & arrows ............ jump to a view
 *   Keyboard .................. ← → turn, ↑ ↓ top/bottom, Enter zoom, Esc close zoom
 * Unlike the original it removes its listeners on unmount and doesn't auto-play for
 * visitors who prefer reduced motion.
 */

const MOVE_TRAIL_MS = 380
const WHEEL_LOCK_MS = 550

/** `moved`: not a click. `turned`: this drag already changed the view, so no top/bottom jump. */
type Drag = { x: number; y: number; moved: boolean; turned: boolean; item: number | null }

export interface ProductShowcaseProps {
  title: string
  /** Already formatted, e.g. "$34.00". */
  price?: string
  views: ShowcaseView[]
  /** Time per view while auto-playing, or false. */
  autoplayMs?: number | false
  zoom?: number
}

export function ProductShowcase({
  title,
  price,
  views,
  autoplayMs = 4000,
  zoom = 1.9,
}: ProductShowcaseProps) {
  const count = views.length
  const rootRef = useRef<HTMLDivElement>(null)
  const [active, setActive] = useState(0)
  const [zoomed, setZoomed] = useState(false)
  const [moving, setMoving] = useState(false)
  const [touched, setTouched] = useState(false)
  const [hovered, setHovered] = useState(false)
  const [dragging, setDragging] = useState(false)
  const [panning, setPanning] = useState(false)
  const reducedMotion = usePrefersReducedMotion()
  const phone = useMediaQuery('(max-width: 640px)')
  const { t } = useI18n()

  const drag = useRef<Drag | null>(null)
  const moveTimer = useRef<number | undefined>(undefined)
  const wheelLock = useRef(0)

  useEffect(() => () => window.clearTimeout(moveTimer.current), [])

  const setOrigin = (x: string, y: string) => {
    rootRef.current?.style.setProperty('--ps-ox', x)
    rootRef.current?.style.setProperty('--ps-oy', y)
  }

  // Follows the pointer directly, without a render per mouse move.
  const aim = (event: { clientX: number; clientY: number }) => {
    const item = rootRef.current?.querySelector(`[data-i="${active}"]`)
    if (!item) return
    const rect = item.getBoundingClientRect()
    if (!rect.width || !rect.height) return
    const percent = (value: number) => `${Math.min(100, Math.max(0, value * 100))}%`
    setOrigin(percent((event.clientX - rect.left) / rect.width), percent((event.clientY - rect.top) / rect.height))
  }

  const closeZoom = () => {
    setZoomed(false)
    setOrigin('50%', '50%')
  }

  const go = useCallback(
    (index: number, fromUser = false) => {
      const next = ((index % count) + count) % count
      if (next === active) return
      setActive(next)
      setZoomed(false)
      rootRef.current?.style.setProperty('--ps-ox', '50%')
      rootRef.current?.style.setProperty('--ps-oy', '50%')
      setMoving(true)
      window.clearTimeout(moveTimer.current)
      moveTimer.current = window.setTimeout(() => setMoving(false), MOVE_TRAIL_MS)
      if (fromUser) setTouched(true)
    },
    [active, count],
  )

  const findGroup = (group: ShowcaseView['group']) => views.findIndex((view) => view.group === group)

  // ---------- autoplay: until the visitor interacts; pauses on hover ----------
  useEffect(() => {
    if (!autoplayMs || touched || hovered || reducedMotion || count < 2) return
    const timer = window.setTimeout(() => go(active + 1), autoplayMs)
    return () => window.clearTimeout(timer)
  }, [active, autoplayMs, count, go, hovered, reducedMotion, touched])

  // ---------- horizontal wheel / trackpad swipe; vertical scrolling is left to the page ----------
  useEffect(() => {
    const root = rootRef.current
    if (!root) return
    const onWheel = (event: WheelEvent) => {
      if (Math.abs(event.deltaX) < Math.abs(event.deltaY) || Math.abs(event.deltaX) < 12) return
      event.preventDefault()
      const now = Date.now()
      if (now < wheelLock.current) return
      wheelLock.current = now + WHEEL_LOCK_MS
      go(active + (event.deltaX > 0 ? 1 : -1), true)
    }
    root.addEventListener('wheel', onWheel, { passive: false })
    return () => root.removeEventListener('wheel', onWheel)
  }, [active, go])

  // ---------- pointer ----------
  const onPointerDown = (event: PointerEvent<HTMLDivElement>) => {
    const target = event.target as Element
    if (event.button > 0 || target.closest('button')) return
    // Read now: once the pointer is captured, later events no longer say which item it's over.
    const item = target.closest('[data-i]')?.getAttribute('data-i')
    drag.current = { x: event.clientX, y: event.clientY, moved: false, turned: false, item: item == null ? null : Number(item) }
    event.currentTarget.setPointerCapture?.(event.pointerId)
    setDragging(true)
  }

  const onPointerMove = (event: PointerEvent<HTMLDivElement>) => {
    const d = drag.current
    if (zoomed && (!d || event.pointerType === 'mouse')) {
      setPanning(true)
      aim(event)
    }
    if (!d) return
    const dx = event.clientX - d.x
    const dy = event.clientY - d.y
    if (zoomed) {
      if (Math.hypot(dx, dy) > 6) d.moved = true
      aim(event)
      return
    }
    const step = Math.max(50, (rootRef.current?.clientWidth ?? 0) * 0.08)
    if (Math.abs(dx) > step && Math.abs(dx) > Math.abs(dy)) {
      go(active + (dx < 0 ? 1 : -1), true) // keep dragging to keep turning
      d.x = event.clientX
      d.y = event.clientY
      d.moved = true
      d.turned = true
    } else if (Math.abs(dy) > 70 && Math.abs(dy) > Math.abs(dx) * 1.4 && !d.turned) {
      const target = findGroup(dy > 0 ? 'top' : 'bottom')
      if (target > -1) go(target, true)
      d.moved = true
      d.turned = true
    } else if (Math.hypot(dx, dy) > 8) {
      d.moved = true
    }
  }

  const onPointerUp = (event: PointerEvent<HTMLDivElement>) => {
    const d = drag.current
    if (!d) return
    setDragging(false)
    drag.current = null
    if (d.moved) return
    if (zoomed) {
      closeZoom()
    } else if (d.item === active) {
      setTouched(true)
      setZoomed(true)
      aim(event)
    } else if (d.item !== null) {
      go(d.item, true) // a side product comes to the centre
    }
  }

  const onPointerCancel = () => {
    drag.current = null
    setDragging(false)
  }

  const onKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    const { key } = event
    if (key === 'ArrowRight') go(active + 1, true)
    else if (key === 'ArrowLeft') go(active - 1, true)
    else if (key === 'ArrowUp' && findGroup('top') > -1) go(findGroup('top'), true)
    else if (key === 'ArrowDown' && findGroup('bottom') > -1) go(findGroup('bottom'), true)
    else if (key === 'Enter' || key === ' ') {
      if ((event.target as Element).closest('button')) return // let buttons work normally
      setTouched(true)
      if (zoomed) closeZoom()
      else setZoomed(true)
    } else if (key === 'Escape' && zoomed) closeZoom()
    else return
    event.preventDefault()
  }

  // Shortest signed distance around the loop.
  const offset = (index: number) => {
    let d = index - active
    if (d > count / 2) d -= count
    if (d < -count / 2) d += count
    return d
  }

  const itemStyle = (index: number): CSSProperties => {
    const d = offset(index)
    const a = Math.abs(d)
    const x = d === 0 ? 0 : Math.sign(d) * ((phone ? 82 : 78) + (a - 1) * (phone ? 50 : 46)) // % of item width
    const scale = d === 0 ? 1 : Math.max(0.32, (phone ? 0.42 : 0.52) - (a - 1) * 0.1)
    return {
      transform: `translateX(calc(-50% + ${x}%)) scale(${scale})`,
      opacity: d === 0 ? 1 : a === 1 ? 0.9 : a === 2 ? (phone ? 0 : 0.55) : 0,
      zIndex: 10 - a,
      filter: d === 0 ? undefined : `blur(${a * 0.6}px)`,
    }
  }

  const view = views[active] ?? views[0]
  const sceneStyle = {
    '--ps-c': view.color,
    '--ps-c2': view.tint,
    '--ps-shift': `${-active * 4}%`,
    '--ps-zoom': zoom,
  } as CSSProperties

  return (
    <div
      ref={rootRef}
      className={[
        styles.showcase,
        moving && styles.isMoving,
        zoomed && styles.isZoom,
        dragging && styles.isDragging,
        panning && styles.isPanning,
      ].filter(Boolean).join(' ')}
      style={sceneStyle}
      tabIndex={0}
      role="region"
      aria-roledescription={t.product.viewer}
      aria-label={title}
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
      onPointerCancel={onPointerCancel}
      onPointerLeave={() => setPanning(false)}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onKeyDown={onKeyDown}
    >
      <div className={styles.head}>
        <div className={styles.title}>{title}</div>
        <div className={`${styles.hint} ${touched ? styles.hintHidden : ''}`} aria-hidden="true">
          {count > 1 ? t.product.hintDrag : t.product.hintClick}
        </div>
      </div>

      <div className={styles.info} aria-live="polite">
        {/* Keyed so the text blurs in again for every view. */}
        <div key={active}>
          <p className={styles.label}>{view.label}</p>
          {view.caption && <p className={styles.caption}>{view.caption}</p>}
        </div>
      </div>

      <div className={styles.meta}>
        {price && <div className={styles.price}>{price}</div>}
        {count > 1 && <div className={styles.count}>{active + 1} / {count}</div>}
      </div>

      {/* Keyed so the ring flashes for every view. */}
      <div key={active} className={styles.ring} />

      <div className={styles.track}>
        {views.map((item, index) => (
          <div
            key={`${index}-${item.image}`}
            className={`${styles.item} ${index === active ? styles.isActive : ''}`}
            data-i={index}
            style={itemStyle(index)}
            aria-hidden={index !== active}
          >
            <img src={item.image} alt={t.product.viewAlt(title, item.label)} draggable={false} decoding="async" />
          </div>
        ))}
      </div>

      {count > 1 && (
        <div className={styles.nav}>
          <button type="button" className={styles.arrow} aria-label={t.product.previousView} onClick={() => go(active - 1, true)}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"
              strokeLinejoin="round" aria-hidden="true">
              <path d="M15 6l-6 6 6 6" />
            </svg>
          </button>
          <div className={styles.pills}>
            {views.map((item, index) => (
              <button
                key={`${index}-${item.short_label}`}
                type="button"
                className={`${styles.pill} ${index === active ? styles.isOn : ''}`}
                aria-pressed={index === active}
                onClick={() => go(index, true)}
              >
                {item.short_label}
              </button>
            ))}
          </div>
          <button type="button" className={styles.arrow} aria-label={t.product.nextView} onClick={() => go(active + 1, true)}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"
              strokeLinejoin="round" aria-hidden="true">
              <path d="M9 6l6 6-6 6" />
            </svg>
          </button>
        </div>
      )}
    </div>
  )
}
