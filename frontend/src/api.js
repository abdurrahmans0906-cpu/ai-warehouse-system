// Centralized dynamic API base URL
// Works seamlessly when accessed via localhost, 127.0.0.1, or local network IP (e.g., 192.168.0.107)
export const API_BASE = process.env.REACT_APP_API_URL || `http://${window.location.hostname || "127.0.0.1"}:8000`;
