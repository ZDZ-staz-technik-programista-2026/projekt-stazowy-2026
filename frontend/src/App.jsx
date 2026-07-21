import { useEffect, useState } from 'react'
import './App.css'
import Banner from './Banner'
import StatusBadge from './StatusBadge'
import Header from './Header';
import EntriesList from './EntriesList';
import EntriesForm from './EntriesForm';
import SupervisorView from './SupervisorView';

const API_URL = import.meta.env.VITE_API_URL;
if (!API_URL) {
  throw new Error('VITE_API_URL is not set — copy .env.example to .env');
}


function App() {
  const [status, setStatus] = useState("loading")
  const [counterOfRefresh, setCounterOfRefresh] = useState(0)
  const [responseFromBackend, setResponseFromBackend] = useState("")
  const [selectedRole, setSelectedRole] = useState("student")
  const handleRefresh = () => {
    setCounterOfRefresh(prev => prev+1)
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
  const [userId, setUserId] = useState(1)
  return (
    <>
      <Banner></Banner>
      <Header headerText={selectedRole == "Student" ? "Internship Journal" : "Approval Queue"} onUserChange={setUserId} onUserChangeRole={setSelectedRole}></Header>
      {selectedRole == "Student" ? <EntriesList userId={userId} counterOfRefresh={counterOfRefresh}></EntriesList> : <SupervisorView/>}
    </>
  )
}

export default App
