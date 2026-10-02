// Runtime API base for static mirrors (GitHub Pages / HF / Vercel).
// Empty string = same origin (correct when served by the Worker itself).
// Mirrors set this to the deployed API origin, e.g. https://japan-launch-check.<acct>.workers.dev
window.API_BASE_URL = "";
