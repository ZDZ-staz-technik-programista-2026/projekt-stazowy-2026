import { Fragment, useEffect, useState } from "react";
import StatusBadge from "./StatusBadge";
import EntriesForm from "./EntriesForm";
import UpdateForm from "./UpdateForm";

const API_URL = import.meta.env.VITE_API_URL;

export default function EntriesList({ userId, counterOfRefresh, setCounterOfRefresh, editingEntry, setEditingEntry }) {
    const [entriesList, setEntriesList] = useState([]);
    const [status, setStatus] = useState("loading");
    const [errorMessage, setErrorMessage] = useState("");
    const [showForm, setShowForm] = useState(false);
    useEffect(() => {
        if (!userId) return;

        setStatus("loading");
        setErrorMessage("");
        
        fetch(`${API_URL}/api/entries?user_id=${userId}`)
            .then(response => {
                return response.json().then(data => {
                    if (!response.ok) {
                        throw new Error(data?.message || "Failed to fetch entries");
                    }
                    return data;
                });
            })
            .then((data) => {
                if (Array.isArray(data)) {
                    setStatus("loaded");
                    setEntriesList(data);
                } else {
                    throw new Error("Invalid data format");
                }
            })
            .catch(error => {
                console.error(`Error: ${error.message}`);
                setErrorMessage(error.message);
                setStatus("unreachable");
            });
    }, [userId, counterOfRefresh]);

    function handleSubmit(entry){
        fetch(`${API_URL}/api/entries/${entry.id}/submit?user_id=${userId}`,{
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
        })
        .then((response) => {
            if(!response.ok){
                throw new Error("Failed to submit entry")
            }
            return response.json
        })
        .then(() => {
            setCounterOfRefresh(prev => prev+1)
        }).catch(error => {
            con
        })
    }
    function editEntry(selectedEntry){
        setShowForm(false);
        setEditingEntry(selectedEntry);
    }


    let pText = "";
    if (status === "loaded") {
        if (showForm) {
            pText = "New entry";
        } else if (editingEntry) {
            pText = "Edit entry";
        } else if (entriesList.length === 0) {
            pText = "Start documenting your internship";
        } else {
            pText = "My entries";
        }
    }

    return (
        <div>
            {pText && (
                <p className="text-xl px-4 py-4 text-text-primary">
                    {pText}
                </p>
            )}
            {!showForm && !editingEntry && status === "loaded" && (
                <p className="px-4 py-2">
                    <button className="bg-accent text-white text-lg py-2 px-4 rounded" onClick={() => setShowForm(!showForm)}>+ New Entry</button>
                </p>
            )}
            
            {showForm && (
                <EntriesForm userId={userId} setCounter={setCounterOfRefresh} setShowForm={setShowForm} />
            )}
            
            {editingEntry && (
                <UpdateForm entry={editingEntry} setCounter={setCounterOfRefresh} onClose={() => setEditingEntry(null)}></UpdateForm>
            )}
            
            <div className="rounded-card border border-border-strong bg-surface-card mt-4 m-3 overflow-hidden">
                {status === "loading" && (
                    <p className="p-6 text-center text-text-muted text-base">
                        ⏳ Loading entries...
                    </p>
                )}

                {status === "unreachable" && (
                    <p className="p-6 text-center text-status-revision-fg text-base">
                        ❌ {errorMessage || "Connection error"}
                    </p>
                )}

                {status === "loaded" && entriesList.length === 0 && !showForm && !editingEntry && (
                    <p className="p-6 text-text-muted text-base">
                        Start documenting your internship by creating your first entry.
                    </p>
                )}

                {status === "loaded" && entriesList.length > 0 && !showForm && !editingEntry && (
                    <table className="w-full table-fixed">
                        <colgroup>
                            <col className="w-28" />
                            <col className="w-32" />
                            <col className="w-16" />
                            <col />
                            <col className="w-40" />
                            <col className="w-40" />
                        </colgroup>
                        <thead>
                            <tr className="border-b border-border">
                                <th className="text-left font-medium text-text-secondary text-sm py-2 px-3">Date</th>
                                <th className="text-left font-medium text-text-secondary text-sm py-2 px-3">Time</th>
                                <th className="text-left font-medium text-text-secondary text-sm py-2 px-3">Hours</th>
                                <th className="text-left font-medium text-text-secondary text-sm py-2 px-3">Description</th>
                                <th className="text-left font-medium text-text-secondary text-sm py-2 px-3">Status</th>
                                <th className="text-left font-medium text-text-secondary text-sm py-2 px-3">Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {entriesList.map((entry) => (
                                <Fragment key={entry.id}>
                                    <tr className="border-b border-border last:border-0">
                                        <td className="py-3 px-3 font-mono text-base text-text-primary">{entry.date}</td>
                                        <td className="py-3 px-3 font-mono text-base text-text-primary">
                                            {entry.start_time.toString().substring(0,5)}-{entry.end_time.toString().substring(0,5)}
                                        </td>
                                        <td className="py-3 px-3 font-mono text-base text-text-primary">
                                            {entry.calculated_hours.toString().substring(0,4)}h
                                        </td>
                                        <td className="py-3 px-3 text-base text-text-primary truncate">
                                            {entry.description}
                                        </td>
                                        <td className="py-3 px-3">
                                            <StatusBadge status={entry.status} />
                                        </td>
                                        {entry.status === "draft" || entry.status === "needs_revision" ?
                                            <td className="py-3 px-3 flex gap-2">
                                                <button className="rounded-control border border-border-strong text-text-primary text-sm font-medium py-1 px-3 hover:bg-surface-page" onClick={() => editEntry(entry)}>
                                                    Edit
                                                </button>
                                                <button className="rounded-control border border-border-strong text-text-primary text-sm font-medium py-1 px-3 hover:bg-surface-page" onClick={() => handleSubmit(entry)}>
                                                    Submit
                                                </button>
                                            </td>
                                        : <td className="py-3 px-3"></td>}
                                    </tr>
                                    {entry.latest_review && (
                                        <tr className="bg-surface-page">
                                            <td colSpan={6} className="py-3 px-3 italic text-text-secondary">
                                                {entry.latest_review.comment}
                                            </td>
                                        </tr>
                                    )}
                                </Fragment>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}