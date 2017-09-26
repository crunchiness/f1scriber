import io
import av


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


class AudioIterable2:
    def __init__(self, path):
        self.container = av.open(path)
        self.stream = next(s for s in self.container.streams if s.type == 'audio')

    def __iter__(self):
        for packet in self.container.demux(self.stream):
            for frame in packet.decode():
                yield frame
        raise StopIteration()


audio_file_name = 'resources/output.aac'
# audio_file_name = 'http://radio.m-1.fm:80/m1/mp3'

ai = AudioIterable2(audio_file_name)

resampler = av.AudioResampler(
    format=av.AudioFormat('s16').packed,
    layout='mono',
    rate=16000,
)

data = b''


def send(smth):
    print len(smth)


for i, frame in enumerate(ai):
    fram = resampler.resample(frame)
    data += fram.planes[0].to_bytes()
    if len(data) > 32*1024:
        send(data[:32*1024])
        data = data[32*1024:]
if len(data) > 0:
    send(data[:32 * 1024])
    data = data[32 * 1024:]

