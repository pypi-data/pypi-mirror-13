import gzip
import math
import os
import pickle
import re
import random
from subprocess import call # ToDo: remove once Python 3.5 available in Anaconda
run = call
import csv

import vcf
import pysam

from pgtools import toolbox

GZIPPED_FASTA=False
GFF_GENE_SOURCES = ['ensembl_havana']
GFF_GENE_IDENTIFIERS = ['gene']

CODON_TABLE = {'GUC': 'V', 'ACC': 'T', 'GUA': 'V', 'GUG': 'V', 'GUU': 'V', 'AAC': 'N', 'CCU': 'P', 'UGG': 'W',
               'AGC': 'S', 'AUC': 'I', 'CAU': 'H', 'AAU': 'N', 'AGU': 'S', 'ACU': 'T', 'CAC': 'H', 'ACG': 'T',
               'CCG': 'P', 'CCA': 'P', 'ACA': 'T', 'CCC': 'P', 'GGU': 'G', 'UCU': 'S', 'GCG': 'A', 'UGC': 'C',
               'CAG': 'Q', 'GAU': 'D', 'UAU': 'Y', 'CGG': 'R', 'UCG': 'S', 'AGG': 'R', 'GGG': 'G', 'UCC': 'S',
               'UCA': 'S', 'GAG': 'E', 'GGA': 'G', 'UAC': 'Y', 'GAC': 'D', 'GAA': 'E', 'AUA': 'I', 'GCA': 'A',
               'CUU': 'L', 'GGC': 'G', 'AUG': 'M', 'CUG': 'L', 'CUC': 'L', 'AGA': 'R', 'CUA': 'L', 'GCC': 'A',
               'AAA': 'K', 'AAG': 'K', 'CAA': 'Q', 'UUU': 'F', 'CGU': 'R', 'CGA': 'R', 'GCU': 'A', 'UGU': 'C',
               'AUU': 'I', 'UUG': 'L', 'UUA': 'L', 'CGC': 'R', 'UUC': 'F', 'UAA': 'X', 'UAG': 'X', 'UGA': 'X'}

ALPHANUMERIC = [chr(i) for i in range(48, 58)] + [chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)]

WHITESPACE = re.compile(r'\s*')


class GenomeSequenceSet(object):
    """
    Computes offsets into a FASTA file for each sequence, then extracts subsequences from the file as needed.

    Assumes all sequences are stored one per file in the specified folder.

    If GZIPPED is True, assume FASTA files are gzipped.
    """
    GZIPPED = True
    FNAME_TEMPLATE = 'Homo_sapiens.GRCh38.dna.chromosome.{}.fa'

    def __init__(self, fasta_folder, gzipped=GZIPPED_FASTA):
        self.offsets = {}
        self.fasta_folder = fasta_folder
        self.gzipped = gzipped

    def extract(self, chrom, start, end):
        """
        Get sequence of a genomic region. Assuming the sequences are stored
        in a separate file per chromosome, we examine the first few lines of the file
        to compute offsets into the file, then read and return the appropriate region.

        If doing this in a high-throughput fashion it may save some time to pre-compute
        the offsets and store them somewhere.
        """
        assert end > start
        # identify file:
        chrom_fname = os.path.join(self.fasta_folder, self.FNAME_TEMPLATE.format(chrom))

        if self.gzipped:
            chrom_fname += '.gz'
            fasta_file = gzip.open(chrom_fname, 'r')
        else:
            fasta_file = open(chrom_fname, 'r')

        # examine the file to determine header line length and data line length (again, assumed constant)
        header = fasta_file.readline()
        header_size = len(header)

        first_line = fasta_file.readline()
        line_size = len(first_line)

        start_loc = compute_fasta_offset(sequence_location=start, header_size=header_size, line_size=line_size)
        end_loc = compute_fasta_offset(sequence_location=end, header_size=header_size, line_size=line_size)

        fasta_file.seek(start_loc)
        seq = fasta_file.read(end_loc - start_loc).replace('\n', '')
        fasta_file.close()
        # print seq

        return seq


def lightweight_gff_parser(gff_fname, sources=[], identifiers=[]):
    """
    Simple GFF parser that returns a list of dictionaries of items matching the selected sources and identifiers
    """
    sources = set(sources)
    identifiers = set(identifiers)

    items = []

    with open(gff_fname, 'r') as gff_file:
        for line in gff_file:
            if line[0] != '#':  # not a header ine
                split_line = line.split('\t')
                source, identifier = split_line[1], split_line[2]
                if source in sources and identifier in identifiers:
                    # if we have a match, process the rest of the line
                    chrom = split_line[0]
                    start = int(split_line[3])
                    end = int(split_line[4])
                    strand = split_line[6]
                    fields = dict(field_value_pair.split('=') for field_value_pair in split_line[8].split(';'))
                    items.append({'chrom': chrom, 'start': start, 'end': end, 'strand': strand, 'fields': fields})
    return items


def gff_to_gene_dict(gff_file, sources=GFF_GENE_SOURCES, identifiers=GFF_GENE_IDENTIFIERS):
    """
    Simple GFF parser that returns a dictionary of genes keyed by Ensembl ID, as well as a translation dictionary
    mapping gene names to Ensembl IDs.
    """
    sources = set(sources)
    identifiers = set(identifiers)

    gene_dict, gene_name_to_ensembl = {}, {}

    for line_num, line in enumerate(gff_file):
        if line[0] != '#':  # not a header ine
            split_line = line.split('\t')
            if len(split_line) < 7:
                print((line_num, split_line))
            source, identifier = split_line[1], split_line[2]
            if source in sources and identifier in identifiers:
                # if we have a match, process the rest of the line

                chrom = split_line[0]
                start = int(split_line[3])
                end = int(split_line[4])

                if split_line[6] == '+':
                    strand = 1
                elif split_line[6] == '-':
                    strand = -1
                else:
                    strand = 0

                fields = dict(field_value_pair.split('=') for field_value_pair in split_line[8].split(';'))
                version = float(fields['version'])
                gene_name = fields['Name']
                ensembl_id = fields['gene_id']

                assert ensembl_id not in gene_dict  # make sure no duplicate ensembl IDs
                gene_dict[ensembl_id] = {'chrom': chrom, 'start': start, 'end': end, 'strand': strand,
                                         'version': version, 'gene_name': gene_name, 'ensembl_id': ensembl_id}

                if gene_name not in gene_name_to_ensembl or version > gene_dict[ensembl_id]['version']:
                    gene_name_to_ensembl[gene_name] = ensembl_id

    return gene_dict, gene_name_to_ensembl


#***********************************************************************************************************************
# Classes for wrapping genome data
#***********************************************************************************************************************

class Genome(object):
    """
    Serves up gene locations and sequences.
    """

    def __init__(self, fasta_folder=FASTA_FOLDER, gff_fname=GFF_FNAME, gene_pickle_fname=GENE_INFO_PICKLE_FNAME,
                 translation_data_pickle_fname=TRANSLATION_DATA_PICKLE_FNAME):
        self.fasta_folder = fasta_folder
        self.gff_fname = gff_fname
        self.gene_pickle_fname = gene_pickle_fname
        self.translation_data_pickle_fname = translation_data_pickle_fname

        # initialize gene names and coordinate data either from pre-generated
        # data or de novo from a GFF file
        gene_pickle_file = toolbox.find_file_gzipped(self.gene_pickle_fname, 'rb')
        translation_data_pickle_file = toolbox.find_file_gzipped(self.translation_data_pickle_fname, 'rb')

        if translation_data_pickle_file is not None and gene_pickle_file is not None:
            print(('Loading gene info from {}'.format(gene_pickle_fname)))
            self.gene_info = pickle.load(gene_pickle_file)
            gene_pickle_file.close()
            print(('Loading name translation data from {}'.format(translation_data_pickle_fname)))
            self.gene_name_to_ensembl = pickle.load(translation_data_pickle_file)
            translation_data_pickle_file.close()
        else:
            print('Generating gene info and translation data from GFF...')
            self.generateDictionaries()
            print('Done.')

        # initialize sequence object
        self.genome_sequence = GenomeSequenceSet(self.fasta_folder)

    def generateDictionaries(self):

        gff_file = toolbox.find_file_gzipped(self.gff_fname, 'r')

        if gff_file is None:
            raise Exception('GFF file not found! Looked for {} and {}'.format(self.gff_fname, self.gff_fname + '.gz'))

        # generate from GFF
        self.gene_info, self.gene_name_to_ensembl = gff_to_gene_dict(gff_file)
        gff_file.close()

        # write out to pickle to save time in future
        with gzip.open(self.gene_pickle_fname + '.gz', 'wb') as gene_pickle_file:
            pickle.dump(self.gene_info, gene_pickle_file, protocol=-1)

        with gzip.open(self.translation_data_pickle_fname + '.gz', 'wb') as translation_data_pickle_file:
            pickle.dump(self.gene_name_to_ensembl, translation_data_pickle_file, protocol=-1)

    def queryByEnsemblId(self, ensembl_id):
        """
        Return a dictionary of information fields about the gene specified
        by the given ensembl_id.

        :param ensembl_id:
        :return:
        """
        return self.gene_info[ensembl_id]

    def queryByGeneName(self, gene_name):
        """
        Returns a dictionary of information fields about the gene specified
        by the given gene name. Returns None if the gene name has no Ensembl ID
        or if the Ensembl ID is not found in the info data.

        :param gene_name:
        :return:
        """
        if gene_name in self.gene_name_to_ensembl:
            ensembl_name = self.gene_name_to_ensembl[gene_name]
            if ensembl_name in self.gene_info:
                return self.gene_info[ensembl_name]
            else:
                return None
        else:
            return None

    def getDNASequence(self, chromosome, start, end, strand):
        """
        Return the sequence of the specified genomic region.
        :param chromosome:
        :param start:
        :param end:
        :param strand:
        :return:
        """
        base_sequence = self.genome_sequence.extract(chrom=chromosome, start=start, end=end)

        if strand == -1:
            return rev_complement(base_sequence)
        else:
            return base_sequence

    def getDNASequenceByName(self, gene_name):
        """
        Returns the genomic sequence of the specified gene name
        :param gene_name:
        :return:
        """
        gene_info = self.queryByGeneName(gene_name)
        return self.getDNASequence(gene_info['chrom'], gene_info['start'], gene_info['end'], gene_info['strand'])


#***********************************************************************************************************************
# Preprocssing VCF file (may not need anymore)
#***********************************************************************************************************************


def filterVCF(vCF, d_tmp=TMP_DIR, quality=None, chromosome=None, position=None, list_gene=None, list_sNP=None, snpSift=SNPSIFT):
    """
    Filter VCF with snpSIFT and store as a new file
    """

    if not (quality is not None or chromosome or position or list_gene or list_sNP): # allow quality=0
        raise ValueError(
            'Must specify 1 filtering critetion from: quality, chromosome, position, list_gene, or list_sNP')

    # Set up file to temporarily hold filtered VCF
    f_tmp = os.path.join(d_tmp, 'filteredVCF')
    # assert not os.path.isfile(f_tmp), '%s already exists' % f_tmp

    # List snpSift command
    list_command = [snpSift, 'filter', '', vCF, '>', f_tmp]

    # Add snpSift filters

    if quality is not None: # allow quality=0
        # Add quality filter
        # print('quality:', quality)
        # TODO: chrX style
        list_command[-4] = '|'.join([list_command[-4], 'QUAL>=%s' % quality])

    if chromosome:
        # Add chromosome filter
        # print('chromosome:', chromosome)
        list_command[-4] = '|'.join([list_command[-4], 'CHROM=\'%s\'' % chromosome])

    if position:
        # Add position filter
        # print('position:', position)
        pos1, pos2 = position.split(':')
        pos1 = int(pos1)
        pos2 = int(pos2)
        # Position 1 must be less than position 2
        assert pos1 < pos2, '-p | --position pos1:pos2 where pos1 < pos2'
        list_command[-4] = '|'.join([list_command[-4], 'POS>%s & POS<%s' % (pos1, pos2)])

    elif list_gene:
        # Add gene filter
        # print('list_gene:', list_gene)
        for i in list_gene:
            list_command[-4] = '|'.join([list_command[-4], 'ANN[*].GENE=\'%s\'' % i])

    elif list_sNP:
        # Add SNP filter
        # print('list_sNP:', list_sNP)
        for i in list_sNP:
            list_command[-4] = '|'.join([list_command[-4], 'ID=\'%s\'' % i])

    # Finalize snpSift filter by trimming the '|' in the beginning and wrapping with quotation
    list_command[-4] = '"' + list_command[-4][1:] + '"'
    # print('list_command:', list_command)

    # Finalize snpSift command
    command = ' '.join(list_command)
    print(('snpSIFT command line:', command))

    # Run snpSift
    run(command, shell=True)

    return f_tmp


def parseVCF(vCF,
             start=False,
             POS=False,
             end=False,
             affected_start=False,
             affected_end=False,
             REF=False,
             ALT=False,
             annotation=False,
             impact=False,
             var_type=False,
             var_subtype=False,
             gene=False,
             feature=False):
    """
    Extract information from the filtered VCF, and return as list of dictionaries for entries
    """

    vcf_reader = vcf.Reader(filename=vCF)

    list_ = []

    for r in vcf_reader:
        dict_ = {}

        if start:
            dict_['start'] = r.start

        if POS:
            dict_['POS'] = r.POS

        if end:
            dict_['end'] = r.end

        if affected_start:
            dict_['affected_start'] = r.affected_start

        if affected_end:
            dict_['affected_end'] = r.affected_end

        if REF:
            dict_['REF'] = r.REF

        if ALT:
            dict_['ALT'] = r.ALT

        if annotation:
            # Sequence ontology
            dict_['annotation'] = set(x.split('|')[1] for x in r.INFO['ANN'])
            # print('annotation:\t%s' % set(x.split('|')[1] for x in r.INFO['ANN']))

        if impact:
            # {HIGH, MODERATE, LOW, MODIFIER}
            dict_['impact'] = set(x.split('|')[2] for x in r.INFO['ANN'])
            # print('impact:\t%s' % set(x.split('|')[2] for x in r.INFO['ANN']))

        if var_type:
            dict_['var_type'] = r.var_type

        if var_subtype:
            dict_['var_subtype'] = r.var_subtype

        if gene:
            dict_['gene'] = set(x.split('|')[3] for x in r.INFO['ANN'])
            # print('gene:\t%s' % set(x.split('|')[3] for x in r.INFO['ANN']))

        if feature:
            dict_['feature'] = set(x.split('|')[5] for x in r.INFO['ANN'])
            # print('feature:\t%s' % set(x.split('|')[5] for x in r.INFO['ANN']))

        list_.append(dict_)

    return list_


class Variants(object):
    """
    Serves up variants from a tabix-indexed VCF file
    """
    # field mappings for various flavors of VCF
    FREE_BAYES = {'core_fields':
                  {0:('chrom', str),
                   1: ('pos', int),
                   3: ('ref', str),
                   4: ('alt', str),
                   5: ('qual', float)},
              'info_position': 7,
              'info_fields':{
                  'PM': ('precious', bool),
                  'NSF': ('frameshift', bool),
                  'NSN': ('nonsense', bool),
                  'NSM': ('missense', bool),
                  'TYPE': ('type', str),
                  'ODDS': ('odds', float)}
              }

    def __init__(self, vcf_filename, field_model=VariantSet.FREE_BAYES):
        self.variant_file = pysam.Tabixfile(vcf_filename)
        self.field_model = field_model

    def _parse_row(self, variant_tuple):
        variant_dict={}
        # get core fields
        for position, (destination, parse_func) in list(self.field_model['core_fields'].items()):
            variant_dict[destination] = parse_func(variant_tuple[position])
        # get info fieds
        split_info = variant_tuple[self.field_model['info_position']].split(';')

        for field_atom in split_info:
            field, value = field_atom.split('=')
            if field in self.field_model['info_fields']:
                destination, parse_func = self.field_model['info_fields'][field]
                variant_dict[destination] = parse_func(value)

        return variant_dict

    def get_variants(self, chrom, start, end):
        variants = []
        for variant_tuple in self.variant_file.fetch(reference=chrom, start=start, end=end, parser=pysam.asTuple()):
            variants.append(self._parse_row(variant_tuple))
        return variants


def vcf_to_bed(filtered_vcf_filename, output_filename):
    """
    Extract information from the filtered VCF, interpret it and store it as a tab-delimited BED file
    """

    vcf_reader = vcf.Reader(filename=filtered_vcf_filename)

    with open(output_filename, 'wt') as outfile:
        dict_writer = csv.DictWriter(outfile,
                                     fieldnames=['chrom', 'start', 'end', 'affected_start', 'affected_end', 'ref', 'qual', 'alt', 'annotation', 'impact', 'var_type', 'var_subtype', 'gene', 'feature'],
                                     dialect=csv.excel_tab)
        for r in vcf_reader:
            row_dict = {}
            row_dict['chrom'] = r.CHROM
            row_dict['start'] = r.start
            # row_dict['POS'] = r.POS
            row_dict['end'] = r.end
            try:
                row_dict['affected_start'] = r.affected_start
                row_dict['affected_end'] = r.affected_end
            except AttributeError:
                pass
            row_dict['ref'] = r.REF
            row_dict['qual'] = r.QUAL
            row_dict['alt'] = r.ALT[0]
            # Sequence ontology
            row_dict['annotation'] = ','.join(x.split('|')[1] for x in r.INFO['ANN'])
            # {HIGH, MODERATE, LOW, MODIFIER}
            row_dict['impact'] = ','.join(x.split('|')[2] for x in r.INFO['ANN'])
            row_dict['var_type'] = r.var_type
            row_dict['var_subtype'] = r.var_subtype
            row_dict['gene'] = ','.join(x.split('|')[3] for x in r.INFO['ANN'])
            row_dict['feature'] = ','.join(x.split('|')[5] for x in r.INFO['ANN'])

            dict_writer.writerow(row_dict)


def bgzip_and_tabix(bed_filename):
    run(['bgzip', bed_filename])
    compressed_filename = bed_filename + '.gz'
    tabix_commands = ['tabix', '-s', '0', '-b', '1', '-e', '2', '-f', compressed_filename]
    # print('tabix command line: {}'.format(' '.join(tabix_commands)))
    run(['tabix', '-s', '1', '-b', '2', '-e', '3', '-f', compressed_filename])

