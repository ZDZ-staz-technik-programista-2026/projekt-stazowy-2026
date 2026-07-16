import './App.css'
import Banner from './Banner'
import StatusBadge from './StatusBadge'

function App() {
  

  return (
    <>
      <Banner></Banner>
      <div>
        <h1>Internship Journal</h1>
        <StatusBadge status="draft" />
        <StatusBadge status="submitted" />
        <StatusBadge status="needs_revision" />
        <StatusBadge status="approved" />
      </div>
    </>
  )
}

export default App
