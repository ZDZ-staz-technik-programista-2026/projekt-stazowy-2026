import { Fragment, useEffect, useState } from "react";
import StatusBadge from "./StatusBadge";
import EntriesForm from "./EntriesForm";
import UpdateForm from "./UpdateForm";

const API_URL = import.meta.env.VITE_API_URL;

// Main component responsible for displaying, filtering, and managing user's journal entries
export default function EntriesList({ userId, counterOfRefresh, setCounterOfRefresh, editingEntry, setEditingEntry, setBaseEntries, setDraftEntry }) {
    
    // --- CORE DATA & UI STATES ---
    const [entriesList, setEntriesList] = useState([]); // Holds the raw data fetched from the API
    const [status, setStatus] = useState("loading"); // Tracks the API request status (loading, loaded, unreachable)
    const [errorMessage, setErrorMessage] = useState("");
    const [showForm, setShowForm] = useState(false); // Toggles the visibility of the "New Entry" form

    // --- FILTER STATES ---
    // Beginner approach: Using separate state variables for each filter option instead of a single object/array
    const [filterDateFrom, setFilterDateFrom] = useState("");
    const [filterDateTo, setFilterDateTo] = useState("");
    
    const [isDraftSelected, setIsDraftSelected] = useState(false);
    const [isSubmittedSelected, setIsSubmittedSelected] = useState(false);
    const [isApprovedSelected, setIsApprovedSelected] = useState(false);
    const [isRevisionSelected, setIsRevisionSelected] = useState(false);

    // --- DATA FETCHING ---
    // Runs when the component mounts or when userId / counterOfRefresh changes
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
                    setBaseEntries(data); // Passes data up to the parent component (App.jsx)
                } else {
                    throw new Error("Invalid data format");
                }
            })
            .catch(error => {
                console.error(`Error: ${error.message}`);
                setErrorMessage(error.message);
                setStatus("unreachable");
            });
    }, [userId, counterOfRefresh, setBaseEntries]);

    // --- API ACTIONS ---
    // Submits a specific entry to the supervisor by changing its status via API
    function handleSubmit(entry) { 
        setErrorMessage("");
        
        fetch(`${API_URL}/api/entries/${entry.id}/submit`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                user_id: userId,
            }) 
        })
        .then((response) => {
            return response.json().then(data => {
                if (!response.ok) {
                    throw new Error(data?.message || "Failed to submit entry");
                }
                return data;
            });
        })
        .then(() => {
            setCounterOfRefresh(prev => prev + 1); // Triggers a re-fetch of the data list
        })
        .catch((error) => {
            setErrorMessage(error.message); 
        });
    }

    // Opens the UpdateForm for a specific entry
    function editEntry(selectedEntry){
        setShowForm(false);
        setEditingEntry(selectedEntry);
    }

    // Dynamic header text depending on what is currently displayed
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

    // --- FILTERING LOGIC ---
    // This creates a new array of entries to be displayed, based on the selected filter states.
    // It runs on every render, evaluating every item in the original 'entriesList'.
    let filteredEntries = entriesList.filter(function(entry) {
        // 1. Date filters: exclude items outside the selected range
        if (filterDateFrom !== "" && entry.date < filterDateFrom) {
            return false;
        }
        if (filterDateTo !== "" && entry.date > filterDateTo) {
            return false;
        }

        // 2. Status filters: check if ANY status button is clicked
        let anyStatusSelected = isDraftSelected || isSubmittedSelected || isApprovedSelected || isRevisionSelected;
        
        // If no status filters are active, show all entries (that passed the date check)
        if (anyStatusSelected === false) {
            return true;
        }
        
        // 3. If at least one status is selected, check if the current entry matches ANY of the selected ones
        if (isDraftSelected === true && entry.status === "draft") {
            return true;
        }
        if (isSubmittedSelected === true && entry.status === "submitted") {
            return true;
        }
        if (isApprovedSelected === true && entry.status === "approved") {
            return true;
        }
        if (isRevisionSelected === true && entry.status === "needs_revision") {
            return true;
        }

        // If it doesn't match any selected status, hide it
        return false;
    });

    // Helper function to reset all filter state variables to their default values
    function clearAllFilters() {
        setFilterDateFrom("");
        setFilterDateTo("");
        setIsDraftSelected(false);
        setIsSubmittedSelected(false);
        setIsApprovedSelected(false);
        setIsRevisionSelected(false);
    }

    return (
        <div>
            {pText && (
                <p className="text-xl px-4 py-4 text-text-primary">
                    {pText}
                </p>
            )}
            
            {/* Top action buttons: Only visible if forms are closed and data is loaded */}
            {!showForm && !editingEntry && status === "loaded" && (
                <div className="px-4 py-2 flex justify-between items-center">
                    <button
                        className="bg-accent text-white text-lg py-2 px-4 rounded focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2"
                        onClick={() => setShowForm(!showForm)}
                    >
                        + New Entry
                    </button>

                    <button
                        className="border border-green-800 text-green-800 text-lg py-2 px-4 rounded hover:bg-green-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green-700 focus-visible:ring-offset-2"
                        onClick={() => {
                            window.open(
                                `${API_URL}/api/export_csv?user_id=${userId}`,
                                "_blank"
                            );
                        }}
                    >
                        Download CSV
                    </button>
                </div>
            )}
            
            {/* Conditional rendering of the Create or Update forms */}
            {showForm && (
                <EntriesForm userId={userId} setCounter={setCounterOfRefresh} setShowForm={setShowForm}  setDraftEntry={setDraftEntry}/>
            )}
            
            {editingEntry && (
                <UpdateForm entry={editingEntry} setCounter={setCounterOfRefresh} onClose={() => setEditingEntry(null) } setDraftEntry={setDraftEntry}></UpdateForm>
            )}
            
            <div className="rounded-card border border-border-strong bg-surface-card mt-4 m-3 overflow-hidden">
                
                {/* Error and Loading states UI */}
                {errorMessage && status === "loaded" && (
                    <div className="m-4 p-4 text-sm text-status-revision-fg bg-surface-page border border-border-strong rounded-control">
                        <strong>Error:</strong> {errorMessage}
                    </div>
                )}

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
                    <>
                        {/* --- FILTERING UI SECTION --- */}
                        <div className="px-4 py-3 border-b border-border bg-surface-page flex flex-col gap-3">
                            <div className="flex flex-wrap items-center gap-2">
                                <span className="font-medium text-sm text-text-secondary w-24 shrink-0">Filter Status:</span>
                                
                                <div className="flex flex-wrap gap-2">
                                    {/* Individual filter buttons that toggle their specific state on click */}
                                    {isDraftSelected ? (
                                        <button onClick={() => setIsDraftSelected(false)} className="flex items-center gap-2 bg-status-draft-bg text-status-draft-fg rounded-control py-1 px-3 text-sm hover:opacity-80">
                                            <div className="h-2.5 w-2.5 rounded-full bg-status-draft-fg"></div>
                                            <span className="font-medium">Draft ✕</span>
                                        </button>
                                    ) : (
                                        <button onClick={() => setIsDraftSelected(true)} className="flex items-center gap-2 bg-surface-card text-text-secondary border border-border-strong rounded-control py-1 px-3 text-sm hover:bg-surface-page">
                                            <div className="h-2.5 w-2.5 rounded-full bg-border-strong"></div>
                                            <span>Draft</span>
                                        </button>
                                    )}

                                    {isSubmittedSelected ? (
                                        <button onClick={() => setIsSubmittedSelected(false)} className="flex items-center gap-2 bg-status-submitted-bg text-status-submitted-fg rounded-control py-1 px-3 text-sm hover:opacity-80">
                                            <div className="h-2.5 w-2.5 rounded-full bg-status-submitted-fg"></div>
                                            <span className="font-medium">Submitted ✕</span>
                                        </button>
                                    ) : (
                                        <button onClick={() => setIsSubmittedSelected(true)} className="flex items-center gap-2 bg-surface-card text-text-secondary border border-border-strong rounded-control py-1 px-3 text-sm hover:bg-surface-page">
                                            <div className="h-2.5 w-2.5 rounded-full bg-border-strong"></div>
                                            <span>Submitted</span>
                                        </button>
                                    )}

                                    {isRevisionSelected ? (
                                        <button onClick={() => setIsRevisionSelected(false)} className="flex items-center gap-2 bg-status-revision-bg text-status-revision-fg rounded-control py-1 px-3 text-sm hover:opacity-80">
                                            <div className="h-2.5 w-2.5 rounded-full bg-status-revision-fg"></div>
                                            <span className="font-medium">Needs revision ✕</span>
                                        </button>
                                    ) : (
                                        <button onClick={() => setIsRevisionSelected(true)} className="flex items-center gap-2 bg-surface-card text-text-secondary border border-border-strong rounded-control py-1 px-3 text-sm hover:bg-surface-page">
                                            <div className="h-2.5 w-2.5 rounded-full bg-border-strong"></div>
                                            <span>Needs revision</span>
                                        </button>
                                    )}

                                    {isApprovedSelected ? (
                                        <button onClick={() => setIsApprovedSelected(false)} className="flex items-center gap-2 bg-status-approved-bg text-status-approved-fg rounded-control py-1 px-3 text-sm hover:opacity-80">
                                            <div className="h-2.5 w-2.5 rounded-full bg-status-approved-fg"></div>
                                            <span className="font-medium">Approved ✕</span>
                                        </button>
                                    ) : (
                                        <button onClick={() => setIsApprovedSelected(true)} className="flex items-center gap-2 bg-surface-card text-text-secondary border border-border-strong rounded-control py-1 px-3 text-sm hover:bg-surface-page">
                                            <div className="h-2.5 w-2.5 rounded-full bg-border-strong"></div>
                                            <span>Approved</span>
                                        </button>
                                    )}
                                </div>
                            </div>
                            
                            <div className="flex flex-wrap items-center gap-2">
                                <span className="font-medium text-sm text-text-secondary w-24 shrink-0">Date Range:</span>
                                <div className="flex items-center gap-2 flex-wrap">
                                    <input 
                                        type="date" 
                                        className="border border-border-strong rounded-control px-2 py-1 text-sm focus:outline-accent bg-surface-card text-text-primary h-[30px]"
                                        value={filterDateFrom}
                                        onChange={(e) => setFilterDateFrom(e.target.value)}
                                    />
                                    <span className="text-text-secondary">-</span>
                                    <input 
                                        type="date" 
                                        className="border border-border-strong rounded-control px-2 py-1 text-sm focus:outline-accent bg-surface-card text-text-primary h-[30px]"
                                        value={filterDateTo}
                                        onChange={(e) => setFilterDateTo(e.target.value)}
                                    />
                                    
                                    {/* Clear dates button - visible only if at least one date is selected */}
                                    {(filterDateFrom !== "" || filterDateTo !== "") ? (
                                        <button onClick={() => { setFilterDateFrom(""); setFilterDateTo(""); }} className="ml-2 flex items-center gap-1 bg-surface-card border border-border-strong rounded-control py-1 px-3 text-sm text-text-secondary hover:text-text-primary hover:bg-surface-page">
                                            Clear dates ✕
                                        </button>
                                    ) : null}
                                </div>
                            </div>
                            
                            {/* Clear all filters button - visible if ANY filter is active */}
                            {(isDraftSelected || isSubmittedSelected || isApprovedSelected || isRevisionSelected || filterDateFrom !== "" || filterDateTo !== "") ? (
                                <div className="pt-2 mt-1 border-t border-border-strong flex justify-end">
                                    <button onClick={clearAllFilters} className="text-sm text-accent hover:underline px-1">
                                        Clear all filters
                                    </button>
                                </div>
                            ) : null}
                        </div>

                        {/* --- TABLE RENDERING --- */}
                        {filteredEntries.length === 0 ? (
                            <p className="p-6 text-text-muted text-base">
                                No entries match your filters.
                            </p>
                        ) : (
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
                                    {filteredEntries.map((entry) => (
                                        <Fragment key={entry.id}>
                                            <tr className="border-b border-border last:border-0">
                                                <td className="py-3 px-3 font-mono text-base text-text-primary whitespace-nowrap">{entry.date}</td>
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
                                                {/* Edit/Submit actions are only available for entries in draft or needs_revision status */}
                                                {entry.status === "draft" || entry.status === "needs_revision" ?
                                                    <td className="py-3 px-3 flex gap-2">
                                                        <button className="rounded-control border border-border-strong text-text-primary text-sm font-medium py-1 px-3 hover:bg-surface-page focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2" onClick={() => editEntry(entry)}>
                                                            Edit
                                                        </button>
                                                        <button className="rounded-control border border-border-strong text-text-primary text-sm font-medium py-1 px-3 hover:bg-surface-page focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2" onClick={() => handleSubmit(entry)}>
                                                            Submit
                                                        </button>
                                                    </td>
                                                : <td className="py-3 px-3"></td>}
                                            </tr>
                                            {/* Renders supervisor comments directly below the row if they exist */}
                                            {entry.latest_review && entry.latest_review.comment && (
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
                    </>
                )}
            </div>
        </div>
    );
}