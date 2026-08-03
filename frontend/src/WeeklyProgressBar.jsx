/**
 * Component displaying the progress towards the 40-hour weekly cap.
 * Provides an advisory warning if remaining hours cannot accommodate a typical workday.
 */
export default function WeeklyProgressBar({ totalHours }) {
    const WEEKLY_CAP = 40.0;
    const TYPICAL_ENTRY_HOURS = 8.0;

    const parsedHours = Number(totalHours);
    const safeHours = Number.isFinite(parsedHours) ? parsedHours : 0;
    const roundedHours = Math.round(safeHours * 10) / 10;
    const rawRemaining = WEEKLY_CAP - safeHours;
    const remaining = Math.max(
        0,
        Math.round(rawRemaining * 10) / 10
    );
    const percentage = Math.min(
        100,
        Math.max(0, (safeHours / WEEKLY_CAP) * 100)
    );
    // Warning should appear whenever adding a typical 8h entry would exceed the cap
    const showsWarning = rawRemaining < TYPICAL_ENTRY_HOURS;

    return (
        <div className="mt-6 pt-4 border-t border-border-strong">
            <div className="flex justify-between items-center mb-2">
                <span className="text-base text-text-secondary font-medium">
                    Weekly Capacity
                </span>

                <span className="font-mono font-bold text-text-primary">
                    {roundedHours}h / {WEEKLY_CAP}h
                </span>
            </div>

            <div className="w-full h-4 bg-surface-page border border-border rounded-full overflow-hidden">
                <div
                    className="h-full bg-accent transition-all duration-500"
                    style={{ width: `${percentage}%` }}
                ></div>
            </div>

            {showsWarning && (
                <div className="mt-3 p-3 bg-status-revision-bg text-status-revision-fg rounded-control text-sm flex items-start gap-2">
                    <span className="text-base leading-none mt-0.5 shrink-0">
                        ⚠️
                    </span>

                    <p>
                        <strong>Advisory:</strong> You have{" "}
                        <strong>{remaining.toFixed(1)}h</strong> remaining this
                        week. A typical full-day entry might exceed your
                        40-hour cap.
                    </p>
                </div>
            )}
        </div>
    );
}