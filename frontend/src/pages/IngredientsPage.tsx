import { Link } from 'react-router'

import { fetchIngredientsPage } from '../api/client'
import type { IngredientsPageData } from '../api/types'
import plasterBauble from '../assets/design/plaster-bauble.webp'
import { SectionNav } from '../components/common/SectionNav'
import { ArrowRightIcon } from '../components/icons'
import { ChapterSection } from '../components/ingredients/ChapterSection'
import { Grain } from '../components/ingredients/Illustrations'
import { ErrorScreen, LoadingScreen } from '../components/StatusScreen'
import { useSite } from '../context/site'
import { useAsync } from '../hooks/useAsync'
import styles from './IngredientsPage.module.css'

export function IngredientsPage() {
  const page = useAsync('ingredients', fetchIngredientsPage)

  if (page.status === 'loading') return <LoadingScreen variant="page" />
  if (page.status === 'error') {
    return <ErrorScreen variant="page" error={page.error} onRetry={page.retry} />
  }
  return <IngredientsView page={page.data} />
}

function IngredientsView({ page }: { page: IngredientsPageData }) {
  const { content } = useSite()
  const first = page.chapters[0]

  return (
    <div id="top" className={styles.page}>
      <title>{`${page.hero_title} — ${content.studio_name}`}</title>
      <meta
        name="description"
        content="Soy wax, hand-cast plaster, wicks, fragrance and colour: everything that goes into our handmade candles."
      />
      {/* Dark top that fades into the cream page, as in the design. */}
      <div className={styles.backdrop} aria-hidden="true" />

      <div className={styles.inner}>
        <section className={`${styles.hero} ${styles.rise}`} aria-labelledby="ingredients-title">
          <div className={styles.heroText}>
            <p className={styles.eyebrow}>{page.hero_eyebrow}</p>
            <div>
              <h1 id="ingredients-title" className={styles.heroTitle}>{page.hero_title}</h1>
              <p className={styles.heroLede}>{page.hero_text}</p>
            </div>
            {first && page.hero_link_text && (
              <a href={`#${first.anchor}`} className={styles.heroLink}>
                {page.hero_link_text}
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                  strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M12 5v14M6 13l6 6 6-6" />
                </svg>
              </a>
            )}
          </div>

          <div className={styles.heroPicture}>
            {page.hero_image ? (
              <img className={styles.heroPhoto} src={page.hero_image} alt="" />
            ) : (
              <div
                className={styles.linen}
                role="img"
                aria-label="An unpainted plaster vessel with raised holly relief on warm linen"
              >
                <Grain frequency="0.9 0.06" seed={4} tint="0 0 0 0 .55  0 0 0 0 .45  0 0 0 0 .35  0 0 0 .5 0" opacity={0.5} />
                <div className={styles.linenShadow} />
                <img className={styles.linenVessel} src={plasterBauble} alt="" />
              </div>
            )}
            {page.hero_image_label && <span className={styles.heroLabel}>{page.hero_image_label}</span>}
          </div>
        </section>

        {page.chapters.map((chapter, index) => (
          <ChapterSection key={chapter.anchor} chapter={chapter} openFirstQuestion={index === 0} />
        ))}

        <section className={`${styles.cta} reveal`} aria-labelledby="ingredients-cta">
          <div className={styles.ctaText}>
            <h2 id="ingredients-cta" className={styles.ctaTitle}>{page.cta_title}</h2>
            <p className={styles.ctaLede}>{page.cta_text}</p>
          </div>
          <Link to="/#winter" className={styles.ctaButton}>
            {page.cta_button_text}
            <ArrowRightIcon />
          </Link>
        </section>
      </div>

      {page.chapters.length > 0 && (
        <SectionNav
          title={page.nav_title}
          label="Ingredients on this page"
          links={page.chapters.map((chapter) => ({ id: chapter.anchor, label: chapter.nav_label }))}
        />
      )}
    </div>
  )
}
