import { useEffect, useState } from 'react'
import './App.css'
import Banner from './Banner'
import Header from './Header'
import EntriesList from './EntriesList'
import SupervisorView from './SupervisorView'

const API_URL = import.meta.env.VITE_API_URL
if (!API_URL) {
  throw new Error('VITE_API_URL is not set — copy .env.example to .env')
}

function App() {
  const [status, setStatus] = useState("loading")
  const [counterOfRefresh, setCounterOfRefresh] = useState(0)
  const [responseFromBackend, setResponseFromBackend] = useState("")
  const [selectedRole, setSelectedRole] = useState(null)
  const [userId, setUserId] = useState(null)
  const [editingEntry, setEditingEntry] = useState(null);
  const handleRefresh = () => {
  setCounterOfRefresh(prev => prev + 1)
}

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

  let content
  let headerText = "Loading..."

  if (selectedRole === "Student") {
    headerText = "Internship Journal"
    content = (
      <>
        <EntriesList
          key={userId}
          userId={userId}
          counterOfRefresh={counterOfRefresh}
          setCounterOfRefresh={setCounterOfRefresh}
          editingEntry={editingEntry}
          setEditingEntry={setEditingEntry}
        />
      </>
    )
  } else if (selectedRole === "Supervisor") {
    headerText = "Approval Queue"
    content = <SupervisorView setCounterOfRefresh={setCounterOfRefresh}/>
  } else if (selectedRole === null) {
    content = <p>Loading...</p>
  } else {
    content = <p>Unknown role.</p>
  }

  return (
    <>
      <Banner />
      <Header
        headerText={headerText}
        onUserChange={setUserId}
        onUserChangeRole={setSelectedRole}
        setEditingEntry={setEditingEntry}
      />
      {content}
    </>
  )
}

export default App