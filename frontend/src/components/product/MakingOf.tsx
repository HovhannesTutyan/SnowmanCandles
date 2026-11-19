import type { ProductDetail } from '../../api/types'
import { useSite } from '../../context/site'
import { useI18n } from '../../i18n/context'
import { Flame } from './Flame'
import styles from './MakingOf.module.css'

/** "The making of": the product's own story, or the shared one from Site content. */
export function MakingOf({ product }: { product: ProductDetail }) {
  const { content } = useSite()
  const { t } = useI18n()
  const title = product.story_title || content.story_title
  const text = product.story_text || content.story_text

  return (
    <section className={styles.story} aria-labelledby="making-of-title">
      <div className={styles.row}>
        <div className={`${styles.text} reveal`}>
          <p className={styles.kicker}>{t.product.makingOfKicker}</p>
          <h2 id="making-of-title" className={styles.title}>{title}</h2>
          <p className={styles.lede}>{text}</p>
          <ol className={styles.steps}>
            {t.product.makingOfSteps.map((step, index) => (
              <li key={step}>
                <div className={styles.stepNumber}>{String(index + 1).padStart(2, '0')}</div>
                <div className={styles.stepLabel}>{step}</div>
              </li>
            ))}
          </ol>
        </div>

        <div className={`${styles.art} reveal`}>
          <div className={styles.halo} />
          <div className={styles.floor} />
          <div className={`${styles.pieceWrap} bob`}>
            <div className={styles.piece}>
              <img
                src={product.image}
                alt={product.flame ? t.product.glowingAlt(product.title) : product.title}
                loading="lazy"
              />
              {product.flame && <Flame x={product.flame.x} y={product.flame.y} />}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
