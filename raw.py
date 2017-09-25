#!/usr/bin/env python

import argparse
import io
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types


class AudioIterable:
    def __init__(self, path, chunk_size):
        self.path = path
        self.chunk_size = chunk_size

    def __iter__(self):
        with io.open(self.path, 'rb') as audio_file:
            while True:
                chunk = audio_file.read(self.chunk_size)
                if len(chunk) > 0:
                    yield chunk
                else:
                    raise StopIteration()


def transcribe_streaming(stream_file):
    client = speech.SpeechClient()

    stream = AudioIterable(stream_file, 32 * 1024)
    requests = (types.StreamingRecognizeRequest(audio_content=chunk) for chunk in stream)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='en-US')
    streaming_config = types.StreamingRecognitionConfig(config=config)

    # streaming_recognize returns a generator.
    # [START migration_streaming_response]
    responses = client.streaming_recognize(streaming_config, requests)
    # [END migration_streaming_request]
    print responses
    for response in responses:
        for result in response.results:
            print('Finished: {}'.format(result.is_final))
            print('Stability: {}'.format(result.stability))
            alternatives = result.alternatives
            for alternative in alternatives:
                print('Confidence: {}'.format(alternative.confidence))
                print('Transcript: {}'.format(alternative.transcript))
                # [END migration_streaming_response]


    # [END def_transcribe_streaming]


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(
    #     description=__doc__,
    #     formatter_class=argparse.RawDescriptionHelpFormatter)
    # parser.add_argument('stream', help='File to stream to the API')
    # args = parser.parse_args()
    #
    audio_file_name = 'resources/output.aac'
    transcribe_streaming(audio_file_name)
