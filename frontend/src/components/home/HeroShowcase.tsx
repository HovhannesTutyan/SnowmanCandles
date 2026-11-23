import { useEffect, useState } from 'react'

import type { HeroSlide } from '../../api/types'
import { usePrefersReducedMotion } from '../../hooks/usePrefersReducedMotion'
import { useI18n } from '../../i18n/context'
import { Link } from '../../i18n/Link'
import type { Messages } from '../../i18n/messages/en'
import type { PriceFormatter } from '../../lib/format'
import { slideLinkPath } from '../../lib/items'
import styles from './HeroShowcase.module.css'

export const SLIDE_DURATION_MS = 4000

interface HeroShowcaseProps {
  slides: HeroSlide[]
  formatPrice: PriceFormatter
  /** Shown on the pedestal when there are no slides yet. */
  fallbackImage: string
}

function captionMeta(slide: HeroSlide, formatPrice: PriceFormatter, t: Messages) {
  if (slide.subtitle) return slide.subtitle
  if (slide.link) return `${t.productType[slide.link.product_type]} · ${formatPrice(slide.link.price)}`
  return ''
}

/**
 * The rotating pieces on the hero pedestal. Each slide is shown for
 * SLIDE_DURATION_MS; hovering or focusing pauses it, the bars jump to a slide,
 * and it stays still for visitors who prefer reduced motion.
 */
export function HeroShowcase({ slides, formatPrice, fallbackImage }: HeroShowcaseProps) {
  const [active, setActive] = useState(0)
  const [paused, setPaused] = useState(false)
  const reducedMotion = usePrefersReducedMotion()
  const { t } = useI18n()
  const count = slides.length
  const autoplay = count > 1 && !paused && !reducedMotion

  useEffect(() => {
    if (!autoplay) return
    // Re-armed whenever `active` changes, so a manual pick gets a full turn too.
    const timer = window.setTimeout(() => setActive((i) => (i + 1) % count), SLIDE_DURATION_MS)
    return () => window.clearTimeout(timer)
  }, [active, autoplay, count])

  // Slides can change after a refetch; never point past the end.
  const current = count > 0 ? active % count : 0
  const previous = (current - 1 + count) % count

  return (
    <div
      className={styles.showcase}
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
      onFocus={() => setPaused(true)}
      onBlur={() => setPaused(false)}
    >
      <div className={styles.stage}>
        <svg className={styles.ring} viewBox="0 0 200 200" aria-hidden="true">
          <circle cx="100" cy="100" r="96" fill="none" stroke="#C08A4E" strokeWidth="1.2"
            strokeDasharray="1.5 6" strokeLinecap="round" />
        </svg>
        <div className={styles.halo} />
        <div className={styles.pedestal} />
        <div className={styles.shadow} />

        {count === 0 ? (
          <div className={`${styles.slide} ${styles.slideActive}`}>
            <div className={`${styles.piece} bob`}>
              <img src={fallbackImage} alt="" />
            </div>
          </div>
        ) : (
          slides.map((slide, index) => (
            <div
              key={slide.id}
              className={[
                styles.slide,
                index === current && styles.slideActive,
                count > 1 && index === previous && styles.slideLeaving,
              ].filter(Boolean).join(' ')}
              aria-hidden={index !== current}
            >
              {slide.image &&
                (slide.link ? (
                  <Link
                    to={slideLinkPath(slide.link)}
                    className={`${styles.piece} bob`}
                    tabIndex={-1}
                    aria-hidden="true"
                  >
                    <img src={slide.image} alt={slide.title} />
                  </Link>
                ) : (
                  <div className={`${styles.piece} bob`}>
                    <img src={slide.image} alt={slide.title} />
                  </div>
                ))}
            </div>
          ))
        )}
      </div>

      {count > 0 && (
        <div className={styles.captionRow}>
          <div className={styles.captions} aria-live={autoplay ? 'off' : 'polite'}>
            {slides.map((slide, index) => (
              <div
                key={slide.id}
                className={`${styles.caption} ${index === current ? styles.captionActive : ''}`}
                aria-hidden={index !== current}
              >
                <div className={styles.captionTitle}>
                  {slide.link ? (
                    <Link
                      to={slideLinkPath(slide.link)}
                      className={styles.captionTitleLink}
                      tabIndex={index === current ? 0 : -1}
                    >
                      {slide.title}
                    </Link>
                  ) : (
                    slide.title
                  )}
                </div>
                <div className={styles.captionMeta}>
                  {captionMeta(slide, formatPrice, t)}
                  {slide.button_text && (
                    <>
                      {' '}
                      <Link
                        to={slide.link ? slideLinkPath(slide.link) : '/#winter'}
                        className={styles.captionLink}
                        tabIndex={index === current ? 0 : -1}
                      >
                        {slide.button_text}
                      </Link>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>

          {count > 1 && (
            <div
              className={`${styles.bars} ${paused ? styles.paused : ''}`}
              style={{ gridTemplateColumns: `repeat(${count}, minmax(0, 1fr))` }}
            >
              {slides.map((slide, index) => (
                <button
                  key={slide.id}
                  type="button"
                  className={styles.bar}
                  aria-label={t.home.showSlide(slide.title)}
                  aria-current={index === current}
                  onClick={() => setActive(index)}
                >
                  <span className={styles.barTrack}>
                    {index === current && (
                      // Keyed so the fill animation restarts on every slide change.
                      <span
                        key={`${current}-${autoplay}`}
                        className={`${styles.barFill} ${autoplay ? '' : styles.barFull}`}
                        style={{ animationDuration: `${SLIDE_DURATION_MS}ms` }}
                      />
                    )}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
