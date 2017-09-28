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
    def __init__(self, path, output_chunk_size, output_rate, realtime=True, time_limit=None, output_format='s16', output_layout='mono'):
        """

        :type path: str
        :type output_chunk_size: int
        :type output_rate: int
        :type realtime: bool
        :type time_limit: float
        """
        if output_format != 's16':
            raise NotImplementedError('output_format {} is not supported.'.format(output_format))
        if output_layout != 'mono':
            raise NotImplementedError('output_layout {} is not supported.'.format(output_layout))

        self._realtime = realtime
        self._chunk_size = output_chunk_size
        self._time_limit = time_limit
        self._bit_rate = output_rate * 16
        self._chunk_duration = output_chunk_size * 8 / self._bit_rate

        self._afi = AudioFrameIterable(path)
        self._resampler = av.AudioResampler(
            format=av.AudioFormat(output_format).packed,
            layout=output_layout,
            rate=output_rate,
        )

        self._buffer = b''
        self._timestamp = 0
        self._duration_processed = 0

    def __iter__(self):
        for frame in self._afi:
            new_frame = self._resampler.resample(frame)
            self._buffer += new_frame.planes[0].to_bytes()
            if len(self._buffer) >= self._chunk_size:
                chunk = self._buffer[:self._chunk_size]
                self._buffer = self._buffer[self._chunk_size:]
                if self._realtime:
                    self.__wait()
                if self._time_limit is not None:
                    self.__cap()
                yield chunk
        while len(self._buffer) > 0:
            chunk = self._buffer[:self._chunk_size]
            self._buffer = self._buffer[self._chunk_size:]
            if self._realtime:
                self.__wait()
            if self._time_limit is not None:
                self.__cap()
            yield chunk
        raise StopIteration()

    def __wait(self):
        now = time.time()
        if now - self._timestamp < self._chunk_duration:
            time.sleep(self._chunk_duration - (now - self._timestamp))
        self._timestamp = time.time()

    def __cap(self):
        if self._duration_processed >= self._time_limit:
            raise StopIteration()
        self._duration_processed += self._chunk_duration

    @property
    def is_realtime(self):
        return self._realtime

    @property
    def bit_rate(self):
        return self._bit_rate


# audio_file_name = 'resources/output.aac'
# # audio_file_name = 'http://radio.m-1.fm:80/m1/mp3'
#
# ai = AudioIterable(audio_file_name, 32 * 1024, 16000)
# print 'bit_rate', ai.bit_rate, 'kbps'
# print 'chunk_length', ai._chunk_duration, 's'
#
# with open('out.pcm', 'w') as f:
#     for chunk in ai:
#         f.write(chunk)

