import { useEffect, useState } from "react";
import StatusBadge from "./StatusBadge";

const API_URL = import.meta.env.VITE_API_URL;

export default function EntriesList({ userId, counterOfRefresh }) {

    const [entriesList, setEntriesList] = useState([]);
    const [status, setStatus] = useState("loading");

    useEffect(() => {
        setStatus("loading");
        fetch(`${API_URL}/api/entries?user_id=${userId}`)
            .then(response => response.json())
            .then((data) => {
                setStatus("loaded");
                setEntriesList(data);
            })
            .catch(error => {
                console.log(`Error: ${error.message}`);
                setStatus("unreachable");
            });
    }, [userId, counterOfRefresh]);

    return (
        <div className="rounded-card border border-border-strong bg-surface-card mt-4  m-3 overflow-hidden">

            {status == "loading" && (
                <p className="p-6 text-center text-text-muted text-base">
                    ⏳ Loading entries...
                </p>
            )}

            {status == "unreachable" && (
                <p className="p-6 text-center text-status-revision-fg text-base">
                    ❌ Connection error
                </p>
            )}

            {status == "loaded" && entriesList.length == 0 && (
                <p className="p-6 text-center text-text-muted text-base">
                    No entries yet.
                </p>
            )}

            {status == "loaded" && entriesList.length > 0 && (
                <table className="w-full table-fixed">
                    <colgroup>
                        <col className="w-28" />
                        <col className="w-32" />
                        <col className="w-16" />
                        <col />
                        <col className="w-40" />
                        <col className="w-24" />
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
                            <>
                                <tr key={entry.id} className="border-b border-border last:border-0">
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
                                    {entry.status == "draft" || entry.status == "needs_revision" ?
                                        <td className="py-3 px-3">
                                            <button className="rounded-control border border-border-strong text-text-primary text-sm font-medium py-1 px-3 hover:bg-surface-page">
                                                Submit
                                            </button>
                                        </td>
                                    : <td className="py-3 px-3"></td>}
                                </tr>
                            </>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}