import calendar
import csv
import datetime
import gzip
import itertools
import math
import operator
import os
import random
import re

import numpy
import scipy
import scipy.stats
import scipy.signal
import pandas
from . import romannumerals
from functools import reduce


CODON_TABLE = {'GUC': 'V', 'ACC': 'T', 'GUA': 'V', 'GUG': 'V', 'GUU': 'V', 'AAC': 'N', 'CCU': 'P', 'UGG': 'W',
               'AGC': 'S', 'AUC': 'I', 'CAU': 'H', 'AAU': 'N', 'AGU': 'S', 'ACU': 'T', 'CAC': 'H', 'ACG': 'T',
               'CCG': 'P', 'CCA': 'P', 'ACA': 'T', 'CCC': 'P', 'GGU': 'G', 'UCU': 'S', 'GCG': 'A', 'UGC': 'C',
               'CAG': 'Q', 'GAU': 'D', 'UAU': 'Y', 'CGG': 'R', 'UCG': 'S', 'AGG': 'R', 'GGG': 'G', 'UCC': 'S',
               'UCA': 'S', 'GAG': 'E', 'GGA': 'G', 'UAC': 'Y', 'GAC': 'D', 'GAA': 'E', 'AUA': 'I', 'GCA': 'A',
               'CUU': 'L', 'GGC': 'G', 'AUG': 'M', 'CUG': 'L', 'CUC': 'L', 'AGA': 'R', 'CUA': 'L', 'GCC': 'A',
               'AAA': 'K', 'AAG': 'K', 'CAA': 'Q', 'UUU': 'F', 'CGU': 'R', 'CGA': 'R', 'GCU': 'A', 'UGU': 'C',
               'AUU': 'I', 'UUG': 'L', 'UUA': 'L', 'CGC': 'R', 'UUC': 'F'}

WHITESPACE = re.compile(r'\s*')

ALPHANUMERIC = [chr(i) for i in range(48, 58)] + [chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)]

# TMP_DIR = '/data/nrnb01_nobackup/dskola'
TMP_DIR = '/tmp/{}'.format(os.environ['USER'])


def first_upper(text):
    if len(text) == 1:
        return text[0].upper()
    else:
        return text[0].upper() + text[1:]


def first_lower(text):
    if len(text) == 1:
        return text[0].lower()
    else:
        return text[0].lower() + text[1:]


def rev_complement(seq):
    complements = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'N': 'N', '': ''}
    return ''.join([complements[x] for x in seq[::-1]])


def dna_to_rna(seq):
    return seq.replace('T', 'U')


def rna_to_dna(seq):
    return seq.replace('U', 'T')


def translate_dna(dna_sequence, reading_frame_offset=0, reading_frame_direction=1):
    """
    Returns a list of 1-letter amino acid strings corresponding to the translated codons in a sequence of DNA characters
    at a specified offset (0,1,2) and direction (-1 or 1)
    """
    assert reading_frame_offset in (0, 1, 2)
    assert reading_frame_direction in (-1, 1)

    if reading_frame_direction == -1:
        dna_sequence = rev_complement(dna_sequence)

    return [CODON_TABLE[codon] for codon in
            split_codons(sequence=dna_to_rna(dna_sequence), reading_frame_offset=reading_frame_offset,
                         reading_frame_direction=reading_frame_direction)]


def translate_rna(rna_sequence, reading_frame_offset=0, reading_frame_direction=1):
    """
    Returns a list of 1-letter amino acid strings corresponding to the translated codons in a sequence of DNA characters
    at a specified offset (0,1,2) and direction (-1 or 1)
    """
    return [CODON_TABLE[codon] for codon in
            split_codons(sequence=rna_sequence, reading_frame_offset=reading_frame_offset,
                         reading_frame_direction=reading_frame_direction)]


def split_codons(sequence, reading_frame_offset=0, reading_frame_direction=1):
    """
    Returns a list of 3-character strings representing codons extracted from a sequence of DNA characters
    at a specified offset (0,1,2) and direction (-1 or 1)
    """
    assert reading_frame_offset in (0, 1, 2)
    assert reading_frame_direction in (-1, 1)

    codons = []

    num_codons = int((len(sequence) - reading_frame_offset) / 3)

    for codon in range(num_codons):
        codons.append(sequence[codon * 3 + reading_frame_offset:(codon + 1) * 3 + reading_frame_offset])

    return codons


def parse_line_dict(line, field_names, split_char='\t', strict=True, defaults=None):
    """
    Divides a string into a dictionary of named fields and values, assuming
    the values are given in the same order as <field_names> and separated by <split_char>
    """
    if not strict:
        assert len(field_names) == len(defaults)

    result = {}
    split_line = line.strip().split(split_char)

    for idx, field in enumerate(field_names):
        try:
            result[field] = split_line[idx]
        except IndexError as ie:
            if strict:
                print()
                'Missing field {} in line: {}'.format(field, line)
                raise ie
            else:
                result[field] = defaults[idx]
    return result


def dict_apply(func, dict_1, dict_2):
    new_dict = {}
    all_keys = set(dict_1.keys()).union(list(dict_2.keys()))
    for k in all_keys:
        if k in dict_1 and k in dict_2:
            new_dict[k] = func(dict_1[k], dict_2[k])
        elif k in dict_1:
            new_dict[k] = dict_1[k]
        else:
            new_dict[k] = dict_2[k]
    return new_dict


def dict_add(dict_1, dict_2):
    return dict_apply(operator.add, dict_1, dict_2)


def dict_sub(dict_1, dict_2):
    return dict_apply(operator.sub, dict_1, dict_2)


def dict_diff(dict_a, dict_b):
    """
    Performs an elementwise subtraction of dict_b from dict_a
    """
    diff_dict = {}
    a = set(dict_a.keys())
    b = set(dict_b.keys())
    a_only = a.difference(b)
    b_only = b.difference(a)
    common = a.intersection(b)
    for k in a_only:
        diff_dict[k] = dict_a[k]
    for k in b_only:
        diff_dict[k] = -dict_b[k]
    for k in common:
        diff_dict[k] = dict_a[k] - dict_b[k]
    return diff_dict


def split_with_defaults(line, split_char='\t', defaults=[]):
    """
    Divides a string into a list of values separated by <split_char>.

    Populate missing values with the corresponding items from <defaults>
    """
    split_line = line.strip().split(split_char)
    assert len(split_line) <= len(defaults)
    return split_line + defaults[len(split_line) - len(defaults):]


def freq(an_iterable):
    """
    Generates a dictionary of object frequencies for the given iterable
    """
    freq_dict = {}
    for c in an_iterable:
        if c not in freq_dict:
            freq_dict[c] = 1
        else:
            freq_dict[c] += 1
    return freq_dict


def mode(an_iterable, rank=0, exclude=[]):
    """
    Returns the most common object in <an_iterable> that is not in <exclude_list>
    This is the default behavior, if <rank> is 0. If <rank> != 0, return the <rank>+1-most
    common item in <an_iterable>.
    """
    if exclude:
        exclude_set = set(exclude)
        return \
            sorted([f for f in list(freq(an_iterable).items()) if f[0] not in exclude_set], key=lambda x: x[1], reverse=True)[
                rank][0]
    else:
        return sorted(list(freq(an_iterable).items()), key=lambda x: x[1], reverse=True)[rank][0]


def convert_chroms(chrom_string, dest='ucsc'):
    """
    Refactored to auto-detect source (<source> parameter will be ignored).
    :param chrom_string:
    :param source:
    :param dest:
    :return:
    """
    try:
        chrom_string = str(romannumerals.roman_to_int(chrom_string))
    except ValueError:
        pass

    if dest == 'ensembl':
        if chrom_string == 'chrM':
            return 'dmel_mitochonrdion_genome'
        elif chrom_string[:3].lower() == 'chr':
            return chrom_string[3:]
        else:
            return chrom_string
    elif dest == 'ucsc':
        if chrom_string == 'dmel_mitochondrion_genome':
            return 'chrM'
        elif chrom_string[:3].lower() == 'chr':
            return chrom_string
        else:
            return 'chr{}'.format(chrom_string)
    elif dest == 'yeast':
        if chrom_string[:3].lower() == 'chr':
            chrom_string = chrom_string[3:]
        try:
            return romannumerals.int_to_roman(int(chrom_string))
        except ValueError:
            return chrom_string

    else:
        raise ValueError('Unknown destination {}'.format(dest))


# def convert_chroms(chrom_string, source, dest):
#     if source == dest:
#         return chrom_string
#     if source == 'ucsc':
#         if dest == 'ensembl':
#             if chrom_string == 'chrM':
#                 return 'dmel_mitochonrdion_genome'
#             elif chrom_string[:3].lower() == 'chr':
#                 return chrom_string[3:]
#             else:
#                 return chrom_string
#         else:
#             raise ValueError('Unknown destination {} for source {}'.format(dest, source))
#     elif source == 'ensembl':
#         if dest == 'ucsc':
#             if chrom_string == 'dmel_mitochondrion_genome':
#                 return 'chrM'
#             return 'chr{}'.format(chrom_string)
#         else:
#             raise ValueError('Unknown destination {} for source {}'.format(dest, source))
#     else:
#         raise ValueError('Unknown source {}'.format(source))


def convert_csv_to_tsv(filepath):
    """

    :param filepath:
    :return:

    Convert <filepath> to a .tsv file with the same mantissa
    """
    with open(filepath, 'rU') as infile:
        r = csv.reader(infile, dialect=csv.excel)
    with open(filepath.strip('.csv') + '.tsv', 'w') as outfile:
        w = csv.writer(outfile, dialect=csv.excel_tab)
    for line in r:
        w.writerow(line)


def home_path(subfolder):
    """
    Return a path consisting of "subfolder" joined to the current user's home directory
    """
    return os.path.join(os.environ['HOME'], subfolder)


def parse_path(fullpath):
    """
    :param fullpath:
    :return:

    Parses <fullpath> into its components and returns a tuple consisting of the directory, the filename mantissa and the extension.
    """
    split_path = fullpath.split(os.sep)
    path_prefix = os.sep.join(split_path[:-1])
    filename = split_path[-1]
    split_filename = filename.split('.')
    filename_prefix = '.'.join(split_filename[:-1])
    extension = split_filename[-1]
    return path_prefix, filename_prefix, extension


def rev_complement(seq):
    complements = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'N': 'N', '': ''}
    return [complements[x] for x in seq[::-1]]


def DNA_to_RNA(seq):
    return seq.replace('T', 'U')


def RNA_to_DNA(seq):
    return seq.replace('U', 'T')


def parse_chromosome_ID(chromosome_identifier):
    """
    Parses a chromosome identifier and returns an integer chromosome number.
    The identifier consists of two parts (first optional):
        first, one of the words "chr", "chromosome", or nothing.
        second, a numeric digit or roman numeral representing the chromosome number
    The two parts may be separated by any amount of whitespace.
    If no valid match to this pattern is found, it will return None
    """
    re.IGNORECASE = False
    chromosome_identifier = str(chromosome_identifier).strip()
    # OK, it's not a refseq/genbank troublemaker, maybe it's some flavor of numerical identifier . . .
    m = re.match(r"(?P<prefix>chro?m?o?s?o?m?e?|\b)\s*(?P<number>\d+|\b|\B)(?P<numeral>[MDCLXVI]*\Z)",
                 chromosome_identifier)

    if m and bool(m.group('number')) != bool(
            m.group('numeral')):  # check that the pattern matches and we don't have both a number and a numeral
        if m.group('numeral'):
            try:
                num = str(romannumerals.roman_to_int(m.group('numeral')))
            except ValueError as ex:
                return None
            else:
                return num
        elif m.group('number'):
            try:
                num = m.group('number')
            except ValueError as ex:
                return None
            else:
                return num
    # if it doesn't fit any of these patterns, just return the original input
    return chromosome_identifier


def parse_fasta_list(fasta):
    """

    :param fasta:
    :return:

    Returns the contents of a FASTA string as a list of dictionaries, each with a header and sequence key-value pair.
    """
    return [{'header': split_seq[0], 'sequence': ''.join(split_seq[1:])} for split_seq in
            [seq.split('\n') for seq in fasta.split('>')]]


def parse_fasta_dict(fasta):
    """
    :param fasta:
    :return:

    Returns the contents of a FASTA string as a dictionary of sequences keyed by the first substring in the header string prior to a space
    """
    return dict(
            [(re.split(WHITESPACE, split_seq[0])[0], ''.join(split_seq[1:])) for split_seq in
             [seq.split('\n') for seq in fasta.split('>')] if re.split(WHITESPACE, split_seq[0])[0] != ''])


def write_fasta_dict(sequence_dict, fasta_filename, COL_WIDTH=60):
    """
    Given a dictionary <sequence_dict> of genetic sequence, write out the contents to a FASTA-formatted text file at <fname>
    :param sequence_dict:
    :return:
    """
    with open(fasta_filename, 'w') as fasta_file:
        for seq in numerical_string_sort(sequence_dict):
            fasta_file.write('>{}\n'.format(seq))
            pointer = 0
            while pointer + COL_WIDTH < len(sequence_dict[seq]):
                fasta_file.write(sequence_dict[seq][pointer:pointer + COL_WIDTH] + '\n')
                pointer += COL_WIDTH
            if pointer < len(sequence_dict[seq]):
                fasta_file.write(sequence_dict[seq][pointer:] + '\n')


def compute_fasta_offset(sequence_location, header_size, line_size, cr_lf_size=1):
    """
    Given a location on a FASTA sequence (assuming one sequence per file),
    the length of the header line and a line length (including CR/LF),
    (assumes the line size is constant throughout the file),
    returns the file location of the specified sequence location
    """
    num_lines = int(sequence_location / (line_size - cr_lf_size))
    line_offset = sequence_location % (line_size - cr_lf_size)
    return num_lines * line_size + line_offset + header_size


def convert_nbinom_params(mu, var):
    """
    Converts mean and variance into the n and p parameters used by scipy.stats
    """
    if not var > mu:
        raise ValueError('Variance must be greater than mean for negative binomial distribution')

    p = mu / float(var)
    n = mu * p / float(1 - p)
    return n, p


def convert_binom_params(mu, var):
    """
    Returns the n and p parameters of a binomial distribution that has expected value <mu> and expected variance <var>
    :param mu:
    :param var:
    :return:
    """
    p = (var - mu) / float(-mu)
    n = iround(mu / float(p))
    return n, p


def fit_neg_binom(data):
    """
    Estimates n and p parameters (as defined by scipy.stats) of a negative binomial distribution fitting the data
    :param data:
    :return:
    """
    mu = data.mean()
    var = data.var()
    return convert_nbinom_params(mu, var)


def convert_normal_lognormal(mu, var):
    """
    Converts the parameters mu and sigma of a lognormal distribution to the expected mean
    and variance of such a distribution. The log of such a distribution will have
    mean and variance equal to it's parameters
    
    See http://www.mathworks.com/help/stats/lognstat.html for details
    """
    mu = float(mu)
    var = float(var)
    new_mu = math.exp(mu + var / 2)
    new_var = math.exp(2 * mu + var) * (math.exp(var) - 1)
    return new_mu, new_var


def convert_lognormal_normal(mu, var):
    """
    Converts the moments of a lognormal distribution (mean and variance)
    to the parameters mu and sigma needed to generate such a distribution.
    
    See http://www.mathworks.com/help/stats/lognstat.html for details
    """
    mu = float(mu)
    var = float(var)
    new_mu = math.log(mu ** 2 / math.sqrt(var + mu ** 2))
    new_sigma = math.sqrt(math.log(var / mu ** 2 + 1))
    return new_mu, new_sigma


def logit(arr):
    return numpy.log(arr / (1 - arr))


def logistic(arr, L, k, x0=0):
    return L / (1 + numpy.exp(-k * (arr - x0)))


def rank(arr):
    """
    Return an array consisting of the ranks of the elements in <arr>. Currently doesn't explicitly deal with ties,
    so behavior is not specified.
    """
    r = numpy.zeros(len(arr), dtype=numpy.int)
    a = numpy.argsort(arr)
    i = numpy.arange(len(arr))
    r[a[i]] = i
    return r


def quadratic_formula(a, b, c):
    """
    Returns the two real-valued solutions to the quadratic formula (if they exist).
    :param a:
    :param b:
    :param c:
    :return:
    """
    d = b ** 2 - 4 * a * c
    if d >= 0:
        sol1 = (-b + math.sqrt(d)) / float(2 * a)
        sol2 = (-b - math.sqrt(d)) / float(2 * a)
        return sol1, sol2
    else:
        print()
        'No real solutions'


def dist_similarity_pcc(arr1, arr2, bin_min=None, bin_max=None, num_bins=100):
    if bin_min is None:
        bin_min = min(arr1.min(), arr2.min())
    if bin_max is None:
        bin_max = max(arr1.max, arr2.max)
    h1 = numpy.histogram(arr1, numpy.linspace(0, bin_max, num=num_bins))[0]
    h2 = numpy.histogram(arr2, numpy.linspace(0, bin_max, num=num_bins))[0]
    return scipy.stats.pearsonr(h1, h2)[0]


def equilibirum(A, B, Kd):
    """
    Returns the final concentrations [AB],[A],[B]
    given the total concentrations of reactants A and B and the
    dissociation constant Kd
    """
    a = 1
    b = -(B + A + Kd)
    c = A * B
    sol1, sol2 = quadratic_formula(a, b, c)

    A_1 = A - sol1
    B_1 = B - sol1
    A_2 = A - sol2
    B_2 = B - sol2

    error_1 = A_1 * B_1 / sol1 - Kd
    error_2 = A_2 * B_2 / sol2 - Kd

    if error_1 < error_2 and sol1 > 0 and A_1 > 0 and B_1 > 0:
        return sol1, A_1, B_1
    elif sol2 > 0 and A_2 > 0 and B_2 > 0:
        return sol2, A_2, B_2
    else:
        print()
        "No plausible solutions found (all solutions involve negative concentrations)!"


def generate_genome_table(fasta_filename, genome_table_filename=''):
    total_size = 0
    genome_table = {}
    with open(fasta_filename, 'rU') as fasta_file:
        print()
        'Checking the lengths of all sequences in {} ...'.format(fasta_filename)
        fasta_dict = parse_fasta_dict(fasta_file.read())
    for chrom in sorted(fasta_dict):
        if len(fasta_dict[chrom]) > 0:
            genome_table[chrom] = len(fasta_dict[chrom])
            total_size += genome_table[chrom]
            print()
            '{}\t{}'.format(chrom, genome_table[chrom])
    print()
    'Total size: {}'.format(total_size)
    if genome_table_filename:
        with open(genome_table_filename, 'w') as genome_table_file:
            print()
            'Writing genome table to {}'.format(genome_table_filename)
            genome_table_writer = csv.writer(genome_table_file, dialect=csv.excel_tab)
            for chrom in sorted(genome_table):
                genome_table_writer.writerow([chrom, genome_table[chrom]])
    return genome_table


def count_seq_sizes(fasta_file, verbose=True):
    """

    :param fasta_file:
    :return:

    Analyzes a FASTA file and returns a dictionary of sizes keyed by sequence name.
    """
    start_time = datetime.datetime.now()
    seq_sizes = {}
    for line in fasta_file:
        if line.startswith('>'):
            seq_name = re.split(WHITESPACE, line[1:].strip())[0]
            if verbose:
                print()
                'Analyzing sequence {}'.format(seq_name)
            seq_sizes[seq_name] = 0
        else:
            seq_sizes[seq_name] += len(line.strip())
    print()
    'Done in {}.'.format(datetime.datetime.now() - start_time)
    return seq_sizes


def indent(text, numtabs=1):
    """
    Indents a block of text by adding a specified number of tabs (default 1) to 
    the beginning of each line
    """
    return '\n'.join(['\t' * numtabs + line for line in text.split('\n')])


def first_leaf(nested_dict):
    """
    On the assumption that all the leaves of a nested dictionary (tree) structure are in some way equivalent,
    this is a quick method of returning the first such leaf without knowing the specific keys used
    to construct the nested dict.
    """
    partial_dict = nested_dict
    while True:  # infinite loop
        try:
            # see if we are dictionary-like, and if so go down one level
            partial_dict = partial_dict[list(partial_dict.keys())[0]]
        except AttributeError:
            try:
                # if not, perhaps we are a list or other list-like object?
                partial_dict = list(partial_dict)
            except TypeError:
                # we're not dictionary-like and not list-like, assume we're a leaf and return
                return partial_dict
            else:
                # if we are list-like, go down to the next level
                partial_dict = partial_dict[0]


def sterilize_dict(unclean_dict):
    """
    Recursively converts a data structure containing one or more nested levels of collections.defaultdict to plain dicts.

    It will stop the breadth-first search at the first level that is not convertible to a dict, and copy these subtrees over to the
    new structure
    """
    try:
        # unclean_dict.default_factory = None
        clean_dict = dict(unclean_dict)
        # print clean_dict
    except TypeError:
        return unclean_dict
    except ValueError:
        return unclean_dict
    else:
        # if type(unclean_dict) == type({}):
        for k in list(unclean_dict.keys()):
            # print 'key: {}'.format(k)
            clean_dict[k] = sterilize_dict(unclean_dict[k])
        return clean_dict


def flatten(l, ltypes=(list, tuple)):
    """
    :param l: a list to flatten
    :param ltypes: valid variable types to unflatten
    :return: a flattened list

    Flattens an arbitrarily-deep nested list

    Credit: http://rightfootin.blogspot.com/2006/09/more-on-python-flatten.html
    adapted from Mike C. Fletcher's BasicTypes
    """
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return ltype(l)


def threshold(vec, thresh):
    return numpy.greater_equal(vec, thresh) * vec


def quantize(vector, precision_factor):
    """
    Returns a copy of <vector> that is scaled by <precision_factor> and then rounded to the nearest integer.
    To re-scale, simply divide by <precision_factor>.
    
    Note that because of rounding, an open interval from (x,y) will give rise 
    to up to (x - y) * <precision_factor> + 1 bins.
    """
    return (numpy.asarray(vector) * precision_factor).round(0)


def set_partitions(parent_set, num_partitions):
    """
    A very efficient algorithm (Algorithm U) is described by Knuth in the Art of Computer Programming, Volume 4, Fascicle 3B to find all set partitions with a given number of blocks.
    Python implementation by Adeel Zafar Soomro, retrieved from "http://codereview.stackexchange.com/questions/1526/finding-all-k-subset-partitions" on May 30, 2014. Variables renamed by me.
    """
    m = num_partitions
    ns = parent_set

    def visit(n, a):
        ps = [[] for i in range(m)]
        for j in range(n):
            ps[a[j + 1]].append(ns[j])
        return ps

    def f(mu, nu, sigma, n, a):
        if mu == 2:
            yield visit(n, a)
        else:
            for v in f(mu - 1, nu - 1, (mu + sigma) % 2, n, a):
                yield v
        if nu == mu + 1:
            a[mu] = mu - 1
            yield visit(n, a)
            while a[nu] > 0:
                a[nu] = a[nu] - 1
                yield visit(n, a)
        elif nu > mu + 1:
            if (mu + sigma) % 2 == 1:
                a[nu - 1] = mu - 1
            else:
                a[mu] = mu - 1
            if (a[nu] + sigma) % 2 == 1:
                for v in b(mu, nu - 1, 0, n, a):
                    yield v
            else:
                for v in f(mu, nu - 1, 0, n, a):
                    yield v
            while a[nu] > 0:
                a[nu] = a[nu] - 1
                if (a[nu] + sigma) % 2 == 1:
                    for v in b(mu, nu - 1, 0, n, a):
                        yield v
                else:
                    for v in f(mu, nu - 1, 0, n, a):
                        yield v

    def b(mu, nu, sigma, n, a):
        if nu == mu + 1:
            while a[nu] < mu - 1:
                visit(n, a)
                a[nu] = a[nu] + 1
            visit(n, a)
            a[mu] = 0
        elif nu > mu + 1:
            if (a[nu] + sigma) % 2 == 1:
                for v in f(mu, nu - 1, 0, n, a):
                    yield v
            else:
                for v in b(mu, nu - 1, 0, n, a):
                    yield v
            while a[nu] < mu - 1:
                a[nu] = a[nu] + 1
                if (a[nu] + sigma) % 2 == 1:
                    for v in f(mu, nu - 1, 0, n, a):
                        yield v
                else:
                    for v in b(mu, nu - 1, 0, n, a):
                        yield v
            if (mu + sigma) % 2 == 1:
                a[nu - 1] = 0
            else:
                a[mu] = 0
        if mu == 2:
            visit(n, a)
        else:
            for v in b(mu - 1, nu - 1, (mu + sigma) % 2, n, a):
                yield v

    n = len(ns)
    a = [0] * (n + 1)
    for j in range(1, m + 1):
        a[n - m + j] = j - 1
    return f(m, n, 0, n, a)


def count_lines(fname):
    """
    Returns the number of lines in <fname>
    """
    with open(fname) as f:
        i = -1
        for i, x in enumerate(f):
            pass
    return i + 1


def triangular_kernel(bandwidth, normalize=False):
    midpoint = int(bandwidth / float(2) - 0.5)
    kern = numpy.zeros(bandwidth)
    for pos in range(bandwidth):
        kern[pos] = 1 - abs(midpoint - pos) / float(midpoint + 1)
    if normalize:
        return kern / float(bandwidth)
    else:
        return kern


def gaussian_kernel(sd, sd_cutoff=3, normalize=False):
    bw = sd_cutoff * sd * 2 + 1
    midpoint = sd_cutoff * sd
    kern = numpy.zeros(bw)
    frozen_rv = scipy.stats.norm(scale=sd)
    for i in range(bw):
        kern[i] = frozen_rv.pdf(i - midpoint)
    return kern


def apply_kernel(vec, kern):
    # print('Vector has shape: {}, Kernel has shape: {}'.format(vec.shape, kern.shape))
    return scipy.signal.fftconvolve(vec, kern, mode='same')


def bisect_root(solve_func, lower_bound, upper_bound, convergence_tolerance, max_iters=float('inf')):
    """
    Implements the bisection method of numerically finding a root of an equation in one
    variable. If multiple roots exist, only one will be found.

    <solve_func> must be a function that takes a single parameter that returns zero when
        the parameter is equal to a root.

    <lower_bound> and <upper_bound> specify the boundaries of the search space.

    <convergence_tolerance> specificies how close to zero the function output must be to
        considered converged.

    <max_iters>: maximum number of iterations to run (defaults to infinite)
    """
    iter_count = 0

    f_b = solve_func((lower_bound + upper_bound) / float(2))

    while math.fabs(f_b) > convergence_tolerance and iter_count <= max_iters:
        iter_count += 1
        midpoint = (lower_bound + upper_bound) / float(2)

        # print iter_count, lower_bound, upper_bound
        # print midpoint

        f_a = solve_func(lower_bound)
        f_b = solve_func(midpoint)
        f_c = solve_func(upper_bound)

        # print '\t{}, {}, {}'.format(f_a, f_b, f_c)
        if f_b == 0:
            return midpoint
        elif math.copysign(1, f_a) != math.copysign(1, f_b):
            upper_bound = midpoint
        elif math.copysign(1, f_c) != math.copysign(1, f_b):
            lower_bound = midpoint

    return midpoint


def mean(x):
    return sum(x) / float(len(x))


def sample_SD(x):
    mean_x = mean(x)
    return math.sqrt(sum([(i - mean_x) ** 2 for i in x]) / float(len(x) - 1))


def pearson(x, y):
    scorex = []
    scorey = []

    mean_x = mean(x)
    mean_y = mean(y)

    sample_SD_x = math.sqrt(sum([(i - mean_x) ** 2 for i in x]) / float(len(x) - 1))
    sample_SD_y = math.sqrt(sum([(j - mean_y) ** 2 for j in y]) / float(len(y) - 1))

    scorex = [(i - mean_x) / sample_SD_x for i in x]

    scorey = [(j - mean_y) / sample_SD_y for j in y]

    # multiplies both lists together into 1 list (hence zip) and sums the whole list
    return sum([i * j for i, j in zip(scorex, scorey)]) / float(len(x) - 1)


def quantile(data, q):
    """
    Returns the value corresponding to the <q> quantile of <data>
    """
    if len(data) > 0:
        return sorted(data)[min(len(data) - 1, max(0, int(round(len(data) * q))))]
    else:
        print(data)
        return None


def quantiles(data):
    """
    Returns a pandas Series of the quantiles of data in <data>. Quantiles start at 1 / (len(data) + 1) and
    end at len(data) / (len(data) + 1) to avoid singularities at the 0 and 1 quantiles.
    to prevent
    :param data:
    :return:
    """
    sort_indices = numpy.argsort(data)
    quants = pandas.Series(numpy.zeros(len(data)))
    quants.index = data.index
    quants[sort_indices] = (numpy.arange(len(data)) + 1) / float(len(data) + 1)
    return quants


def gaussian_norm(data):
    """
    Quantile normalizes the given data to a standard Gaussian distribution
    :param data:
    :return:
    """
    quants = quantiles(data)
    std_normal = scipy.stats.norm(loc=0, scale=1)
    normed = pandas.Series([std_normal.ppf(x) for x in quants])
    normed.index = data.index
    return normed


def de_norm(quants, original_data):
    """
    Given a matched vector of quantiles and the original
    :param quants:
    :param original_data:
    :return:
    """
    return original_data.order().iloc[numpy.array(quants * len(quants)).astype(int)]


def degauss(normed_values, original_data):
    """
    Given a Series of values normalized to a standard Gaussian,
    and the original distribution of values, return a de-quantile-normalized Series.
    """
    quants = scipy.stats.norm(loc=0, scale=1).cdf(normed_values)
    return de_norm(quants, original_data)


def qnorm(p, mean=0.0, sd=1.0):
    """
    Modified from the author's original perl code (original comments follow below)
    by dfield@yahoo-inc.com.  May 3, 2004.
 
    Lower tail quantile for standard normal distribution function.
 
    This function returns an approximation of the inverse cumulative
    standard normal distribution function.  I.e., given P, it returns
    an approximation to the X satisfying P = Pr{Z <= X} where Z is a
    random variable from the standard normal distribution.
 
    The algorithm uses a minimax approximation by rational functions
    and the result has a relative error whose absolute value is less
    than 1.15e-9.
 
    Author:      Peter John Acklam
    Time-stamp:  2000-07-19 18:26:14
    E-mail:      pjacklam@online.no
    WWW URL:     http://home.online.no/~pjacklam
    """

    if p <= 0 or p >= 1:
        # The original perl code exits here, we'll throw an exception instead
        raise ValueError("Argument to ltqnorm %f must be in open interval (0,1)" % p)

    # Coefficients in rational approximations.
    a = (-3.969683028665376e+01, 2.209460984245205e+02, \
         - 2.759285104469687e+02, 1.383577518672690e+02, \
         - 3.066479806614716e+01, 2.506628277459239e+00)
    b = (-5.447609879822406e+01, 1.615858368580409e+02, \
         - 1.556989798598866e+02, 6.680131188771972e+01, \
         - 1.328068155288572e+01)
    c = (-7.784894002430293e-03, -3.223964580411365e-01, \
         - 2.400758277161838e+00, -2.549732539343734e+00, \
         4.374664141464968e+00, 2.938163982698783e+00)
    d = (7.784695709041462e-03, 3.224671290700398e-01, \
         2.445134137142996e+00, 3.754408661907416e+00)

    # Define break-points.
    plow = 0.02425
    phigh = 1 - plow

    # Rational approximation for lower region:
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        z = (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
            ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)

    # Rational approximation for upper region:
    elif phigh < p:
        q = math.sqrt(-2 * math.log(1 - p))
        z = -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
            ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)

    # Rational approximation for central region:
    else:
        q = p - 0.5
        r = q * q
        z = (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
            (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
    # transform to non-standard:
    return mean + z * sd  # !@#$% sorry, just discovered Sep. 9, 2011


def SEP(n, p):
    """
    Returns the standard error of the proportion.
    """
    return math.sqrt(p * (1 - p) / float(n))


def iround(x):
    """iround(number) -> integer
    Round a number to the nearest integer.
    Author: Gribouillis on daniweb.com
    """
    y = round(float(x)) - 0.5
    return int(y) + (y > 0)


def round_sig(number, n):
    """
    Rounds <number> to <n> significant figures
    """
    if number == 0:
        return 0
    else:
        return round(number, -int(math.floor(math.log10(abs(number)))) + (n - 1))


def datecode(delimiter='', month_type='num'):
    """
    Returns a string containing the current year, month and day, optionally separated by <delimiter>
    """
    n = datetime.datetime.now()

    if month_type == 'num':
        mon = '{:02}'.format(n.month)
    elif month_type == 'short':
        mon = calendar.month_abbr[n.month]
    elif month_type == 'long':
        mon = calendar.month_name[n.month]
    else:
        raise ValueError("Invalid value {} for parameter <month_type>".format(month_type))

    return delimiter.join(('{:02}'.format(n.year), mon, '{:02}'.format(n.day)))


def filter_file_list(path, file_list=[], endswith=''):
    """
    Returns the members of <file_list> that:
        1. Exist in <path>
            and
        2. Have size > 0
        3. Ends with <endswith>, if specified
        
    If no <file_list)> is given, return every file in the list that has size > 0
    """
    if not file_list:
        file_list = os.listdir(path)
    return [fname for fname in file_list if
            os.path.isfile(os.path.join(path, fname)) and os.stat(os.path.join(path, fname)).st_size > 0 and (
                not endswith or fname[-len(endswith):] == endswith)]


def prep_curve(x_y_tuples, curve_type):
    """
    Prepares and returns a list of x_y tuples by prepending or appending the appropriate endpoints depending on the curve type.
    
    If <curve_type> is 'ROC', (0,1) and (1,0) points will be added to extend the curve to the corners.
    
    If <curve_type> is 'PR', (0,y_0) and (x_n,0) points will be added, where y_0 is the first y-value (precision)
    and x_n is the last x-value (recall). This has the effect of terminating the ends of the curve with line
    segments directly to the axes.
    
    If <curve_type> is 'plain', no points will be added and only the area under the known points will be calculated (no extrapolation).
    """
    sorted_tuples = sorted(x_y_tuples, key=lambda x: (x[0], -x[1]))

    if curve_type == 'PR':
        if sorted_tuples[0][0] != 0:
            sorted_tuples = [(0, sorted_tuples[0][1])] + sorted_tuples
        if sorted_tuples[-1][1] != 0:
            sorted_tuples += [(sorted_tuples[-1][0], 0)]
    elif curve_type == 'ROC':
        if sorted_tuples[0] != (1, 0):
            sorted_tuples = [(1, 0)] + sorted_tuples
        if sorted_tuples[-1] != (0, 1):
            sorted_tuples += [(0, 1)]
    elif curve_type == 'plain':
        pass
    else:
        raise ValueError('Invalid value for curve_type. Got: {}'.format(curve_type))

    return sorted_tuples


def MCC(TP, TN, FP, FN):
    """
    Returns the Matthews Correlation Coefficient
    """
    return (TP * TN - FP * FN) / math.sqrt((TP + FP) * (TP + FN) * (TN + FP) * (TN + FN))


def AUC(x_y_tuples, curve_type='PR'):
    """
    Given a list of tuples of x-y pairs returns the area under the curve described by those pairs.
    
    If <curve_type> is 'ROC', (0,1) and (1,0) points will be added to extend the curve to the corners.
    
    If <curve_type> is 'PR', (0,y_0) and (x_n,0) points will be added, where y_0 is the first y-value (precision)
    and x_n is the last x-value (recall). This has the effect of terminating the ends of the curve with line
    segments directly to the axes.
    
    If <curve_type> is 'plain', no points will be added and only the area under the known points will be calculated (no extrapolation).
    
    The curve between the points is modeled as a straight line between points.
    """
    sorted_tuples = prep_curve(x_y_tuples, curve_type)

    auc = 0

    for item_idx in range(1, len(sorted_tuples)):
        auc += (sorted_tuples[item_idx - 1][1] + sorted_tuples[item_idx][1]) / 2 * (
            sorted_tuples[item_idx][0] - sorted_tuples[item_idx - 1][0])
    return auc


def rep(string):
    """Generator that yields an infinite supply of the given string"""
    while True:
        yield string


def establish_path(path_to_check, silent=False):
    if not (os.path.isdir(path_to_check) or os.path.isfile(path_to_check) or os.path.islink(path_to_check)):
        if not silent:
            print()
            "Path {} does not exist, creating ...".format(path_to_check)
        path_dirs = []
        p, q = os.path.split(path_to_check)
        # print 'p: {}, q: {}'.format(p, q)
        while p != '/':
            path_dirs.append(q)
            p, q = os.path.split(p)
        #             print 'p: {}, q: {}'.format(p, q)
        path_dirs.append(q)
        path_dirs.append(p)
        partial_path = ''
        #         print path_dirs
        for path_element in path_dirs[::-1]:
            partial_path = os.path.join(partial_path, path_element)
            #             print partial_path
            if not (os.path.isdir(partial_path) or os.path.isfile(partial_path) or os.path.islink(partial_path)):
                os.mkdir(partial_path)
    else:
        if not silent:
            print()
            'Path {} already exists.'.format(path_to_check)


def bootstrap(seq, n):
    """
    Return <n> samples obtained from <seq> by sampling with replacement
    """
    samples = []
    for i in range(n):
        samples.append(random.choice(seq))
    return samples


def flatten_list(nested_list):
    """
    Returns one flat list from a nested list (list of lists)
    Should be easier to comprehend than the syntax of a the nested list comprehension that would otherwise be used
    """
    new_list = []
    for sublist in nested_list:
        for item in sublist:
            new_list.append(item)
    return new_list


def tsv(filename):
    """
    Given the filename of a tsv file, returns a csv.reader object
    """
    try:
        in_file = open(filename, 'rU')
        return csv.reader(in_file, dialect='excel-tab')
    except IOError as io:
        print()
        "I/O error attempting to open {}".format(filename)
        print()
        ", ".join(io.args)
        return None


def convert(input, type):
    """
    Little in-line func to do string-specified type conversions
    """
    if type == 'float':
        return float(input)
    elif type == 'int':
        return int(input)
    elif type == 'str':
        return str(input)
    else:
        return None


def smart_convert(data_string):
    """
    Attempts to convert a raw string into the following data types, returns the first successful:
        int, float, boolean, str
    """
    value = data_string.strip()
    type_list = [int, float]
    for var_type in type_list:
        try:
            converted_var = var_type(value)
            return converted_var
        except ValueError:
            pass
    # No match found
    if value == 'True':
        return True
    if value == 'False':
        return False
    return str(value)


def sliding_mean(a, window_size=1):
    b = numpy.zeros(len(a))
    for i in range(len(a)):
        b[i] = numpy.sum(a[max(0, i - window_size):min(len(a), i + window_size + 1)]) / float(window_size * 2 + 1)
    return b


def freq(input_iterable, case_sensitive=True):
    """
    Returns a dictionary keyed by each item in <input_iterable>, returning a dictionary
    keyed by value holding the number of occurrances of that value.
    """
    freq_dist = {}
    for item in input_iterable:
        if not case_sensitive:
            item = item.lower()
        if item not in freq_dist:
            freq_dist[item] = 1
        else:
            freq_dist[item] += 1
    return freq_dist


def unique(input_iterable, case_sensitive=True):
    """
    Return a list of all unique items in <input_iterable>
    """
    if case_sensitive:
        return list(set(list(input_iterable)))
    else:
        return list(set([i.lower() for i in input_iterable]))


def common_items(iterable_of_iterables):
    """
    Returns the combined intersection of all iterables within <iterable_of_iterables>
    """
    set_list = [set(it) for it in iterable_of_iterables]  # convert to list of sets
    common_items = set(set_list[0])
    for i in range(1, len(set_list)):
        common_items = common_items.intersection(set_list[i])
    return common_items


def clean_string(string, illegal_chars=[' ', '\t', ',', ';', '|'], replacement_char='_'):
    """
    Returns a copy of string that has all non-allowed characters replaced by a new character (default: underscore)
    """
    new_string = string
    for illegal_char in illegal_chars:
        new_string = new_string.replace(illegal_char, replacement_char)
    return new_string


def nCk(n, k):
    """
    Returns the number of combinations of n choose k (binomial coefficient).
    """
    mul = lambda x, y: x * y
    return int(round(reduce(mul, (float(n - i) / (i + 1) for i in range(k)), 1)))


def partial_shuffle(sequence, n=None):
    """
    Efficiently returns n random members of sequence (without replacement)
    """
    if n == None:
        n = len(sequence)
    sequence_copy = list(sequence)
    assert n <= len(sequence_copy)
    draw = []
    for i in range(n):
        r = random.randint(0, len(sequence_copy) - 1)
        # print r, sequence_copy
        draw.append(sequence_copy[r])
        if r == len(sequence_copy) - 1:
            sequence_copy.pop()
        else:
            sequence_copy[r] = sequence_copy.pop()
    return draw


def geomean(iterable):
    """
    Returns the geometric mean (the n-th root of the product of n terms) of an iterable
    """
    n = 0
    first_item = True
    for x in iterable:
        n += 1
        if first_item:
            product = x
            first_item = False
        else:
            product *= x
    return product ** (1 / float(n))


def confusion_matrix(precision, recall, positives, universe):
    """
    Given precision and recall for a test, as well as the number of positive results and the size of the tested space (universe),
    return a dictionary with the expected fraction of true positives, false positives, true negatives and false negatives, as well as their
    absolute numbers given the size of the universe, as well as estimates of the Real Positives and Real Negatives.
    """
    assert recall > 0  # otherwise size of false negatives becomes infinite

    TP = precision * positives
    TPF = TP / float(universe)

    FP = (1 - precision) * positives
    FPF = FP / float(universe)

    TN = universe - TP - FP
    TNF = TN / float(universe)

    FN = TP * (1 - recall) / recall
    FNF = FN / float(universe)

    RP = max(0, min(universe, TP + FN))
    RPF = RP / float(universe)

    RN = universe - RP
    RNF = RN / float(universe)

    TPR = recall

    TNR = TN / float(RN)
    FPR = FP / float(RN)

    return {'TP': TP, 'TPF': TPF, 'FP': FP, 'FPF': FPF, 'TN': TN, 'TNF': TNF, 'FN': FN, 'FNF': FNF, 'RP': RP,
            'RPF': RPF, 'RN': RN, 'RNF': RNF, 'TPR': TPR, 'TNR': TNR, 'specificity': TNR, 'FPR': FPR,
            'sensitivity': recall}


def jaccard(iterable_1, iterable_2):
    s_1 = set(iterable_1)
    s_2 = set(iterable_2)
    return len(s_1.intersection(s_2)) / len(s_1.union(s_2))


def expected_overlap(universe_size, precision_A, recall_A, positives_A, precision_B, recall_B, positives_B,
                     split_values=False, search_space_integration_method='min'):
    """
    Given precision, recall, number of called positives and size of tested space (universe) for two datasets,
    A & B, return the number of expected overlapping values (intersection of positives in A with positives in B).
    
    If split_values is True, return the overlapping true positives and overlapping false positives as a tuple of (Ov_TP, Ov_FP)
    
    Note: the datasets must be filtered to include only the hits present in the intersection of the tested spaces before calculating the
    input parameters - otherwise the results are invalid.
    
    Note: The expectation of overlap assumes conditional independence of the errors of the two datasets - which is rare.
    Dependence will lead to an observed overlap greater than the expectation calculated here.
    
    <search_space_integration_method> specifies the function used to integrate the two estimates of the size of RP and RN
    for the two datasets:
    
    armean = arithmetic mean
    geomean = geometric mean
    min = minimum
    max = maximum
    """
    # print 'recall_A: {}, recall_B:{}'.format(recall_A, recall_B)

    if recall_A == 0 or recall_B == 0:
        return 0
    # print ('recalls are OK')
    matrixA = confusion_matrix(precision_A, recall_A, positives_A, universe_size)
    matrixB = confusion_matrix(precision_B, recall_B, positives_B, universe_size)

    if search_space_integration_method == 'armean':
        consensusRP = (matrixA['RP'] + matrixB['RP']) / 2
        consensusRN = (matrixA['RN'] + matrixB['RN']) / 2
    elif search_space_integration_method == 'geomean':
        # print 'RP:'
        # print matrixA['RP'], matrixB['RP']
        # print 'RN'
        # print matrixA['RN'], matrixB['RN']
        consensusRP = math.sqrt(matrixA['RP'] * matrixB['RP'])
        consensusRN = math.sqrt(matrixA['RN'] * matrixB['RN'])

    elif search_space_integration_method == 'min':
        consensusRP = min(matrixA['RP'], matrixB['RP'])
        consensusRN = min(matrixA['RN'], matrixB['RN'])
    elif search_space_integration_method == 'max':
        consensusRP = max(matrixA['RP'], matrixB['RP'])
        consensusRN = max(matrixA['RN'], matrixB['RN'])
    else:
        raise ValueError(
                "Invalid argument for search_space_integration_method: {}".format(search_space_integration_method))

    overlapsTP = recall_A * recall_B * consensusRP
    overlapsFP = matrixA['FPR'] * matrixB['FPR'] * consensusRN

    if split_values:
        return overlapsTP, overlapsFP
    else:
        # print overlapsTP + overlapsFP

        return overlapsTP + overlapsFP


def expected_overlap_FDR(precision_A, recall_A, positives_A, FDR_A, precision_B, recall_B, positives_B, FDR_B):
    """
    """
    expected_overlap_A = positives_A * precision_B * recall_A + positives_A * (1 - precision_B) * FDR_A
    # expected_overlap_B = positives_B * precision_A * recall_B + positives_B * (1 - precision_A) * FDR_B
    return expected_overlap_A  # , expected_overlap_B


def group_iter(lst, n):
    """group([0,3,4,10,2,3], 2) => iterator

    Group an iterable into an n-tuples iterable. Incomplete tuples
    are discarded e.g.

    >>> list(group(range(10), 3))
    [(0, 1, 2), (3, 4, 5), (6, 7, 8)]

    Author: Brian Quinlan
    Date: 2004
    URL: http://code.activestate.com/recipes/303060-group-a-list-into-sequential-n-tuples/
    """
    return zip(*[itertools.islice(lst, i, None, n) for i in range(n)])


def reshape(seq, how):
    """Reshape the sequence according to the template in ``how``.

    Examples
    ========

    >>> from sympy.utilities import reshape
    >>> seq = range(1, 9)

    >>> reshape(seq, [4]) # lists of 4
    [[1, 2, 3, 4], [5, 6, 7, 8]]

    >>> reshape(seq, (4,)) # tuples of 4
    [(1, 2, 3, 4), (5, 6, 7, 8)]

    >>> reshape(seq, (2, 2)) # tuples of 4
    [(1, 2, 3, 4), (5, 6, 7, 8)]

    >>> reshape(seq, (2, [2])) # (i, i, [i, i])
    [(1, 2, [3, 4]), (5, 6, [7, 8])]

    >>> reshape(seq, ((2,), [2])) # etc....
    [((1, 2), [3, 4]), ((5, 6), [7, 8])]

    >>> reshape(seq, (1, [2], 1))
    [(1, [2, 3], 4), (5, [6, 7], 8)]

    >>> reshape(tuple(seq), ([[1], 1, (2,)],))
    (([[1], 2, (3, 4)],), ([[5], 6, (7, 8)],))

    >>> reshape(tuple(seq), ([1], 1, (2,)))
    (([1], 2, (3, 4)), ([5], 6, (7, 8)))

    >>> reshape(range(12), [2, [3, set([2])], (1, (3,), 1)])
    [[0, 1, [2, 3, 4, set([5, 6])], (7, (8, 9, 10), 11)]]

    Author: Chris Smith
    Date: 14 Sep 2012
    URL: http://code.activestate.com/recipes/578262-reshape-a-sequence/
    """
    m = sum(flatten(how))
    n, rem = divmod(len(seq), m)
    if m < 0 or rem:
        raise ValueError('template must sum to positive number '
                         'that divides the length of the sequence')
    i = 0
    how_type = type(how)
    rv = [None] * n
    for k in range(len(rv)):
        rv[k] = []
        for hi in how:
            if type(hi) is int:
                rv[k].extend(seq[i: i + hi])
                i += hi
            else:
                n = sum(flatten(hi))
                hi_type = type(hi)
                rv[k].append(hi_type(reshape(seq[i: i + n], hi)[0]))
                i += n
        rv[k] = how_type(rv[k])
    return type(seq)(rv)


def group(iterator, n=2, partial_final_item=False):
    """ Given an iterator, it returns sub-lists made of n items
    (except the last that can have len < n)
    inspired by http://countergram.com/python-group-iterator-list-function

    Author: Sandro Tosi
    Date: 11 Apr 2011
    URL: http://sandrotosi.blogspot.com/2011/04/python-group-list-in-sub-lists-of-n.html
    Modified slightly with option to return partial final items or not by Dylan Skola Oct 02, 2014
    """
    accumulator = []
    for item in iterator:
        accumulator.append(item)
        if len(accumulator) == n:  # tested as fast as separate counter
            yield accumulator
            accumulator = []  # tested faster than accumulator[:] = []
            # and tested as fast as re-using one list object
    if len(accumulator) != 0 and (len(accumulator) == n or partial_final_item):
        yield accumulator


def finite_difference(signal):
    output = numpy.zeros(len(signal))
    for i in range(len(signal) - 1):
        output[i] = signal[i + 1] - signal[i]
    return output


def find_0_crossings(signal, start_pos, rising_falling=''):
    """
    Find all indices at which the <signal> vector crosses the 0 axis.

    If <rising_falling> is 'rising', report only ascending crossings of the 0 axis
    If <rising_falling> is 'falling', report only descending crossings of the 0 axis
    """
    if rising_falling:
        assert rising_falling in ('rising', 'falling')
    crossings = []
    prev_val = signal[start_pos]
    for i in range(start_pos, len(signal)):
        if rising_falling == 'rising' or not rising_falling:
            if prev_val <= 0 and signal[i] > 0:
                crossings.append(i)
        elif rising_falling == 'falling' or not rising_falling:
            if prev_val >= 0 and signal[i] < 0:
                crossings.append(i)
        prev_val = signal[i]
    return crossings


def merge_dfs(df_sequence):
    """
    Given a sequence of pandas DataFrames, return a DataFrame containing the merged contents
    of the individual DataFrames. That is, column and row indices will be the union of the components,
    and the contents of a cell will be the value appearing earliest in the sequence (if more than
    one non-NaN value exists).
    """
    total_df = df_sequence[0]
    if len(df_sequence) > 1:
        for df in df_sequence[1:]:
            total_df = total_df.combine_first(df)
    return total_df


class Raveller(object):
    """
    Within the context of a hierarchical index structure,
     convert scalar indices to 3-D indices and vice-versa.
    """

    def __init__(self, rows_per_page, cols_per_row):
        self.cols_per_row = cols_per_row
        self.rows_per_page = rows_per_page
        self.items_per_page = self.rows_per_page * self.cols_per_row

    def ravel(self, page, row, col):
        """
        Convert page, row and col address into a scalar index
        """
        assert row < self.rows_per_page
        assert col < self.cols_per_row
        return page * self.items_per_page + row * self.cols_per_row + col

    def unravel(self, index):
        """
        Convert a scalar index into page, row and col address
        """
        page = int(index / self.items_per_page)
        index -= page * self.items_per_page
        row = int(index / self.cols_per_row)
        index -= row * self.cols_per_row
        return page, row, index


def robust_pcc(vector_1, vector_2, return_pval=False):
    """
    Calculates the PCC between <vector_1> and <vector_2> in such a way as to guarantee a result
    under almost any circumstances. That is, it is robust to:
        * NaN values in either vector (positions with a NaN in either vector will be excluded)
        * inappropriate datatype (scipy.stat.pearsonr normally only works on numpy.float64)
    :param vector_1:
    :param vector_2:
    :param return_pval:
    :return:
    """

    if vector_1.dtype != numpy.float64:
        vector_1 = vector_1.astype(numpy.float64)

    if vector_2.dtype != numpy.float64:
        vector_2 = vector_2.astype(numpy.float64)

    non_nan = numpy.nonzero(numpy.equal((1 - numpy.isnan(vector_1)) * (1 - numpy.isnan(vector_2)), True))[0]

    # print non_nan

    pcc_tuple = scipy.stats.pearsonr(vector_1[non_nan], vector_2[non_nan])

    if return_pval:
        return pcc_tuple
    else:
        return pcc_tuple[0]


def remove_nans(vector):
    """
    Simply return a new vector with all NaN values stripped. Easier than masking.
    :param vector:
    :return:
    """
    return vector[numpy.nonzero(numpy.equal(numpy.isnan(vector), False))[0]]


def remove_joint_nans(vector_1, vector_2):
    """
    Returns a pair of vectors consisting of all locations that are Not(NaN in vector 1 AND NaN in vector 2)
    :param vector_1:
    :param vector_2:
    :return:
    """
    non_nans = numpy.nonzero(numpy.equal((1 - numpy.isnan(vector_1)) * (1 - numpy.isnan(vector_2)), True))[0]
    return vector_1[non_nans], vector_2[non_nans]


def random_identifier(length, allowed_chars=ALPHANUMERIC):
    """
    Returns a random alphanumeric identifier
    """
    return ''.join(random.sample(allowed_chars, length))


class MemMap(object):
    def __init__(self, arr, read_only=False, tmp_dir=TMP_DIR):
        establish_path(tmp_dir)
        random_fname = os.path.join(tmp_dir, '{}.npy'.format(random_identifier(32)))
        numpy.save(random_fname, arr=arr)
        self.fname = random_fname
        self.array = numpy.load(random_fname, mmap_mode=('r+', 'r')[read_only])

    def __del__(self):
        try:
            os.remove(self.fname)
        except Exception as ex:
            print()
            'Tried to remove temporary memmap file {} but caught {} instead!'.format(self.fname, ex)


def replace_with_mem_map(arr, read_only=True, tmp_dir=TMP_DIR):
    return MemMap(arr, read_only=True, tmp_dir=TMP_DIR).array


def get_open_fds():
    '''
    return the number of open file descriptors for current process

    .. warning: will only work on UNIX-like os-es.
    '''
    import subprocess

    pid = os.getpid()
    procs = subprocess.check_output(
            ["lsof", '-w', '-Ff', "-p", str(pid)])

    nprocs = len(
            [s for s in procs.split('\n') if s and s[0] == 'f' and s[1:].isdigit()]
    )
    return nprocs


def flexible_split(arr, num_splits, view=True):
    """
    Performs much like numpy.split() but doesn't raise an exception if the array cannot be split perfectly evenly.
    Instead the last sub-array will be of slightly-different size.

    If <num_splits> is greater than the length of <arr>, remaining sub-arrays will be empty.

    If <view> is true, return a list of views into the original array

    :param arr:
    :param num_splits:
    :return:
    """
    l = len(arr)
    offset = iround(l / float(num_splits))
    sub_arrs = []
    for i in range(num_splits):
        start_pos = i * offset
        if i < num_splits - 1:
            end_pos = (i + 1) * offset
        else:
            end_pos = l
        sub_arrs.append(arr[start_pos:end_pos])
    return sub_arrs


def string_compare(string_1, string_2):
    """
    Since Numpy doesn't implement the .equal() ufunc for string arrays, and there doesn't seem to be a built-in
    in the standard libraries, I've created my own for this, though since it loops over the arrays its not very
    performant.

    Returns a boolean array in which the value at each position is equal to the equality of the two strings at the
     corresponding position.

    :param string_1:
    :param string_2:
    :return:
    """
    assert len(string_1) == len(string_2)
    L = len(string_1)
    comparison = numpy.zeros(L, dtype=numpy.bool)
    for i in range(L):
        comparison[i] = string_1[i] == string_2[i]
    return comparison


def sse(vec_1, vec_2):
    return ((vec_1 - vec_2) ** 2).sum()


def mse(vec_1, vec_2):
    return sse(vec_1, vec_2) / float(len(vec_1))


def rmse(vec_1, vec_2):
    return numpy.sqrt(mse(vec_1, vec_2))


class Serializer(object):
    def __init__(self):
        self.cur_index = -1
        self.index_to_name = []
        self.name_to_index = {}

    def add_item(self, name):
        self.cur_index += 1
        self.index_to_name.append(name)
        assert name not in self.name_to_index
        self.name_to_index[name] = self.cur_index
        return self.cur_index

    def get_index(self, name):
        '''
        Return an existing index for <name> if present, otherwise make one and return it.
        :param name:
        :return:
        '''
        if name in self.name_to_index:
            return self.name_to_index[name]
        else:
            self.cur_index += 1
            self.name_to_index[name] = self.cur_index
            self.index_to_name.append(name)
            return self.cur_index


def semi_pcc(x, y, mean_x, mean_y):
    """
    Returns the equivalent of a Pearson Correlation, only with pre-defined means for both vectors.
    """
    e_x = x - mean_x
    e_y = y - mean_y
    return numpy.dot(e_x, e_y) / (numpy.sqrt(numpy.dot(e_x, e_x)) * numpy.sqrt(numpy.dot(e_y, e_y)))


def l2_norm(arr):
    """
    Returns the L2 norm of <arr> much faster than numpy.linalg.norm
    :param x:
    :param y:
    :return:
    """
    return numpy.sqrt(numpy.dot(arr, arr))


def cosine_similarity(x, y):
    """
    Returns the cosine similarity of two vectors
    :param x:
    :param y:
    :return:
    """
    return numpy.dot(x, y) / (l2_norm(x) * l2_norm(y))


def numerical_string_sort(string_iterable, reverse=False):
    """
    Returns a sorted version of <string_iterable> that sorts numerical components of the strings in numerical, not lexicographical order
    """
    digit_parser = re.compile(r'[A-Za-z]+|\d+')

    def maybe_int(s):
        try:
            return int(s)
        except ValueError:
            return s

    return sorted(string_iterable, key=lambda x: [maybe_int(s) for s in re.findall(digit_parser, x)], reverse=reverse)


def unmean(cur_mean, cur_N, value_to_remove):
    """
    Removes the influence of <value_to_remove> from a mean value that currently is calculated
    from <cur_N> samples.

    That is, if <value_to_remove> is the <cur_N>th sample, return what the mean of the 1-(<cur_N>-1)th samples
    must be.
    """
    return cur_mean * (float(cur_N) / float(cur_N - 1)) - (value_to_remove / float(cur_N - 1))


def find_file_gzipped(base_filename, mode='r'):
    """
    Convenience function that looks first for a gzipped version of a file, then a plaintext
    version, and returns a file handle if successful, and None if not.
    :param base_filename:
    :return:
    """
    try:
        return gzip.open(base_filename + '.gz', mode)
    except (IOError, OSError):
        try:
            return open(base_filename, mode)
        except (IOError, OSError):
            return None

def reverse_map_dict(my_dict):
    """
    Assuming that <my_dict> contains iterables of value elements, generate and return a 'reverse-mapped' dictionary from <my_dict>
    such that the new dictionary is keyed by all the value elements that appear in <my_dict> and contains a list of keys
    in the original dictionary that were linked to that value.
    """
    reversed_dict = {}
    for k, v in my_dict.items():
        for element in v:
            if element not in reversed_dict:
                reversed_dict[element] = []
            reversed_dict[element].append(k)
    return reversed_dict


def argmax2d(arr):
    """
    Returns the coordinates of the maximum value in a 2D array-like
    """
    m = float('-Inf')
    m_i = 0
    m_j = 0
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            if arr[i,j] > m:
                m_i=i
                m_j=j
                m=arr[i,j]
    return m_i,m_j
