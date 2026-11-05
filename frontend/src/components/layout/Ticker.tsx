import { Fragment } from 'react'

import { repeatToLength } from '../../lib/repeat'
import styles from './Ticker.module.css'

interface TickerProps {
  messages: string[]
}

/** The scrolling announcement bar at the very top of the page. */
export function Ticker({ messages }: TickerProps) {
  if (messages.length === 0) return null

  const items = repeatToLength(messages, 4)

  return (
    <div className={styles.ticker}>
      {/* Screen readers get the messages once, not the moving copies. */}
      <p className="visually-hidden">{messages.join('. ')}</p>
      <div className={styles.track} aria-hidden="true">
        {/* Two identical halves: the track slides by -50% and loops seamlessly. */}
        {[0, 1].map((half) => (
          <Fragment key={half}>
            {items.map((message, index) => (
              <Fragment key={index}>
                <span className={styles.message}>{message}</span>
                <span className={styles.star}>✦</span>
              </Fragment>
            ))}
          </Fragment>
        ))}
      </div>
    </div>
  )
}
