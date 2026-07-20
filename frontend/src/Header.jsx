import { useEffect, useState } from "react"

const API_URL = import.meta.env.VITE_API_URL;
export default function Header({ headerText, onUserChange }) {

  const [users,setUsers] = useState([])
  const [status, setStatus] = useState("loading")
  useEffect(() => {
    fetch(`${API_URL}/api/users`)
        .then(response => response.json())
        .then((data) => {
            setStatus("loaded")
            setUsers(data)
            if(data.length > 0 && onUserChange){
                onUserChange(data[0].id)
            }
        })
        .catch(error => {
            console.log(`Error: ${error}`)
            setStatus("unreachable")
        })
  }, [])
  return (
    <div className="grid grid-cols-3 items-center bg-surface-card border border-border-strong rounded-card p-4 mt-4">
        <h1 className="col-start-2 justify-self-center text-xl text-text-primary">{headerText}</h1>
        <select
          aria-label="Logged user"
          className="col-start-3 justify-self-end text-base text-accent border text-text-primary border-border-strong rounded-control px-3 py-1.5 bg-transparent cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-accent"
          disabled={status != "loaded"}
          value={users.id}
          onChange={(e) => onUserChange(e.target.value)}
        >
          {status == "loading" && <option>⏳ Loading...</option>}
          {status == "unreachable" && <option>❌ Connection error</option>}
          {status === "loaded" && users.map((user) => (
              <option key={user.id} value={user.id}> {user.role === "Student" ? "👤" : "👨‍💼"} {user.name} </option>
          ))}
        </select>
    </div>
  )
}