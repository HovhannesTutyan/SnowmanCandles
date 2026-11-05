/**
 * Images from the original design. They are used wherever the admin has not
 * uploaded a replacement (every SiteContent image is optional).
 */
import carouselCandle from '../assets/design/carousel-candle.webp'
import hollyBaubleCandle from '../assets/design/holly-bauble-candle.webp'
import pineGarlandBauble from '../assets/design/pine-garland-bauble.webp'
import plasterBauble from '../assets/design/plaster-bauble.webp'
import snowmenCampfire from '../assets/design/snowmen-campfire.webp'
import vintageRoadsterCandle from '../assets/design/vintage-roadster-candle.webp'

import type { ContentImages } from '../api/types'

export const designImages: Record<keyof ContentImages, string> = {
  made_before: plasterBauble,
  made_after: hollyBaubleCandle,
  video: snowmenCampfire,
  single_tile: vintageRoadsterCandle,
  sets_tile: snowmenCampfire,
  custom_1: pineGarlandBauble,
  custom_2: carouselCandle,
}

/** Admin-uploaded images, with the design's image wherever none was uploaded. */
export function withDesignFallbacks(images: ContentImages): Record<keyof ContentImages, string> {
  const resolved = { ...designImages }
  for (const key of Object.keys(designImages) as (keyof ContentImages)[]) {
    resolved[key] = images[key] ?? designImages[key]
  }
  return resolved
}
