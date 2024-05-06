export function formatTime(microseconds) {
  const seconds = microseconds / 1000;
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = Math.round(seconds % 60);

  // Creating a padded string for minutes and seconds for uniformity
  const paddedMinutes = String(minutes).padStart(2, "0");
  const paddedSeconds = String(remainingSeconds).padStart(2, "0");

  // Creating the final formatted string
  return `${hours}:${paddedMinutes}:${paddedSeconds}`;
}

export function formatForCopy(date) {
  const hours = date.getHours();
  const minutes = date.getMinutes();
  return `${hours}u${minutes}m`;
}

export function formatCardTime(start, end) {
  // Create a Date object from the start timestamp
  const startDate = new Date(start);
  // Format the start date and time
  const startDay = startDate.getDate().toString().padStart(2, "0");
  const startMonth = (startDate.getMonth() + 1).toString().padStart(2, "0");
  const startHour = startDate.getHours().toString().padStart(2, "0");
  const startMinute = startDate.getMinutes().toString().padStart(2, "0");
  const formattedStart = `${startDay}/${startMonth}: ${startHour}:${startMinute}`;

  // Check if the end timestamp is not null
  if (end !== null) {
    // Create a Date object from the end timestamp
    const endDate = new Date(end);
    // Format the end time
    const endHour = endDate.getHours().toString().padStart(2, "0");
    const endMinute = endDate.getMinutes().toString().padStart(2, "0");
    const formattedEnd = `${endHour}:${endMinute}`;

    // Return the full date range string
    return `${formattedStart} - ${formattedEnd}`;
  } else {
    // Return the string with "nog bezig"
    return `${formattedStart} - nog bezig`;
  }
}

export function convertToDatetimeLocal(date) {
  const offset = date.getTimezoneOffset() * 60000; // Convert offset to milliseconds
  const localDate = new Date(date.getTime() - offset); // Adjust date to local time
  return localDate.toISOString().slice(0, 16); // Convert to ISO string without 'Z'
}
