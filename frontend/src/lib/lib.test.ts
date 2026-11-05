import { describe, expect, it } from 'vitest'

import { designImages, withDesignFallbacks } from './designImages'
import { createPriceFormatter } from './format'
import { repeatToLength } from './repeat'
import { makeContent } from '../test/fixtures'

describe('createPriceFormatter', () => {
  it('formats API decimal strings in the shop currency', () => {
    expect(createPriceFormatter('USD')('24.00')).toBe('$24.00')
    expect(createPriceFormatter('EUR')('1250.5')).toBe('€1,250.50')
  })

  it('falls back gracefully for an unknown currency code', () => {
    expect(createPriceFormatter('ZZ')('24')).toBe('24.00 ZZ')
  })

  it('returns non-numeric input unchanged', () => {
    expect(createPriceFormatter('USD')('n/a')).toBe('n/a')
  })
})

describe('repeatToLength', () => {
  it('repeats items until the minimum length is reached', () => {
    expect(repeatToLength(['a', 'b'], 5)).toEqual(['a', 'b', 'a', 'b', 'a', 'b'])
  })

  it('handles empty and already-long lists', () => {
    expect(repeatToLength([], 5)).toEqual([])
    expect(repeatToLength([1, 2, 3], 2)).toEqual([1, 2, 3])
  })
})

describe('withDesignFallbacks', () => {
  it('uses uploaded images and the design image for the rest', () => {
    const images = withDesignFallbacks(makeContent().images)
    expect(images.made_after).toBe('http://localhost/media/homepage/after.webp')
    expect(images.made_before).toBe(designImages.made_before)
  })
})
