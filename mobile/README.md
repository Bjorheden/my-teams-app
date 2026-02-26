# Mobile – MyTeams Expo App

## Overview

React Native + Expo + TypeScript mobile app.
Runs **outside Docker** via Expo Go on your phone or an Android/iOS emulator.

## Checkpoint 1 – Status

The mobile scaffold exists but has no backend calls yet.
Backend integration starts in **Checkpoint 3**.

## Setup

```bash
cd mobile

# Install dependencies
npm install

# Start the Expo dev server
npx expo start
```

Then:
- Press `a` to open in Android emulator
- Press `i` to open in iOS simulator
- Scan the QR code with Expo Go on your phone

## Connecting to the Backend

The backend runs at `http://localhost:8000` on your machine.

- **Android emulator**: use `http://10.0.2.2:8000` (emulator loopback)
- **Physical device**: use your machine's LAN IP, e.g. `http://192.168.1.100:8000`
- **iOS simulator**: `http://localhost:8000` works directly

The API base URL is configured in `app/config.ts` (added in CP3).

## Project Structure

```
mobile/
├── package.json
├── tsconfig.json
└── app/
    ├── _layout.tsx      ← Expo Router root layout (CP3)
    ├── index.tsx        ← Home / placeholder screen
    ├── config.ts        ← API base URL config (CP3)
    └── (tabs)/          ← Tab navigation screens (CP3)
```

## TypeScript Check

```bash
npx tsc --noEmit
```

## Linting

```bash
npx eslint app --ext .ts,.tsx
```
