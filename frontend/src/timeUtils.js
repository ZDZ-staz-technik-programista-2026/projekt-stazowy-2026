export function calculateDecimalHours(startTime, endTime) {
    if (!startTime || !endTime) {
        return 0;
    }
    const time1 = startTime.split(":");
    const time2 = endTime.split(":");
    const minutes1 = parseInt(time1[0], 10) * 60 + parseInt(time1[1], 10);
    const minutes2 = parseInt(time2[0], 10) * 60 + parseInt(time2[1], 10);
    const diffInMinutes = Math.max(0, minutes2 - minutes1);
    return Number((diffInMinutes / 60).toFixed(1));
}