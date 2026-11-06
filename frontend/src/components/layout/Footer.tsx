import { useI18n } from '../../i18n/context'
import { Link } from '../../i18n/Link'

import type { SiteContent } from '../../api/types'
import styles from './Footer.module.css'

const YEAR = new Date().getFullYear()

interface FooterProps {
  content: SiteContent
}

export function Footer({ content }: FooterProps) {
  const { studio_name, footer_text, contact_email, contact_phone, instagram_handle } = content
  const { t } = useI18n()
  const handle = instagram_handle.replace(/^@/, '')
  const hasContact = Boolean(contact_email || contact_phone || handle)

  return (
    <footer id="footer" className={styles.footer}>
      <div className={styles.grid}>
        <div>
          <div className={styles.brand}>{studio_name}</div>
          <p className={styles.tagline}>{footer_text}</p>
        </div>

        <nav aria-label={t.footer.shop} className={styles.column}>
          <div className={styles.heading}>{t.footer.shop}</div>
          <Link to="/#winter">{t.footer.winter}</Link>
          <Link to="/#shop">{t.footer.single}</Link>
          <Link to="/#shop">{t.footer.sets}</Link>
        </nav>

        <nav aria-label={t.footer.help} className={styles.column}>
          <div className={styles.heading}>{t.footer.help}</div>
          <Link to="/#made">{t.footer.made}</Link>
          <Link to="/decorate">{t.footer.decorate}</Link>
          <Link to="/ingredients">{t.footer.ingredients}</Link>
          <Link to="/candle-care">{t.footer.care}</Link>
          <Link to="/#custom">{t.footer.custom}</Link>
          <a href="#footer">{t.footer.contact}</a>
        </nav>

        {hasContact && (
          <div className={styles.column}>
            <div className={styles.heading}>{t.footer.sayHello}</div>
            {contact_email && <a href={`mailto:${contact_email}`}>{contact_email}</a>}
            {contact_phone && (
              <a href={`tel:${contact_phone.replace(/[^\d+]/g, '')}`}>{contact_phone}</a>
            )}
            {handle && (
              <a href={`https://instagram.com/${handle}`} target="_blank" rel="noopener noreferrer">
                Instagram @{handle}
              </a>
            )}
          </div>
        )}
      </div>
      <div className={styles.bottom}>
        © {YEAR} {studio_name}
      </div>
    </footer>
  )
}
