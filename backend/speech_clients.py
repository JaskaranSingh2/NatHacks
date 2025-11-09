from google.cloud import speech, texttospeech
from google.api_core.exceptions import GoogleAPICallError, DefaultCredentialsError
from pydub import AudioSegment
from pydub.playback import play
import io, logging, os
from collections import OrderedDict

# pip3 install google-cloud-speech google-cloud-texttospeech pydub

# TODO: verify caching is OK
# TODO: 2nd round of unit tests, hardware integration tests

LOGGER = logging.getLogger("speechclients")

class TTS:
    """
    Wrapper for Google TTS api
    text --> audio
    includes caching
    """
    def __init__(self, language_code="en-US", gender="NEUTRAL"):
        self.client = texttospeech.TextToSpeechClient()
        self.voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            ssml_gender=texttospeech.SsmlVoiceGender[gender]
        )
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        self.enabled = False
        self.fail_count = 0
        self.cache = OrderedDict()
        
        # handling errors in initialization
        try:
            self.client = texttospeech.TextToSpeechClient()
            self.enabled = True
            LOGGER.info("TTS initialized successfully")
        except DefaultCredentialsError as e:
            LOGGER.warning("TTS not initialized properly: {e}")
        except Exception as e:
            LOGGER.warning("TTS encountered unexpected error during initialization: {e}")
            

    def synthesize(self, text: str, retries=3, delay=0.5):
        """
        Converts text into speech and returns generated audio (to be saved to file or played live)
        """
        # initial validation
        if not self.enabled or not text:
            return None
        
        # check cache first
        if text in self.cache:
            self.cache[text] = response
            return self.cache[text][1]
        
        for attempt in range(retries):
            try:
                response = self.client.synthesize_speech(
                    input=texttospeech.SynthesisInput(text=text), 
                    voice=self.voice, 
                    audio_config=self.audio_config
                )
                self.cache[text] = response
                if len(self.cache) > 32:
                    self.cache.popitem(last=False)
                return response
            except GoogleAPICallError as e:
                LOGGER.warning(f"TTS failed during its {attempt+1}th attempt: {e}")
            except Exception as e:
                LOGGER.warning(f"TTS.synthesize() encounter unexpected error: {e}")
        return None

    def writeAudioOutputToFile(self, response, output_path: str = "output.mp3"):
        """
        save audio output of TTS.synthesize() to a file
        """
        with open(output_path, "wb") as out:
            out.write(response.audio_content)
        return output_path
    
    def playAudioOutputLive(self, response):
        """
        play audio output of TTS.synthesize() out loud without saving to file
        """
        audio_bytes = io.BytesIO(response.audio_content)
        sound = AudioSegment.from_file(audio_bytes, format="mp3")
        play(sound)




class STT:
    """
    Wrapper speech-to-text (STT) api
    audio --> text
    """

    def __init__(self, language_code="en-US", timeout_s=10.0, max_retries=3):
        self.enabled = False
        self.language_code = language_code
        self.cache = OrderedDict()
        self.timeout_s = timeout_s
        self.max_retries = max_retries
        
        try:
            self.client = speech.SpeechClient()
            self.enabled = True
            LOGGER.info("STT initialized successfully")
        except DefaultCredentialsError as e:
            self.client = None
            LOGGER.warning(f"STT not initialized properly: {e}")
        except Exception as e:
            self.client = None
            LOGGER.warning(f"STT encountered unexpected error during initialization: {e}")
            

    def transcribe(self, filename: str) -> str:
        """
        converts audio file to text via Google cloud speech
        """
        if not self.enabled:
            LOGGER.warning("STT disabled: no transcription")
            return None
        
        if not os.path.exists(filename):
            LOGGER.warning(f"STT: file named {filename} is not found")
            return None
        
        if filename in self.cache:
            return self.cache[filename]
        
        # actual transcription
        with open(filename, "rb") as audio_file:
            content = audio_file.read()
        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=self.language_code,
        )

        for attempt in range(self.max_retries):
            try:
                response = self.client.recognize(config=config, audio=audio)
                if not response.results:
                    return None
                result_text = response.results[0].alternatives[0].transcript.strip()
                self.cache[filename] = result_text
                return result_text
            except GoogleAPICallError as e:
                LOGGER.warning(f"STT.transcribe() failed attempt {attempt+1}: {e}")
            except Exception as e:
                LOGGER.warning(f"STT.transcribe() encountered unexpected error: {e}")
        
        return result_text
    
