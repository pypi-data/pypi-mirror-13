
from coralogix import CoralogixHTTPSHandler


class spider(object):

    def get_files(self):
        pass

    def weave(self):
        processes = list()
        for file in self.get_files():
            process = Process(target=self.spawn, args=(f,))
            processes.append(process)
            process.start()

    def spawn(self, filename):
        logger.info()
        tailer = Tailer(filename)
        tailor.watch()

if __name__ == "__main__":
    pass