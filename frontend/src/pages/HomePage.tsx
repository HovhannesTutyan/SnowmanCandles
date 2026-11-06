import { useEffect, useMemo } from 'react'
import { useLocation } from 'react-router'

import { fetchHome } from '../api/client'
import type { HomeData } from '../api/types'
import { CollectionGrid } from '../components/home/CollectionGrid'
import { CustomBand } from '../components/home/CustomBand'
import { Hero } from '../components/home/Hero'
import { HowItsMade } from '../components/home/HowItsMade'
import { Newsletter } from '../components/home/Newsletter'
import { ShopByType, type TypeTile } from '../components/home/ShopByType'
import { ErrorScreen, LoadingScreen } from '../components/StatusScreen'
import { useSite } from '../context/site'
import { useI18n } from '../i18n/context'
import { useAsync } from '../hooks/useAsync'
import { withDesignFallbacks } from '../lib/designImages'

export function HomePage() {
  const { locale } = useI18n()
  const home = useAsync(`home/${locale}`, (signal) => fetchHome(locale, signal))

  if (home.status === 'loading') return <LoadingScreen variant="page" />
  if (home.status === 'error') {
    return <ErrorScreen variant="page" error={home.error} onRetry={home.retry} />
  }
  return <HomeView data={home.data} />
}

/** Scrolls to "/#section" links (e.g. from a product page) once the sections exist. */
function useScrollToHash() {
  const { hash, key } = useLocation()
  useEffect(() => {
    if (!hash) return
    document.getElementById(decodeURIComponent(hash.slice(1)))?.scrollIntoView()
  }, [hash, key])
}

function HomeView({ data }: { data: HomeData }) {
  const { content, formatPrice } = useSite()
  const { t } = useI18n()
  const { slides, featured_candles, featured_collections } = data
  useScrollToHash()

  const items = useMemo(
    () => [...featured_candles, ...featured_collections],
    [featured_candles, featured_collections],
  )
  const images = withDesignFallbacks(content.images)

  const tiles: TypeTile[] = [
    {
      title: t.home.singleTile,
      text: content.single_tile_text,
      image: images.single_tile,
      background: '#8C2A1E',
      textColor: '#F6D9D2',
      imageStyle: { width: '64%', maxWidth: 360, margin: '0 -16px -10px 0' },
    },
    {
      title: t.home.setsTile,
      text: content.sets_tile_text,
      image: images.sets_tile,
      background: '#6B4A2E',
      textColor: '#F0E1CF',
      imageStyle: { width: '64%', maxWidth: 380, margin: '0 -8px -14px 0' },
    },
  ]

  return (
    <>
      {/* React 19 hoists <title> into <head>. */}
      <title>{t.home.pageTitle(content.studio_name)}</title>
      <Hero content={content} slides={slides} items={items} formatPrice={formatPrice} />
      <CollectionGrid
        eyebrow={content.collection_eyebrow}
        title={content.collection_title}
        items={items}
        formatPrice={formatPrice}
      />
      <HowItsMade
        content={content}
        images={{ before: images.made_before, after: images.made_after, video: images.video }}
      />
      <ShopByType tiles={tiles} />
      <CustomBand
        title={content.custom_title}
        text={content.custom_text}
        buttonText={content.custom_button_text}
        images={[images.custom_1, images.custom_2]}
      />
      <Newsletter title={content.newsletter_title} text={content.newsletter_text} />
    </>
  )
}
