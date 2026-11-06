import { createContext, useContext } from 'react'

import { INTL_LOCALE, localizePath, type Locale } from './locales'
import { en, type Messages } from './messages/en'
import { hy } from './messages/hy'
import { ru } from './messages/ru'

const MESSAGES: Record<Locale, Messages> = { hy, en, ru }

export interface I18n {
  locale: Locale
  /** Interface texts in the current language. */
  t: Messages
  /** The same site path in the current language, e.g. "/candle-care" -> "/en/candle-care". */
  path: (to: string) => string
  /** BCP 47 tag for Intl formatting, e.g. "hy-AM". */
  intlLocale: string
}

export function createI18n(locale: Locale): I18n {
  return {
    locale,
    t: MESSAGES[locale],
    path: (to) => localizePath(to, locale),
    intlLocale: INTL_LOCALE[locale],
  }
}

// Components rendered on their own (e.g. in unit tests) get English.
export const I18nContext = createContext<I18n>(createI18n('en'))

/** The current language, its interface texts and a helper for links. */
export function useI18n(): I18n {
  return useContext(I18nContext)
}
