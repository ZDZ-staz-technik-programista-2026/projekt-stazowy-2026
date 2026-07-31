/**
 * Utility functions for time handling and arithmetic.
 */

/**
 * Parses start and end time strings (HH:MM format) and returns 
 * the difference in decimal hours (e.g. 1 hour 30 mins -> 1.5).
 */
export function calculateDecimalHours(startTime, endTime) {
    if (!startTime || !endTime) {
        return 0;
    }
    const time1 = startTime.split(":");
    const time2 = endTime.split(":");
    
    // Convert both timestamps completely into minutes since midnight
    const minutes1 = parseInt(time1[0], 10) * 60 + parseInt(time1[1], 10);
    const minutes2 = parseInt(time2[0], 10) * 60 + parseInt(time2[1], 10);
    
    // Math.max guarantees we don't output negative times for overnight/backwards ranges
    const diffInMinutes = Math.max(0, minutes2 - minutes1);
    
    // Format to 1 decimal place limit
    return Number((diffInMinutes / 60).toFixed(1));
}