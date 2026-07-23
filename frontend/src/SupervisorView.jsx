import SupervisorList from "./SupervisorList";

export default function SupervisorView({
    userId,
    counterOfRefresh,
    setCounterOfRefresh,
}) {
    return (
        <div className="rounded-card border border-border-strong bg-surface-card mt-4 overflow-hidden">
            <SupervisorList
                userId={userId}
                counterOfRefresh={counterOfRefresh}
                setCounterOfRefresh={setCounterOfRefresh}
            />
        </div>
    );
}