import { useEffect, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL;

export default function EntriesList({userId}){
    
    const [entriesList, setEntiresList] = useState([])
    const [status, setStatus] = useState("loading")
    useEffect(() => {
        fetch(`http://localhost:8000/api/entries?user_id=${userId}`)
            .then(response => response.json())
            .then((data) => {
                setStatus("loaded")
                setEntiresList(data)
            })
            .catch(error => {
                console.log(`Error: ${error}`)
                setStatus("unreachable")
            })
    }, [userId])
    
    return(
        <div>
            {status == "loading" && <option>⏳ Loading entries...</option>}
            {status == "unreachable" && <option>❌ Connection error</option>}
            {status === "loaded" && entriesList.map((entry) => 
                <div key={entry.id}>
                    {entry.id}, {entry.date}, {entry.start_time}, {entry.end_time}, {entry.description}
                </div>
            )}
        </div>
    )
}