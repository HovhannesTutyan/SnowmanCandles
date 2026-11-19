import { useServerHead } from '../../lib/serverHead'

interface PageHeadProps {
  title: string
  description?: string
}

/**
 * The page's <title> and description (React 19 hoists them into <head>). Renders nothing
 * on the page the visitor landed on: the server already sent the right tags there.
 */
export function PageHead({ title, description }: PageHeadProps) {
  const serverHead = useServerHead()
  if (serverHead) return null
  return (
    <>
      <title>{title}</title>
      {description && <meta name="description" content={description} />}
    </>
  )
}
