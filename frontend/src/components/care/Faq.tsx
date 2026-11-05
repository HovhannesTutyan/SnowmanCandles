import { useId, useState } from 'react'

import styles from './Faq.module.css'

interface FaqProps {
  title: string
  items: { question: string; answer: string }[]
}

/** One answer open at a time; the first starts open, as in the design. */
export function Faq({ title, items }: FaqProps) {
  const [open, setOpen] = useState<number | null>(0)
  const baseId = useId()

  if (items.length === 0) return null

  return (
    <section id="faq" className={styles.section} aria-labelledby={`${baseId}-title`}>
      <h2 id={`${baseId}-title`} className={`${styles.title} reveal`}>{title}</h2>
      <div className={styles.list}>
        {items.map((item, index) => {
          const expanded = open === index
          const panelId = `${baseId}-panel-${index}`
          return (
            <div key={`${index}-${item.question}`} className={`${styles.row} reveal`}>
              <h3 className={styles.heading}>
                <button
                  type="button"
                  className={styles.question}
                  aria-expanded={expanded}
                  aria-controls={panelId}
                  onClick={() => setOpen(expanded ? null : index)}
                >
                  {item.question}
                  <span className={styles.plus} aria-hidden="true">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent)"
                      strokeWidth="2" strokeLinecap="round">
                      <path d="M12 5v14M5 12h14" />
                    </svg>
                  </span>
                </button>
              </h3>
              <p id={panelId} className={styles.answer} hidden={!expanded}>
                {item.answer}
              </p>
            </div>
          )
        })}
      </div>
    </section>
  )
}
