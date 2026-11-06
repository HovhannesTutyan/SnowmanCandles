import { useEffect, useId, useState } from 'react'
import { useLocation } from 'react-router'

import { useCart } from '../../context/cart'
import { useI18n } from '../../i18n/context'
import { Link } from '../../i18n/Link'
import { BagIcon, CloseIcon, LogoIcon, MenuIcon, SearchIcon } from '../icons'
import styles from './Header.module.css'
import { LanguageSwitcher } from './LanguageSwitcher'

// Homepage sections work from every page; the footer is on every page.
const NAV_LINKS = [
  { to: '/#winter', key: 'shop' },
  { to: '/#made', key: 'made' },
  { to: '/decorate', key: 'inspiration' },
  { to: '/ingredients', key: 'ingredients' },
  { to: '/candle-care', key: 'care' },
  { to: '/#custom', key: 'custom' },
  { to: '#footer', key: 'contact' },
] as const

interface HeaderProps {
  studioName: string
}

export function Header({ studioName }: HeaderProps) {
  const [menuOpen, setMenuOpen] = useState(false)
  const navId = useId()
  const { count, openPanel } = useCart()
  const { pathname } = useLocation()
  const { t, path } = useI18n()

  useEffect(() => {
    if (!menuOpen) return
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setMenuOpen(false)
    }
    document.addEventListener('keydown', onKeyDown)
    return () => document.removeEventListener('keydown', onKeyDown)
  }, [menuOpen])

  return (
    <header className={styles.header}>
      <div className={styles.inner}>
        <Link to="/" className={styles.logo}>
          <LogoIcon />
          <span className={styles.logoText}>{studioName}</span>
        </Link>

        <nav
          id={navId}
          aria-label={t.nav.main}
          className={`${styles.nav} ${menuOpen ? styles.navOpen : ''}`}
        >
          {NAV_LINKS.map((link) =>
            link.to.startsWith('#') ? (
              <a key={link.to} href={link.to} onClick={() => setMenuOpen(false)}>
                {t.nav[link.key]}
              </a>
            ) : (
              <Link
                key={link.to}
                to={link.to}
                onClick={() => setMenuOpen(false)}
                aria-current={path(link.to) === pathname ? 'page' : undefined}
              >
                {t.nav[link.key]}
              </Link>
            ),
          )}
        </nav>

        <div className={styles.actions}>
          <LanguageSwitcher />
          {/* Search is visual only for now. The bag opens the basket panel. */}
          <button type="button" className={styles.iconButton} aria-label={t.header.search}>
            <SearchIcon />
          </button>
          <button
            type="button"
            className={styles.iconButton}
            aria-label={t.header.cart(count)}
            aria-haspopup="dialog"
            onClick={openPanel}
          >
            <BagIcon />
            {count > 0 && (
              // Keyed by count so the bump animation replays on every add.
              <span key={count} className={styles.badge} aria-hidden="true">
                {count > 99 ? '99+' : count}
              </span>
            )}
          </button>
          <button
            type="button"
            className={`${styles.iconButton} ${styles.menuButton}`}
            aria-label={menuOpen ? t.header.closeMenu : t.header.openMenu}
            aria-expanded={menuOpen}
            aria-controls={navId}
            onClick={() => setMenuOpen((open) => !open)}
          >
            {menuOpen ? <CloseIcon /> : <MenuIcon />}
          </button>
        </div>
      </div>
    </header>
  )
}
