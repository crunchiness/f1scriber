import av
import time


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
    def __init__(self, path, output_chunk_size, output_rate, realtime=True, output_format='s16', output_layout='mono'):
        if output_format != 's16':
            raise NotImplementedError('output_format {} is not supported.'.format(output_format))
        if output_layout != 'mono':
            raise NotImplementedError('output_layout {} is not supported.'.format(output_layout))
        self.realtime = realtime
        self.afi = AudioFrameIterable(path)
        self.chunk_size = output_chunk_size
        self.resampler = av.AudioResampler(
            format=av.AudioFormat(output_format).packed,
            layout=output_layout,
            rate=output_rate,
        )
        self.buffer = b''
        self.timestamp = 0
        self.bit_rate = output_rate * 16
        self.chunk_length = output_chunk_size * 8 / self.bit_rate
        self.time_limit = 60
        self.chunk_time = 0

    def __iter__(self):
        for frame in self.afi:
            new_frame = self.resampler.resample(frame)
            self.buffer += new_frame.planes[0].to_bytes()
            if len(self.buffer) >= self.chunk_size:
                chunk = self.buffer[:self.chunk_size]
                self.buffer = self.buffer[self.chunk_size:]
                if self.realtime:
                    self.__wait()
                self.__cap()
                yield chunk
        while len(self.buffer) > 0:
            chunk = self.buffer[:self.chunk_size]
            self.buffer = self.buffer[self.chunk_size:]
            if self.realtime:
                self.__wait()
            self.__cap()
            yield chunk
        raise StopIteration()

    def __wait(self):
        now = time.time()
        if now - self.timestamp < self.chunk_length:
            time.sleep(self.chunk_length - (now - self.timestamp))
        self.timestamp = time.time()
        print self.chunk_time

    def __cap(self):
        if self.chunk_time >= self.time_limit:
            raise StopIteration()
        self.chunk_time += self.chunk_length

#
# audio_file_name = 'resources/output.aac'
# # audio_file_name = 'http://radio.m-1.fm:80/m1/mp3'
#
# ai = AudioIterable(audio_file_name, 32 * 1024, 16000)
# print 'bit_rate', ai.bit_rate, 'kbps'
# print 'chunk_length', ai.chunk_length, 's'
#
# with open('out.pcm', 'w') as f:
#     for chunk in ai:
#         f.write(chunk)

