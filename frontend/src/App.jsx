import './App.css'
import StatusBadge from './StatusBadge'

function App() {
  

  return (
    <>
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
