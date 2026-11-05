import { useId, useState, type FormEvent } from 'react'

import styles from './Newsletter.module.css'

interface NewsletterProps {
  title: string
  text: string
}

/** Visual only for now: submitting shows a note instead of saving the email. */
export function Newsletter({ title, text }: NewsletterProps) {
  const [submitted, setSubmitted] = useState(false)
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
          <label htmlFor={inputId} className="visually-hidden">Email address</label>
          <input
            id={inputId}
            className={styles.input}
            type="email"
            name="email"
            placeholder="you@example.com"
            autoComplete="email"
            required
          />
          <button type="submit" className={styles.button}>Subscribe</button>
        </form>
        <p className={styles.note} role="status">
          {submitted ? 'Thanks! Newsletter sign-up is opening soon.' : ''}
        </p>
      </div>
    </section>
  )
}
