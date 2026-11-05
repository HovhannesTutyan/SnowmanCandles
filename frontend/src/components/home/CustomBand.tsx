import styles from './CustomBand.module.css'

interface CustomBandProps {
  title: string
  text: string
  buttonText: string
  images: [string, string]
}

/** "Want it in your colours?" call to action. */
export function CustomBand({ title, text, buttonText, images }: CustomBandProps) {
  return (
    <section id="custom" className={styles.section} aria-labelledby="custom-title">
      <div className={`${styles.band} reveal`}>
        <div className={styles.copy}>
          <h2 id="custom-title" className={styles.title}>{title}</h2>
          <p className={styles.text}>{text}</p>
          {/* No custom-order form yet: points visitors to the contact details. */}
          <a href="#footer" className={styles.button}>{buttonText}</a>
        </div>
        <div className={styles.images}>
          <img className={`${styles.imageA} floaty`} src={images[0]} alt="" loading="lazy" />
          <img className={`${styles.imageB} floaty`} src={images[1]} alt="" loading="lazy" />
        </div>
      </div>
    </section>
  )
}
