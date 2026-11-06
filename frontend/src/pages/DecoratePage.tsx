import { useState } from 'react'

import { fetchDecoratePage } from '../api/client'
import type { DecoratePageData } from '../api/types'
import groupedHeights from '../assets/design/decorate-grouped-heights.webp'
import heroShelf from '../assets/design/decorate-hero-shelf.webp'
import { InlineText } from '../components/common/RichText'
import { GallerySlider } from '../components/decorate/GallerySlider'
import { Lightbox } from '../components/decorate/Lightbox'
import { ArrowRightIcon } from '../components/icons'
import { ErrorScreen, LoadingScreen } from '../components/StatusScreen'
import { useSite } from '../context/site'
import { useI18n } from '../i18n/context'
import { Link } from '../i18n/Link'
import { useAsync } from '../hooks/useAsync'
import { usePrefersReducedMotion } from '../hooks/usePrefersReducedMotion'
import { toParagraphs } from '../lib/text'
import styles from './DecoratePage.module.css'

export function DecoratePage() {
  const { locale } = useI18n()
  const page = useAsync(`decorate/${locale}`, (signal) => fetchDecoratePage(locale, signal))

  if (page.status === 'loading') return <LoadingScreen variant="page" />
  if (page.status === 'error') {
    return <ErrorScreen variant="page" error={page.error} onRetry={page.retry} />
  }
  return <DecorateView page={page.data} />
}

function DecorateView({ page }: { page: DecoratePageData }) {
  const { content } = useSite()
  const { t } = useI18n()
  const [viewing, setViewing] = useState<number | null>(null)
  const reducedMotion = usePrefersReducedMotion()
  const hasGallery = page.gallery.length > 0

  return (
    <div id="top" className={styles.page}>
      <title>{`${t.decorate.pageTitle} — ${content.studio_name}`}</title>
      <meta name="description" content={t.decorate.description} />
      {/* Dark top that fades into the cream page, as in the design. */}
      <div className={styles.backdrop} aria-hidden="true" />

      <div className={styles.inner}>
        <section className={`${styles.hero} ${styles.rise}`} aria-labelledby="decorate-title">
          <div className={styles.heroText}>
            <p className={styles.eyebrow}>{page.hero_eyebrow}</p>
            <div>
              <h1 id="decorate-title" className={styles.heroTitle}>{page.hero_title}</h1>
              <p className={styles.heroLede}>{page.hero_text}</p>
            </div>
            {hasGallery && page.hero_link_text && (
              <a href="#gallery" className={styles.heroLink}>
                {page.hero_link_text}
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent)"
                  strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M12 5v14M6 13l6 6 6-6" />
                </svg>
              </a>
            )}
          </div>
          <div className={styles.heroPicture}>
            {page.hero_video ? (
              // Silent and looping, like a moving picture. Visitors who prefer less motion
              // get the first frame and can press play themselves.
              <video
                key={`${page.hero_video}-${reducedMotion}`}
                src={page.hero_video}
                poster={page.hero_image ?? undefined}
                aria-label={page.hero_image_alt}
                autoPlay={!reducedMotion}
                controls={reducedMotion}
                muted
                loop
                playsInline
                preload={reducedMotion ? 'none' : 'auto'}
              />
            ) : (
              <img src={page.hero_image ?? heroShelf} alt={page.hero_image_alt} />
            )}
          </div>
        </section>

        <section className={styles.story} aria-labelledby="story-title">
          <h2 id="story-title" className={`${styles.storyTitle} reveal`}>{page.story_title}</h2>
          {page.story_subtitle && (
            <p className={`${styles.storySubtitle} reveal`}>{page.story_subtitle}</p>
          )}
          {page.story_text && (
            <div className={`${styles.storyText} reveal`}>
              {toParagraphs(page.story_text).map((paragraph, index) => (
                <p key={index}>
                  <InlineText text={paragraph} strongClassName={styles.strong} />
                </p>
              ))}
            </div>
          )}

          {page.rooms.length > 0 && (
            <ul className={styles.rooms} aria-label={t.decorate.rooms}>
              {page.rooms.map((room, index) => {
                const picture = room.gallery_index === null ? null : page.gallery[room.gallery_index]
                const inner = (
                  <>
                    {picture && (
                      <div className={styles.roomImage}>
                        <img src={picture.image} alt="" loading="lazy" draggable={false} />
                      </div>
                    )}
                    <div className={styles.roomBody}>
                      <div className={styles.roomTitle}>{room.title}</div>
                      <div className={styles.roomText}>{room.text}</div>
                    </div>
                  </>
                )
                return (
                  <li key={`${index}-${room.title}`} className={`${styles.room} reveal`}>
                    {picture ? (
                      <button
                        type="button"
                        className={styles.roomButton}
                        aria-label={t.decorate.openRoom(room.title, room.text)}
                        onClick={() => setViewing(room.gallery_index)}
                      >
                        {inner}
                      </button>
                    ) : (
                      inner
                    )}
                  </li>
                )
              })}
            </ul>
          )}
        </section>

        {hasGallery && (
          <section id="gallery" className={styles.gallery} aria-labelledby="gallery-title">
            <div className={`${styles.galleryHead} reveal`}>
              <h2 id="gallery-title" className={styles.galleryTitle}>{page.gallery_title}</h2>
              {page.gallery_text && <p className={styles.galleryText}>{page.gallery_text}</p>}
            </div>
            <div className="reveal">
              <GallerySlider pictures={page.gallery} onOpen={setViewing} />
            </div>
          </section>
        )}

        <section className={`${styles.cta} reveal`} aria-labelledby="decorate-cta">
          <div className={styles.ctaText}>
            <h2 id="decorate-cta" className={styles.ctaTitle}>{page.cta_title}</h2>
            <p className={styles.ctaLede}>{page.cta_text}</p>
            <Link to="/#winter" className={styles.ctaButton}>
              {page.cta_button_text}
              <ArrowRightIcon />
            </Link>
          </div>
          <div className={styles.ctaPicture}>
            <img src={page.cta_image ?? groupedHeights} alt="" loading="lazy" />
          </div>
        </section>
      </div>

      {viewing !== null && hasGallery && (
        <Lightbox
          pictures={page.gallery}
          index={viewing}
          onIndexChange={setViewing}
          onClose={() => setViewing(null)}
        />
      )}
    </div>
  )
}
