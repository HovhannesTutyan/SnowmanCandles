/*
 * Translation helpers for admin forms.
 *
 * django-modeltranslation shows every translated field three times (Title [en], Title [hy],
 * Title [ru]). This script:
 *   - groups the three boxes under one heading, labelled English / Armenian / Russian;
 *   - marks Armenian and Russian boxes that are still empty ("Missing");
 *   - adds a toolbar with live counts, a language filter and "Translate missing";
 *   - adds a "Translate" button to each group (re-translates that one field).
 * Translations are only filled into the form: nothing is saved until you press Save.
 */
(function () {
  'use strict'

  const configElement = document.getElementById('languages-config')
  if (!configElement) return
  const config = JSON.parse(configElement.textContent)
  const SOURCE = config.source
  const TARGETS = config.targets
  const LANGS = [SOURCE, ...TARGETS]
  const SUFFIX = new RegExp('_(' + LANGS.join('|') + ')$')
  const FILTER_KEY = 'languages-admin-filter'
  const BATCH_TEXTS = 40
  const BATCH_CHARS = 12000

  const OFF_HINT =
    'Automatic translation is off. Add a translation service key to backend/.env to turn it on (see the README).'

  function el(tag, className, text) {
    const node = document.createElement(tag)
    if (className) node.className = className
    if (text !== undefined) node.textContent = text
    return node
  }

  function isTemplate(node) {
    // The hidden "empty form" Django copies when you click "Add another …".
    return Boolean(node.closest('.empty-form')) || /__prefix__/.test(node.name || '')
  }

  // ---------------------------------------------------------------- grouping

  function fieldName(row) {
    const label = row.querySelector('label')
    const text = label ? label.textContent : ''
    return text.replace(/\s*\[(?:en|hy|ru)\]\s*:?\s*$/i, '').replace(/:\s*$/, '').trim()
  }

  function decorateRow(row, lang, input) {
    row.classList.add('lang-row', 'lang-row-' + lang)
    row.dataset.lang = lang
    input.setAttribute('lang', lang)
    const label = row.querySelector('label')
    if (label) {
      const required = label.classList.contains('required')
      label.textContent = ''
      label.append(el('span', 'lang-badge', lang.toUpperCase()), el('span', 'lang-name', config.names[lang]))
      if (required) label.append(el('span', 'lang-required', ' (required)'))
    }
    if (lang !== SOURCE) {
      // The help text is shown once, under the English box.
      row.querySelectorAll('.help').forEach((help) => help.remove())
    }
    if (input.tagName === 'TEXTAREA') fitTextarea(input)
    if (lang !== SOURCE) {
      const flag = el('span', 'lang-flag')
      flag.setAttribute('aria-live', 'polite')
      input.after(flag)
    }
  }

  /** Long texts get tall boxes, short ones small boxes (admin textareas are 10 rows). */
  function fitTextarea(textarea) {
    const value = textarea.value || ''
    const lines = value.split(/\r?\n/).reduce((sum, line) => sum + Math.max(1, Math.ceil(line.length / 95)), 0)
    textarea.rows = Math.min(14, Math.max(3, lines + 1))
  }

  function buildGroups(root) {
    const inputs = Array.from(root.querySelectorAll('input.mt, textarea.mt')).filter(
      (input) => input.name && !input.closest('.lang-group'),
    )
    const byBase = new Map()
    inputs.forEach((input) => {
      const match = input.name.match(SUFFIX)
      if (!match) return
      const base = input.name.slice(0, -match[0].length)
      if (!byBase.has(base)) byBase.set(base, {})
      byBase.get(base)[match[1]] = input
    })

    byBase.forEach((members, base) => {
      if (!LANGS.every((lang) => members[lang])) return
      const rows = LANGS.map((lang) => members[lang].closest('.form-row'))
      if (rows.some((row) => !row) || new Set(rows).size !== LANGS.length) return

      const group = el('div', 'lang-group')
      group.dataset.base = base
      const head = el('div', 'lang-group-head')
      head.append(el('span', 'lang-group-name', fieldName(rows[0])))
      const button = el('button', 'lang-translate-one', 'Translate')
      button.type = 'button'
      button.title = config.enabled
        ? 'Translate this English text into ' + TARGETS.map((l) => config.names[l]).join(' and ')
        : OFF_HINT
      button.disabled = !config.enabled
      head.append(button)

      rows[0].before(group)
      group.append(head, ...rows)
      LANGS.forEach((lang, i) => decorateRow(rows[i], lang, members[lang]))
      refreshGroup(group)
    })
  }

  // ---------------------------------------------------------------- state

  function inputOf(group, lang) {
    const row = group.querySelector('.lang-row-' + lang)
    return row && row.querySelector('input.mt, textarea.mt')
  }

  function english(group) {
    const input = inputOf(group, SOURCE)
    return input ? input.value.trim() : ''
  }

  function refreshGroup(group) {
    const hasEnglish = Boolean(english(group))
    TARGETS.forEach((lang) => {
      const input = inputOf(group, lang)
      const row = input && input.closest('.lang-row')
      if (!row) return
      const missing = hasEnglish && !input.value.trim()
      row.classList.toggle('lang-missing', missing)
      if (missing) row.classList.remove('lang-draft')
      const flag = row.querySelector('.lang-flag')
      if (flag) {
        flag.textContent = missing
          ? 'Missing: the site shows English for now'
          : row.classList.contains('lang-draft')
            ? 'Draft: check it, then Save'
            : ''
      }
    })
    const button = group.querySelector('.lang-translate-one')
    if (button) button.disabled = !config.enabled || !hasEnglish
  }

  function liveGroups() {
    return Array.from(document.querySelectorAll('.lang-group')).filter((g) => !g.closest('.empty-form'))
  }

  function missingCount(lang) {
    return liveGroups().filter((group) => {
      const input = inputOf(group, lang)
      return english(group) && input && !input.value.trim()
    }).length
  }

  // ---------------------------------------------------------------- toolbar

  let toolbar = null

  function buildToolbar() {
    const form = document.querySelector('#content-main form')
    if (!form || !liveGroups().length) return

    toolbar = el('div', 'lang-toolbar')
    toolbar.setAttribute('role', 'region')
    toolbar.setAttribute('aria-label', 'Translations')

    const status = el('div', 'lang-toolbar-status')
    status.append(el('strong', '', 'Translations'))
    TARGETS.forEach((lang) => {
      const item = el('span', 'lang-count')
      item.dataset.lang = lang
      status.append(item)
    })

    const filter = el('div', 'lang-filter')
    filter.setAttribute('role', 'group')
    filter.setAttribute('aria-label', 'Show languages')
    const options = [['all', 'All languages']]
      .concat(TARGETS.map((lang) => [lang, 'English + ' + config.names[lang]]))
      .concat([['en', 'English only']])
    options.forEach(([value, label]) => {
      const button = el('button', 'lang-filter-option', label)
      button.type = 'button'
      button.dataset.filter = value
      filter.append(button)
    })

    const translateAll = el('button', 'lang-translate-all', 'Translate missing')
    translateAll.type = 'button'
    translateAll.disabled = !config.enabled

    const actions = el('div', 'lang-toolbar-actions')
    actions.append(filter, translateAll)

    const message = el('p', 'lang-toolbar-message')
    message.setAttribute('role', 'status')
    message.setAttribute('aria-live', 'polite')
    message.textContent = config.enabled
      ? 'Write the English text, then use Translate. Check the drafts before you Save.'
      : OFF_HINT + ' Until then, type the Armenian and Russian under each English text.'

    toolbar.append(status, actions, message)
    const anchor = form.querySelector('.errornote') || form.firstElementChild
    if (anchor && anchor.classList.contains('errornote')) anchor.after(toolbar)
    else form.prepend(toolbar)

    let saved = 'all'
    try {
      saved = localStorage.getItem(FILTER_KEY) || 'all'
    } catch (e) {
      /* storage unavailable */
    }
    setFilter(saved)
    refreshToolbar()
  }

  function refreshToolbar() {
    if (!toolbar) return
    let total = 0
    toolbar.querySelectorAll('.lang-count').forEach((item) => {
      const count = missingCount(item.dataset.lang)
      total += count
      item.classList.toggle('is-missing', count > 0)
      item.textContent =
        config.names[item.dataset.lang] + ': ' + (count ? count + ' missing' : 'complete ✓')
    })
    const button = toolbar.querySelector('.lang-translate-all')
    button.disabled = !config.enabled || total === 0
    button.title = config.enabled ? (total ? '' : 'Nothing to translate') : OFF_HINT
  }

  function setFilter(value) {
    if (!['all', 'en', ...TARGETS].includes(value)) value = 'all'
    document.body.dataset.langFilter = value
    if (toolbar) {
      toolbar.querySelectorAll('.lang-filter-option').forEach((button) => {
        button.setAttribute('aria-pressed', String(button.dataset.filter === value))
      })
    }
    try {
      localStorage.setItem(FILTER_KEY, value)
    } catch (e) {
      /* storage unavailable */
    }
  }

  function say(text, isError) {
    const message = toolbar && toolbar.querySelector('.lang-toolbar-message')
    if (!message) {
      if (isError) window.alert(text)
      return
    }
    message.textContent = text
    message.classList.toggle('is-error', Boolean(isError))
  }

  // ---------------------------------------------------------------- translating

  function csrfToken() {
    const input = document.querySelector('[name=csrfmiddlewaretoken]')
    return input ? input.value : ''
  }

  async function requestTranslations(texts) {
    const response = await fetch(config.translateUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken() },
      body: JSON.stringify({ texts: texts, targets: TARGETS }),
      credentials: 'same-origin',
    })
    let data = {}
    try {
      data = await response.json()
    } catch (e) {
      /* not JSON */
    }
    if (!response.ok) throw new Error(data.error || 'Translation failed (' + response.status + ').')
    return data
  }

  /** Translates the English text of `groups`, filling only `onlyEmpty` boxes or all of them. */
  async function translateGroups(groups, onlyEmpty) {
    const texts = Array.from(new Set(groups.map(english).filter(Boolean)))
    const results = {}
    let batch = []
    let chars = 0
    const flush = async () => {
      if (!batch.length) return
      const data = await requestTranslations(batch)
      batch.forEach((text, i) => {
        results[text] = {}
        TARGETS.forEach((lang) => {
          results[text][lang] = (data[lang] || [])[i]
        })
      })
      batch = []
      chars = 0
    }
    for (const text of texts) {
      if (batch.length >= BATCH_TEXTS || chars + text.length > BATCH_CHARS) await flush()
      batch.push(text)
      chars += text.length
    }
    await flush()

    let filled = 0
    groups.forEach((group) => {
      const result = results[english(group)]
      if (!result) return
      TARGETS.forEach((lang) => {
        const input = inputOf(group, lang)
        if (!input || !result[lang] || (onlyEmpty && input.value.trim())) return
        input.value = result[lang]
        input.closest('.lang-row').classList.add('lang-draft')
        input.dispatchEvent(new Event('change', { bubbles: true }))
        filled += 1
      })
      refreshGroup(group)
    })
    refreshToolbar()
    return filled
  }

  async function withBusy(button, label, work) {
    const original = button.textContent
    button.disabled = true
    button.textContent = label
    document.body.classList.add('lang-busy')
    try {
      await work()
    } catch (error) {
      say(error.message, true)
    } finally {
      button.textContent = original
      document.body.classList.remove('lang-busy')
      refreshToolbar()
      liveGroups().forEach(refreshGroup)
    }
  }

  function onTranslateAll(button) {
    const groups = liveGroups().filter(
      (group) => english(group) && TARGETS.some((lang) => !inputOf(group, lang).value.trim()),
    )
    if (!groups.length) return
    withBusy(button, 'Translating…', async () => {
      say('Translating ' + groups.length + ' text' + (groups.length === 1 ? '' : 's') + '…')
      const filled = await translateGroups(groups, true)
      say(
        'Filled ' + filled + ' translation' + (filled === 1 ? '' : 's') +
          ' (marked “Draft”). Read them through and correct anything, then Save.',
      )
    })
  }

  function onTranslateOne(button) {
    const group = button.closest('.lang-group')
    const hasText = TARGETS.some((lang) => inputOf(group, lang).value.trim())
    if (hasText && !window.confirm('Replace the Armenian and Russian text of this field with a new translation?')) {
      return
    }
    withBusy(button, 'Translating…', async () => {
      await translateGroups([group], false)
      say('Translated “' + group.querySelector('.lang-group-name').textContent + '”. Check it, then Save.')
    })
  }

  // ---------------------------------------------------------------- wiring

  document.addEventListener('click', (event) => {
    const target = event.target.closest('button')
    if (!target) return
    if (target.classList.contains('lang-translate-all')) onTranslateAll(target)
    else if (target.classList.contains('lang-translate-one')) onTranslateOne(target)
    else if (target.classList.contains('lang-filter-option')) setFilter(target.dataset.filter)
  })

  document.addEventListener('input', (event) => {
    const group = event.target.closest && event.target.closest('.lang-group')
    if (!group || isTemplate(event.target)) return
    const row = event.target.closest('.lang-row')
    if (row) row.classList.remove('lang-draft')
    refreshGroup(group)
    refreshToolbar()
  })

  document.addEventListener('formset:added', (event) => {
    buildGroups(event.target)
    refreshToolbar()
  })
  document.addEventListener('formset:removed', refreshToolbar)

  function init() {
    buildGroups(document)
    buildToolbar()
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init)
  else init()
})()
