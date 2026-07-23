import { Fragment, useEffect, useState } from "react";
import StatusBadge from "./StatusBadge";

const API_URL = import.meta.env.VITE_API_URL;

export default function ApprovalQueue({
    userId,
    counterOfRefresh,
    setCounterOfRefresh,
}) {
    const [entriesList, setEntriesList] = useState([]);
    const [usersList, setUsersList] = useState([]);
    const [status, setStatus] = useState("loading");
    const [errorMessage, setErrorMessage] = useState("");
    const [returnEntryId, setReturnEntryId] = useState(null);
    const [returnComment, setReturnComment] = useState("");

    useEffect(() => {
        if (!userId) return;
        
        setStatus("loading");
        setErrorMessage("");

        Promise.all([
            fetch(`${API_URL}/api/entries?user_id=${userId}`)
                .then(async (response) => {
                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error(
                            data?.message || "Failed to fetch entries"
                        );
                    }

                    return data;
                }),

            fetch(`${API_URL}/api/users`)
                .then(async (response) => {
                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error("Failed to fetch users");
                    }

                    return data;
                }),
        ])
            .then(([entries, users]) => {
                if (
                    !Array.isArray(entries) ||
                    !Array.isArray(users)
                ) {
                    throw new Error("Invalid data format");
                }

                setEntriesList(entries);
                setUsersList(users);
                setStatus("loaded");
            })
            .catch((error) => {
                console.error(error);
                setErrorMessage(error.message);
                setStatus("unreachable");
            });
    }, [userId, counterOfRefresh]);


    const refresh = () => {
        setCounterOfRefresh((prev) => prev + 1);
    };


    const getUserName = (id) => {
        const user = usersList.find(
            (user) => user.id === id
        );

        return user?.name || "Unknown user";
    };

    function handleApprove(entryId) {
        fetch(`${API_URL}/api/entries/${entryId}/approve`,{
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                created_by: userId,
            }) 
        }).then((response) => response.json())
        .then(
            setCounterOfRefresh(prev => prev+1)
        )
        .catch(error =>
            console.log(error.message)
        )
    }


    function handleReturn(entryId){
        fetch(`${API_URL}/api/entries/${entryId}/return`,{
            method: "POST",
            headers:{
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                created_by: userId,
                comment: returnComment
            }),
        })
        .then((response) => response.json())
        .then(refresh())
        .catch(error =>
            console.log(error.message)
        )
    }

    const submittedEntries = entriesList.filter(
        (entry) => entry.status === "submitted"
    );
    return (
        <div>
            <div className="rounded-card border border-border-strong bg-surface-card mt-4 m-3 overflow-hidden">

                {status === "loading" && (
                    <p className="p-6 text-center text-text-muted">
                        Loading entries...
                    </p>
                )}
                {status === "unreachable" && (
                    <p className="p-6 text-center text-status-revision-fg">
                        {errorMessage}
                    </p>
                )}
                {status === "loaded" &&
                    submittedEntries.length === 0 && (
                        <div className="flex flex-col items-center justify-center min-h-[420px]">
                        <h2 className="text-3xl font-medium text-text-primary mb-6">
                            All caught up!
                        </h2>

                            <p className="text-lg text-text-muted">
                                There are no entries waiting for your approval
                            </p>
                        </div>
                    )}
                {status === "loaded" &&
                    submittedEntries.length > 0 && (
                    <div className="overflow-x-auto">
                        <table className="w-full table-fixed">
                        <colgroup>
                            <col className="w-40" />
                            <col className="w-32" />
                            <col className="w-36" />
                            <col className="w-20" />
                            <col />
                            <col className="w-40" />
                            <col className="w-32" />
                            <col className="w-52" />
                        </colgroup>
                            <thead>
                                <tr className="border-b border-border">

                                    <th className="text-left font-medium text-text-secondary text-sm py-2 px-3">
                                        Student
                                    </th>

                                    <th className="text-left font-medium text-text-secondary text-sm py-2 px-3">
                                        Date
                                    </th>

                                    <th className="text-left font-medium text-text-secondary text-sm py-2 px-3">
                                        Time
                                    </th>

                                    <th className="text-left font-medium text-text-secondary text-sm py-2 px-3">
                                        Hours
                                    </th>

                                    <th className="text-left font-medium text-text-secondary text-sm py-2 px-3">
                                        Description
                                    </th>

                                    <th className="text-left font-medium text-text-secondary text-sm py-2 px-3">
                                        Blockers
                                    </th>

                                    <th className="text-left font-medium text-text-secondary text-sm py-2 px-3">
                                        Status
                                    </th>

                                    <th className="text-left font-medium text-text-secondary text-sm py-2 px-3">
                                        Action
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {submittedEntries.map((entry) => (
                                    <Fragment key={entry.id}>
                                        <tr className="border-b border-border">
                                            <td className="py-3 px-3 text-base text-text-primary">
                                                {getUserName(entry.user_id)}
                                            </td>
                                            <td className="py-3 px-3 font-mono text-base text-text-primary">
                                                {entry.date}
                                            </td>
                                            <td className="py-3 px-3 font-mono text-base text-text-primary whitespace-nowrap">
                                                {entry.start_time
                                                    ?.toString()
                                                    .substring(0, 5)}
                                                {" - "}
                                                {entry.end_time
                                                    ?.toString()
                                                    .substring(0, 5)}
                                            </td>
                                            <td className="py-3 px-3 font-mono text-base text-text-primary">
                                                {(entry.calculated_hours).toFixed(2)}h
                                            </td>
                                            <td className="py-3 px-3 text-base text-text-primary truncate">
                                                {entry.description}
                                            </td>

                                            <td className="py-3 px-3 text-base text-text-primary truncate">
                                                {entry.blockers || "-"}
                                            </td>

                                            <td className="py-3 px-3">
                                                <StatusBadge
                                                    status={entry.status}
                                                />
                                            </td>
                                            <td className="py-3 px-3">
                                                <div className="flex gap-2">
                                                    <button
                                                        className="bg-accent text-white text-sm py-1 px-4 rounded-control"
                                                        onClick = {() => {
                                                            handleApprove(entry.id)
                                                            refresh()
                                                        }}
                                                    >
                                                        Approve
                                                    </button>
                                                    <button
                                                        className="rounded-control border border-red-500 text-red-600 text-sm py-1 px-4 hover:bg-red-50"
                                                        onClick={() => {
                                                            setReturnEntryId(entry.id);
                                                            setReturnComment("");
                                                        }}
                                                    >
                                                        Return
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                        {returnEntryId === entry.id && (
                                            <tr className="bg-surface-page">
                                                <td
                                                    colSpan={8}
                                                    className="py-3 px-3"
                                                >
                                                    <input
                                                        className="w-full rounded-control border border-border-strong px-3 py-2"
                                                        placeholder="Type reason for return (mandatory)..."
                                                        value={returnComment}
                                                        onChange={(e) =>
                                                            setReturnComment(
                                                                e.target.value
                                                            )
                                                        }
                                                    />
                                                    <div className="flex gap-2 mt-3">
                                                        <button
                                                            className="rounded-control border border-border-strong text-text-primary text-sm py-1 px-4 hover:bg-surface-page"
                                                            onClick={() => {
                                                                setReturnEntryId(null);
                                                                setReturnComment("");
                                                            }}
                                                        >
                                                            Cancel
                                                        </button>
                                                        <button
                                                            disabled={
                                                                !returnComment.trim()
                                                            }
                                                            className="rounded-control border border-red-500 text-red-600 text-sm py-1 px-4 hover:bg-red-50 disabled:opacity-50"
                                                            onClick={() => {
                                                                handleReturn(entry.id)
                                                            }}
                                                        >
                                                            Confirm return
                                                        </button>
                                                    </div>
                                                </td>
                                            </tr>
                                        )}
                                    </Fragment>
                                ))}
                            </tbody>
                        </table>
                        </div>
                    )}
            </div>
        </div>
    );
}