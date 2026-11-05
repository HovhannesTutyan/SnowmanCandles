import { useCallback, useEffect, useRef, useState, type PointerEvent } from 'react'

import type { GalleryPicture } from '../../api/types'
import { ArrowRightIcon } from '../icons'
import styles from './GallerySlider.module.css'

const GAP = 16

interface GallerySliderProps {
  pictures: GalleryPicture[]
  onOpen: (index: number) => void
}

/**
 * A row of square pictures: drag with the mouse, swipe on touch, ← → keys when focused,
 * or the round buttons. Clicking a picture opens it full size.
 */
export function GallerySlider({ pictures, onOpen }: GallerySliderProps) {
  const trackRef = useRef<HTMLDivElement>(null)
  const drag = useRef<{ x: number; left: number; moved: boolean } | null>(null)
  const justDragged = useRef(false)
  const [position, setPosition] = useState({ atStart: true, atEnd: false, progress: 0 })
  const count = pictures.length

  const update = useCallback(() => {
    const track = trackRef.current
    if (!track) return
    const max = track.scrollWidth - track.clientWidth
    setPosition({
      atStart: track.scrollLeft <= 4,
      atEnd: track.scrollLeft >= max - 4,
      progress: track.scrollWidth ? Math.min(1, (track.scrollLeft + track.clientWidth) / track.scrollWidth) : 1,
    })
  }, [])

  useEffect(() => {
    update()
    window.addEventListener('resize', update)
    return () => window.removeEventListener('resize', update)
  }, [update, count])

  const step = () => {
    const first = trackRef.current?.firstElementChild
    return first ? first.getBoundingClientRect().width + GAP : 300
  }

  const go = (direction: 1 | -1) => {
    const track = trackRef.current
    if (!track) return
    const s = step()
    track.scrollTo({ left: Math.round((track.scrollLeft + direction * s) / s) * s, behavior: 'smooth' })
  }

  // Mouse drag; touch devices swipe natively.
  const onPointerDown = (event: PointerEvent<HTMLDivElement>) => {
    if (event.pointerType !== 'mouse' || event.button !== 0 || !trackRef.current) return
    drag.current = { x: event.clientX, left: trackRef.current.scrollLeft, moved: false }
  }
  const onPointerMove = (event: PointerEvent<HTMLDivElement>) => {
    const track = trackRef.current
    if (!drag.current || !track) return
    const dx = event.clientX - drag.current.x
    if (!drag.current.moved && Math.abs(dx) > 6) {
      drag.current.moved = true
      track.classList.add(styles.dragging)
      track.setPointerCapture(event.pointerId)
    }
    if (drag.current.moved) track.scrollLeft = drag.current.left - dx
  }
  const endDrag = () => {
    const track = trackRef.current
    if (!drag.current || !track) return
    justDragged.current = drag.current.moved
    if (drag.current.moved) {
      track.classList.remove(styles.dragging)
      const s = step()
      track.scrollTo({ left: Math.round(track.scrollLeft / s) * s, behavior: 'smooth' })
    }
    drag.current = null
  }

  const shown = Math.max(1, Math.round(position.progress * count))

  return (
    <div>
      <div
        ref={trackRef}
        className={styles.track}
        tabIndex={0}
        role="region"
        aria-roledescription="carousel"
        aria-label={`Styling gallery, ${count} pictures. Use the left and right arrow keys to scroll.`}
        onScroll={update}
        onKeyDown={(event) => {
          if (event.key === 'ArrowRight') {
            event.preventDefault()
            go(1)
          } else if (event.key === 'ArrowLeft') {
            event.preventDefault()
            go(-1)
          }
        }}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={endDrag}
        onPointerCancel={endDrag}
      >
        {pictures.map((picture, index) => (
          <button
            key={picture.id}
            type="button"
            className={styles.slide}
            aria-label={`Open picture ${index + 1} of ${count}: ${picture.caption}`}
            onClick={() => {
              if (justDragged.current) {
                justDragged.current = false // a drag, not a click
                return
              }
              onOpen(index)
            }}
          >
            <img src={picture.image} alt={picture.alt} loading="lazy" draggable={false} />
            <span className={styles.caption} aria-hidden="true">{picture.caption}</span>
          </button>
        ))}
      </div>

      <div className={styles.controls}>
        <div className={styles.progress}>
          <div className={styles.progressTrack} aria-hidden="true">
            <div className={styles.progressBar} style={{ width: `${Math.round(position.progress * 100)}%` }} />
          </div>
          <span className={styles.progressLabel}>
            {shown} / {count}
          </span>
        </div>
        <div className={styles.buttons}>
          <button
            type="button"
            className={styles.navButton}
            aria-label="Previous pictures"
            onClick={() => go(-1)}
            disabled={position.atStart}
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
              strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M19 12H5M11 6l-6 6 6 6" />
            </svg>
          </button>
          <button
            type="button"
            className={styles.navButton}
            aria-label="Next pictures"
            onClick={() => go(1)}
            disabled={position.atEnd}
          >
            <ArrowRightIcon size={22} />
          </button>
        </div>
      </div>
    </div>
  )
}
