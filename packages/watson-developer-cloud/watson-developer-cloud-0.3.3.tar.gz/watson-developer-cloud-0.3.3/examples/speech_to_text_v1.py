import json
from os.path import join, dirname
from watson_developer_cloud import SpeechToTextV1 as SpeechToText


speech_to_text = SpeechToText(username='YOUR SERVICE USERNAME',
                              password='YOUR SERVICE PASSWORD')

print(json.dumps(speech_to_text.models(), indent=2))

with open(join(dirname(__file__), '../resources/speech.wav'), 'rb') as audio_file:
    print(json.dumps(speech_to_text.recognize(audio_file,
                                              content_type='audio/wav'), indent=2))
