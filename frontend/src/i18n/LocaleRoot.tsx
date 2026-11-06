import { useEffect, useMemo } from 'react'
import { Outlet, useLocation } from 'react-router'

import { createI18n, I18nContext } from './context'
import { DEFAULT_LOCALE, INTL_LOCALE, LOCALES, localizePath, splitLocale, type Locale } from './locales'

/**
 * Root of each language's routes ("/", "/en", "/ru"): provides the language to the page,
 * sets <html lang> and tells search engines where the other languages are.
 */
export function LocaleRoot({ locale }: { locale: Locale }) {
  const i18n = useMemo(() => createI18n(locale), [locale])
  const { pathname } = useLocation()
  const { path } = splitLocale(pathname)

  useEffect(() => {
    document.documentElement.lang = INTL_LOCALE[locale]
  }, [locale])

  const origin = typeof window === 'undefined' ? '' : window.location.origin

  return (
    <I18nContext.Provider value={i18n}>
      {/* React 19 hoists these into <head>. */}
      {LOCALES.map((other) => (
        <link key={other} rel="alternate" hrefLang={other} href={origin + localizePath(path, other)} />
      ))}
      <link rel="alternate" hrefLang="x-default" href={origin + localizePath(path, DEFAULT_LOCALE)} />
      <Outlet />
    </I18nContext.Provider>
  )
}
