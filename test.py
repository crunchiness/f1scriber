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


audio_file_name = 'resources/output.aac'
container = av.open(audio_file_name)
for frame in container.decode():
    print frame
# n = AudioIterable(audio_file_name, 32*1024)
# asdf = [len(chunk) for chunk in n]
# print asdf

# with io.open(audio_file_name, 'rb') as audio_file:
#     size = -1
#     while size != 0:
#         chunk = audio_file.read(32*1024)
#         size = len(chunk)
#         print type(chunk), size
