import type { IngredientChapter } from '../../api/types'
import { useI18n } from '../../i18n/context'
import { CardIcon } from './CardIcon'
import styles from './ChapterSection.module.css'
import { Disclosure } from './Disclosure'
import { ChapterArt } from './Illustrations'

interface ChapterSectionProps {
  chapter: IngredientChapter
  /** Open the first question (the design opens the first one on the page). */
  openFirstQuestion?: boolean
}

/** One ingredient: a big banner, then text with points, questions, cards and swatches. */
export function ChapterSection({ chapter, openFirstQuestion = false }: ChapterSectionProps) {
  const { t } = useI18n()
  const titleId = `${chapter.anchor}-title`
  const hasQuestions = chapter.questions.length > 0

  const points = chapter.points.length > 0 && (
    <ul className={styles.points}>
      {chapter.points.map((point, index) => (
        <li key={`${index}-${point.lead}`} className={styles.point}>
          <span className={styles.dot} aria-hidden="true" />
          <span>
            <strong>{point.lead}</strong> — {point.text}
          </span>
        </li>
      ))}
    </ul>
  )

  return (
    <section id={chapter.anchor} className={styles.chapter} aria-labelledby={titleId}>
      <div
        className={`${styles.banner} ${chapter.banner_text === 'light' ? styles.bannerLight : ''} ${
          chapter.illustration === 'colour' ? styles.bannerColour : ''
        } reveal`}
        style={{ backgroundColor: chapter.banner_color }}
      >
        <div className={styles.art} aria-hidden="true">
          {chapter.banner_image ? (
            <img className={styles.photo} src={chapter.banner_image} alt={chapter.title} />
          ) : (
            <ChapterArt kind={chapter.illustration} colors={chapter.swatches.map((s) => s.color)} />
          )}
        </div>
        <div className={styles.bannerText}>
          <h2 id={titleId} className={styles.title}>{chapter.title}</h2>
          <p className={styles.intro}>{chapter.intro}</p>
        </div>
      </div>

      <div className={`${styles.content} ${hasQuestions ? styles.contentSplit : ''} reveal`}>
        {hasQuestions ? (
          <>
            <div className={styles.textColumn}>
              {chapter.paragraphs.map((paragraph, index) => (
                <p key={index} className={styles.paragraph}>{paragraph}</p>
              ))}
              {points}
            </div>
            <div className={styles.questions}>
              {chapter.questions.map((item, index) => (
                <Disclosure
                  key={`${index}-${item.question}`}
                  question={item.question}
                  answer={item.answer}
                  defaultOpen={openFirstQuestion && index === 0}
                />
              ))}
            </div>
          </>
        ) : (
          <>
            {chapter.paragraphs.length > 0 && (
              <div className={styles.paragraphRow}>
                {chapter.paragraphs.map((paragraph, index) => (
                  <p key={index} className={styles.paragraph}>{paragraph}</p>
                ))}
              </div>
            )}
            {points}
          </>
        )}

        {chapter.cards.length > 0 && (
          <div>
            {chapter.cards_title && <h3 className={styles.cardsTitle}>{chapter.cards_title}</h3>}
            <ul className={styles.cards}>
              {chapter.cards.map((card, index) => (
                <li key={`${index}-${card.title}`} className={styles.card}>
                  <CardIcon name={card.icon} />
                  <div className={styles.cardTitle}>{card.title}</div>
                  <p className={styles.cardText}>{card.text}</p>
                </li>
              ))}
            </ul>
          </div>
        )}

        {chapter.swatches.length > 0 && (
          <ul className={styles.swatches} aria-label={t.ingredients.palette(chapter.title)}>
            {chapter.swatches.map((swatch, index) => (
              <li key={`${index}-${swatch.name}`} className={styles.swatch}>
                <span className={styles.swatchColor} style={{ background: swatch.color }} aria-hidden="true" />
                <div className={styles.swatchName}>{swatch.name}</div>
                {swatch.note && <div className={styles.swatchNote}>{swatch.note}</div>}
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}
