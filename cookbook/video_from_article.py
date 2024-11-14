from mosaico.audio_transcribers.assemblyai import AssemblyAIAudioTranscriber
from mosaico.script_generators.news import NewsVideoScriptGenerator
from mosaico.speech_synthesizers.elevenlabs import ElevenLabsSpeechSynthesizer
from mosaico.video.project import VideoProject, VideoProjectConfig


# Setup
### Note: To deal with AI, see cookbooks at AI section.
script_generator = NewsVideoScriptGenerator(
    context="breaking news text...", api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL
)

speech_synthesizer = ElevenLabsSpeechSynthesizer(
    api_key=ELEVENLABS_API_KEY,
    voice_id="Xb7hH8MSUJpSbSDYk0k2",
    voice_stability=0.8,
    voice_similarity_boost=0.75,
    voice_speaker_boost=False,
)

# Create assets
images = [...]  # List of image Assets

audio_transcriber = AssemblyAIAudioTranscriber(api_key=ASSEMBLYAI_API_KEY)
config = VideoProjectConfig(name="Breaking News")
project = VideoProject.from_script_generator(
    script_generator,
    images,
    config=config,
    speech_synthesizer=speech_synthesizer,
    audio_transcriber=audio_transcriber,
)
