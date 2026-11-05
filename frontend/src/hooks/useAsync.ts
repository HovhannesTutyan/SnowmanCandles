import { useCallback, useEffect, useRef, useState } from 'react'

export type AsyncState<T> =
  | { status: 'loading' }
  | { status: 'error'; error: Error }
  | { status: 'success'; data: T }

type Settled<T> = { key: string; state: AsyncState<T> }

/**
 * Runs `load` whenever `key` changes (or `retry` is called) and returns its state.
 * Requests that are superseded or unmounted are aborted, and a new key shows
 * "loading" straight away instead of the previous key's data.
 */
export function useAsync<T>(
  key: string,
  load: (signal: AbortSignal) => Promise<T>,
): AsyncState<T> & { retry: () => void } {
  const [attempt, setAttempt] = useState(0)
  const requestKey = `${key}#${attempt}`
  const [settled, setSettled] = useState<Settled<T> | null>(null)

  // Always call the latest `load` without re-running the request when only its identity changes.
  const loadRef = useRef(load)
  useEffect(() => {
    loadRef.current = load
  })

  useEffect(() => {
    const controller = new AbortController()
    loadRef.current(controller.signal)
      .then((data) => setSettled({ key: requestKey, state: { status: 'success', data } }))
      .catch((error: unknown) => {
        if (controller.signal.aborted) return
        const err = error instanceof Error ? error : new Error(String(error))
        setSettled({ key: requestKey, state: { status: 'error', error: err } })
      })
    return () => controller.abort()
  }, [requestKey])

  const retry = useCallback(() => setAttempt((n) => n + 1), [])
  const state: AsyncState<T> =
    settled && settled.key === requestKey ? settled.state : { status: 'loading' }

  return { ...state, retry }
}
