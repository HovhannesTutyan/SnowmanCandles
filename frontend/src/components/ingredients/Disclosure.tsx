import { useId, useState } from 'react'

import styles from './Disclosure.module.css'

interface DisclosureProps {
  question: string
  answer: string
  defaultOpen?: boolean
}

/** A question that opens and closes on its own (several can be open at once). */
export function Disclosure({ question, answer, defaultOpen = false }: DisclosureProps) {
  const [open, setOpen] = useState(defaultOpen)
  const panelId = useId()

  return (
    <div className={styles.row}>
      <h3 className={styles.heading}>
        <button
          type="button"
          className={styles.button}
          aria-expanded={open}
          aria-controls={panelId}
          onClick={() => setOpen((o) => !o)}
        >
          {question}
          <span className={styles.plus} aria-hidden="true">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--accent)"
              strokeWidth="2" strokeLinecap="round">
              <path d="M12 5v14M5 12h14" />
            </svg>
          </span>
        </button>
      </h3>
      <p id={panelId} className={styles.answer} hidden={!open}>
        {answer}
      </p>
    </div>
  )
}
