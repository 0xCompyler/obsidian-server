import os
import json
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import SpeechToTextV1
from moviepy.editor import VideoFileClip
from ibm_watson.websocket import RecognizeCallback

#! Initialize STT Model

try:
    with open('speechtotext.json', 'r') as credentialsFile:
            credentials1 = json.loads(credentialsFile.read())
            STT_API_KEY_ID = credentials1.get('apikey')
            STT_URL = credentials1.get('url')

except json.decoder.JSONDecodeError:
    print("Speech to text credentials file is empty, please enter the credentials and try again.")
    exit()

STT_language_model = "Earnings call language model"
STT_acoustic_model = "Earnings call acoustic model"

authenticator = IAMAuthenticator(STT_API_KEY_ID)
speech_to_text_client = SpeechToTextV1(
    authenticator=authenticator
)
speech_to_text_client.set_service_url(STT_URL)


def video_to_audio(video_path: str):
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile("DUMP/temp.mp3")

    myFlag = {"flag": 1}
    return json.dumps(myFlag, indent=2)


class MyRecognizeCallback(RecognizeCallback):
    def __init__(self):
        RecognizeCallback.__init__(self)

    def on_data(self, data):
        print(json.dumps(data, indent=2))

    def on_error(self, error):
        print('Error received: {0}'.format(error))

    def on_inactivity_timeout(self, error):
        print('Inactivity timeout: {0}'.format(error))


myRecognizeCallback = MyRecognizeCallback()


def speech_to_text():
    fileName = "DUMP/temp.mp3"
    filename_converted = fileName.replace(
        " ", "-").replace("'", "").lower()
    print("Processing ...\n")
    with open("DUMP/temp.mp3", 'rb') as audio_file:
        speech_recognition_results = speech_to_text_client.recognize(
                    audio=audio_file,
                    content_type='audio/mp3',
                    recognize_callback=myRecognizeCallback,
                    model='en-US_BroadbandModel',
                    keywords=['redhat', 'data and AI', 'Linux', 'Kubernetes'],
                    keywords_threshold=0.5,
                    timestamps=True,
                    speaker_labels=True,
                    word_alternatives_threshold=0.9
                ).get_result()

    
    transcript = ''
    for chunks in speech_recognition_results['results']:
        if 'alternatives' in chunks.keys():
            alternatives = chunks['alternatives'][0]
            if 'transcript' in alternatives:
                transcript = transcript + \
                    alternatives['transcript']
                transcript += '\n'

    with open('transcribe.txt', "w") as text_file:
        text_file.write(transcript.replace("%HESITATION", ""))

    speakerLabels = speech_recognition_results["speaker_labels"]
    print("Done Processing ...\n")
    extractedData = []
    for i in speech_recognition_results["results"]:
        if i["word_alternatives"]:
            mydict = {'from': i["word_alternatives"][0]["start_time"], 'transcript': i["alternatives"]
                        [0]["transcript"].replace("%HESITATION", ""), 'to': i["word_alternatives"][0]["end_time"]}
            extractedData.append(mydict)

    finalOutput = []
    finalOutput.append({"filename": filename_converted.split('.')[0] +'.txt'})
    for i in extractedData:
        for j in speakerLabels:
            if i["from"] == j["from"] and i["to"] == j["to"]:
                mydictTemp = {"from": i["from"],
                                "to": i["to"],
                                "transcript": i["transcript"],
                                "speaker": j["speaker"],
                                "confidence": j["confidence"],
                                "final": j["final"],
                                }
                finalOutput.append(mydictTemp)
    os.remove("DUMP/temp.mp3")
    return finalOutput




if __name__ == '__main__':
    video_to_audio("/Users/arijitroy/Projects/quartz/DUMP/Amethyst.mp4")
    print(speech_to_text())