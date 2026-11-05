import { useEffect, useState } from 'react'

/**
 * The id of the section currently in view (the last one whose top has passed the
 * upper third of the window), for highlighting the matching link in a section nav.
 */
export function useActiveSection(ids: string[]): string | null {
  const [active, setActive] = useState<string | null>(null)
  const key = ids.join(',')

  useEffect(() => {
    const sections = key
      .split(',')
      .map((id) => document.getElementById(id))
      .filter((el): el is HTMLElement => el !== null)
    if (sections.length === 0 || typeof IntersectionObserver === 'undefined') return

    const update = () => {
      const line = window.innerHeight / 3
      let current: string | null = null
      for (const section of sections) {
        if (section.getBoundingClientRect().top <= line) current = section.id
      }
      setActive(current)
    }

    // Re-check whenever a section crosses the viewport; cheaper than a scroll listener.
    const observer = new IntersectionObserver(update, {
      threshold: [0, 0.25, 0.5, 0.75, 1],
    })
    sections.forEach((section) => observer.observe(section))
    update()
    return () => observer.disconnect()
  }, [key])

  return active
}
