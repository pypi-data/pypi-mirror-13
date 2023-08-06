#!/usr/bin/env python3
import sys
from csv import DictReader, DictWriter

# from "man 8 bonnie++"
# Data volumes for the 80 column text display use
# "K" for KiB (1024 bytes),
# "M" for MiB (1048576 bytes),
# and "G" for GiB (1073741824 bytes).
# So K/sec means a multiple of 1024 bytes per second.

class intByte(int):
    _units = ('G', 'M', 'K', 'B')
    def __new__(cls, *args, **kwargs):
        if len(args):
            if isinstance(args[0], str):
                value = super(intByte, cls).__new__(cls, args[0][:-1], **kwargs)
                unit = args[0][-1:]
                for i, x in enumerate(cls._units):
                    if unit == cls._units[len(cls._units)-1]:
                        break
                    if unit == x:
                        value *= 1024
                        unit = cls._units[i+1]
            else:
                value = args[0]
        return super(intByte, cls).__new__(cls, value, **kwargs)

    def __str__(self):
        val = self
        for unit in reversed(self._units):
            # bonnie++ does not print values with exponent (15696M does not output as 15.32G)
            if unit == self._units[len(self._units)-1] or val < 1024 or (val/1024 - int(val/1024)) > 0.0:
                return '%d%s' % (val, unit)
            val /= 1024

class intMicroseconds(int):
    _units = ('ms', 'us')
    def __new__(cls, *args, **kwargs):
        if len(args) > 0:
            if isinstance(args[0], str):
                value = super(intMicroseconds, cls).__new__(cls, args[0][:-2], **kwargs)
                unit = args[0][-2:]
                for i, x in enumerate(cls._units):
                    if unit == cls._units[len(cls._units)-1]:
                        break
                    if unit == x:
                        value *= 1000
                        unit = cls._units[i+1]
            else:
                value = args[0]
        return super(intMicroseconds, cls).__new__(cls, value, **kwargs)

    def __str__(self):
        val = self
        for unit in reversed(self._units):
            if unit == self._units[len(self._units)-1] or val < 100000:
                return '%d%s' % (val, unit)
            val /= 1000
        
class roundFloat(float):
    def __str__(self):
        return format(self, '.1f')

FIELDS = (
    ('format_version', str, False),
    ('bonnie_version', str, False),
    ('name', str, False),
    ('concurrency', int, False),
    ('seed', int, False),
    ('file_size', intByte, False),
    ('io_chunk_size', int, False), #TODO
    ('putc', int, True),
    ('putc_cpu', int, True),
    ('put_block', int, True),
    ('put_block_cpu', int, True),
    ('rewrite', int, True),
    ('rewrite_cpu', int, True),
    ('getc', int, True),
    ('getc_cpu', int, True),
    ('get_block', int, True),
    ('get_block_cpu', int, True),
    ('seeks', roundFloat, True),
    ('seeks_cpu', int, True),
    ('num_files', int, True),
    ('max_size', int, True), #TODO
    ('min_size', int, True), #TODO
    ('num_dirs', int, True), #TODO
    ('file_chunk_size', int, True), #TODO
    ('seq_create', int, True),
    ('seq_create_cpu', int, True),
    ('seq_stat', int, True),
    ('seq_stat_cpu', int, True),
    ('seq_del', int, True),
    ('seq_del_cpu', int, True),
    ('ran_create', int, True),
    ('ran_create_cpu', int, True),
    ('ran_stat', int, True),
    ('ran_stat_cpu', int, True),
    ('ran_del', int, True),
    ('ran_del_cpu', int, True),
    ('putc_latency', intMicroseconds, True),
    ('put_block_latency', intMicroseconds, True),
    ('rewrite_latency', intMicroseconds, True),
    ('getc_latency', intMicroseconds, True),
    ('get_block_latency', intMicroseconds, True),
    ('seeks_latency', intMicroseconds, True),
    ('seq_create_latency', intMicroseconds, True),
    ('seq_stat_latency', intMicroseconds, True),
    ('seq_del_latency', intMicroseconds, True),
    ('ran_create_latency', intMicroseconds, True),
    ('ran_stat_latency', intMicroseconds, True),
    ('ran_del_latency', intMicroseconds, True),
)

FIELDNAMES = []
FIELDTYPES = []
AVG_FIELDS = []
for n, t, a in FIELDS:
    FIELDNAMES.append(n)
    FIELDTYPES.append(t)
    if a:
        AVG_FIELDS.append((n, t))

class BonnieDictReader(DictReader):
    def __init__(self, f):
        super(BonnieDictReader, self).__init__(f, fieldnames=FIELDNAMES, restkey=None, restval=None, dialect='excel')
    
    def __next__(self):
        d = super(BonnieDictReader, self).__next__()
        if all([k == v for k, v in d.items()]):
            # Values and keys are equal, this is a header line so read the next
            d = super(BonnieDictReader, self).__next__()

        if len(FIELDTYPES) >= len(d):
            # extract the values in the same order as the csv header
            ivalues = map(d.get, self._fieldnames) 
            # apply type conversions
            iconverted = []
            for x, y in zip(FIELDTYPES, ivalues):
                if y in ('', '+++++', '++++', '+++'):
                    # don't convert
                    iconverted.append(y)
                else:
                    iconverted.append(x(y))
            ivonverted = tuple(iconverted)

            # pass the field names and the converted values to the dict constructor
            d = dict(zip(self._fieldnames, iconverted)) 
        return d

class BonnieDictWriter(DictWriter):
    def __init__(self, f):
        super(BonnieDictWriter, self).__init__(f, fieldnames=FIELDNAMES, restval=None, dialect='excel')


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Average sets of bonnie++ test results.')
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    args = parser.parse_args()

    groupedRows = {}
    source_data = BonnieDictReader(args.infile)
    for r in source_data:
        if not r['name'] in groupedRows:
            groupedRows[r['name']] = []
        groupedRows[r['name']].append(r)

    csvout = BonnieDictWriter(args.outfile)
    for name, groupRows in groupedRows.items():
        if len(groupRows) <= 1:
            # Not enough rows in this group
            continue

        avgRow = {}
        for fieldName, fieldType in AVG_FIELDS:
            itemCount = len(groupRows)
            _sum = 0
            if all([row[fieldName] == groupRows[0][fieldName] for row in groupRows]):
                # All columns equal
                continue

            for row in groupRows:
                if row[fieldName] in ('', '+++++', '++++', '+++'):
                    itemCount -= 1
                else:
                    _sum += row[fieldName]
            if itemCount > 1:
                avgRow[fieldName] = fieldType(_sum / itemCount)
            else:
                avgRow[fieldName] = 'yyyyy'

        # Copy missing common collumns from last row
        for fieldName in (FIELDNAMES - avgRow.keys()):
            avgRow[fieldName] =  row[fieldName]

        csvout.writerow(avgRow)

if __name__ == '__main__':
    main()
