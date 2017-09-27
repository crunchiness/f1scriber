import av


class AudioFrameIterable:
    def __init__(self, path):
        self.container = av.open(path)
        self.stream = next(s for s in self.container.streams if s.type == 'audio')

    def __iter__(self):
        for packet in self.container.demux(self.stream):
            for frame in packet.decode():
                yield frame
        raise StopIteration()


class AudioIterable:
    def __init__(self, path, output_chunk_size, output_rate, output_format='s16', output_layout='mono'):
        self.afi = AudioFrameIterable(path)
        self.chunk_size = output_chunk_size
        self.resampler = av.AudioResampler(
            format=av.AudioFormat(output_format).packed,
            layout=output_layout,
            rate=output_rate,
        )
        self.buffer = b''

    def __iter__(self):
        for frame in self.afi:
            new_frame = self.resampler.resample(frame)
            self.buffer += new_frame.planes[0].to_bytes()
            if len(self.buffer) >= self.chunk_size:
                chunk = self.buffer[:self.chunk_size]
                self.buffer = self.buffer[self.chunk_size:]
                yield chunk
        while len(self.buffer) > 0:
            chunk = self.buffer[:self.chunk_size]
            self.buffer = self.buffer[self.chunk_size:]
            yield chunk
        raise StopIteration()


audio_file_name = 'resources/output.aac'
# audio_file_name = 'http://radio.m-1.fm:80/m1/mp3'

ai = AudioIterable(audio_file_name, 32*1024, 16000)

with open('out.pcm', 'w') as f:
    for chunk in ai:
        f.write(chunk)
