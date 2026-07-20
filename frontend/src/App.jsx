import { useEffect, useState } from 'react'
import './App.css'
import Banner from './Banner'
import StatusBadge from './StatusBadge'
import Header from './Header';
import EntriesList from './EntriesList';

const API_URL = import.meta.env.VITE_API_URL;
if (!API_URL) {
  throw new Error('VITE_API_URL is not set — copy .env.example to .env');
}

function App() {
  const [status, setStatus] = useState("loading")
  const [responseFromBackend, setResponseFromBackend] = useState("")
  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then(response => response.json())
      .then((data) => {
        setResponseFromBackend(data.status)
        setStatus("ok")
      })
      .catch((error) => {
        console.error(`Error message: ${error}`)
        setStatus("unreachable")
      })
        
  }, [])
  const [userId, setUserId] = useState(1)
  return (
    <>
      <Banner></Banner>
      <Header headerText="Internship Journal" onUserChange={setUserId}></Header>
      {console.log(userId)}
      <EntriesList userId={userId}></EntriesList>
      <div>
        <StatusBadge status="draft" />
        <StatusBadge status="submitted" />
        <StatusBadge status="needs_revision" />
        <StatusBadge status="approved" />
        <p>
          Server status: {status === 'loading' && 'checking...'}
          {status === 'ok' && responseFromBackend}
          {status === 'unreachable' && 'unreachable'}
        </p>
      </div>
    </>
  )
}

export default App
