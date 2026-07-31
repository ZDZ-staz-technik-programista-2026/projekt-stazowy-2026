/**
 * Main application entry point. 
 * Manages global application state such as the currently logged-in user, their role, 
 * and orchestration of data refetches across sibling components.
 */
import { useEffect, useState, useCallback } from 'react'
import './App.css'
import Banner from './Banner'
import Header from './Header'
import EntriesList from './EntriesList'
import SupervisorView from './SupervisorView'
import WorkStats from './WorkStats'
import DailyHours from './DailyHours'

const API_URL = import.meta.env.VITE_API_URL
if (!API_URL) {
  throw new Error('VITE_API_URL is not set — copy .env.example to .env')
}

function App() {
  const [status, setStatus] = useState("loading")
  
  // counterOfRefresh acts as a simple trigger. When incremented, it forces 
  // child components (like EntriesList and WorkStats) to refetch their data.
  const [counterOfRefresh, setCounterOfRefresh] = useState(0)
  
  const [responseFromBackend, setResponseFromBackend] = useState("")
  const [selectedRole, setSelectedRole] = useState(null)
  const [userId, setUserId] = useState(null)
  const [editingEntry, setEditingEntry] = useState(null);
  const [entries, setBaseEntries] = useState(null)
  
  // draftEntry holds real-time unsaved form data so the DailyHours 
  // component can calculate total hours dynamically as the user types.
  const [draftEntry, setDraftEntry] = useState(null); 
  const [dailyLimit, setDailyLimit] = useState(8.0);

  // useCallback prevents unnecessary re-renders of the Header component.
  // When a user changes, we clear previous entries and drafts to prevent data leakage.
  const handleUserChange = useCallback((newId) => {
    setUserId(newId)
    setBaseEntries(null)
    setDraftEntry(null)
  }, [])

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

  // Render different dashboard views based on the simulated logged-in user role
  if (selectedRole === "Student") {
    headerText = "Internship Journal"
    content = (
      <>
        <WorkStats userId={userId} counterOfRefresh={counterOfRefresh} />
        <DailyHours entries={entries} draftEntry={draftEntry} dailyLimit={dailyLimit} />
        <EntriesList
          key={userId} // Forces complete remount of the list when user changes
          userId={userId}
          counterOfRefresh={counterOfRefresh}
          setCounterOfRefresh={setCounterOfRefresh}
          editingEntry={editingEntry}
          setEditingEntry={setEditingEntry}
          setBaseEntries={setBaseEntries}
          setDraftEntry={setDraftEntry} 
        />
      </>
    )
  } else if (selectedRole === "Supervisor") {
    headerText = "Approval Queue"
    content = <SupervisorView
              userId={userId}
              counterOfRefresh={counterOfRefresh}
              setCounterOfRefresh={setCounterOfRefresh}
    />
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
        onUserChange={handleUserChange}
        onUserChangeRole={setSelectedRole}
        onUserLimitChange={setDailyLimit}
        setEditingEntry={setEditingEntry}
      />
      {content}
    </>
  )
}

export default App