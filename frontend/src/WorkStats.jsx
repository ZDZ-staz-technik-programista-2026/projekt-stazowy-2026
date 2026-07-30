import { useEffect, useState } from "react";

export default function WorkStats({ userId, counterOfRefresh}) {
    const [stats, setStats] = useState(null);
    const [status, setStatus] = useState("loading");
    const [errorMessage, setErrorMessage] = useState("");
    const API_URL = import.meta.env.VITE_API_URL

    useEffect(() => {
        if(!userId){
            return
        }
        setStatus("loading")
        setErrorMessage("")
        fetch(`${API_URL}/api/stats?user_id=${userId}`)
            .then(response => {
                return response.json().then(data => {
                    if(!response.ok){
                        throw new Error(data.message || "Failed to fetch stats")
                    }else{
                        return data
                    }
                })
            })
            .then(data => {
                if(Array.isArray(data) && data.length > 0){
                    setStats(data[0])
                    setStatus("loaded")
                }else{
                    throw new Error("Invalid data format")
                }
            }).catch(error => {
                setErrorMessage(error.message)
                setStatus("error")
            })
    }, [userId, counterOfRefresh])

    if(status === "loading"){
        return(
            <div className="rounded-card border border-border-strong bg-surface-card mt-4 m-3 p-6 text-center text-text-muted">
                ⏳ Loading weekly summary...
            </div>      
        )
    }
    if(status === "error"){
        return(
            <div className="m-3 mt-4 p-4 text-sm text-status-revision-fg bg-surface-page border border-border-strong rounded-control">
                <strong>Error loading stats:</strong> {errorMessage}
            </div>
        );
    }

    if(!stats){
        return null
    }
    
    return(
        <>
            <div className="rounded-card border border-border-strong bg-surface-card mt-4 m-3 p-6">
                        <h2 className="text-lg font-medium text-text-primary mb-4">This Week's Summary:</h2>
                        {stats.entry_count == 0 ? 
                            <p className="text-text-muted">
                                No entries logged for this week. Start working to see your progress!
                            </p>
                        : 
                            <div className="p-4 mt-4 border rounded-card border-border-strong">
                                <p className="text-xl"><span className="text-accent">{stats.student_name}</span> stats:</p>
                                <p className="text-lg mt-4 text-text-secondary uppercase tracking-wide">Entry count: {stats.entry_count}</p>
                                <p className="text-lg mt-4 text-text-secondary uppercase tracking-wide">Total hours worked: {stats.total_hours}</p>
                                <p className="text-lg mt-4 text-text-secondary uppercase tracking-wide">Percentage of approved entries: {stats.approved_percentage.toFixed(0)}%</p>
                            </div>
                        }
            </div>

        </>
    );
}