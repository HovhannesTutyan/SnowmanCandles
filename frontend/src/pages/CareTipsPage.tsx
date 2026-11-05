import { Link } from 'react-router'

import { fetchCarePage } from '../api/client'
import type { CarePageData } from '../api/types'
import { Faq } from '../components/care/Faq'
import { CandlelitScene, ShelfScene } from '../components/care/Scenes'
import { SectionNav } from '../components/common/SectionNav'
import { ErrorScreen, LoadingScreen } from '../components/StatusScreen'
import { useSite } from '../context/site'
import { useAsync } from '../hooks/useAsync'
import { itemPath } from '../lib/items'
import styles from './CareTipsPage.module.css'

const PAGE_TITLE = 'Candle Care & Tips'

export function CareTipsPage() {
  const page = useAsync('care', fetchCarePage)

  if (page.status === 'loading') return <LoadingScreen variant="page" />
  if (page.status === 'error') {
    return <ErrorScreen variant="page" error={page.error} onRetry={page.retry} />
  }
  return <CareTipsView page={page.data} />
}

function CareTipsView({ page }: { page: CarePageData }) {
  const { content, formatPrice } = useSite()
  const product = page.fragrance_product

  const sections = [
    page.tips.length > 0 && { id: 'tips', label: 'Tips' },
    page.rituals.length > 0 && { id: 'care', label: 'Care' },
    { id: 'fragrance', label: 'Fragrance' },
    page.faqs.length > 0 && { id: 'faq', label: 'FAQ' },
  ].filter((link): link is { id: string; label: string } => Boolean(link))

  return (
    <div id="top" className={styles.page}>
      <title>{`${PAGE_TITLE} — ${content.studio_name}`}</title>
      <meta
        name="description"
        content="How to burn, care for and reuse your hand-painted candles: first burn, wick trimming, placement, care rituals and FAQ."
      />
      {/* Dark top that fades into the cream page, as in the design. */}
      <div className={styles.backdrop} aria-hidden="true" />

      <div className={styles.cards}>
        <section className={`${styles.card} ${styles.hero} ${styles.rise}`} aria-labelledby="care-title">
          <div className={styles.heroHead}>
            <h1 id="care-title" className={styles.heroTitle}>{page.hero_title}</h1>
            <p className={styles.heroText}>{page.hero_text}</p>
          </div>
          <CandlelitScene
            photo={page.hero_image}
            label="Painted candles glowing on a wooden table in a dark, warm room"
          />
        </section>

        {page.tips.length > 0 && (
          <section id="tips" className={`${styles.card} ${styles.tipsCard} reveal`} aria-labelledby="tips-title">
            <h2 id="tips-title" className={styles.eyebrow}>{page.tips_eyebrow}</h2>
            <ol className={styles.tips}>
              {page.tips.map((tip, index) => (
                <li key={`${index}-${tip.title}`} className={styles.tip}>
                  <div className={styles.tipNumber} aria-hidden="true">
                    {String(index + 1).padStart(2, '0')}
                  </div>
                  <h3 className={styles.tipTitle}>{tip.title}</h3>
                  <p className={styles.tipText}>{tip.text}</p>
                </li>
              ))}
            </ol>
          </section>
        )}

        {page.rituals.length > 0 && (
          <section id="care" className={`${styles.card} ${styles.rituals} reveal`} aria-labelledby="rituals-title">
            <h2 id="rituals-title" className={styles.sectionTitle}>{page.rituals_title}</h2>
            <ul className={styles.ritualList}>
              {page.rituals.map((ritual, index) => (
                <li key={`${index}-${ritual.title}`} className={styles.ritual}>
                  <span className={styles.dot} aria-hidden="true" />
                  <div>
                    <div className={styles.ritualTitle}>{ritual.title}</div>
                    <div className={styles.ritualText}>{ritual.text}</div>
                  </div>
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>

      <section id="fragrance" className={styles.fragrance} aria-labelledby="fragrance-title">
        <div className={`${styles.fragranceText} reveal`}>
          <p className={styles.eyebrow}>{page.fragrance_eyebrow}</p>
          <h2 id="fragrance-title" className={styles.sectionTitle}>{page.fragrance_title}</h2>
          <p className={styles.lede}>{page.fragrance_text}</p>
          <ul className={styles.points}>
            {page.fragrance_tips.map((point, index) => (
              <li key={`${index}-${point.lead}`} className={styles.point}>
                <span className={styles.dot} aria-hidden="true" />
                <div>
                  <strong>{point.lead}</strong> {point.text}
                </div>
              </li>
            ))}
          </ul>
        </div>
        <ShelfScene photo={page.fragrance_image} label="Painted bauble candles on a warm wooden shelf">
          {product && (
            <Link to={itemPath(product)} className={styles.productChip}>
              {product.title} · {formatPrice(product.price)}
            </Link>
          )}
        </ShelfScene>
      </section>

      <Faq title={page.faq_title} items={page.faqs} />

      <SectionNav title={PAGE_TITLE} links={sections} />
    </div>
  )
}
