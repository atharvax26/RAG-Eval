import { createBrowserRouter } from 'react-router-dom'
import Upload from './pages/Upload'
import Progress from './pages/Progress'
import Comparison from './pages/Comparison'
import CostAnalysis from './pages/CostAnalysis'
import Explorer from './pages/Explorer'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Upload />,
  },
  {
    path: '/progress/:corpusId',
    element: <Progress />,
  },
  {
    path: '/comparison/:corpusId',
    element: <Comparison />,
  },
  {
    path: '/cost/:corpusId',
    element: <CostAnalysis />,
  },
  {
    path: '/explorer/:corpusId',
    element: <Explorer />,
  },
])
