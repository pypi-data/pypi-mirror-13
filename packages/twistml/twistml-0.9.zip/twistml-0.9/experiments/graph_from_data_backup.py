r"""<summary>

    <extended summary>

    <routine listings>

    <see also>

    <notes>

    <references>

    <examples>

:Author:
    Matthias Manhertz
:Copyright:
    (c) Matthias Manhertz 2015
:Licence:
    MIT
"""

import pickle
from matplotlib.backends.backend_pdf import PdfPages
import twistml as tml
import optparse
from os import path
from matplotlib import pyplot as plt


def main(data_list, pdf_path):

    fig_list = []
    for data in data_list:
        fig = tml.utility.multi_group_bar_chart(
            data=data['data'],
            errors=data['errors'],
            setting_labels=data['setting_labels'],
            source_labels=data['source_labels'],
            x_label=data['x_label'],
            y_label=data['y_label'],
            title=data['title'],
            ylim=data['ylim'],
            colors=['#A5ACAF', '#002244', '#345d73', '#69BE28'])
        fig_list.append(fig)

    if pdf_path:
        pp = PdfPages(pdffilepath)
        for fig in fig_list:
            pp.savefig(fig)
        pp.close()
    else:
        for fig in fig_list:
            plt.show()
            #fig.show(block=True)

    pass


def _check_file(filepath, name, parser):
    if not filepath:
        parser.error("Please enter a filepath for the {}".format(name))
    if not path.exists(filepath):
        parser.error("{} is not a valid filepath.".format(filepath))
    pass


if __name__ == '__main__':
    usage = 'usage: %prog [options] data_file'
    parser = optparse.OptionParser(usage=usage)

    parser.add_option("-p", "--pdf",
                      type="string", dest="pdffile",
                      help="store the graphs to this .pdf file")

    (options, args) = parser.parse_args()

    if not len(args) == 1:
        parser.error("Please enter exactly one filepath for the {}".format(
            'file with the data backup.'))
    _check_file(args[0], 'data file', parser)

    if options.pdffile:
        _check_dir(options.pdffile, 'pdf file (-p, --pdf)', parser)

    with open(args[0]) as f:
        data = pickle.load(f)

    main(data, options.pdffile)

