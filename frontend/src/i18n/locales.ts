/**
 * The site's languages. Armenian is the default and lives at the site root
 * ("/candles/…"); English and Russian get a prefix ("/en/candles/…", "/ru/candles/…").
 */
export const LOCALES = ['hy', 'en', 'ru'] as const
export type Locale = (typeof LOCALES)[number]

export const DEFAULT_LOCALE: Locale = 'hy'

/** Address prefix of each language ("" for the default). */
export const LOCALE_PREFIX: Record<Locale, string> = { hy: '', en: '/en', ru: '/ru' }

/** For Intl number formatting and the <html lang> attribute. */
export const INTL_LOCALE: Record<Locale, string> = { hy: 'hy-AM', en: 'en-US', ru: 'ru-RU' }

/** Each language in its own words, for the language menu. */
export const LOCALE_NAMES: Record<Locale, string> = { hy: 'Հայերեն', en: 'English', ru: 'Русский' }

/** Short labels for the header button. */
export const LOCALE_SHORT: Record<Locale, string> = { hy: 'ՀԱՅ', en: 'EN', ru: 'РУС' }

/**
 * Turns a site path ("/", "/candle-care", "/#winter") into the same path in `locale`.
 * Anything that isn't a site-absolute path (hashes, full URLs) is returned unchanged.
 */
export function localizePath(path: string, locale: Locale): string {
  if (!path.startsWith('/')) return path
  const prefix = LOCALE_PREFIX[locale]
  if (!prefix) return path
  if (path === '/') return prefix
  if (path.startsWith('/#') || path.startsWith('/?')) return prefix + path.slice(1)
  return prefix + path
}

/** The language a pathname belongs to, and the pathname without its prefix. */
export function splitLocale(pathname: string): { locale: Locale; path: string } {
  for (const locale of LOCALES) {
    const prefix = LOCALE_PREFIX[locale]
    if (prefix && (pathname === prefix || pathname.startsWith(prefix + '/'))) {
      return { locale, path: pathname.slice(prefix.length) || '/' }
    }
  }
  return { locale: DEFAULT_LOCALE, path: pathname || '/' }
}
