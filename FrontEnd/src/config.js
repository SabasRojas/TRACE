// config.js

let serverMode = "local"; // "ip" or "local"

/**
 * Get the current API base URL based on the server mode.
 * @returns {string} The base URL for API requests.
 */
export function getApiBase() {
    if (serverMode === "local") {
        return "http://localhost:8000";
    } else {
        return "http://10.1.0.10:8000"; // your server IP
    }
}

/**
 * Set the server mode to "local" or "ip".
 * @param {"local" | "ip"} mode - The mode to set ("local" for localhost, "ip" for server IP).
 */
export function setServerMode(mode) {
    serverMode = mode;
}

