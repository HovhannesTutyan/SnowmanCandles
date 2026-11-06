import { useId, useState, type FormEvent } from 'react'

import { useI18n } from '../../i18n/context'
import styles from './Newsletter.module.css'

interface NewsletterProps {
  title: string
  text: string
}

/** Visual only for now: submitting shows a note instead of saving the email. */
export function Newsletter({ title, text }: NewsletterProps) {
  const [submitted, setSubmitted] = useState(false)
  const { t } = useI18n()
  const inputId = useId()

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSubmitted(true)
  }

  return (
    <section className={`${styles.section} reveal`} aria-labelledby={`${inputId}-title`}>
      <div className={styles.inner}>
        <h2 id={`${inputId}-title`} className={styles.title}>{title}</h2>
        <p className={styles.text}>{text}</p>
        <form className={styles.form} onSubmit={handleSubmit}>
          <label htmlFor={inputId} className="visually-hidden">{t.home.emailLabel}</label>
          <input
            id={inputId}
            className={styles.input}
            type="email"
            name="email"
            placeholder={t.home.emailPlaceholder}
            autoComplete="email"
            required
          />
          <button type="submit" className={styles.button}>{t.home.subscribe}</button>
        </form>
        <p className={styles.note} role="status">
          {submitted ? t.home.subscribed : ''}
        </p>
      </div>
    </section>
  )
}
