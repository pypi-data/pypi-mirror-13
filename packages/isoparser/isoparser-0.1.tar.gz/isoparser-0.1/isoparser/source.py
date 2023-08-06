import datetime
import struct
import urllib

import path_table
import record
import volume_descriptors


SECTOR_LENGTH = 2048


class SourceError(Exception):
    pass


class Source(object):
    def __init__(self):
        self._buff = None
        self._sectors = {}
        self.cursor = None

    def __len__(self):
        return len(self._buff) - self.cursor

    def unpack_raw(self, l):
        if l > len(self):
            raise SourceError("Source buffer under-run")
        data = self._buff[self.cursor:self.cursor + l]
        self.cursor += l
        return data

    def unpack_all(self):
        return self.unpack_raw(len(self))

    def unpack_boundary(self):
        return self.unpack_raw(SECTOR_LENGTH - (self.cursor % SECTOR_LENGTH))

    def unpack_both(self, st):
        a = self.unpack('<'+st)
        b = self.unpack('>'+st)
        if a != b:
            raise SourceError("Both-endian value mismatch")
        return a

    def unpack_string(self, l):
        return self.unpack_raw(l).rstrip(' ')

    def unpack(self, st):
        if st[0] not in '<>':
            st = '<' + st
        d = struct.unpack(st, self.unpack_raw(struct.calcsize(st)))
        if len(st) == 2:
            return d[0]
        else:
            return d

    def unpack_vd_datetime(self):
        return self.unpack_raw(17)  # TODO

    def unpack_dir_datetime(self):
        epoch = datetime.datetime(1970, 1, 1)
        date = self.unpack_raw(7)
        t = [struct.unpack('<B', i)[0] for i in date[:-1]]
        t.append(struct.unpack('<b', date[-1])[0])
        t[0] += 1900
        t_offset = t.pop(-1) * 15 * 60.    # Offset from GMT in 15min intervals, converted to secs
        t_timestamp = (datetime.datetime(*t) - epoch).total_seconds() - t_offset
        t_datetime = datetime.datetime.fromtimestamp(t_timestamp)
        t_readable = t_datetime.strftime('%Y-%m-%d %H:%M:%S')
        return t_readable

    def unpack_volume_descriptor(self):
        ty = self.unpack('B')
        identifier = self.unpack_string(5)
        version = self.unpack('B')

        if identifier != "CD001":
            raise SourceError("Wrong volume descriptor identifier")
        if version != 1:
            raise SourceError("Wrong volume descriptor version")
        
        if ty == 0:
            vd = volume_descriptors.BootVD(self)
        elif ty == 1:
            vd = volume_descriptors.PrimaryVD(self)
        elif ty == 2:
            vd = volume_descriptors.SupplementaryVD(self)
        elif ty == 3:
            vd = volume_descriptors.PartitionVD(self)
        elif ty == 255:
            vd = volume_descriptors.TerminatorVD(self)
        else:
            raise SourceError("Unknown volume descriptor type: %d" % ty)
        return vd

    def unpack_path_table(self):
        return path_table.PathTable(self)

    def unpack_record(self):
        length = self.unpack('B')
        if length == 0:
            return None
        return record.Record(self, length-1)

    def seek(self, start_sector, length=SECTOR_LENGTH):
        self.cursor = 0
        self._buff = ""
        n_sectors = 1 + (length - 1) // SECTOR_LENGTH
        for sector in range(start_sector, start_sector + n_sectors):
            data = self._sectors.get(sector)
            if data is None:
                data = self._fetch(sector)
                self._sectors[sector] = data
            self._buff += data
        self._buff = self._buff[:length]

    def _fetch(self, sector):
        raise NotImplementedError


class FileSource(Source):
    def __init__(self, path):
        super(FileSource, self).__init__()
        self._file = open(path, 'rb')

    def _fetch(self, sector):
        self._file.seek(sector*SECTOR_LENGTH)
        return self._file.read(SECTOR_LENGTH)


class HTTPSource(Source):
    def __init__(self, url):
        super(HTTPSource, self).__init__()
        self._url = url

    def _fetch(self, sector):
        opener = urllib.FancyURLopener()
        opener.http_error_206 = lambda *a, **k: None
        opener.addheader("Range", "bytes=%d-%d" % (
            SECTOR_LENGTH * sector,
            SECTOR_LENGTH * (sector + 1) - 1))
        return opener.open(self._url).read()