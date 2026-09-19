# VaaniShield

VaaniShield is an innovative application designed to protect users from social engineering scams by detecting synthetic or cloned speech and identifying risky conversational contexts in audio inputs. It combines real-time voice authenticity analysis with multilingual speech-to-text transcription and contextual risk assessment to flag suspicious activity.

## Table of Contents

-   [Features](#features)
-   [Tech Stack](#tech-stack)
-   [Project Structure](#project-structure)
-   [Installation](#installation)
    -   [Prerequisites](#prerequisites)
    -   [Backend Setup](#backend-setup)
    -   [Frontend Setup](#frontend-setup)
-   [Usage](#usage)
    -   [Running the Application](#running-the-application)
    -   [API Usage](#api-usage)
-   [Contributing](#contributing)

## Features

VaaniShield offers a robust set of features to combat voice-based scams:

*   **Real-time Voice Authenticity Detection**: Employs classic Digital Signal Processing (DSP) features (pitch jitter, shimmer, spectral flatness) for fast, CPU-efficient, and offline anti-spoofing analysis to identify synthetic/cloned speech.
*   **Multilingual Speech-to-Text Transcription**: Utilizes OpenAI's Whisper model to transcribe audio in English, Hindi, and Marathi.
*   **Contextual Risk Assessment**: Scans transcribed text for keywords commonly associated with social engineering scams to provide a contextual risk score.
*   **Web-based User Interface**: A modern Next.js application allows users to easily upload audio files and visualize real-time analysis results, including authenticity scores, transcripts, and contextual risk flags.
*   **Explainable Detection**: Provides human-readable reasons for flagging audio, mapping DSP features to identifiable voice characteristics.
*   **Programmatic API Access**: Exposes a FastAPI endpoint for seamless integration into other systems for audio analysis.
*   **Test Audio Generation**: Includes a utility script to create synthetic 'natural-like' and 'cloned-like' audio samples for testing and development.

## Tech Stack

VaaniShield is built using a modern full-stack architecture:

**Backend:**
*   **Language**: Python
*   **Framework**: FastAPI
*   **Server**: Uvicorn
*   **Speech-to-Text**: OpenAI Whisper
*   **Audio Processing**: Librosa, NumPy, SciPy, SoundFile (for DSP feature extraction)

**Frontend:**
*   **Language**: TypeScript
*   **Framework**: Next.js
*   **Library**: React
*   **Styling**: Tailwind CSS
*   **Audio Visualization**: Web Audio API (inferred for waveform display)

## Project Structure

The repository is organized into two main parts: `backend` for the API and detection logic, and `frontend` for the user interface.

```
VaaniShield/
├── backend/
│   ├── app/
│   │   ├── detection.py        # Core voice authenticity detection logic
│   │   ├── main.py             # FastAPI application entry point
│   │   └── transcript.py       # Speech-to-text and contextual risk assessment
│   ├── generate_test_audio.py  # Script to generate synthetic test audio
│   ├── requirements.txt        # Python dependencies
│   └── test_audio/             # Sample test audio files
├── frontend/
│   ├── app/                    # Next.js pages and root layout
│   │   ├── page.tsx            # Main application page
│   │   └── layout.tsx          # Root layout
│   ├── components/             # Reusable React components (e.g., Waveform, RiskGauge)
│   ├── lib/                    # Frontend utility functions
│   ├── public/                 # Static assets
│   ├── package.json            # Node.js dependencies
│   └── ...                     # Other Next.js configuration files
└── README.md
```

## Installation

Follow these steps to set up and run VaaniShield locally.

### Prerequisites

*   **Python 3.8+**
*   **Node.js (LTS recommended)** and **npm** or **yarn**
*   **Git**

### Backend Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/girish-indurkar/VaaniShield.git
    cd VaaniShield
    ```

2.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

3.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

4.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Frontend Setup

1.  **Navigate back to the project root and then to the frontend directory:**
    ```bash
    cd ..
    cd frontend
    ```

2.  **Install Node.js dependencies:**
    ```bash
    npm install
    # Or if you prefer yarn
    # yarn install
    ```

## Usage

### Running the Application

To run the full VaaniShield application, you need to start both the backend API and the frontend web server.

1.  **Start the Backend API:**
    Open a new terminal, navigate to the `backend` directory, activate your virtual environment, and run the FastAPI server:
    ```bash
    cd VaaniShield/backend
    # Activate virtual environment (if not already active)
    # On Windows: .\venv\Scripts\activate
    # On macOS/Linux: source venv/bin/activate
    uvicorn app.main:app --reload --port 8000
    ```
    The backend API will be running at `http://localhost:8000`.

2.  **Start the Frontend Web Server:**
    Open another new terminal, navigate to the `frontend` directory, and start the Next.js development server:
    ```bash
    cd VaaniShield/frontend
    npm run dev
    # Or if you used yarn
    # yarn dev
    ```
    The frontend application will be available in your browser at `http://localhost:3000`.

    You can now upload audio files via the web interface and see the authenticity detection, transcription, and risk assessment results.

### API Usage

For developers, you can interact directly with the backend API. The main endpoint is `/analyze`.

**Endpoint:** `POST /analyze`

**Parameters:**
*   `file`: An audio file (form-data)
*   `language`: The language of the audio (form-data, `en` for English, `hi` for Hindi, `mr` for Marathi). Defaults to `en`.

**Example using `curl`:**

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "accept: application/json" \
  -F "file=@/path/to/your/audio.wav" \
  -F "language=en"
```

Replace `/path/to/your/audio.wav` with the actual path to your audio file.

## Contributing

We welcome contributions to VaaniShield! If you'd like to contribute, please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and ensure they adhere to the project's coding standards.
4.  Write clear, concise commit messages.
5.  Submit a pull request with a detailed description of your changes.

