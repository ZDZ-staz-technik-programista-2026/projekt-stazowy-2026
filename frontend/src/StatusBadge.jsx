export default function StatusBadge({ status }) {

    const labels = {
        "needs_revision": "Needs revision",
        "approved": "Approved",
        "submitted": "Submitted",
        "draft": "Draft"
    }
    const classes = {
        needs_revision: {
            bg: "bg-status-revision-bg",
            dot: "bg-status-revision-fg",
            text: "text-status-revision-fg"
        },
        approved: {
            bg: "bg-status-approved-bg",
            dot: "bg-status-approved-fg",
            text: "text-status-approved-fg"
        },
        submitted: {
            bg: "bg-status-submitted-bg",
            dot: "bg-status-submitted-fg",
            text: "text-status-submitted-fg"
        },
        draft: {
            bg: "bg-status-draft-bg",
            dot: "bg-status-draft-fg",
            text: "text-status-draft-fg"
        }
    }
    return (
        <div className="flex p-1">
            <div className={`${classes[status].bg} rounded-control flex items-center py-1 px-3`}>
                <div className={`h-2.5 w-2.5 rounded-full ${classes[status].dot} mr-2`}></div>
                <span className={`font-medium text-base ${classes[status].text}`}>{labels[status]}</span>
            </div>
        </div>
    )
}