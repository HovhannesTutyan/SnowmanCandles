import { useId, useState, type FormEvent } from 'react'

import { ApiError, outOfStockProblems, placeOrder } from '../api/client'
import type { PlacedOrder } from '../api/types'
import cartStyles from '../components/cart/Cart.module.css'
import { CartTotals } from '../components/cart/CartTotals'
import { PageHead } from '../components/layout/PageHead'
import { useCart } from '../context/cart'
import { useSite } from '../context/site'
import { useCartDetails } from '../hooks/useCartDetails'
import { useI18n } from '../i18n/context'
import { Link } from '../i18n/Link'
import type { Messages } from '../i18n/messages/en'
import { parseItemKey } from '../lib/items'
import basketStyles from './BasketPage.module.css'
import styles from './CheckoutPage.module.css'

type FieldName = 'full_name' | 'phone' | 'email' | 'city' | 'address' | 'notes'
type Values = Record<FieldName, string>
type Errors = Partial<Record<FieldName, string>>

const EMPTY: Values = { full_name: '', phone: '', email: '', city: '', address: '', notes: '' }
const REQUIRED: FieldName[] = ['full_name', 'phone', 'city', 'address']
const PHONE = /^\+?[\d\s()-]{7,20}$/
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function validate(values: Values, t: Messages): Errors {
  const errors: Errors = {}
  for (const field of REQUIRED) {
    if (!values[field].trim()) errors[field] = t.checkout.required
  }
  if (values.phone.trim() && !PHONE.test(values.phone.trim())) errors.phone = t.checkout.invalidPhone
  if (values.email.trim() && !EMAIL.test(values.email.trim())) errors.email = t.checkout.invalidEmail
  return errors
}

/** Server field errors -> our messages ("This field is required." -> t.checkout.required). */
function serverErrors(body: unknown, t: Messages): Errors {
  const errors: Errors = {}
  if (!body || typeof body !== 'object') return errors
  for (const field of Object.keys(EMPTY) as FieldName[]) {
    const messages = (body as Record<string, unknown>)[field]
    if (!Array.isArray(messages)) continue
    errors[field] =
      field === 'phone' ? t.checkout.invalidPhone : field === 'email' ? t.checkout.invalidEmail : t.checkout.required
  }
  return errors
}

/** /checkout: delivery details and the order summary. No payment: the shop calls to confirm. */
export function CheckoutPage() {
  const { t, locale } = useI18n()
  const { content } = useSite()
  const { lines, clear } = useCart()
  const { items, subtotal, canCheckout, refresh } = useCartDetails()
  const { formatPrice } = useSite()
  const [values, setValues] = useState<Values>(EMPTY)
  const [errors, setErrors] = useState<Errors>({})
  const [formError, setFormError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [placed, setPlaced] = useState<PlacedOrder | null>(null)
  const [honeypot, setHoneypot] = useState('')
  const formId = useId()

  const title = <PageHead title={`${t.checkout.pageTitle} — ${content.studio_name}`} />

  if (placed) {
    return (
      <div className={basketStyles.page}>
        {title}
        <div className={`${basketStyles.inner} ${styles.success}`}>
          <div className={`${basketStyles.card} ${styles.successCard}`} role="status">
            <div className={styles.successIcon} aria-hidden="true">
              <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4"
                strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 12.5l4.5 4.5L19 7.5" />
              </svg>
            </div>
            <h1 className={styles.successTitle}>{t.checkout.successTitle}</h1>
            <p className={styles.successNumber}>{t.checkout.orderNumber(placed.number)}</p>
            <p className={styles.successText}>{content.order_success_text}</p>
            <Link to="/" className={cartStyles.primaryButton}>
              {t.checkout.keepShopping}
            </Link>
          </div>
        </div>
      </div>
    )
  }

  if (lines.length === 0) {
    return (
      <div className={basketStyles.page}>
        {title}
        <div className={basketStyles.inner}>
          <div className={basketStyles.card}>
            <div className={cartStyles.empty}>
              <p className={cartStyles.emptyTitle}>{t.checkout.emptyTitle}</p>
              <p className={cartStyles.emptyText}>{t.basket.emptyHint}</p>
              <Link to="/#winter" className={cartStyles.primaryButton}>
                {t.basket.continueShopping}
              </Link>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const change = (field: FieldName) => (event: { target: { value: string } }) => {
    const value = event.target.value
    setValues((v) => ({ ...v, [field]: value }))
    if (errors[field]) setErrors((e) => ({ ...e, [field]: undefined }))
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setFormError('')
    const found = validate(values, t)
    setErrors(found)
    if (Object.keys(found).length > 0) {
      setFormError(t.checkout.fixErrors)
      document.getElementById(`${formId}-${Object.keys(found)[0]}`)?.focus()
      return
    }
    if (!canCheckout) {
      setFormError(t.basket.fixProblems)
      return
    }
    setSubmitting(true)
    try {
      const order = await placeOrder(
        {
          items: lines.flatMap((line) => {
            const parsed = parseItemKey(line.key)
            return parsed ? [{ ...parsed, scent: line.scent ?? '', quantity: line.quantity }] : []
          }),
          full_name: values.full_name.trim(),
          phone: values.phone.trim(),
          email: values.email.trim(),
          city: values.city.trim(),
          address: values.address.trim(),
          notes: values.notes.trim(),
          language: locale,
          website: honeypot,
        },
        locale,
      )
      if (!order?.number) throw new Error('Unexpected order answer.')
      setPlaced(order)
      clear()
      window.scrollTo({ top: 0 })
    } catch (error) {
      if (outOfStockProblems(error)) {
        setFormError(t.checkout.stockChanged)
        refresh()
      } else if (error instanceof ApiError && error.status === 400) {
        const fieldErrors = serverErrors(error.body, t)
        setErrors(fieldErrors)
        setFormError(Object.keys(fieldErrors).length ? t.checkout.fixErrors : t.checkout.failed)
      } else {
        setFormError(t.checkout.failed)
      }
    } finally {
      setSubmitting(false)
    }
  }

  const field = (name: FieldName, label: string, options: { type?: string; autoComplete?: string; hint?: string } = {}) => {
    const id = `${formId}-${name}`
    const error = errors[name]
    const describedBy = [options.hint && `${id}-hint`, error && `${id}-error`].filter(Boolean).join(' ') || undefined
    return (
      <div className={`${styles.field} ${error ? styles.fieldError : ''}`}>
        <label htmlFor={id}>
          {label}
          {REQUIRED.includes(name) && <span aria-hidden="true"> *</span>}
        </label>
        <input
          id={id}
          name={name}
          type={options.type ?? 'text'}
          autoComplete={options.autoComplete}
          value={values[name]}
          onChange={change(name)}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy}
          aria-required={REQUIRED.includes(name) || undefined}
        />
        {options.hint && <span id={`${id}-hint`} className={styles.hint}>{options.hint}</span>}
        {error && <span id={`${id}-error`} className={styles.error}>{error}</span>}
      </div>
    )
  }

  return (
    <div className={basketStyles.page}>
      {title}
      <div className={basketStyles.inner}>
        <header className={basketStyles.head}>
          <h1 className={basketStyles.title}>{t.checkout.title}</h1>
          <p className={basketStyles.intro}>{t.checkout.intro}</p>
        </header>

        <div className={basketStyles.grid}>
          <form className={basketStyles.card} onSubmit={handleSubmit} noValidate aria-labelledby={`${formId}-title`}>
            <h2 id={`${formId}-title`} className={basketStyles.sectionTitle}>{t.checkout.details}</h2>
            <div className={styles.fields}>
              {field('full_name', t.checkout.fullName, { autoComplete: 'name' })}
              {field('phone', t.checkout.phone, { type: 'tel', autoComplete: 'tel', hint: t.checkout.phoneHint })}
              {field('email', t.checkout.email, { type: 'email', autoComplete: 'email' })}
              {field('city', t.checkout.city, { autoComplete: 'address-level2' })}
              <div className={styles.wide}>
                {field('address', t.checkout.address, { autoComplete: 'street-address' })}
              </div>
              <div className={`${styles.field} ${styles.wide}`}>
                <label htmlFor={`${formId}-notes`}>{t.checkout.notes}</label>
                <textarea
                  id={`${formId}-notes`}
                  name="notes"
                  rows={3}
                  value={values.notes}
                  placeholder={t.checkout.notesPlaceholder}
                  onChange={change('notes')}
                />
              </div>
            </div>

            {/* Left empty by people (hidden); bots tend to fill it in. */}
            <div className={styles.honeypot} aria-hidden="true">
              <label htmlFor={`${formId}-website`}>Website</label>
              <input id={`${formId}-website`} name="website" tabIndex={-1} autoComplete="off"
                value={honeypot} onChange={(e) => setHoneypot(e.target.value)} />
            </div>

            {formError && (
              <p className={styles.formError} role="alert">
                {formError}{' '}
                {formError === t.checkout.stockChanged && <Link to="/basket">{t.checkout.backToBasket}</Link>}
              </p>
            )}

            <div className={styles.actions}>
              <Link to="/basket" className={basketStyles.back}>← {t.checkout.backToBasket}</Link>
              <button type="submit" className={cartStyles.primaryButton} disabled={submitting || !canCheckout}>
                {submitting ? t.checkout.placing : t.checkout.placeOrder}
              </button>
            </div>
          </form>

          <aside className={`${basketStyles.card} ${basketStyles.summary}`} aria-labelledby={`${formId}-summary`}>
            <h2 id={`${formId}-summary`} className={basketStyles.sectionTitle}>{t.checkout.summary}</h2>
            <ul className={styles.summaryLines}>
              {items.map(({ line, details, lineTotal, problem }) => (
                <li key={`${line.key}|${line.scent ?? ''}`} className={problem ? styles.summaryProblem : undefined}>
                  <span className={styles.summaryImage} style={{ background: details?.tint }}>
                    {details?.image && <img src={details.image} alt="" />}
                    <span className={styles.summaryQty}>{line.quantity}</span>
                  </span>
                  <span className={styles.summaryText}>
                    <span className={styles.summaryTitle}>{details?.title ?? '…'}</span>
                    {details?.scent && <span className={styles.summaryMeta}>{t.basket.scent(details.scent)}</span>}
                    {problem && <span className={cartStyles.lineWarning}>{t.basket.fixProblems}</span>}
                  </span>
                  <span className={styles.summaryPrice}>{details ? formatPrice(lineTotal.toFixed(2)) : ''}</span>
                </li>
              ))}
            </ul>
            <CartTotals subtotal={subtotal} />
          </aside>
        </div>
      </div>
    </div>
  )
}
