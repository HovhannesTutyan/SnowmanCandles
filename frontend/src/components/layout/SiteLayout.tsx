import type { CSSProperties } from 'react'
import { Outlet, ScrollRestoration } from 'react-router'

import { fetchSite } from '../../api/client'
import { SiteProvider } from '../../context/SiteProvider'
import { useI18n } from '../../i18n/context'
import { useAsync } from '../../hooks/useAsync'
import { CartPanel } from '../cart/CartPanel'
import { ErrorScreen, LoadingScreen } from '../StatusScreen'
import { Footer } from './Footer'
import { Header } from './Header'
import { Ticker } from './Ticker'

/** Ticker, header and footer around every page, with the site texts loaded once. */
export function SiteLayout() {
  const { locale } = useI18n()
  const site = useAsync(`site/${locale}`, (signal) => fetchSite(locale, signal))

  if (site.status === 'loading') return <LoadingScreen />
  if (site.status === 'error') return <ErrorScreen error={site.error} onRetry={site.retry} />

  const content = site.data
  // The accent colour chosen in the admin drives buttons, links and the logo flame.
  const themeStyle = { '--accent': content.accent_color } as CSSProperties

  return (
    <SiteProvider content={content}>
      <div style={themeStyle}>
        <Ticker messages={content.ticker_messages} />
        <Header studioName={content.studio_name} />
        <main>
          <Outlet />
        </main>
        <Footer content={content} />
      </div>
      <CartPanel />
      <ScrollRestoration />
    </SiteProvider>
  )
}
