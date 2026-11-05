import type { CSSProperties } from 'react'

import type { HeroSlide, SiteContent, ShopItem } from '../../api/types'
import type { PriceFormatter } from '../../lib/format'
import { designImages } from '../../lib/designImages'
import { ArrowRightIcon, PlayIcon } from '../icons'
import styles from './Hero.module.css'
import { HeroShowcase } from './HeroShowcase'
import { ProductTrain } from './ProductTrain'
import { Snowfall } from './Snowfall'

interface HeroProps {
  content: SiteContent
  slides: HeroSlide[]
  items: ShopItem[]
  formatPrice: PriceFormatter
}

const riseDelay = (seconds: number): CSSProperties => ({ animationDelay: `${seconds}s` })

export function Hero({ content, slides, items, formatPrice }: HeroProps) {
  return (
    <section id="top" className={styles.hero}>
      <Snowfall />
      <div className={styles.inner}>
        <div className={styles.copy}>
          <p className={`${styles.eyebrow} ${styles.rise}`} style={riseDelay(0.1)}>
            {content.hero_eyebrow}
          </p>
          <h1 className={`${styles.title} ${styles.rise}`} style={riseDelay(0.25)}>
            {content.hero_title}
          </h1>
          <p className={`${styles.text} ${styles.rise}`} style={riseDelay(0.45)}>
            {content.hero_text}
          </p>
          <div className={`${styles.actions} ${styles.rise}`} style={riseDelay(0.6)}>
            <a href="#winter" className={styles.primary}>
              {content.hero_button_text}
              <ArrowRightIcon />
            </a>
            <a href="#made" className={styles.secondary}>
              <span className={`${styles.playDot} pulse`}>
                <PlayIcon />
              </span>
              {content.hero_video_button_text}
            </a>
          </div>
        </div>

        <div className={`${styles.showcaseWrap} ${styles.rise}`} style={riseDelay(0.35)}>
          <HeroShowcase
            slides={slides}
            formatPrice={formatPrice}
            fallbackImage={designImages.made_after}
          />
        </div>
      </div>

      <ProductTrain items={items} />
    </section>
  )
}
