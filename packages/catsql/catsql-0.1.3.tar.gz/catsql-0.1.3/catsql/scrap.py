class CsvRowWriter:
    def __init__(self, stream, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect,
                                 lineterminator='', **kwds)
        self.encoder = codecs.getincrementalencoder(encoding)()
        self.stream = stream

    def writerow(self, row):
        try:
            self.queue.truncate(0)
            self.writer.writerow([str(s).encode("utf-8") for s in row])
            # Fetch UTF-8 output from the queue ...
            data = self.queue.getvalue()
            data = data.decode("utf-8")
            # ... and reencode it into the target encoding
            data = self.encoder.encode(data)
            print(data, file=self.stream)
        except AttributeError:
            print("HELLO")
            self.writer.writerow(list(unicode(c) for c in row))
            data = self.queue.getvalue()
            print("'{}'".format(data))
            self.queue.truncate(0)
            data = self.queue.getvalue()
            print("'{}'".format(data))
            # python3
            pass
        return data

