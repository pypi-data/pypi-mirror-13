from ariblib import tsopen
from ariblib.packet import payload, pid
from ariblib.sections import ProgramAssociationSection, ProgramMapSection

def ver(args):
    with tsopen(args.inpath) as ts:
        pat = next(ts.sections(ProgramAssociationSection))
        pmt_number, pmt_pid = next(pat.pmt_items)
        version_number = -1
        outpath = args.inpath + '_' + str(version_number)
        out = open(outpath, 'wb')
        for packet in ts:
            if pid(packet) == pmt_pid:
                pmt = ProgramMapSection(payload(packet)[1])
                if (pmt_number == pmt.program_number and
                        version_number != pmt.version_number):
                    out.close()
                    version_number = pmt.version_number
                    outpath = args.inpath + '_' + str(version_number)
                    print("new file {}".format(outpath))
                    out = open(outpath, 'wb')
            out.write(packet)
    out.close()


def add_parser(parsers):
    parser = parsers.add_parser('ver')
    parser.set_defaults(command=ver)
    parser.add_argument('inpath', help='input file path')
