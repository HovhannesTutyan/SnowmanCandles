import { Link } from 'react-router'

import type { SiteContent } from '../../api/types'
import { ArrowRightIcon, BrushIcon, PlayIcon } from '../icons'
import styles from './HowItsMade.module.css'

interface HowItsMadeProps {
  content: SiteContent
  images: { before: string; after: string; video: string }
}

export function HowItsMade({ content, images }: HowItsMadeProps) {
  const steps = [
    { title: content.step1_title, text: content.step1_text, className: styles.step1 },
    { title: content.step2_title, text: content.step2_text, className: styles.step2 },
    { title: content.step3_title, text: content.step3_text, className: styles.step3 },
  ]

  const videoInner = (
    <>
      <img className={styles.videoImage} src={images.video} alt="" loading="lazy" />
      <span className={styles.videoText}>
        <span className={`${styles.videoPlay} pulse`}>
          <PlayIcon size={20} />
        </span>
        <span className={styles.videoTitle}>{content.video_title}</span>
        {content.video_caption && (
          <span className={styles.videoCaption}>{content.video_caption}</span>
        )}
      </span>
    </>
  )

  return (
    <section id="made" className={styles.section} aria-labelledby="made-title">
      <div className={styles.inner}>
        <div className={`${styles.intro} reveal`}>
          <p className={styles.eyebrow}>How it's made</p>
          <h2 id="made-title" className={styles.title}>{content.made_title}</h2>
          <p className={styles.text}>{content.made_text}</p>
          <Link to="/candle-care" className={styles.careLink}>
            Candle care &amp; tips
            <ArrowRightIcon />
          </Link>
        </div>

        <div className={styles.row}>
          {/* Plaster to painted: the painted image is wiped in behind the brush. */}
          <div className={`${styles.paintBox} reveal`}>
            <div className={styles.paintStage}>
              <img className={styles.paintImage} src={images.before} alt="Unpainted plaster piece" />
              <img
                className={`${styles.paintImage} ${styles.painted}`}
                src={images.after}
                alt="The same piece after hand-painting"
              />
              <div className={styles.brush} aria-hidden="true">
                <BrushIcon />
              </div>
            </div>
          </div>

          <div className={styles.side}>
            <ol className={styles.steps}>
              {steps.map((step, index) => (
                <li key={index} className={`${styles.step} ${step.className}`}>
                  <span className={styles.stepNumber}>{String(index + 1).padStart(2, '0')}</span>
                  <div>
                    <div className={styles.stepTitle}>{step.title}</div>
                    <div className={styles.stepText}>{step.text}</div>
                  </div>
                </li>
              ))}
            </ol>

            {content.video_url ? (
              <a
                className={styles.video}
                href={content.video_url}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={`Play the video: ${content.video_title} (opens in a new tab)`}
              >
                {videoInner}
              </a>
            ) : (
              <div className={styles.video}>{videoInner}</div>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}
