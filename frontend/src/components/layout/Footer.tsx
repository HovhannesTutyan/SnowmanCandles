import { Link } from 'react-router'

import type { SiteContent } from '../../api/types'
import styles from './Footer.module.css'

const YEAR = new Date().getFullYear()

interface FooterProps {
  content: SiteContent
}

export function Footer({ content }: FooterProps) {
  const { studio_name, footer_text, contact_email, contact_phone, instagram_handle } = content
  const handle = instagram_handle.replace(/^@/, '')
  const hasContact = Boolean(contact_email || contact_phone || handle)

  return (
    <footer id="footer" className={styles.footer}>
      <div className={styles.grid}>
        <div>
          <div className={styles.brand}>{studio_name}</div>
          <p className={styles.tagline}>{footer_text}</p>
        </div>

        <nav aria-label="Shop" className={styles.column}>
          <div className={styles.heading}>Shop</div>
          <Link to="/#winter">Winter collection</Link>
          <Link to="/#shop">Single candles</Link>
          <Link to="/#shop">Candle sets</Link>
        </nav>

        <nav aria-label="Help" className={styles.column}>
          <div className={styles.heading}>Help</div>
          <Link to="/#made">How it's made</Link>
          <Link to="/decorate">Decorate with candles</Link>
          <Link to="/ingredients">What's inside our candles</Link>
          <Link to="/candle-care">Candle care &amp; tips</Link>
          <Link to="/#custom">Custom orders</Link>
          <a href="#footer">Contact</a>
        </nav>

        {hasContact && (
          <div className={styles.column}>
            <div className={styles.heading}>Say hello</div>
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
