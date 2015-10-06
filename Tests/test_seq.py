# This code is part of the Biopython distribution and governed by its
# license.  Please see the LICENSE file that should have been included
# as part of this package.

from __future__ import print_function
import unittest

import sys
from Bio import Seq
from Bio.Alphabet import IUPAC
from Bio import Alphabet
from Bio.Data.IUPACData import ambiguous_dna_complement, ambiguous_rna_complement
from Bio.Data.IUPACData import ambiguous_dna_values, ambiguous_rna_values
from Bio.Data.CodonTable import TranslationError


if sys.version_info[0] == 3:
    array_indicator = "u"
else:
    array_indicator = "c"


class SeqTest(unittest.TestCase):
    def setUp(self):
        self.s = Seq.Seq("TCAAAAGGATGCATCATG", IUPAC.unambiguous_dna)

    def test_as_string(self):
        """Test converting Seq to string"""
        self.assertEqual("TCAAAAGGATGCATCATG", str(self.s))

    def test_length(self):
        """Test len method on Seq object"""
        self.assertEqual(18, len(self.s))

    def test_first_nucleotide(self):
        """Test getting first nucleotide of Seq"""
        self.assertEqual("T", self.s[0])

    def test_last_nucleotide(self):
        """Test getting last nucleotide of Seq"""
        self.assertEqual("G", self.s[-1])

    def test_slicing(self):
        """Test slicing of Seq"""
        self.assertEqual("AA", str(self.s[3:5]))

    def test_reverse(self):
        """Test reverse using -1 stride"""
        self.assertEqual("GTACTACGTAGGAAAACT", self.s[::-1])

    def test_extract_third_nucleotide(self):
        """Test extracting every third nucleotide (slicing with stride 3)"""
        self.assertEqual("TAGTAA", str(self.s[0::3]))
        self.assertEqual("CAGGTT", str(self.s[1::3]))
        self.assertEqual("AAACCG", str(self.s[2::3]))

    def test_alphabet_letters(self):
        """Test nucleotides in DNA Seq"""
        self.assertEqual("GATC", self.s.alphabet.letters)

    def test_alphabet(self):
        """Test alphabet of derived Seq object"""
        t = Seq.Seq("T", IUPAC.unambiguous_dna)
        u = self.s + t
        self.assertEqual("IUPACUnambiguousDNA()", str(u.alphabet))

    def test_length_concatenated_unambiguous_seq(self):
        """Test length of concatenated Seq object with unambiguous DNA"""
        t = Seq.Seq("T", IUPAC.unambiguous_dna)
        u = self.s + t
        self.assertEqual(19, len(u))

    def test_concatenation_of_seq(self):
        t = Seq.Seq("T", IUPAC.unambiguous_dna)
        u = self.s + t
        self.assertEqual(str(self.s) + "T", str(u))

    def test_concatenation_error(self):
        """Test DNA Seq objects cannot be concatenated with Protein Seq
        objects"""
        with self.assertRaises(TypeError):
            self.s + Seq.Seq("T", IUPAC.protein)

    def test_concatenation_of_ambiguous_and_unambiguous_dna(self):
        """Test concatenated Seq object with ambiguous and unambiguous DNA
        returns ambiguous Seq"""
        t = Seq.Seq("T", IUPAC.ambiguous_dna)
        u = self.s + t
        self.assertEqual("IUPACAmbiguousDNA()", str(u.alphabet))


from Bio.Seq import MutableSeq
import array


class MutableSeqTest(unittest.TestCase):
    def setUp(self):
        self.s = Seq.Seq("TCAAAAGGATGCATCATG", IUPAC.unambiguous_dna)
        self.mutable_s = MutableSeq("TCAAAAGGATGCATCATG", IUPAC.ambiguous_dna)

    def test_mutableseq_creation(self):
        """Test creating MutableSeqs in multiple ways"""
        mutable_s = MutableSeq("TCAAAAGGATGCATCATG", IUPAC.ambiguous_dna)
        self.assertIsInstance(mutable_s, MutableSeq, "Creating MutableSeq")

        mutable_s = self.s.tomutable()
        self.assertIsInstance(mutable_s, MutableSeq, "Converting Seq to mutable")

        array_seq = MutableSeq(array.array(array_indicator, "TCAAAAGGATGCATCATG"),
                               IUPAC.ambiguous_dna)
        self.assertIsInstance(array_seq, MutableSeq, "Creating MutableSeq using array")

    def test_repr(self):
        self.assertEqual("MutableSeq('TCAAAAGGATGCATCATG', IUPACAmbiguousDNA())",
                         repr(self.mutable_s))

    def test_as_string(self):
        self.assertEqual("TCAAAAGGATGCATCATG", str(self.mutable_s))

    def test_length(self):
        self.assertEqual(18, len(self.mutable_s))

    def test_converting_to_immutable(self):
        self.assertIsInstance(self.mutable_s.toseq(), Seq.Seq)

    def test_first_nucleotide(self):
        self.assertEqual('T', self.mutable_s[0])

    def test_setting_slices(self):
        self.assertEqual(MutableSeq('CAAA', IUPAC.ambiguous_dna),
                         self.mutable_s[1:5], "Slice mutable seq")

        self.mutable_s[1:3] = "GAT"
        self.assertEqual(MutableSeq("TGATAAAGGATGCATCATG", IUPAC.ambiguous_dna),
                         self.mutable_s,
                         "Set slice with string and adding extra nucleotide")

        self.mutable_s[1:3] = self.mutable_s[5:7]
        self.assertEqual(MutableSeq("TAATAAAGGATGCATCATG", IUPAC.ambiguous_dna),
                         self.mutable_s, "Set slice with MutableSeq")

        self.mutable_s[1:3] = array.array(array_indicator, "GAT")
        self.assertEqual(MutableSeq("TGATTAAAGGATGCATCATG", IUPAC.ambiguous_dna),
                         self.mutable_s, "Set slice with array")

    def test_setting_item(self):
        self.mutable_s[3] = "G"
        self.assertEqual(MutableSeq("TCAGAAGGATGCATCATG", IUPAC.ambiguous_dna),
                         self.mutable_s)

    def test_deleting_slice(self):
        del self.mutable_s[4:5]
        self.assertEqual(MutableSeq("TCAAAGGATGCATCATG", IUPAC.ambiguous_dna),
                         self.mutable_s)

    def test_deleting_item(self):
        del self.mutable_s[3]
        self.assertEqual(MutableSeq("TCAAAGGATGCATCATG", IUPAC.ambiguous_dna),
                         self.mutable_s)

    def test_appending(self):
        self.mutable_s.append("C")
        self.assertEqual(MutableSeq("TCAAAAGGATGCATCATGC", IUPAC.ambiguous_dna),
                         self.mutable_s)

    def test_inserting(self):
        self.mutable_s.insert(4, "G")
        self.assertEqual(MutableSeq("TCAAGAAGGATGCATCATG", IUPAC.ambiguous_dna),
                         self.mutable_s)

    def test_popping_last_item(self):
        self.assertEqual("G", self.mutable_s.pop())

    def test_remove_items(self):
        self.mutable_s.remove("G")
        self.assertEqual(MutableSeq("TCAAAAGATGCATCATG", IUPAC.ambiguous_dna),
                         self.mutable_s, "Remove first G")

        self.assertRaises(ValueError, self.mutable_s.remove, 'Z')

    def test_count(self):
        self.assertEqual(7, self.mutable_s.count("A"))

    def test_index(self):
        self.assertEqual(2, self.mutable_s.index("A"))

    def test_reverse(self):
        """Test using reverse method"""
        self.mutable_s.reverse()
        self.assertEqual(MutableSeq("GTACTACGTAGGAAAACT", IUPAC.ambiguous_dna),
                         self.mutable_s)

    def test_reverse_with_stride(self):
        """Test reverse using -1 stride"""
        self.assertEqual(MutableSeq("GTACTACGTAGGAAAACT", IUPAC.ambiguous_dna),
                         self.mutable_s[::-1])

    def test_extend_method(self):
        self.mutable_s.extend("GAT")
        self.assertEqual(MutableSeq("TCAAAAGGATGCATCATGGAT", IUPAC.ambiguous_dna),
                         self.mutable_s)

    def test_extend_with_mutable_seq(self):
        self.mutable_s.extend(MutableSeq("TTT", IUPAC.ambiguous_dna))
        self.assertEqual(MutableSeq("TCAAAAGGATGCATCATGTTT", IUPAC.ambiguous_dna),
                         self.mutable_s)

    def test_delete_stride_slice(self):
        del self.mutable_s[4:6-1]
        self.assertEqual(MutableSeq("TCAAAGGATGCATCATG", IUPAC.ambiguous_dna),
                         self.mutable_s)

    def test_extract_third_nucleotide(self):
        """Test extracting every third nucleotide (slicing with stride 3)"""
        self.assertEqual(MutableSeq("TAGTAA", IUPAC.ambiguous_dna), self.mutable_s[0::3])
        self.assertEqual(MutableSeq("CAGGTT", IUPAC.ambiguous_dna), self.mutable_s[1::3])
        self.assertEqual(MutableSeq("AAACCG", IUPAC.ambiguous_dna), self.mutable_s[2::3])

    def test_set_wobble_codon_to_n(self):
        """Test setting wobble codon to N (set slice with stride 3)"""
        self.mutable_s[2::3] = "N" * len(self.mutable_s[2::3])
        self.assertEqual(MutableSeq("TCNAANGGNTGNATNATN", IUPAC.ambiguous_dna),
                         self.mutable_s)


###########################################################################
s = Seq.Seq("TCAAAAGGATGCATCATG", IUPAC.unambiguous_dna)
t = Seq.Seq("T", IUPAC.ambiguous_dna)
u = s + t
string_seq = MutableSeq("TCAAAAGGATGCATCATG", IUPAC.ambiguous_dna)
array_seq = MutableSeq(array.array(array_indicator, "TCAAAAGGATGCATCATG"),
                       IUPAC.ambiguous_dna)
converted_seq = s.tomutable()
###########################################################################
print("")
print("Testing Seq addition")
print("====================")
dna = [Seq.Seq("ATCG", IUPAC.ambiguous_dna),
       Seq.Seq("gtca", Alphabet.generic_dna),
       Seq.MutableSeq("GGTCA", Alphabet.generic_dna),
       Seq.Seq("CTG-CA", Alphabet.Gapped(IUPAC.unambiguous_dna, "-")),
       "TGGTCA"]
rna = [Seq.Seq("AUUUCG", IUPAC.ambiguous_rna),
       Seq.MutableSeq("AUUCG", IUPAC.ambiguous_rna),
       Seq.Seq("uCAg", Alphabet.generic_rna),
       Seq.MutableSeq("UC-AG", Alphabet.Gapped(Alphabet.generic_rna, "-")),
       Seq.Seq("U.CAG", Alphabet.Gapped(Alphabet.generic_rna, ".")),
       "UGCAU"]
nuc = [Seq.Seq("ATCG", Alphabet.generic_nucleotide), "UUUTTTACG"]
protein = [Seq.Seq("ATCGPK", IUPAC.protein),
           Seq.Seq("atcGPK", Alphabet.generic_protein),
           Seq.Seq("T.CGPK", Alphabet.Gapped(IUPAC.protein, ".")),
           Seq.Seq("T-CGPK", Alphabet.Gapped(IUPAC.protein, "-")),
           Seq.Seq("MEDG-KRXR*", Alphabet.Gapped(Alphabet.HasStopCodon(IUPAC.extended_protein, "*"), "-")),
           Seq.MutableSeq("ME-K-DRXR*XU", Alphabet.Gapped(Alphabet.HasStopCodon(IUPAC.extended_protein, "*"), "-")),
           Seq.Seq("MEDG-KRXR@", Alphabet.HasStopCodon(Alphabet.Gapped(IUPAC.extended_protein, "-"), "@")),
           Seq.Seq("ME-KR@", Alphabet.HasStopCodon(Alphabet.Gapped(IUPAC.protein, "-"), "@")),
           Seq.Seq("MEDG.KRXR@", Alphabet.Gapped(Alphabet.HasStopCodon(IUPAC.extended_protein, "@"), ".")),
           "TEDDF"]
for a in dna + rna:
    for b in nuc:
        c = a + b
        assert str(c) == str(a) + str(b)
for a in rna:
    for b in rna:
        try:
            c = a + b
            assert str(c) == str(a) + str(b)
        except ValueError as e:
            print("%s + %s\n-> %s" % (repr(a.alphabet), repr(b.alphabet), str(e)))
for a in dna:
    for b in dna:
        try:
            c = a + b
            assert str(c) == str(a) + str(b)
        except ValueError as e:
            print("%s + %s\n-> %s" % (repr(a.alphabet), repr(b.alphabet), str(e)))
    for b in rna:
        try:
            c = a + b
            assert (isinstance(a, str) or isinstance(b, str)), \
                   "DNA+RNA addition should fail!"
        except TypeError:
            pass
        try:
            c = b + a
            assert (isinstance(a, str) or isinstance(b, str)), \
                   "RNA+DNA addition should fail!"
        except TypeError:
            pass
for a in protein:
    for b in protein:
        try:
            c = a + b
            assert str(c) == str(a) + str(b)
        except ValueError as e:
            print("%s + %s\n-> %s" % (repr(a.alphabet), repr(b.alphabet), str(e)))
    for b in nuc + dna + rna:
        try:
            c = a + b
            assert (isinstance(a, str) or isinstance(b, str)), \
                   "Protein+Nucleotide addition should fail!"
        except TypeError:
            pass
for a in nuc:
    for b in dna + rna + nuc:
        c = a + b
        assert str(c) == str(a) + str(b)
for a in dna + rna + nuc:
    for b in protein:
        try:
            c = a + b
            assert (isinstance(a, str) or isinstance(b, str)), \
                   "Nucleotide+Protein addition should fail!"
        except TypeError:
            pass

###########################################################################
print("")
print("Testing Seq string methods")
print("==========================")
for a in dna + rna + nuc + protein:
    if not isinstance(a, Seq.Seq):
        continue
    assert str(a.strip()) == str(a).strip()
    assert str(a.lstrip()) == str(a).lstrip()
    assert str(a.rstrip()) == str(a).rstrip()
    assert str(a.lower()) == str(a).lower()
    assert str(a.upper()) == str(a).upper()
    test_chars = ["-", Seq.Seq("-"), Seq.Seq("*"), "-X@"]
    alpha = Alphabet._get_base_alphabet(a.alphabet)
    if isinstance(alpha, Alphabet.DNAAlphabet):
        test_chars.append(Seq.Seq("A", IUPAC.ambiguous_dna))
    if isinstance(alpha, Alphabet.RNAAlphabet):
        test_chars.append(Seq.Seq("A", IUPAC.ambiguous_rna))
    if isinstance(alpha, Alphabet.NucleotideAlphabet):
        test_chars.append(Seq.Seq("A", Alphabet.generic_nucleotide))
    if isinstance(alpha, Alphabet.ProteinAlphabet):
        test_chars.append(Seq.Seq("K", Alphabet.generic_protein))
        test_chars.append(Seq.Seq("K-", Alphabet.Gapped(Alphabet.generic_protein, "-")))
        test_chars.append(Seq.Seq("K@", Alphabet.Gapped(IUPAC.protein, "@")))
        # Setup a clashing alphabet sequence
        b = Seq.Seq("-", Alphabet.generic_nucleotide)
    else:
        b = Seq.Seq("-", Alphabet.generic_protein)
    try:
        print(str(a.strip(b)))
        assert False, "Alphabet should have clashed!"
    except TypeError:
        pass  # Good!

    for chars in test_chars:
        str_chars = str(chars)
        assert str(a.strip(chars)) == str(a).strip(str_chars)
        assert str(a.lstrip(chars)) == str(a).lstrip(str_chars)
        assert str(a.rstrip(chars)) == str(a).rstrip(str_chars)
        assert a.find(chars) == str(a).find(str_chars)
        assert a.find(chars, 2, -2) == str(a).find(str_chars, 2, -2)
        assert a.rfind(chars) == str(a).rfind(str_chars)
        assert a.rfind(chars, 2, -2) == str(a).rfind(str_chars, 2, -2)
        assert a.count(chars) == str(a).count(str_chars)
        assert a.count(chars, 2, -2) == str(a).count(str_chars, 2, -2)
        # Now check splits
        assert [str(x) for x in a.split(chars)] \
               == str(a).split(str(chars))
        assert [str(x) for x in a.rsplit(chars)] \
               == str(a).rsplit(str(chars))
        for max_sep in [0, 1, 2, 999]:
            assert [str(x) for x in a.split(chars, max_sep)] \
                   == str(a).split(str(chars), max_sep)
            assert [str(x) for x in a.rsplit(chars, max_sep)] \
                   == str(a).rsplit(str(chars), max_sep)
del a, alpha, chars, str_chars, test_chars
del dna, rna, nuc, protein
###########################################################################
print("")
print("Checking ambiguous complements")
print("==============================")

# See bug 2380, Bio.Nexus was polluting the dictionary.
assert "-" not in ambiguous_dna_values
assert "?" not in ambiguous_dna_values


def complement(sequence):
    # TODO - Add a complement function to Bio/Seq.py?
    # There is already a complement method on the Seq and MutableSeq objects.
    return Seq.reverse_complement(sequence)[::-1]


def sorted_dict(d):
    """A sorted repr of a dictionary."""
    return "{%s}" % ", ".join("%s: %s" % (repr(k), repr(v))
                              for k, v in sorted(d.items()))

print("")
print("DNA Ambiguity mapping: %s" % sorted_dict(ambiguous_dna_values))
print("DNA Complement mapping: %s" % sorted_dict(ambiguous_dna_complement))
for ambig_char, values in sorted(ambiguous_dna_values.items()):
    compl_values = complement(values)
    print("%s={%s} --> {%s}=%s" %
        (ambig_char, values, compl_values, ambiguous_dna_complement[ambig_char]))
    assert set(compl_values) == set(ambiguous_dna_values[ambiguous_dna_complement[ambig_char]])

print("")
print("RNA Ambiguity mapping: %s" % sorted_dict(ambiguous_rna_values))
print("RNA Complement mapping: %s" % sorted_dict(ambiguous_rna_complement))
for ambig_char, values in sorted(ambiguous_rna_values.items()):
    compl_values = complement(values).replace("T", "U")  # need to help as no alphabet
    print("%s={%s} --> {%s}=%s" %
        (ambig_char, values, compl_values, ambiguous_rna_complement[ambig_char]))
    assert set(compl_values) == set(ambiguous_rna_values[ambiguous_rna_complement[ambig_char]])

print("")
print("Reverse complements:")
for sequence in [Seq.Seq("".join(sorted(ambiguous_rna_values))),
            Seq.Seq("".join(sorted(ambiguous_dna_values))),
            Seq.Seq("".join(sorted(ambiguous_rna_values)), Alphabet.generic_rna),
            Seq.Seq("".join(sorted(ambiguous_dna_values)), Alphabet.generic_dna),
            Seq.Seq("".join(sorted(ambiguous_rna_values)).replace("X", ""), IUPAC.IUPACAmbiguousRNA()),
            Seq.Seq("".join(sorted(ambiguous_dna_values)).replace("X", ""), IUPAC.IUPACAmbiguousDNA()),
            Seq.Seq("AWGAARCKG")]:  # Note no U or T
        print("%s -> %s"
              % (repr(sequence), repr(Seq.reverse_complement(sequence))))
        assert str(sequence) \
           == str(Seq.reverse_complement(Seq.reverse_complement(sequence))), \
           "Dobule reverse complement didn't preserve the sequence!"
print("")

###########################################################################

test_seqs = [s, t, u,
             Seq.Seq("ATGAAACTG"),
             "ATGAAACtg",
             # TODO - Fix ambiguous translation
             # Seq.Seq("ATGAARCTG"),
             # Seq.Seq("AWGAARCKG"),  # Note no U or T
             # Seq.Seq("".join(ambiguous_rna_values)),
             # Seq.Seq("".join(ambiguous_dna_values)),
             # Seq.Seq("".join(ambiguous_rna_values), Alphabet.generic_rna),
             # Seq.Seq("".join(ambiguous_dna_values), Alphabet.generic_dna),
             # Seq.Seq("".join(ambiguous_rna_values), IUPAC.IUPACAmbiguousDNA()),
             # Seq.Seq("".join(ambiguous_dna_values), IUPAC.IUPACAmbiguousRNA()),
             # Seq.Seq("AWGAARCKG", Alphabet.generic_dna),
             Seq.Seq("AUGAAACUG", Alphabet.generic_rna),
             Seq.Seq("ATGAAACTG", IUPAC.unambiguous_dna),
             Seq.Seq("ATGAAA-CTG", Alphabet.Gapped(IUPAC.unambiguous_dna)),
             Seq.Seq("ATGAAACTGWN", IUPAC.ambiguous_dna),
             Seq.Seq("AUGAAACUG", Alphabet.generic_rna),
             Seq.Seq("AUGAAA==CUG", Alphabet.Gapped(Alphabet.generic_rna, "=")),
             Seq.Seq("AUGAAACUG", IUPAC.unambiguous_rna),
             Seq.Seq("AUGAAACUGWN", IUPAC.ambiguous_rna),
             Seq.Seq("ATGAAACTG", Alphabet.generic_nucleotide),
             Seq.Seq("AUGAAACTG", Alphabet.generic_nucleotide),  # U and T
             Seq.MutableSeq("ATGAAACTG", Alphabet.generic_dna),
             Seq.MutableSeq("AUGaaaCUG", IUPAC.unambiguous_rna),
             Seq.Seq("ACTGTCGTCT", Alphabet.generic_protein)]
protein_seqs = [Seq.Seq("ATCGPK", IUPAC.protein),
                Seq.Seq("T.CGPK", Alphabet.Gapped(IUPAC.protein, ".")),
                Seq.Seq("T-CGPK", Alphabet.Gapped(IUPAC.protein, "-")),
                Seq.Seq("MEDG-KRXR*", Alphabet.Gapped(Alphabet.HasStopCodon(IUPAC.extended_protein, "*"), "-")),
                Seq.MutableSeq("ME-K-DRXR*XU", Alphabet.Gapped(Alphabet.HasStopCodon(IUPAC.extended_protein, "*"), "-")),
                Seq.Seq("MEDG-KRXR@", Alphabet.HasStopCodon(Alphabet.Gapped(IUPAC.extended_protein, "-"), "@")),
                Seq.Seq("ME-KR@", Alphabet.HasStopCodon(Alphabet.Gapped(IUPAC.protein, "-"), "@")),
                Seq.Seq("MEDG.KRXR@", Alphabet.Gapped(Alphabet.HasStopCodon(IUPAC.extended_protein, "@"), "."))]

# Sanity test on the test sequence alphabets (see also enhancement bug 2597)
for nucleotide_seq in test_seqs:
    if hasattr(nucleotide_seq, "alphabet"):
        if "U" in str(nucleotide_seq).upper():
            assert not isinstance(nucleotide_seq.alphabet, Alphabet.DNAAlphabet)
        if "T" in str(nucleotide_seq).upper():
            assert not isinstance(nucleotide_seq.alphabet, Alphabet.RNAAlphabet)

print("")
print("Transcribe DNA into RNA")
print("=======================")
for nucleotide_seq in test_seqs:
    try:
        expected = Seq.transcribe(nucleotide_seq)
        assert str(nucleotide_seq).replace("t", "u").replace("T", "U") == str(expected)
        print("%s -> %s"
        % (repr(nucleotide_seq), repr(expected)))
    except ValueError as e:
        expected = None
        print("%s -> %s"
        % (repr(nucleotide_seq), str(e)))
    # Now test the Seq object's method
    if isinstance(nucleotide_seq, Seq.Seq):
        try:
            assert repr(expected) == repr(nucleotide_seq.transcribe())
        except ValueError:
            assert expected is None

for s in protein_seqs:
    try:
        print(Seq.transcribe(s))
        assert False, "Transcription shouldn't work on a protein!"
    except ValueError:
        pass
    if not isinstance(s, Seq.Seq):
        continue  # Only Seq has this method
    try:
        print(s.transcribe())
        assert False, "Transcription shouldn't work on a protein!"
    except ValueError:
        pass

print("")
print("Back-transcribe RNA into DNA")
print("============================")
for nucleotide_seq in test_seqs:
    try:
        expected = Seq.back_transcribe(nucleotide_seq)
        assert str(nucleotide_seq).replace("u", "t").replace("U", "T") == str(expected)
        print("%s -> %s"
        % (repr(nucleotide_seq), repr(expected)))
    except ValueError as e:
        expected = None
        print("%s -> %s"
        % (repr(nucleotide_seq), str(e)))
    # Now test the Seq object's method
    if isinstance(nucleotide_seq, Seq.Seq):
        try:
            assert repr(expected) == repr(nucleotide_seq.back_transcribe())
        except ValueError:
            assert expected is None

for s in protein_seqs:
    try:
        print(Seq.back_transcribe(s))
        assert False, "Back transcription shouldn't work on a protein!"
    except ValueError:
        pass
    if not isinstance(s, Seq.Seq):
        continue  # Only Seq has this method
    try:
        print(s.back_transcribe())
        assert False, "Back transcription shouldn't work on a protein!"
    except ValueError:
        pass

print("")
print("Reverse Complement")
print("==================")
for nucleotide_seq in test_seqs:
    try:
        expected = Seq.reverse_complement(nucleotide_seq)
        print("%s\n-> %s"
        % (repr(nucleotide_seq), repr(expected)))
    except ValueError as e:
        expected = None
        print("%s\n-> %s"
        % (repr(nucleotide_seq), str(e)))
    # Now test the Seq object's method
    # (The MutualSeq object acts in place)
    if isinstance(nucleotide_seq, Seq.Seq):
        try:
            assert repr(expected) == repr(nucleotide_seq.reverse_complement())
            assert repr(expected[::-1]) == repr(nucleotide_seq.complement())
        except ValueError:
            assert expected is None

for s in protein_seqs:
    try:
        print(Seq.reverse_complement(s))
        assert False, "Reverse complement shouldn't work on a protein!"
    except ValueError:
        pass
    # Note that these methods are "in place" for the MutableSeq:
    try:
        print(s.complement())
        assert False, "Complement shouldn't work on a protein!"
    except ValueError:
        pass
    try:
        print(s.reverse_complement())
        assert False, "Reverse complement shouldn't work on a protein!"
    except ValueError:
        pass

print("")
print("Translating")
print("===========")
for nucleotide_seq in test_seqs:
    # Truncate to a whole number of codons to avoid translation warning
    nucleotide_seq = nucleotide_seq[:3 * (len(nucleotide_seq) // 3)]
    try:
        expected = Seq.translate(nucleotide_seq)
        print("%s\n-> %s" % (repr(nucleotide_seq), repr(expected)))
    except (ValueError, TranslationError) as e:
        expected = None
        print("%s\n-> %s" % (repr(nucleotide_seq), str(e)))
    # Now test the Seq object's method
    if isinstance(nucleotide_seq, Seq.Seq):
        try:
            assert repr(expected) == repr(nucleotide_seq.translate())
        except (ValueError, TranslationError):
            assert expected is None
    # Now check translate(..., to_stop=True)
    try:
        short = Seq.translate(nucleotide_seq, to_stop=True)
    except (ValueError, TranslationError) as e:
        short = None
    if expected is not None:
        assert short is not None
        assert str(short) == str(expected.split("*")[0])
    if isinstance(nucleotide_seq, Seq.Seq):
        try:
            assert repr(short) == repr(nucleotide_seq.translate(to_stop=True))
        except (ValueError, TranslationError):
            assert short is None

for s in protein_seqs:
    try:
        print(Seq.translate(s))
        assert False, "Translation shouldn't work on a protein!"
    except ValueError:
        pass
    if not isinstance(s, Seq.Seq):
        continue  # Only Seq has this method
    try:
        print(s.translate())
        assert False, "Translation shouldn't work on a protein!"
    except ValueError:
        pass


misc_stops = "TAATAGTGAAGAAGG"
for nucleotide_seq in [misc_stops, Seq.Seq(misc_stops),
                       Seq.Seq(misc_stops, Alphabet.generic_nucleotide),
                       Seq.Seq(misc_stops, Alphabet.DNAAlphabet()),
                       Seq.Seq(misc_stops, IUPAC.unambiguous_dna)]:
    assert "***RR" == str(Seq.translate(nucleotide_seq))
    assert "***RR" == str(Seq.translate(nucleotide_seq, table=1))
    assert "***RR" == str(Seq.translate(nucleotide_seq, table="SGC0"))
    assert "**W**" == str(Seq.translate(nucleotide_seq, table=2))
    assert "**WRR" == str(Seq.translate(nucleotide_seq,
                                        table='Yeast Mitochondrial'))
    assert "**WSS" == str(Seq.translate(nucleotide_seq, table=5))
    assert "**WSS" == str(Seq.translate(nucleotide_seq, table=9))
    assert "**CRR" == str(Seq.translate(nucleotide_seq,
                                        table='Euplotid Nuclear'))
    assert "***RR" == str(Seq.translate(nucleotide_seq, table=11))
    assert "***RR" == str(Seq.translate(nucleotide_seq, table='Bacterial'))
del misc_stops

for s in protein_seqs:
    try:
        print(Seq.translate(s))
        assert False, "Shouldn't work on a protein!"
    except ValueError:
        pass

assert Seq.translate("TAT") == "Y"
assert Seq.translate("TAR") == "*"
assert Seq.translate("TAN") == "X"
assert Seq.translate("NNN") == "X"

assert Seq.translate("TAt") == "Y"
assert Seq.translate("TaR") == "*"
assert Seq.translate("TaN") == "X"
assert Seq.translate("nnN") == "X"

assert Seq.translate("tat") == "Y"
assert Seq.translate("tar") == "*"
assert Seq.translate("tan") == "X"
assert Seq.translate("nnn") == "X"

for codon in ["TA?", "N-N", "AC_", "Ac_"]:
    try:
        print(Seq.translate(codon))
        assert "Translating %s should have failed" % repr(codon)
    except TranslationError:
        pass

ambig = set(IUPAC.IUPACAmbiguousDNA.letters)
for c1 in ambig:
    for c2 in ambig:
        for c3 in ambig:
            values = set([Seq.translate(a + b + c, table=1)
                          for a in ambiguous_dna_values[c1]
                          for b in ambiguous_dna_values[c2]
                          for c in ambiguous_dna_values[c3]])
            t = Seq.translate(c1 + c2 + c3)
            if t == "*":
                assert values == set("*")
            elif t == "X":
                assert len(values) > 1, \
                    "translate('%s') = '%s' not '%s'" \
                    % (c1 + c2 + c3, t, ",".join(values))
            elif t == "Z":
                assert values == set("EQ")
            elif t == "B":
                assert values == set("DN")
            elif t == "J":
                assert values == set("LI")
            else:
                assert values == set(t)
            # TODO - Use the Bio.Data.IUPACData module for the
            # ambiguous protein mappings?
del t, c1, c2, c3, ambig

print("")
print("Seq's .complement() method")
print("==========================")
for nucleotide_seq in test_seqs:
    if isinstance(nucleotide_seq, Seq.Seq):
        try:
            print("%s -> %s"
            % (repr(nucleotide_seq), repr(nucleotide_seq.complement())))
            assert str(nucleotide_seq.complement()) \
                == str(Seq.reverse_complement(nucleotide_seq))[::-1], \
                "Bio.Seq function and method disagree!"
        except ValueError as e:
            print("%s -> %s"
            % (repr(nucleotide_seq), str(e)))

print("")
print("Seq's .reverse_complement() method")
print("==================================")
for nucleotide_seq in test_seqs:
    if isinstance(nucleotide_seq, Seq.Seq):
        try:
            print("%s -> %s"
            % (repr(nucleotide_seq), repr(nucleotide_seq.reverse_complement())))
            assert str(nucleotide_seq.reverse_complement()) \
                == str(Seq.reverse_complement(nucleotide_seq)), \
                "Bio.Seq function and method disagree!"
        except ValueError as e:
            print("%s -> %s"
            % (repr(nucleotide_seq), str(e)))
