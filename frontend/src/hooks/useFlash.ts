import { useCallback, useEffect, useRef, useState } from 'react'

/** A flag that turns on when `flash()` is called and off again after `ms`. */
export function useFlash(ms: number): [active: boolean, flash: () => void] {
  const [active, setActive] = useState(false)
  const timer = useRef<number | undefined>(undefined)

  const flash = useCallback(() => {
    window.clearTimeout(timer.current)
    setActive(true)
    timer.current = window.setTimeout(() => setActive(false), ms)
  }, [ms])

  useEffect(() => () => window.clearTimeout(timer.current), [])

  return [active, flash]
}
