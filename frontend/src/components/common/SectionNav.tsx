import { Fragment } from 'react'

import { useActiveSection } from '../../hooks/useActiveSection'
import styles from './SectionNav.module.css'

interface SectionNavProps {
  title: string
  links: { id: string; label: string }[]
  label?: string
}

/** The floating bar at the bottom of a long page for jumping between its sections. */
export function SectionNav({ title, links, label = 'On this page' }: SectionNavProps) {
  const active = useActiveSection(links.map((link) => link.id))

  return (
    <nav aria-label={label} className={styles.nav}>
      <a href="#top" className={styles.title}>{title}</a>
      <div className={styles.links}>
        {links.map((link, index) => (
          <Fragment key={link.id}>
            {index > 0 && <span className={styles.divider} aria-hidden="true" />}
            <a
              href={`#${link.id}`}
              className={`${styles.link} ${active === link.id ? styles.active : ''}`}
              aria-current={active === link.id ? 'location' : undefined}
            >
              {link.label}
            </a>
          </Fragment>
        ))}
      </div>
    </nav>
  )
}
