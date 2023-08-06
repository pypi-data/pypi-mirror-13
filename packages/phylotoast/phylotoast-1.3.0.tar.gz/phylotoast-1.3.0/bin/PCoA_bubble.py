#!/usr/bin/env python
'''
Create a series of PCoA plots where the marker size varies by relative
abundance of a particular OTU

Author: Shareef M Dabdoub
'''
from __future__ import division
# built-in
import argparse
from collections import OrderedDict, defaultdict
import json
import os
import sys
# 3rd party
try:
    import matplotlib
except ImportError as ie:
    sys.exit('Import Error. Please install missing module: {}'.format(ie))
import matplotlib
matplotlib.use("Agg")  # for use on headless server
import matplotlib.pylab as p
# local
from phylotoast import util, graph_util


def otu_biom_entry_num(ID, biom, entry_type='rows'):
    for i, entry in enumerate(biom[entry_type]):
        if entry['id'] == ID:
            return i


def rel_abundance(otuID, sampleID, biom, scaling_factor=10000):
    otuRow = otu_biom_entry_num(otuID, biom)
    sCol = otu_biom_entry_num(sampleID, biom, 'columns')
    otuAbundance = 0
    sampleAbundance = 0

    for row, col, amt in biom['data']:
        if col == sCol:
            sampleAbundance += amt
        if col == sCol and row == otuRow:
            otuAbundance = amt

    if sampleAbundance == 0:
        return 0

    return otuAbundance / sampleAbundance * scaling_factor


def calculate_xy_range(data):
    xr = [float('inf'), float('-inf')]
    yr = [float('inf'), float('-inf')]

    for cat in data:
        pc1, pc2 = data[cat]['pc1'], data[cat]['pc2']
        if pc1:
            xr[0] = min(min(pc1), xr[0])
            xr[1] = max(max(pc1), xr[1])
        if pc2:
            yr[0] = min(min(pc2), yr[0])
            yr[1] = max(max(pc2), yr[1])

    return xr, yr


def link_samples_to_categories(imap, category_idx):
    """
    Creates a dictionary of category types with all the associated Sample IDs

    :type imap: dict
    :param imap: The mapping data that lists category information
    :type category_idx: int
    :param category_idx: The index in the mapping data of the user-specified
                          category
    :rtype: OrderedDict
    :return: A dictionary of category types mapped to a list of corresponding
              sample IDs
    """
    cat_types = defaultdict(list)
    for row in imap.values():
        cat_types[row[category_idx]].append(row[0])
    return OrderedDict(sorted(cat_types.items(), key=lambda t: t[0]))


def plot_PCoA(cat_data, otu_name, unifrac, names, colors, xr, yr, outDir):
    p.matplotlib.rc('axes', edgecolor='black')
    p.matplotlib.rc('axes', facecolor='grey')
    fig = p.plt.figure()
    ax = fig.add_subplot(111)
#    fig.set_figheight(8)
#    fig.set_figwidth(10)
    legend = []

    for i, cat in enumerate(cat_data):
        p.scatter(cat_data[cat]['pc1'], cat_data[cat]['pc2'],
                  cat_data[cat]['size'], color=colors[i], alpha=0.85, marker='o',
                  edgecolor='black')
#        p.scatter(cat_data[cat]['zpc1'], cat_data[cat]['zpc2'], s=20,
#                  edgecolor=colors[i], facecolor='none', marker='s')
        legend.append(p.Rectangle((0, 0), 1, 1, fc=colors[i]))

    ax.legend(legend, names, loc='best')
    p.title(otu_name, style='italic')
    p.ylabel('PC2 ({:.2f}%)'.format(float(unifrac['varexp'][2])))
    p.xlabel('PC1 ({:.2f}%)'.format(float(unifrac['varexp'][1])))
    p.xlim(round(xr[0]*1.5, 1), round(xr[1]*1.5, 1))
    p.ylim(round(yr[0]*1.5, 1), round(yr[1]*1.5, 1))
    graph_util.rstyle(ax)
    fig.savefig(os.path.join(outDir, '_'.join(otu_name.split())) + '.png',
                facecolor='0.75', edgecolor='none')
    p.plt.close(fig)


def handle_program_options():
    parser = argparse.ArgumentParser(description="Create a series of Principle\
                                     Coordinate plots for each OTU in an \
                                     input list where the plot points are \
                                     varied in size by the relative abundance \
                                     of the OTU (relative to either Sample or\
                                     the total contribution of the OTU to the \
                                     data set.")
    parser.add_argument('-i', '--otu_table', required=True,
                        help="The biom-format file with OTU-Sample abundance \
                              data.")
    parser.add_argument('-u', '--unifrac', required=True,
                        help='Principle coordinates analysis file. \
                              Eg. unweighted_unifrac_pc.txt')
    parser.add_argument('-d', '--names_colors_ids_fn', required=True,
                        help='The name of an input data file containing three\
                              items: Line 1: a tab-separated list of display\
                              names for the different types in the specified \
                              mapping category (--mapping_category), Line 2:\
                              a matching tab-separated list of hexadecimal\
                              colors for each of the category types, \
                              Lines 3-end: a tab-separated pair specifying \
                              OTU ID and OTU Name. Each entry will get a \
                              separate PCoA plot under a file with the name \
                              of the OTU.')
    parser.add_argument('-m', '--mapping', required=True,
                        help="The mapping file specifying group information \
                              for each sample.")
    parser.add_argument('-c', '--map_category', required=True,
                        help="Any mapping category, such as treatment type, \
                              that will be used to group the data in the \
                              output plots. For example, one category \
                              with three types will result in three different\
                              point sets in the final output.")
    parser.add_argument('-o', '--output_dir', default='.',
                        help="The directory to output the PCoA plots to.")

    parser.add_argument('--scaling_factor', default=10000, type=float,
                        help="Species relative abundance is multiplied by this \
                              factor in order to make appropriate visible \
                              bubbles in the output plots. Default is 10000.")
#    parser.add_argument('-n', '--normalization', default='sample',
#                        choices=['sample','otu'],
#                        help="Specifies whether OTU abundance is \
#                        normalized column-wise (per-sample) or row-wise \
#                        (per-OTU).")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Displays species name as each is being plotted \
                              and stored to disk.")

    return parser.parse_args()


def main():
    args = handle_program_options()

    try:
        with open(args.otu_table):
            pass
    except IOError as ioe:
        sys.exit('\nError with OTU/Sample abundance BIOM format file:{}\n'.format(ioe))

    try:
        with open(args.unifrac):
            pass
    except IOError as ioe:
        sys.exit('\nError with principle coordinates analysis file:{}\n'.format(ioe))

    try:
        with open(args.names_colors_ids_fn):
            pass
    except IOError as ioe:
        sys.exit('\nError with input data file:{}\n'.format(ioe))

    try:
        with open(args.mapping):
            pass
    except IOError as ioe:
        sys.exit('\nError with mapping file:{}\n'.format(ioe))

    if not os.path.exists(args.output_dir):
        try:
            os.mkdir(args.output_dir)
        except OSError as oe:
            if os.errno == 2:
                msg = ('One or more directories in the path provided for ' +
                       '--output-dir ({}) do not exist. If you are specifying ' +
                       'a new directory for output, please ensure all other ' +
                       'directories in the path currently exist.')
                sys.exit(msg.format(args.output_dir))
            else:
                msg = ('An error occurred trying to create the output ' +
                       'directory ({}) with message: {}')
                sys.exit(msg.format(args.output_dir, oe.strerror))

    with open(args.otu_table) as bF:
        biom = json.loads(bF.readline())

    unifrac = util.parse_unifrac(args.unifrac)

    otus = {}
    with open(args.names_colors_ids_fn, 'rU') as nciF:
        category_names = nciF.readline().strip().split('\t')
        category_colors = nciF.readline().strip().split('\t')
        for line in nciF.readlines():
            line = line.split()
            otus[line[0]] = ' '.join(line[1:])
    header, imap = util.parse_map_file(args.mapping)

    try:
        category_idx = header.index(args.map_category)
    except ValueError:
        msg = "Error: Specified mapping category '{}' not found"
        sys.exit(msg.format(args.map_category))
    category_ids = link_samples_to_categories(imap, category_idx)

    # plot samples based on relative abundance of some OTU ID
    for otuID in otus:
        cat_data = {cat: {'pc1': [], 'pc2': [], 'size': [], 'zpc1': [], 'zpc2': []}
                    for cat in category_ids}

        for sid in unifrac['pcd']:
            category = cat_data[imap[sid][category_idx]]
            size = rel_abundance(otuID, sid, biom, args.scaling_factor)
            # if size > 0:
            category['pc1'].append(float(unifrac['pcd'][sid][0]))
            category['pc2'].append(float(unifrac['pcd'][sid][1]))
            category['size'].append(size)
#            else:
#                category['zpc1'].append(float(unifrac['pcd'][sid][1]))
#                category['zpc2'].append(float(unifrac['pcd'][sid][2]))

        if args.verbose:
            print 'Plotting chart for {}'.format(otus[otuID])
        xr, yr = calculate_xy_range(cat_data)
        plot_PCoA(cat_data, otus[otuID], unifrac, category_names,
                  category_colors, xr, yr, args.output_dir)

if __name__ == '__main__':
    main()
