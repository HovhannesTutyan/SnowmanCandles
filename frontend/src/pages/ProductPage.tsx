import { Link, useParams } from 'react-router'

import { fetchProduct, isNotFound } from '../api/client'
import type { ProductDetail, ProductKind } from '../api/types'
import { BuyBox } from '../components/product/BuyBox'
import { MakingOf } from '../components/product/MakingOf'
import { ProductGallery } from '../components/product/ProductGallery'
import { ProductShowcase } from '../components/product/ProductShowcase'
import { RelatedProducts } from '../components/product/RelatedProducts'
import { ErrorScreen, LoadingScreen } from '../components/StatusScreen'
import { useSite } from '../context/site'
import { useAsync } from '../hooks/useAsync'
import { NotFoundPage } from './NotFoundPage'
import styles from './ProductPage.module.css'

export function ProductPage({ kind }: { kind: ProductKind }) {
  const { slug = '' } = useParams()
  const product = useAsync(`${kind}/${slug}`, (signal) => fetchProduct(kind, slug, signal))

  if (product.status === 'loading') return <LoadingScreen variant="page" />
  if (product.status === 'error') {
    if (isNotFound(product.error)) {
      return (
        <NotFoundPage
          title="We couldn't find that piece"
          message="It may have been renamed or taken out of the shop."
        />
      )
    }
    return <ErrorScreen variant="page" error={product.error} onRetry={product.retry} />
  }
  // Keyed so scent, quantity and gallery reset when moving to another product.
  return <ProductView key={`${kind}/${slug}`} product={product.data} />
}

function categoryLabel(product: ProductDetail): string {
  if (product.product_type === 'collection') return 'Collections'
  return product.product_type === 'set' ? 'Candle sets' : 'Single candles'
}

function ProductView({ product }: { product: ProductDetail }) {
  const { content, formatPrice } = useSite()
  const hasShowcase = product.showcase_views.length > 0
  // The showcase already shows the main image; the gallery stays for lit and extra photos.
  const showGallery = !hasShowcase || product.flame !== null || product.gallery.length > 0

  return (
    <>
      <title>{`${product.title} — ${content.studio_name}`}</title>
      <meta name="description" content={product.description} />

      <section className={styles.product}>
        <nav aria-label="Breadcrumb" className={`${styles.breadcrumb} ${styles.rise}`}>
          <ol>
            <li><Link to="/">Home</Link></li>
            <li><Link to="/#shop">{categoryLabel(product)}</Link></li>
            <li><span aria-current="page">{product.title}</span></li>
          </ol>
        </nav>

        {hasShowcase && (
          <div className={`${styles.showcase} ${styles.rise}`} style={{ animationDelay: '.1s' }}>
            <ProductShowcase
              title={product.title}
              price={formatPrice(product.price)}
              views={product.showcase_views}
            />
          </div>
        )}

        <div className={styles.grid}>
          {showGallery && (
            <div className={`${styles.galleryColumn} ${styles.rise}`} style={{ animationDelay: '.1s' }}>
              <ProductGallery product={product} />
            </div>
          )}
          <div className={`${styles.buyColumn} ${styles.rise}`} style={{ animationDelay: '.25s' }}>
            <BuyBox product={product} wide={!showGallery} />
          </div>
        </div>
      </section>

      <MakingOf product={product} />
      <RelatedProducts items={product.related} />
    </>
  )
}
