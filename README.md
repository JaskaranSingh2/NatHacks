# NatHacks Assistive Mirror# NatHacks Assistive Mirror



Raspberry Pi smart mirror that guides morning routines with on-device computer vision and optional Google Cloud Vision assist. Built for <150ms capture→overlay latency while keeping the UX senior-friendly.Raspberry Pi smart mirror that guides morning routines with on-device computer vision and optional Google Cloud Vision assist. Built for <150ms capture→overlay latency while keeping the UX senior-friendly.



## Quick Start## Quick Start



### 1. Backend Setup### 1. Backend Setup

```bash```bash

python -m venv .venvpython -m venv .venv

source .venv/bin/activatesource .venv/bin/activate

pip install -r backend/requirements.txtpip install -r backend/requirements.txt

uvicorn backend.app:app --host 0.0.0.0 --port 8000uvicorn backend.app:app --host 0.0.0.0 --port 8000

``````



### 2. Frontend Build### 2. Frontend Build

```bash```bash

cd frontendcd frontend

npm installnpm install

npm run build:mmnpm run build:mm

``````



### 3. MagicMirror Setup### 3. MagicMirror Setup

```bash```bash

cd mirrorcd mirror

npm installnpm install

npm startnpm start

``````



## Architecture## Architecture



- **Backend (FastAPI)**: Computer vision pipeline, WebSocket broadcasting, REST API- **Backend (FastAPI)**: Computer vision pipeline, WebSocket broadcasting, REST API

- **Frontend (React)**: TypeScript SPA with camera access and AR overlays- **Frontend (React)**: TypeScript SPA with camera access and AR overlays

- **MagicMirror Module**: Iframe wrapper that embeds the React app- **MagicMirror Module**: Iframe wrapper that embeds the React app



## Key Components## Key Components



### Backend (`backend/`)### Backend (`backend/`)

- `app.py` - FastAPI server with WebSocket and REST endpoints- `app.py` - FastAPI server with WebSocket and REST endpoints

- `vision_pipeline.py` - MediaPipe face/hands processing with cloud fallback- `vision_pipeline.py` - MediaPipe face/hands processing with cloud fallback

- `cloud_vision.py` - Google Cloud Vision client with rate limiting- `cloud_vision.py` - Google Cloud Vision client with rate limiting

- `task_system.py` - Guided routine management- `task_system.py` - Guided routine management



### Frontend (`frontend/`)### Frontend (`frontend/`)

- React + TypeScript + Vite + Tailwind CSS- React + TypeScript + Vite + Tailwind CSS

- Camera access with getUserMedia- Camera access with getUserMedia

- Canvas 2D overlays (rings, text, progress bars)- Canvas 2D overlays (rings, text, progress bars)

- WebSocket connection to backend- WebSocket connection to backend



### MagicMirror (`modules/MMM-AssistiveCoach/`)### MagicMirror (`modules/MMM-AssistiveCoach/`)

- Iframe wrapper for React SPA- Iframe wrapper for React SPA

- Configuration injection- Configuration injection

- Camera/microphone permissions- Camera/microphone permissions



## API Endpoints## API Endpoints



### REST### REST

- `GET /health` - System status (camera, FPS, pose availability)- `GET /health` - System status (camera, FPS, pose availability)

- `POST /settings` - Configure vision pipeline- `POST /settings` - Configure vision pipeline

- `POST /overlay` - Send overlay commands- `POST /overlay` - Send overlay commands

- `POST /session/start` - Begin guided routine- `POST /session/start` - Begin guided routine



### WebSocket### WebSocket

- `ws://localhost:8000/ws` - Real-time overlay updates- `ws://localhost:8000/ws` - Real-time overlay updates



## Configuration## Configuration



### Backend Settings### Backend Settings

```json```json

{{

  "aruco": true,  "aruco": true,

  "pose": true,  "pose": true,

  "overlay_from_aruco": true,  "overlay_from_aruco": true,

  "aruco_stride": 2,  "aruco_stride": 2,

  "detect_scale": 0.75,  "detect_scale": 0.75,

  "reduce_motion": false  "reduce_motion": false

}}

``````



### MagicMirror Config### MagicMirror Config

```javascript```javascript

{{

  module: "MMM-AssistiveCoach",  module: "MMM-AssistiveCoach",

  position: "fullscreen_above",  position: "fullscreen_above",

  config: {  config: {

    wsUrl: "ws://127.0.0.1:8000/ws",    wsUrl: "ws://127.0.0.1:8000/ws",

    apiBase: "http://127.0.0.1:8000",    apiBase: "http://127.0.0.1:8000",

    reduceMotion: false,    reduceMotion: false,

    showHints: true    showHints: true

  }  }

}}

``````



## Development## Development



### Testing### Testing

```bash```bash

# Backend tests# Backend tests

python -m pytest backend/testspython -m pytest backend/tests



# Vision pipeline test# Vision pipeline test

python backend/vision_pipeline.pypython backend/vision_pipeline.py



# MagicMirror test# MagicMirror test

cd mirror && npm startcd mirror && npm start

``````



### Camera Calibration### Camera Calibration

```bash```bash

python scripts/calibrate_cam.pypython scripts/calibrate_cam.py

``````



### AR Marker Generation### AR Marker Generation

```bash```bash

python scripts/gen_aruco.pypython scripts/gen_aruco.py

``````



## Troubleshooting## Troubleshooting



### Common Issues### Common Issues



1. **Camera not working**: Check `/dev/video0` permissions1. **Camera not working**: Check `/dev/video0` permissions

2. **WebSocket connection failed**: Verify backend is running on port 80002. **WebSocket connection failed**: Verify backend is running on port 8000

3. **MagicMirror not loading**: Run `npm run build:mm` in frontend directory3. **MagicMirror not loading**: Run `npm run build:mm` in frontend directory

4. **Overlays not showing**: Check WebSocket messages in browser dev tools4. **Overlays not showing**: Check WebSocket messages in browser dev tools



### Logs### Logs

- Backend: `backend.log`- Backend: `backend.log`

- Latency metrics: `logs/latency.csv`- Latency metrics: `logs/latency.csv`

- MagicMirror: Check console in Electron dev tools- MagicMirror: Check console in Electron dev tools



## Hardware Requirements## Hardware Requirements



- Raspberry Pi 4+ (8GB RAM recommended)- Raspberry Pi 4+ (8GB RAM recommended)

- Camera module (Pi Camera or USB webcam)- Camera module (Pi Camera or USB webcam)

- Monitor/TV for display- Monitor/TV for display

- Optional: Google Cloud Vision credentials for enhanced accuracy- Optional: Google Cloud Vision credentials for enhanced accuracy



## License## License



MITMIT
