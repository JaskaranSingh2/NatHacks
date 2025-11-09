# Google Vertex AI Voice Assistant Integration

## 🎯 Overview

This document outlines the integration plan for Google Vertex AI voice assistant capabilities into the AssistiveCoach smart mirror system.

## 📋 Prerequisites

### Google Cloud Setup

1. **Google Cloud Project**

   ```bash
   # Create project (if not exists)
   gcloud projects create assistive-coach-ai --name="AssistiveCoach AI"

   # Set project
   gcloud config set project assistive-coach-ai
   ```

2. **Enable Required APIs**

   ```bash
   # Speech-to-Text API
   gcloud services enable speech.googleapis.com

   # Text-to-Speech API
   gcloud services enable texttospeech.googleapis.com

   # Vertex AI API
   gcloud services enable aiplatform.googleapis.com

   # Cloud Storage (for audio files)
   gcloud services enable storage.googleapis.com
   ```

3. **Create Service Account**

   ```bash
   gcloud iam service-accounts create assistivecoach-voice \
     --display-name="AssistiveCoach Voice Assistant"

   # Grant permissions
   gcloud projects add-iam-policy-binding assistive-coach-ai \
     --member="serviceAccount:assistivecoach-voice@assistive-coach-ai.iam.gserviceaccount.com" \
     --role="roles/aiplatform.user"

   gcloud projects add-iam-policy-binding assistive-coach-ai \
     --member="serviceAccount:assistivecoach-voice@assistive-coach-ai.iam.gserviceaccount.com" \
     --role="roles/speech.client"

   # Download credentials
   gcloud iam service-accounts keys create ~/vertex-ai-key.json \
     --iam-account=assistivecoach-voice@assistive-coach-ai.iam.gserviceaccount.com
   ```

4. **Set Environment Variable**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="$HOME/vertex-ai-key.json"
   ```

### Python Dependencies

Add to `backend/requirements.txt`:

```txt
google-cloud-aiplatform>=1.38.0
google-cloud-speech>=2.21.0
google-cloud-texttospeech>=2.14.1
google-cloud-storage>=2.10.0
pyaudio>=0.2.13  # For microphone input
pydub>=0.25.1     # Audio processing
```

Install:

```bash
cd backend
pip install -r requirements.txt
```

## 🏗️ Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User (Microphone Input)                  │
└───────────────────────────┬─────────────────────────────────┘
                            │ Audio Stream
                            ▼
┌─────────────────────────────────────────────────────────────┐
│           Voice Activity Detection (VAD)                    │
│           • Detect wake word: "Hey Mirror"                  │
│           • Buffer audio until silence                      │
└───────────────────────────┬─────────────────────────────────┘
                            │ Audio Chunk
                            ▼
┌─────────────────────────────────────────────────────────────┐
│     Google Cloud Speech-to-Text API                         │
│     • Streaming recognition                                 │
│     • Language: en-US (configurable)                        │
│     • Enhanced models for conversational speech             │
└───────────────────────────┬─────────────────────────────────┘
                            │ Transcribed Text
                            ▼
┌─────────────────────────────────────────────────────────────┐
│           Intent Classification & NLU                       │
│           • Parse command ("start brushing teeth")          │
│           • Extract entities (task_name, step_number)       │
│           • Classify intent (start_task, next_step, help)   │
└───────────────────────────┬─────────────────────────────────┘
                            │ Intent + Entities
                            ▼
┌─────────────────────────────────────────────────────────────┐
│      Context Manager (AssistiveCoach Backend)               │
│      • Current task state (task_id, step_num)               │
│      • User profile (preferences, history)                  │
│      • Session context (time, location)                     │
└───────────────────────────┬─────────────────────────────────┘
                            │ Context Payload
                            ▼
┌─────────────────────────────────────────────────────────────┐
│    Vertex AI Gemini API (Response Generation)               │
│    • Generate natural language response                     │
│    • Consider context & task state                          │
│    • Provide encouragement & guidance                       │
└───────────────────────────┬─────────────────────────────────┘
                            │ Response Text
                            ▼
┌─────────────────────────────────────────────────────────────┐
│       Google Cloud Text-to-Speech API                       │
│       • Neural2 voices (high quality)                       │
│       • Adjust speaking rate (0.9x for clarity)             │
│       • Generate audio stream                               │
└───────────────────────────┬─────────────────────────────────┘
                            │ Audio Response
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Audio Output (System Speakers)                 │
│              • Play response to user                        │
│              • Show text overlay on mirror (HUD)            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│       Action Execution (Task System Integration)            │
│       • Execute command (start task, advance step)          │
│       • Update UI (MagicMirror WebSocket broadcast)         │
│       • Log interaction for analytics                       │
└─────────────────────────────────────────────────────────────┘
```

## 📁 File Structure

```
backend/
├── voice_assistant.py          # Main voice assistant class
├── speech_recognition.py       # Speech-to-Text wrapper
├── text_to_speech.py           # Text-to-Speech wrapper
├── intent_classifier.py        # Intent parsing & NLU
├── context_manager.py          # Session context tracking
├── wake_word_detector.py       # Local wake word detection
└── audio_utils.py              # Audio I/O helpers (PyAudio)

config/
└── voice_assistant.json        # Voice assistant configuration

mirror/modules/MMM-AssistiveCoach/
├── voice_module.js             # Frontend voice UI
└── audio_visualizer.js         # Waveform/listening indicator
```

## 🔧 Implementation Plan

### Phase 1: Basic Speech-to-Text (Week 1)

- ✅ Set up Google Cloud project and credentials
- ✅ Implement `speech_recognition.py` with streaming STT
- ✅ Add microphone input via PyAudio
- ✅ Test transcription accuracy
- ✅ Add endpoint `POST /voice/transcribe`

### Phase 2: Text-to-Speech (Week 1)

- ✅ Implement `text_to_speech.py` with Neural2 voices
- ✅ Add audio playback via system speakers
- ✅ Integrate with existing `speak_text()` function
- ✅ Test voice quality and latency

### Phase 3: Intent Classification (Week 2)

- ✅ Design intent schema (start_task, stop_task, next_step, help, status)
- ✅ Implement rule-based classifier (regex patterns)
- ✅ Add entity extraction (task names, step numbers)
- ✅ Test with sample commands

### Phase 4: Gemini Integration (Week 2)

- ✅ Connect to Vertex AI Gemini API
- ✅ Implement context-aware prompting
- ✅ Add conversation history tracking
- ✅ Test response generation

### Phase 5: Wake Word Detection (Week 3)

- ✅ Implement local wake word detection (Porcupine or custom)
- ✅ Add continuous listening mode
- ✅ Optimize CPU usage (run on separate thread)
- ✅ Add visual indicator on mirror ("Listening...")

### Phase 6: Task Integration (Week 3)

- ✅ Connect voice commands to task system
- ✅ Add voice-triggered task start/stop
- ✅ Implement voice-guided step progression
- ✅ Test end-to-end flow

### Phase 7: Polish & Testing (Week 4)

- ✅ Add error handling and fallbacks
- ✅ Optimize latency (target <1s STT→TTS roundtrip)
- ✅ Add conversation history logging
- ✅ User testing and feedback collection

## 💻 Code Examples

### 1. Speech-to-Text (Streaming)

```python
# backend/speech_recognition.py
from google.cloud import speech_v1p1beta1 as speech
import pyaudio
import queue

class SpeechRecognizer:
    def __init__(self, language_code="en-US"):
        self.client = speech.SpeechClient()
        self.language_code = language_code
        self.audio_queue = queue.Queue()

    def listen_stream(self, callback):
        """Start streaming speech recognition"""
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=self.language_code,
            enable_automatic_punctuation=True,
            model="latest_long",  # Better for conversational speech
        )

        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=True,  # Show partial results
        )

        # Stream audio from microphone
        audio_generator = self._audio_generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=chunk)
            for chunk in audio_generator
        )

        responses = self.client.streaming_recognize(streaming_config, requests)

        for response in responses:
            for result in response.results:
                if result.is_final:
                    transcript = result.alternatives[0].transcript
                    callback(transcript)

    def _audio_generator(self):
        """Generate audio chunks from microphone"""
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1024,
        )

        try:
            while True:
                data = stream.read(1024, exception_on_overflow=False)
                yield data
        finally:
            stream.stop_stream()
            stream.close()
            audio.terminate()
```

### 2. Text-to-Speech

```python
# backend/text_to_speech.py
from google.cloud import texttospeech
import pyaudio

class TextToSpeech:
    def __init__(self, voice_name="en-US-Neural2-J"):
        self.client = texttospeech.TextToSpeechClient()
        self.voice_name = voice_name

    def speak(self, text: str, speed: float = 0.9):
        """Convert text to speech and play audio"""
        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=self.voice_name,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=speed,
            pitch=0.0,
        )

        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )

        # Play audio
        self._play_audio(response.audio_content)

    def _play_audio(self, audio_data: bytes):
        """Play audio data via system speakers"""
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=24000,
            output=True,
        )
        stream.write(audio_data)
        stream.stop_stream()
        stream.close()
        audio.terminate()
```

### 3. Intent Classifier

```python
# backend/intent_classifier.py
import re
from typing import Dict, Optional, List

class IntentClassifier:
    def __init__(self):
        self.intents = {
            "start_task": [
                r"start (.+)",
                r"begin (.+)",
                r"help me (.+)",
                r"i want to (.+)",
            ],
            "stop_task": [
                r"stop",
                r"cancel",
                r"quit",
                r"i'm done",
            ],
            "next_step": [
                r"next",
                r"continue",
                r"what's next",
                r"move on",
            ],
            "repeat": [
                r"repeat",
                r"say that again",
                r"what did you say",
            ],
            "help": [
                r"help",
                r"what can you do",
                r"how does this work",
            ],
            "status": [
                r"where am i",
                r"what step",
                r"progress",
                r"how much longer",
            ],
        }

        self.task_aliases = {
            "brush my teeth": "brush_teeth",
            "brushing teeth": "brush_teeth",
            "wash my face": "wash_face",
            "wash face": "wash_face",
            "comb my hair": "comb_hair",
            "comb hair": "comb_hair",
            "do my eyebrows": "draw_eyebrows",
            "draw eyebrows": "draw_eyebrows",
            "put on makeup": "draw_eyebrows",
        }

    def classify(self, text: str) -> Dict[str, any]:
        """Classify user intent from text"""
        text_lower = text.lower().strip()

        for intent, patterns in self.intents.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower)
                if match:
                    entities = self._extract_entities(intent, match, text_lower)
                    return {
                        "intent": intent,
                        "confidence": 0.95,  # High for regex matches
                        "entities": entities,
                        "raw_text": text,
                    }

        # No match - unknown intent
        return {
            "intent": "unknown",
            "confidence": 0.0,
            "entities": {},
            "raw_text": text,
        }

    def _extract_entities(self, intent: str, match: re.Match, text: str) -> Dict:
        """Extract entities from matched text"""
        entities = {}

        if intent == "start_task" and match.groups():
            task_phrase = match.group(1)
            task_id = self.task_aliases.get(task_phrase)
            if task_id:
                entities["task_id"] = task_id

        return entities
```

### 4. Gemini Response Generator

```python
# backend/voice_assistant.py
import vertexai
from vertexai.generative_models import GenerativeModel

class VoiceAssistant:
    def __init__(self, project_id: str, location: str = "us-central1"):
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel("gemini-1.5-flash")

    def generate_response(self, intent: dict, context: dict) -> str:
        """Generate contextual response using Gemini"""
        prompt = self._build_prompt(intent, context)

        response = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 150,
                "top_p": 0.9,
            },
        )

        return response.text.strip()

    def _build_prompt(self, intent: dict, context: dict) -> str:
        """Build context-aware prompt for Gemini"""
        system_context = """
You are an assistive voice coach for a smart mirror helping users with daily tasks.
You are encouraging, patient, and clear. Keep responses under 2 sentences.
Current context:
"""

        if context.get("current_task"):
            system_context += f"\n- User is working on: {context['current_task']['name']}"
            system_context += f"\n- Current step: {context['current_step']['title']}"
        else:
            system_context += "\n- No active task"

        user_intent = f"\nUser intent: {intent['intent']}"
        if intent.get("entities"):
            user_intent += f"\nEntities: {intent['entities']}"

        user_intent += f"\nUser said: '{intent['raw_text']}'"
        user_intent += "\n\nGenerate a helpful, encouraging response:"

        return system_context + user_intent
```

### 5. FastAPI Integration

```python
# backend/app.py (add these endpoints)

from backend.voice_assistant import VoiceAssistant
from backend.speech_recognition import SpeechRecognizer
from backend.text_to_speech import TextToSpeech
from backend.intent_classifier import IntentClassifier

# Initialize voice components
voice_assistant = VoiceAssistant(
    project_id=os.getenv("GOOGLE_CLOUD_PROJECT", "assistive-coach-ai")
)
speech_recognizer = SpeechRecognizer()
text_to_speech = TextToSpeech()
intent_classifier = IntentClassifier()

@app.post("/voice/command")
async def process_voice_command(audio_data: bytes = File(...)):
    """Process voice command from audio data"""
    # 1. Transcribe audio
    transcript = await speech_recognizer.transcribe_audio(audio_data)

    # 2. Classify intent
    intent = intent_classifier.classify(transcript)

    # 3. Get current context
    context = {
        "current_task": active_task_session.to_dict() if active_task_session else None,
        "current_step": active_task_session.get_current_step() if active_task_session else None,
    }

    # 4. Generate response
    response_text = voice_assistant.generate_response(intent, context)

    # 5. Execute action based on intent
    action_result = await execute_intent_action(intent)

    # 6. Synthesize speech
    audio_response = text_to_speech.synthesize(response_text)

    return {
        "transcript": transcript,
        "intent": intent,
        "response": response_text,
        "action_result": action_result,
        "audio": audio_response,  # Base64 encoded
    }

async def execute_intent_action(intent: dict):
    """Execute action based on classified intent"""
    if intent["intent"] == "start_task":
        task_id = intent["entities"].get("task_id")
        if task_id and task_id in TASKS:
            # Same logic as POST /tasks/{task_id}/start
            return await start_task_internal(task_id)

    elif intent["intent"] == "next_step":
        # Same logic as POST /tasks/next_step
        return await next_step_internal()

    elif intent["intent"] == "stop_task":
        # Same logic as POST /tasks/stop
        return await stop_task_internal()

    return {"status": "no_action"}
```

## 🎤 Voice Commands Reference

### Task Control

- **Start task**: "Hey Mirror, start brushing teeth"
- **Next step**: "Next" / "Continue" / "What's next?"
- **Stop**: "Stop" / "Cancel" / "I'm done"

### Help & Status

- **Help**: "Help" / "What can you do?"
- **Status**: "Where am I?" / "What step am I on?"
- **Repeat**: "Repeat that" / "Say that again"

### Natural Conversation

- **Questions**: "How do I do this?" / "Can you explain this step?"
- **Encouragement**: Voice responds: "You're doing great!" / "Almost there!"

## 🔒 Privacy & Security

### Audio Data Handling

1. **Local processing only** (optional mode):

   - Use offline STT (Vosk or Whisper.cpp)
   - No audio sent to cloud

2. **Minimal data retention**:

   - Don't store raw audio files
   - Only log transcripts (optional, user consent)
   - Delete conversation history after 24 hours

3. **User consent**:
   - Prompt for microphone permission on first use
   - Show "Listening" indicator when mic is active
   - Allow disabling voice features entirely

## 🚀 Next Steps

1. **Pull your Google Vertex changes** from your branch
2. **Review** the integration plan above
3. **Set up** Google Cloud project and credentials
4. **Install** Python dependencies
5. **Run** basic STT/TTS tests
6. **Integrate** with existing task system
7. **Test** end-to-end voice workflow

---

**Ready to integrate!** Let me know when you have the Vertex AI code ready and I'll help merge it with the existing system.
