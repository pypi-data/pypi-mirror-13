import pyaudio
import requests


class TtsWatson:
    RATE = 22050
    SAMPWIDTH = 2
    NCHANNELS = 1
    ACCEPT = 'audio/wav'

    def __init__(self, user, password, voice='en-US_AllisonVoice',
                 url='https://stream.watsonplatform.net/text-to-speech/api', chunk=2048):
        self.user = user
        self.password = password
        self.voice = voice
        self.url = url
        self.chunk = int(chunk)

    def play(self, text):
        print "Transform '" + str(text) + "' into sound"
        req = requests.get(self.url + "/v1/synthesize",
                           auth=(self.user, self.password),
                           params={'text': text, 'voice': self.voice, 'accept': self.ACCEPT},
                           stream=True, verify=False
                           )
        p = pyaudio.PyAudio()

        stream = p.open(format=p.get_format_from_width(self.SAMPWIDTH),
                        channels=self.NCHANNELS,
                        rate=self.RATE,
                        output=True)
        bytesRead = 0
        dataToRead = ''
        for data in req.iter_content(1):
            dataToRead += data
            bytesRead += 1
            if bytesRead % self.chunk == 0:
                stream.write(dataToRead)
                dataToRead = ''
        stream.stop_stream()
        stream.close()
        p.terminate()
        print "Text: '" + str(text) + "' has been transformed !"
