import { useEffect, useSyncExternalStore } from 'react'
import { useLocation } from 'react-router'

/**
 * The server sends each page with its own title, description, language links, preview
 * tags and structured data (marked `data-ssr`, see backend/seo). They're right for the
 * address the visitor landed on, so React adds none of its own there. On the first move
 * to another page they're removed and the pages' own <title>s take over.
 */
let state: { active: boolean; path: string } | null = null
const listeners = new Set<() => void>()

function current() {
  if (!state) {
    const hasServerHead = typeof document !== 'undefined' && document.head.querySelector('[data-ssr]') !== null
    state = { active: hasServerHead, path: typeof window === 'undefined' ? '' : window.location.pathname }
  }
  return state
}

function subscribe(listener: () => void) {
  listeners.add(listener)
  return () => {
    listeners.delete(listener)
  }
}

const isActive = () => current().active

/** True while the server's head tags still describe the page on screen. */
export function useServerHead(): boolean {
  const { pathname } = useLocation()
  const active = useSyncExternalStore(subscribe, isActive, isActive)

  useEffect(() => {
    const head = current()
    if (!head.active || pathname === head.path) return
    head.active = false
    document.head.querySelectorAll('[data-ssr]').forEach((element) => element.remove())
    listeners.forEach((listener) => listener())
  }, [pathname])

  return active
}

/** Tests only: read the document's head again on next use. */
export function resetServerHead() {
  state = null
}
