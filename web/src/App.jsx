import { HashRouter, Routes, Route, Navigate } from 'react-router-dom'
import TourList from './components/TourList.jsx'
import TourDetail from './components/TourDetail.jsx'
import MapView from './components/MapView.jsx'
import PdfViewer from './components/PdfViewer.jsx'

export default function App() {
  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<TourList />} />
        <Route path="/tour/:slug" element={<TourDetail />} />
        <Route path="/tour/:slug/day/:dayNum/map" element={<MapView />} />
        <Route path="/tour/:slug/map" element={<MapView />} />
        <Route path="/tour/:slug/pdf" element={<PdfViewer />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </HashRouter>
  )
}
