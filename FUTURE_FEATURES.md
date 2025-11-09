# Potential Future Features for AssistiveCoach

## 🎯 Core Vision Enhancements

### 1. **Automatic Task Progression**

**Status**: Foundation exists, needs integration

- **Current**: Manual step advancement (press 'N' key)
- **Future**: Auto-advance when vision confirms step completion
  - Detect ArUco marker for required step → advance automatically
  - Hand motion validation → confirm action performed
  - Example: Brushing teeth - detect toothbrush marker + hand motion → auto-advance

**Implementation**:

- Add `validate_step_completion()` in `task_system.py`
- Connect vision pipeline ArUco detection to task session
- Broadcast step completion events via WebSocket

### 2. **Gaze Tracking**

**Technology**: MediaPipe Face Mesh (468 landmarks include iris)

- Track where user is looking on mirror
- Highlight UI elements user is gazing at
- Voice confirmation: "Looking at Brush Teeth task?"
- **Accessibility Win**: Hands-free navigation

**Implementation**:

- Extract iris landmarks (474-478) from face mesh
- Calculate gaze vector using PnP with camera intrinsics
- Map gaze to screen coordinates
- Add `gaze_highlight` overlay type

### 3. **Gesture Controls**

**Technology**: MediaPipe Hands (21 keypoints)

- Recognize hand gestures for control
  - 👍 Thumbs up → Start task
  - ✋ Open palm → Pause
  - 👌 OK sign → Next step
  - ✊ Fist → Stop
- **Accessibility Win**: Control without keyboard/voice

**Implementation**:

- Add `gesture_recognizer.py` with landmark-based classifiers
- Use hand angles and distances to classify gestures
- Map gestures to keyboard shortcuts (1-4, T, N, S)

### 4. **Object Detection for Task Items**

**Technology**: YOLOv8 Nano (runs on Pi 5)

- Detect task-related objects:
  - Toothbrush, toothpaste, towel, comb, makeup items
- Validate user has correct items before starting task
- Guide user: "I don't see a toothbrush. Please place it in view"

**Implementation**:

- Train YOLOv8-nano on ADL objects dataset
- Run inference at low FPS (5-10 Hz) to save CPU
- Add `required_objects` field to TaskStep
- Validate objects present before allowing step advancement

### 5. **Posture Analysis**

**Technology**: MediaPipe Pose (33 body landmarks)

- Detect if user is:
  - Standing too close/far from mirror
  - Slouching (poor posture)
  - Off-center
- Provide gentle corrections: "Please step back a bit"

**Implementation**:

- Add MediaPipe Pose to vision pipeline (already has face/hands)
- Calculate body centerline, shoulder alignment
- Trigger alerts for poor posture
- Helpful for accessibility users

## 🗣️ Voice & Audio Features

### 6. **Google Vertex AI Voice Assistant** 🔥

**Status**: Ready to integrate with your upcoming changes

- **Natural language task selection**: "Hey mirror, help me brush my teeth"
- **Conversational guidance**: User can ask questions during tasks
- **Context-aware responses**: Assistant knows current task step

**Integration Plan**:

```python
# backend/voice_assistant.py
from google.cloud import aiplatform

class VertexVoiceAssistant:
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.client = aiplatform.gapic.PredictionServiceClient()
        self.endpoint = f"projects/{project_id}/locations/{location}/endpoints/..."

    def process_voice_command(self, audio_data: bytes) -> dict:
        # 1. Speech-to-text (Vertex AI Speech API)
        text = self.transcribe_audio(audio_data)

        # 2. Intent classification (Vertex AI custom model or Gemini)
        intent = self.classify_intent(text)

        # 3. Generate response based on context
        response = self.generate_response(intent, self.get_context())

        # 4. Text-to-speech
        audio_response = self.synthesize_speech(response)

        return {"text": response, "audio": audio_response, "action": intent}

    def get_context(self) -> dict:
        # Return current task state, user preferences, etc.
        return {
            "current_task": active_task_session.task_id if active_task_session else None,
            "step": active_task_session.current_step if active_task_session else None,
            "user_profile": ...,
        }
```

**Features**:

- Wake word detection: "Hey Mirror" or "Hey Coach"
- Voice task selection: "Start brushing teeth"
- Mid-task questions: "What's next?" "How do I do this?"
- Encouragement: "You're doing great!" "Almost done!"

### 7. **Ambient Sound Detection**

**Technology**: TensorFlow Lite Audio (YAMNet)

- Detect sounds relevant to tasks:
  - Running water (washing face)
  - Toothbrush electric hum
  - Door opening/closing
- Use as validation signals for step completion

### 8. **Multi-language Support**

- TTS in multiple languages (macOS `say` supports 30+ languages)
- UI text translation via i18n
- Voice commands in user's preferred language

## 🎨 UI/UX Enhancements

### 9. **Customizable Themes**

**Current**: `high-contrast` theme hardcoded
**Future**:

- Multiple theme presets (pastel, dark, colorblind-friendly)
- User-adjustable font size, color, animation speed
- Settings panel accessible via voice/keyboard

### 10. **Progress Gamification**

- Track task completion history
- Award badges for milestones:
  - 🏆 "Brushing Master" - 30 days of brushing
  - 🌟 "Morning Routine Pro" - Complete all 4 tasks in sequence
- Show progress calendar on mirror

### 11. **Adaptive Difficulty**

- Beginner mode: More hints, slower pace, extra guidance
- Expert mode: Minimal UI, faster transitions
- Auto-adjust based on user performance

### 12. **Multi-user Profiles**

- Face recognition to identify user
- Load personalized settings, task history
- "Welcome back, Sarah! Ready to start your morning routine?"

## 🔧 System & Integration

### 13. **Smartphone Companion App**

- Mobile app to:
  - Configure mirror remotely
  - View task history and progress
  - Create custom tasks
  - Update settings without standing at mirror
- Sync via cloud or local WiFi

### 14. **Smart Home Integration**

- **Google Home/Alexa**: Voice control
- **Philips Hue**: Adjust lighting during tasks
- **Smart scale**: Track weight, integrate with health tasks
- **Smart toothbrush**: Sync brushing data

### 15. **Cloud Sync & Backup**

- Store task history in cloud (Firebase, Supabase)
- Sync settings across devices
- Analytics dashboard: "You brushed 28/30 days this month!"

### 16. **Caregiver Dashboard**

- Remote monitoring for elderly/disabled users
- Alerts if tasks not completed
- Video check-ins via mirror
- Medication reminders

## 🧠 AI/ML Advanced Features

### 17. **Personalized Coaching**

**Technology**: Fine-tuned LLM (Gemini or GPT-4)

- Learn user's patterns and preferences
- Offer personalized tips:
  - "You usually skip combing your hair on Mondays. Want a reminder?"
  - "You're faster at brushing in the evening. Try morning sessions at 7:30?"
- Adapt guidance based on success rate

### 18. **Anomaly Detection**

- Detect unusual behavior patterns:
  - User skips tasks for multiple days
  - Tasks take much longer than usual
  - User appears distressed (facial expression analysis)
- Send alerts to caregiver or medical professional

### 19. **Predictive Recommendations**

- ML model predicts which tasks user will struggle with
- Offers proactive help before user gets stuck
- Learns from feedback loop

### 20. **Vision-based Skill Assessment**

- Analyze technique quality:
  - "Your brushing motion is good, but try reaching the back teeth more"
  - "Great job on the eyebrow symmetry!"
- Provide technique improvement suggestions

## 🌐 Accessibility & Inclusion

### 21. **Screen Reader Integration**

- Full ARIA labels on all UI elements
- Announce task steps and progress
- Compatible with JAWS, NVDA, VoiceOver

### 22. **Cognitive Accessibility**

- Simplified language mode
- Pictorial instructions (more images, less text)
- Timer with visual countdown (not just seconds)

### 23. **Motor Accessibility**

- Larger hit targets for UI elements
- Longer timeout for responses
- Switch control support (single-button navigation)

### 24. **Sensory Accommodations**

- High contrast mode (already implemented)
- Reduced motion (already implemented via `prefers-reduced-motion`)
- Audio descriptions of visual content
- Haptic feedback (vibration via paired phone)

## 📊 Analytics & Insights

### 25. **Health Metrics Integration**

- Connect to fitness trackers (Fitbit, Apple Watch)
- Correlate task completion with health data
- "Your brushing routine improved after better sleep!"

### 26. **Performance Analytics**

- Track completion times, success rates
- Identify bottlenecks: "Step 3 always takes 2x longer"
- Suggest optimizations

### 27. **A/B Testing Framework**

- Test different UI layouts, voice prompts
- Measure which versions improve completion rates
- Auto-select best performing variants

## 🚀 Deployment & Scaling

### 28. **Raspberry Pi 5 Optimization**

- Leverage Pi 5's quad-core A76 CPU
- Use hardware H.264 encoder for video streaming
- Optimize memory usage (8GB model)

### 29. **Edge TPU Support**

- Google Coral USB Accelerator for ML inference
- 10x faster pose/hand detection
- Enable more complex models (YOLOv8, custom classifiers)

### 30. **Docker Containerization**

- Dockerize backend + frontend
- Easy deployment: `docker-compose up`
- Include all dependencies (OpenCV, MediaPipe, TF)

## 🎓 Learning & Tutorials

### 31. **Interactive Onboarding**

- Guided tour when user first uses mirror
- Explain each feature with live demo
- Practice task with real-time feedback

### 32. **Video Tutorials**

- Embedded video clips for complex steps
- "Watch how to do this step" button
- Picture-in-picture playback

### 33. **Skill Building Mode**

- Practice mode without time pressure
- Repeat steps until comfortable
- "Master a skill" mini-games

## 🔒 Privacy & Security

### 34. **Local Processing Only**

- Option to disable all cloud features
- All ML inference on-device
- No video/audio uploaded

### 35. **Encrypted Data Storage**

- Encrypt task history and user settings
- Secure API endpoints with JWT auth
- HIPAA-compliant mode for healthcare settings

## Summary: Implementation Priority

### 🔥 **High Priority** (Next 1-2 Months)

1. ✅ Google Vertex AI Voice Assistant (you're pulling this!)
2. Automatic task progression (ArUco validation)
3. Gesture controls (hands-free)
4. Multi-user profiles (face recognition)

### 🌟 **Medium Priority** (3-6 Months)

5. Object detection (task item validation)
6. Gaze tracking (accessibility)
7. Progress gamification (engagement)
8. Smartphone companion app

### 🚀 **Long-term** (6-12 Months)

9. Smart home integration
10. Caregiver dashboard
11. Predictive coaching with fine-tuned LLM
12. Edge TPU optimization

---

**All of these features build on the solid foundation you've created!** The OpenCV integration, task system, and WebSocket architecture make these additions straightforward to implement.
