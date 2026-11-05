import { useId, useState, type ReactNode } from 'react'

import styles from './Accordion.module.css'

export interface AccordionItem {
  title: string
  content: ReactNode
}

/** One panel open at a time; the first starts open, as in the design. */
export function Accordion({ items }: { items: AccordionItem[] }) {
  const [open, setOpen] = useState<number | null>(0)
  const baseId = useId()

  return (
    <div className={styles.accordion}>
      {items.map((item, index) => {
        const expanded = open === index
        const buttonId = `${baseId}-button-${index}`
        const panelId = `${baseId}-panel-${index}`
        return (
          <div key={item.title} className={styles.item}>
            <h2 className={styles.heading}>
              <button
                id={buttonId}
                type="button"
                className={styles.button}
                aria-expanded={expanded}
                aria-controls={panelId}
                onClick={() => setOpen(expanded ? null : index)}
              >
                {item.title}
                <svg className={styles.chevron} width="20" height="20" viewBox="0 0 24 24" fill="none"
                  stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                  aria-hidden="true">
                  <path d="m6 9 6 6 6-6" />
                </svg>
              </button>
            </h2>
            <div id={panelId} role="region" aria-labelledby={buttonId} hidden={!expanded} className={styles.panel}>
              {item.content}
            </div>
          </div>
        )
      })}
    </div>
  )
}
