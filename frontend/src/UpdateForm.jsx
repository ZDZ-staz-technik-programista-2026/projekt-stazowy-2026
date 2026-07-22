import { useState } from "react"

const API_URL = import.meta.env.VITE_API_URL 
export default function UpdateForm({entry, setCounter, onClose}){


    const [editedEntry, setEditedEntry] = useState({
        date: entry.date,
        startTime: entry.start_time,
        endTime: entry.end_time,
        workDescription: entry.description,
        blockers: entry.blockers == "None" ? "" : entry.blockers
    })

    
    const [errors, setErrors] = useState({})

    function handleChange(e) {
        setEditedEntry({ ...editedEntry, [e.target.name]: e.target.value })
        setErrors({ ...errors, [e.target.name]: "" })
    }

    function calculateHours() {
        if (!editedEntry.startTime || !editedEntry.endTime) {
            return "0.0h";
        }
        const time1 = editedEntry.startTime.split(":")
        const time2 = editedEntry.endTime.split(":")
        const minutes1 = parseInt(time1[0], 10) * 60 + parseInt(time1[1], 10)
        const minutes2 = parseInt(time2[0], 10) * 60 + parseInt(time2[1], 10)
        const diffInMinutes = Math.max(0, minutes2 - minutes1)
        const decimalHours = (diffInMinutes / 60).toFixed(1)
        return `${decimalHours}h`
    }

    function handleSubmit(e) {
        e.preventDefault();
        setErrors({});

        const dataToBeSent = {
            "date": editedEntry.date,
            "start_time": editedEntry.startTime,
            "end_time": editedEntry.endTime,
            "description": editedEntry.workDescription,
            "blockers": editedEntry.blockers || "None"
        }

        fetch(`${API_URL}/api/entries/${entry.id}`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(dataToBeSent)
        })
        .then((response) => {
            return response.json().then((data) => {
                if (!response.ok) {
                    const newErrors = {};
                    if (data.code === "INVALID_TIME_RANGE") {
                        newErrors.endTime = data.message;
                    } else if (data.code === "FUTURE_DATE_FORBIDDEN") {
                        newErrors.date = data.message;
                    } else if (data.code === "EMPTY_DESCRIPTION") {
                        newErrors.workDescription = data.message;
                    } else if (data.code === "SCHEDULE_OVERLAP") {
                        newErrors.startTime = data.message;
                    } else if (data.code === "HOURLY_LIMIT_EXCEEDED") {
                        newErrors.endTime = data.message;
                    } else {
                        newErrors.general = data.message;
                    }

                    setErrors(newErrors);
                } else {
                    setCounter(prev => prev+1)
                    onClose()
                }
            });
        })
        .catch((err) => {
            setErrors({ general: "Connection error" });
        });
    }

    return (
        <form className="bg-surface-card border border-border rounded-card p-6 flex flex-col w-full max-w-[450px] mx-auto gap-4 mt-4 text-text-primary" onSubmit={handleSubmit}>
            <div className="flex flex-col gap-1">
                <div className="flex flex-row items-center gap-4">
                    <label className="w-40 shrink-0">Date:</label>
                    <input required name="date" type="date" className="w-full border border-border rounded-control p-2 focus:outline-accent" value={editedEntry.date} onChange={handleChange} />
                </div>
                {errors.date && <span className="text-status-revision-fg text-xs ml-40">{`⚠️${errors.date}`}</span>}
            </div>

            <div className="flex flex-col gap-1">
                <div className="flex flex-row items-center gap-4">
                    <label className="w-40 shrink-0">Start time:</label>
                    <input required name="startTime" type="time" className="w-full border border-border rounded-control p-2 font-mono focus:outline-accent" value={editedEntry.startTime} onChange={handleChange} />
                </div>
                {errors.startTime && <span className="text-status-revision-fg text-xs ml-40">{`⚠️${errors.startTime}`}</span>}
            </div>

            <div className="flex flex-col gap-1">
                <div className="flex flex-row items-center gap-4">
                    <label className="w-40 shrink-0">End time:</label>
                    <input required name="endTime" type="time" className="w-full border border-border rounded-control p-2 font-mono focus:outline-accent" value={editedEntry.endTime} onChange={handleChange} />
                </div>
                {errors.endTime && <span className="text-status-revision-fg  text-xs ml-40">{`⚠️${errors.endTime}`}</span>}
            </div>

            <div className="flex flex-row items-center gap-4">
                <label className="w-40 shrink-0">Calculated:</label>
                <span className="w-full font-mono">{calculateHours()}</span>
            </div>

            <div className="flex flex-col gap-1">
                <div className="flex flex-row items-center gap-4">
                    <label className="w-40 shrink-0">Work description:</label>
                    <textarea required name="workDescription" className="w-full border border-border rounded-control p-2 focus:outline-accent" value={editedEntry.workDescription} onChange={handleChange}></textarea>
                </div>
                {errors.workDescription && <span className="text-status-revision-fg text-xs ml-40">{`⚠️${errors.workDescription}`}</span>}
            </div>

            <div className="flex flex-row items-center gap-4">
                <label className="w-40 shrink-0">Blockers:</label>
                <input name="blockers" type="text" className="w-full border border-border rounded-control p-2 focus:outline-accent" value={editedEntry.blockers} onChange={handleChange} />
            </div>

            {errors.general && <div className="text-status-revision-fg text-sm">{`⚠️${errors.general}`}</div>}

            <div className="flex flex-row gap-2 mt-2">
                <button type="button" onClick={() => {
                    setErrors({})
                    onClose()
                    }} className="border border-border rounded-control px-4 py-2 hover:bg-surface-page transition-colors">
                    Cancel
                </button>
                <button type="submit" className="bg-accent text-surface-card rounded-control px-4 py-2 hover:opacity-90 transition-opacity">
                    Update Entry
                </button>
            </div>
        </form>
    )
}