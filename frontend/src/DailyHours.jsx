/**
 * Calculates and displays the total worked hours for a specific date.
 * Interacts with ongoing user input (draftEntry) to show real-time limits.
 */
export default function DailyHours({ entries, draftEntry, dailyLimit }) {

    if (!entries) {
        return (
            <div className="p-2 m-3 border rounded-card border-border bg-surface-card">  
                <p className="p-4 text-text-muted text-xl">⏳ Loading hours...</p>
            </div>
        )
    }
    
    const currentDate = new Date()
    const year = currentDate.getFullYear()
    const month = String(currentDate.getMonth() + 1).padStart(2,'0')
    const day = String(currentDate.getDate()).padStart(2,'0')
    const todayFormatted = `${year}-${month}-${day}`

    // Determine which date to summarize: if the user is currently editing/creating an entry,
    // track that entry's date. Otherwise, track today.
    const activeDate = (draftEntry && draftEntry.date) ? draftEntry.date : todayFormatted;

    const dateEntries = entries.filter(entry => entry.date === activeDate)
    let totalHours = 0;
    
    dateEntries.forEach(entry => {
        // If we are editing an existing entry, skip its old saved hours in the sum.
        // We will add the new draft hours below instead, avoiding double-counting.
        if (draftEntry && draftEntry.id === entry.id) {
            return; 
        }
        totalHours += entry.calculated_hours;
    });

    // Add the ongoing draft hours (real-time form input)
    if (draftEntry && draftEntry.date === activeDate && typeof draftEntry.hours === 'number') {
        totalHours += draftEntry.hours;
    }

    const isFormActiveForDate = draftEntry && draftEntry.date === activeDate;
    const hasEntriesOrDraft = dateEntries.length > 0 || isFormActiveForDate;

    const limitStr = dailyLimit ? Number(dailyLimit).toFixed(1) : "8.0";
    const dateDisplay = activeDate === todayFormatted ? "today" : activeDate;

    return(
        <div className="p-2 m-3 border rounded-card border-border bg-surface-card flex items-center justify-between">  
            {hasEntriesOrDraft ? <p className="p-4 text-xl">
                {dateDisplay}: <span className="font-mono font-bold text-accent">{totalHours.toFixed(1)}h/{limitStr}h</span>
                </p>:
                <p className="p-4 text-xl text-text-primary">No work hours registered {activeDate === todayFormatted ? "today" : `on ${activeDate}`}.</p>
            }
        </div>
    )
}