// mobile/app/config.ts
// ─────────────────────────────────────────────────────────────────
// LEARNING NOTE – Connecting Expo to a local backend
//
// The backend runs at localhost:8000 ON YOUR MACHINE.
// "localhost" means different things depending on where the app runs:
//
//   iOS Simulator       → localhost resolves to your Mac directly ✅
//   Android Emulator    → localhost = the emulator itself (not your machine!)
//                         Use 10.0.2.2 instead – that's the emulator's
//                         alias for the host machine.
//   Physical device     → Neither works. Use your machine's LAN IP,
//                         e.g. 192.168.1.100  (find via `ipconfig`)
//
// For this checkpoint, set API_BASE_URL to whichever matches your setup.
// ─────────────────────────────────────────────────────────────────

// ▼ CHANGE THIS to match how you're running the app:
//
//   Android Emulator:  "http://10.0.2.2:8000"
//   iOS Simulator:     "http://localhost:8000"
//   Physical device:   "http://<your-LAN-ip>:8000"   e.g. "http://192.168.1.100:8000"

// ▼ Set to your machine's LAN IP when using a physical device.
//   Android Emulator:  "http://10.0.2.2:8000"
//   iOS Simulator:     "http://localhost:8000"
//   Physical device:   "http://<your-LAN-ip>:8000"
export const API_BASE_URL = "http://192.168.0.189:8000";

export const API_V1 = `${API_BASE_URL}/v1`;
