import { useState } from "react"

export default function EntriesForm({ userId, setCounter, setShowForm}) {
    const [formData, setFormData] = useState({
        date: "",
        startTime: "",
        endTime: "",
        workDescription: "",
        blockers: "",
        status: "draft"
    })
    
    const [errors, setErrors] = useState({})

    function handleChange(e) {
        setFormData({ ...formData, [e.target.name]: e.target.value })
        setErrors({ ...errors, [e.target.name]: "" })
    }

    function calculateHours() {
        if (!formData.startTime || !formData.endTime) {
            return "0.0h";
        }
        const time1 = formData.startTime.split(":")
        const time2 = formData.endTime.split(":")
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
            "user_id": userId,
            "date": formData.date,
            "start_time": formData.startTime,
            "end_time": formData.endTime,
            "description": formData.workDescription,
            "blockers": formData.blockers || "None"
        }

        fetch("http://localhost:8000/api/entries", {
            method: "POST",
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
                    setFormData({
                        date: "",
                        startTime: "",
                        endTime: "",
                        workDescription: "",
                        blockers: "",
                        status: "draft"
                    });
                    setShowForm(false)
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
                    <input required name="date" type="date" className="w-full border border-border rounded-control p-2 focus:outline-accent" value={formData.date} onChange={handleChange} />
                </div>
                {errors.date && <span className="text-status-revision-fg text-xs ml-40">{`⚠️${errors.date}`}</span>}
            </div>

            <div className="flex flex-col gap-1">
                <div className="flex flex-row items-center gap-4">
                    <label className="w-40 shrink-0">Start time:</label>
                    <input required name="startTime" type="time" className="w-full border border-border rounded-control p-2 font-mono focus:outline-accent" value={formData.startTime} onChange={handleChange} />
                </div>
                {errors.startTime && <span className="text-status-revision-fg text-xs ml-40">{`⚠️${errors.startTime}`}</span>}
            </div>

            <div className="flex flex-col gap-1">
                <div className="flex flex-row items-center gap-4">
                    <label className="w-40 shrink-0">End time:</label>
                    <input required name="endTime" type="time" className="w-full border border-border rounded-control p-2 font-mono focus:outline-accent" value={formData.endTime} onChange={handleChange} />
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
                    <textarea required name="workDescription" className="w-full border border-border rounded-control p-2 focus:outline-accent" value={formData.workDescription} onChange={handleChange}></textarea>
                </div>
                {errors.workDescription && <span className="text-status-revision-fg text-xs ml-40">{`⚠️${errors.workDescription}`}</span>}
            </div>

            <div className="flex flex-row items-center gap-4">
                <label className="w-40 shrink-0">Blockers:</label>
                <input name="blockers" type="text" className="w-full border border-border rounded-control p-2 focus:outline-accent" value={formData.blockers} onChange={handleChange} />
            </div>

            {errors.general && <div className="text-status-revision-fg text-sm">{`⚠️${errors.general}`}</div>}

            <div className="flex flex-row gap-2 mt-2">
                <button type="button" onClick={() => {
                    setErrors({})
                    setShowForm(false)
                    }} className="border border-border rounded-control px-4 py-2 hover:bg-surface-page transition-colors">
                    Cancel
                </button>
                <button type="submit" className="bg-accent text-surface-card rounded-control px-4 py-2 hover:opacity-90 transition-opacity">
                    Save draft
                </button>
            </div>
        </form>
    )
}