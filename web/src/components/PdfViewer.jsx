import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import styles from './PdfViewer.module.css'

export default function PdfViewer() {
  const { slug } = useParams()
  const navigate = useNavigate()
  const [pdfUrl, setPdfUrl] = useState(null)
  const [tourName, setTourName] = useState('')

  useEffect(() => {
    fetch('data/tours.json')
      .then((r) => r.json())
      .then((tours) => {
        const tour = tours.find((t) => t.slug === slug)
        if (tour?.hasPdf) {
          setPdfUrl(`data/pdf/${slug}.pdf`)
          setTourName(tour.name)
        }
      })
  }, [slug])

  return (
    <div className={styles.page}>
      <header className={styles.appBar}>
        <button className={styles.back} onClick={() => navigate(-1)}>← Back</button>
        <span className={styles.title}>{tourName || 'PDF Guide'}</span>
        {pdfUrl && (
          <a className={styles.download} href={pdfUrl} download>
            Download
          </a>
        )}
      </header>
      {pdfUrl ? (
        <iframe
          className={styles.frame}
          src={pdfUrl}
          title={`${tourName} PDF Guide`}
        />
      ) : (
        <div className={styles.empty}>PDF not available for this tour.</div>
      )}
    </div>
  )
}
