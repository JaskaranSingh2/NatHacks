# voice_assistant.py
from gemini_assistant import GeminiAssistant
from speech_clients import TTS, STT
import logging

# TODO: unit tests, hardware integration tests
# TODO: double check costs for API calls (make sure rate limiting is ok?)

LOGGER = logging.getLogger("voice_assistant")


class VoiceAssistant:
    """
    overarching voice assistant pipeline
    audio -> text -> Gemini -> audio
    """

    def __init__(self, project_id: str, location: str = "us-central1", max_retries: int = 3):
        self.listener = STT()
        self.middleman = GeminiAssistant(project_id, location)
        self.speaker = TTS()
        self.enabled = False
        self.max_retries = max_retries
        
        if self.listener.enabled and self.middleman.enabled and self.speaker.enabled:
            self.enabled = True
        else:
            LOGGER.warning("VoiceAssistant created but some component(s) not enabled")

    def converse(self, audio_file: str, output_file: str = "response.mp3", play_audio: bool = True):
        """
        trasncribe audio, generate response w/ Gemini, speak text
        returns AI's text response
        """
        if not self.enabled:
            LOGGER.warning("VoiceAssistant disabled")
            return None
        
        # TRANSCRIPTION
        user_text = None
        for attempt in range(self.max_retries):
            try:
                user_text = self.listener.transcribe(audio_file)
                if user_text:
                    break
            except Exception as e:
                LOGGER.warning(f"STT failed attempt {attempt+1}: {e}")
        if not user_text:
            LOGGER.info(f"no speech detected in file named {audio_file}")
            return None

        # GENERATE RESPONSE
        ai_response = None
        for attempt in range(self.max_retries):
            try:
                ai_response = self.middleman.generate_text(user_text)
                if ai_response:
                    break
            except Exception as e:
                LOGGER.warning(f"Gemini failed attempt {attempt+1}: {e}")
        if not ai_response:
            LOGGER.warning("Gemini didn't generate a response")
            return None
        
        # SPEAK RESPONSE
        tts_response = None
        for attempt in range(self.max_retries):
            try:
                tts_response = self.speaker.synthesize(ai_response)
                if tts_response:
                    break
            except Exception as e:
                LOGGER.warning(f"TTS failed attempt {attempt+1}: {e}")
        if not tts_response:
            LOGGER.warning("TTS failed to generate audio")
            return ai_response

        # audio_path = self.speaker.writeAudioOutputToFile(tts_response, output_file) # TODO: add 2nd returned item as audio_path if we decide to work with this

        if play_audio:
            self.speaker.playAudioOutputLive(tts_response)

        return ai_response


