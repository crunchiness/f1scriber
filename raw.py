#!/usr/bin/env python

import argparse
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

from test import AudioIterable


def transcribe_streaming(stream_file):
    client = speech.SpeechClient()

    short_glossary_file = open('data/short_glossary.txt', 'r')
    short_glossary = map(lambda x: x.strip(), short_glossary_file.readlines())
    short_glossary_file.close()

    speech_context = types.SpeechContext(phrases=short_glossary)

    stream = AudioIterable(stream_file, 32 * 1024, 16000)
    requests = (types.StreamingRecognizeRequest(audio_content=chunk) for chunk in stream)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='en-GB',
        speech_contexts=[speech_context]
    )
    streaming_config = types.StreamingRecognitionConfig(config=config)

    # streaming_recognize returns a generator.
    # [START migration_streaming_response]
    responses = client.streaming_recognize(streaming_config, requests)

    for response in responses:
        for result in response.results:
            print('Finished: {}'.format(result.is_final))
            print('Stability: {}'.format(result.stability))
            alternatives = result.alternatives
            for alternative in alternatives:
                print('Confidence: {}'.format(alternative.confidence))
                print('Transcript: {}'.format(alternative.transcript))
                # [END migration_streaming_response]


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(
    #     description=__doc__,
    #     formatter_class=argparse.RawDescriptionHelpFormatter)
    # parser.add_argument('stream', help='File to stream to the API')
    # args = parser.parse_args()
    #
    audio_file_name = 'resources/output.aac'
    transcribe_streaming(audio_file_name)
