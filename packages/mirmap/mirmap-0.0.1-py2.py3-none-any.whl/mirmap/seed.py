# -*- coding: utf-8 -*-

#
# Copyright (C) 2011-2013 Charles E. Vejnar
#
# This is free software, licensed under the GNU General Public License v3.
# See /LICENSE for more information.
#

"""Target site identification by seed search."""

from mirmap import utils

def is_gu_wobble(b1, b2):
    """
    Check if 2 nts are a GU wobble if the first sequence was reverse
    complemented.
    """
    return (b1 == 'C' and b2 == 'U') or (b1 == 'A' and b2 == 'G')

def find_pairings(target_subseq, mirna_seq, mirna_skip_start, mismatch_end):
    pairing = []
    # last_pairing is updated each time there is a match/GU
    # we can return a pairing without mismatch at the end.
    last_pairing = 0
    nb_mismatches_except_gu_wobbles = 0
    nb_gu_wobbles = 0
    pairing.extend([0] * mirna_skip_start)
    for i in range(len(target_subseq)):
        tb = target_subseq[i]
        mb = mirna_seq[i + mirna_skip_start]
        is_guw = is_gu_wobble(tb, mb)
        if tb == mb or is_guw:
            if is_guw:
                nb_gu_wobbles += 1
            pairing.append(i + mirna_skip_start + 1)
            last_pairing = i + mirna_skip_start
        else:
            nb_mismatches_except_gu_wobbles += 1
            pairing.append(0)

    return (nb_mismatches_except_gu_wobbles, nb_gu_wobbles,
            pairing if mismatch_end else pairing[: last_pairing + 1])

def get_motif_coordinates(end_site, motif_def, pairing,
                          motif_upstream_extension, motif_downstream_extension,
                          min_target_length):
    """
    Returns motif coordinates based on end_site (1-based)
    """
    if motif_def is None:
        motif_def = 'seed'
    if motif_def == 'seed' or motif_def == 'seed_extended':
        mirna_start_pairing = 0
        if motif_def == 'seed':
            for p in pairing:
                if p == 0:
                    mirna_start_pairing += 1
                else:
                    break
        start_motif = end_site - len(pairing) + 1 - motif_upstream_extension
        end_motif = end_site - mirna_start_pairing + motif_downstream_extension
    elif motif_def == 'site':
        start_motif = (end_site - min_target_length + 1 -
                       motif_upstream_extension)
        end_motif = end_site + motif_downstream_extension
    return start_motif, end_motif

class mmSeed(object):
    def __init__(self, target_seq, mirna_seq, min_target_length=None):
        self.target_seq = target_seq.upper()
        self.mirna_seq = mirna_seq.upper()
        self.len_target_seq = len(self.target_seq)
        self.len_mirna_seq = len(self.mirna_seq)
        if min_target_length is None:
            self.min_target_length = self.len_mirna_seq

    def find_potential_targets_with_seed(self, **kwargs):
        """
        Searches for seed(s) in the target sequence.

        Keyword Args:
            mirna_start_pairing (int): Starting position of the seed in the
                miRNA (from the 5').
            allowed_lengths (list): List of seed length(s).
            allowed_gu_wobbles (dict): For each seed length (key), how many GU
                wobbles are allowed (value).
            allowed_mismatches (dict): For each seed length (key), how many
                mismatches are allowed (value).
            take_best (bool): If seed matches are overlapping, taking or not
                the longest.
        """
        defaults = {
            'mirna_start_pairing': 2,
            'allowed_lengths': [6, 7, 8],
            'allowed_gu_wobbles': {
                6: 0,
                7: 1,
                8: 2
            },
            'allowed_mismatches': {
                6: 0,
                7: 0,
                8: 0
            },
            'take_best': False,
        }
        self.__dict__.update(defaults)
        self.__dict__.update(kwargs)

        # Reset
        self.end_sites = []
        self.seed_lengths = []
        self.nb_mismatches_except_gu_wobbles = []
        self.nb_gu_wobbles = []
        self.pairings = []
        # Compute
        target_seq_rc = utils.reverse_complement(self.target_seq)

        # Sliding window (step size 1 of course) on the target sequence with all
        # possible target site. Nucleotide(s) before mirna_start_pairing has to
        # be paired and we stop before the target site is shorter than
        # min_target_length (=>sites length equal to min_target_length are
        # included) i is 0-based

        upper = self.mirna_start_pairing - 1
        lower = self.len_target_seq - self.min_target_length + 1
        for i in range(upper, lower):
            # We start with the longest seed and stop as soon as we find one
            for seed_length in self.allowed_lengths[::-1]:
                target_subseq = target_seq_rc[i: i + seed_length]
                p = find_pairings(target_subseq, self.mirna_seq,
                                  self.mirna_start_pairing - 1, True)
                nb_mismatches_except_gu_wobbles = p[0]
                nb_gu_wobbles = p[1]
                pairing = p[2]

                t_o = (nb_mismatches_except_gu_wobbles <=
                       self.allowed_mismatches[seed_length])
                t_t = nb_gu_wobbles <= self.allowed_gu_wobbles[seed_length]

                if t_o and t_t:
                    # end_site is 1-based and is the end of the target site on
                    # the real (=not the reverse-complemented) target sequence
                    end_site = (self.len_target_seq - i +
                                self.mirna_start_pairing - 1)
                    self.end_sites.append(end_site)
                    self.seed_lengths.append(seed_length)
                    self.nb_mismatches_except_gu_wobbles.append(
                        nb_mismatches_except_gu_wobbles)
                    self.nb_gu_wobbles.append(nb_gu_wobbles)
                    self.pairings.append(pairing)
                    if self.take_best:
                        break
