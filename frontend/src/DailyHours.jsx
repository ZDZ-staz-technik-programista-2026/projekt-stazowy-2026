export default function DailyHours({counterOfRefresh, entries, draftEntry}) {

    if (!entries) {
        return (
            <div className="p-2 m-3 border rounded-card border-border">  
                <p className="p-4 text-text-muted text-xl">⏳ Loading today's hours...</p>
            </div>
        )
    }
    
    const date = new Date()
    let year = date.getFullYear()
    let month = String(date.getMonth() + 1).padStart(2,'0')
    let day = String(date.getDate()).padStart(2,'0')
    let dateFormatted = `${year}-${month}-${day}`

    let todayEntries = entries.filter(entry => entry.date === dateFormatted)
    let todayHours = 0;
    todayEntries.forEach(entry => {
        if (draftEntry && draftEntry.id === entry.id) {
            return; 
        }
        todayHours += entry.calculated_hours;
    });

    if (draftEntry && draftEntry.date === dateFormatted) {
        todayHours += draftEntry.hours;
    }

    return(
        <div className="p-2 m-3 border rounded-card border-border bg-surface-card flex items-center justify-between">  
            {todayEntries.length != 0 ? <p className="p-4  text-xl">
                today: <span className="font-mono font-bold text-accent">{todayHours.toFixed(1)}h/8.0h</span>
                </p>:
                <p className="p-4 text-xl text-text-primary">No work hours registered today.</p>
            }
        </div>
    )
}