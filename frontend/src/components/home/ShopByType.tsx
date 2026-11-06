import type { CSSProperties } from 'react'

import { useI18n } from '../../i18n/context'
import { Link } from '../../i18n/Link'
import { ArrowRightIcon } from '../icons'
import styles from './ShopByType.module.css'

export interface TypeTile {
  title: string
  text: string
  image: string
  /** Tile colours and image placement from the design. */
  background: string
  textColor: string
  imageStyle: CSSProperties
}

interface ShopByTypeProps {
  tiles: TypeTile[]
}

export function ShopByType({ tiles }: ShopByTypeProps) {
  const { t } = useI18n()
  return (
    <section id="shop" className={styles.section} aria-labelledby="shop-title">
      <div className={styles.inner}>
        <div className={`${styles.head} reveal`}>
          <h2 id="shop-title" className={styles.title}>{t.home.shopByType}</h2>
          <Link to="/decorate" className={styles.ideasLink}>
            {t.home.stylingIdeas}
            <ArrowRightIcon />
          </Link>
        </div>
        <div className={styles.grid}>
          {tiles.map((tile) => (
            <a
              key={tile.title}
              href="#winter"
              className={`${styles.tile} lift reveal`}
              style={{ background: tile.background }}
            >
              <div>
                <div className={styles.tileTitle}>{tile.title}</div>
                <div className={styles.tileText} style={{ color: tile.textColor }}>
                  {tile.text}
                </div>
              </div>
              <img
                className={`${styles.tileImage} pimg`}
                src={tile.image}
                alt=""
                loading="lazy"
                style={tile.imageStyle}
              />
            </a>
          ))}
        </div>
      </div>
    </section>
  )
}
