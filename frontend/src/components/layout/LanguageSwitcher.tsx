import { useEffect, useId, useRef, useState } from 'react'
import { Link as RouterLink, useLocation } from 'react-router'

import { useI18n } from '../../i18n/context'
import { LOCALE_NAMES, LOCALE_SHORT, LOCALES, localizePath, splitLocale } from '../../i18n/locales'
import styles from './LanguageSwitcher.module.css'

/** Header dropdown that opens the current page in another language. */
export function LanguageSwitcher() {
  const { locale, t } = useI18n()
  const [open, setOpen] = useState(false)
  const rootRef = useRef<HTMLDivElement>(null)
  const buttonRef = useRef<HTMLButtonElement>(null)
  const menuId = useId()
  const { pathname, search, hash } = useLocation()
  const { path } = splitLocale(pathname)

  useEffect(() => {
    if (!open) return
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setOpen(false)
        buttonRef.current?.focus()
      }
    }
    const onPointerDown = (event: PointerEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false)
    }
    document.addEventListener('keydown', onKeyDown)
    document.addEventListener('pointerdown', onPointerDown)
    return () => {
      document.removeEventListener('keydown', onKeyDown)
      document.removeEventListener('pointerdown', onPointerDown)
    }
  }, [open])

  return (
    <div ref={rootRef} className={styles.switcher}>
      <button
        ref={buttonRef}
        type="button"
        className={styles.button}
        aria-label={`${t.language.label}: ${LOCALE_NAMES[locale]}`}
        aria-expanded={open}
        aria-controls={menuId}
        onClick={() => setOpen((o) => !o)}
      >
        <GlobeIcon />
        <span className={styles.short} lang={locale}>{LOCALE_SHORT[locale]}</span>
        <svg className={styles.chevron} width="12" height="12" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="m6 9 6 6 6-6" />
        </svg>
      </button>

      <ul id={menuId} className={styles.menu} hidden={!open}>
        {LOCALES.map((other) => (
          <li key={other}>
            <RouterLink
              to={localizePath(path, other) + search + hash}
              className={styles.option}
              lang={other}
              hrefLang={other}
              aria-current={other === locale ? 'true' : undefined}
              onClick={() => setOpen(false)}
            >
              <span>{LOCALE_NAMES[other]}</span>
              {other === locale && (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                  strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M5 12.5l4.5 4.5L19 7.5" />
                </svg>
              )}
            </RouterLink>
          </li>
        ))}
      </ul>
    </div>
  )
}

function GlobeIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="9" />
      <path d="M3 12h18M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3Z" />
    </svg>
  )
}
