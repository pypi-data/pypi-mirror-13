
Complex DNA sequences
~~~~~~~~~~~~~~~~~~~~~

More complex sequences (like plasmids) have many annotated pieces and
benefit from other methods. ``sequence.DNA`` has many methods for
accessing and modifying complex sequences.

The following sequence is a plasmid that integrates at the *S.
cerevisiae* HO locus via ends-out integration, inserting the GEV
transactivator from McIsaac et al. 2011:

.. code:: python

    pKL278 = seqio.read_dna('../files_for_tutorial/maps/pMODKan-HO-pACT1GEV.ape')
Sequences have ``.name`` and ``.id`` attributes that are empty string by
default. By convention, you should fill them with appropriate strings
for your use case - the name is a human-readable name while id should be
a unique number or string.

.. code:: python

    pKL278.name  # Raw genbank name field - truncated due to genbank specifications



.. parsed-literal::

    'pMODKan_HO_pACT1GE'



Large sequences have summary representations, useful for getting a
general idea of which sequence you're manipulating

.. code:: python

    pKL278  # The sequence representation - shows ~40 bases on each side.



.. parsed-literal::

    circular dsDNA:
    tcgcgcgtttcggtgatgacggtgaaaacctctgacacat ... ttaacctataaaaataggcgtatcacgaggccctttcgtc
    agcgcgcaaagccactactgccacttttggagactgtgta ... aattggatatttttatccgcatagtgctccgggaaagcag



Complex sequences usually have annotations to categorize functional or
important elements. This plasmid has a lot of features - it's a yeast
shuttle vector, so it has sequences for propagating in *E. coli*,
sequences for integrating into the *S. cerevisiae* genome, sequences for
selection after transformation, and an expression cassette (promoter,
gene, terminator). In addition, it has common primer sites and annotated
subsequences.

.. code:: python

    pKL278.features  # Man that's way too many features



.. parsed-literal::

    [pGEX_3_primer 'misc_feature' feature (28 to 51) on strand 1,
     pMOD_t1pre 'misc_feature' feature (132 to 154) on strand 0,
     PmeI(1) 'misc_feature' feature (154 to 162) on strand 0,
     HO Targeting 1 'misc_feature' feature (162 to 725) on strand 0,
     pMOD_t1suf 'misc_feature' feature (725 to 755) on strand 0,
     KANMX Wach et al 1994 (genome del. project) 'misc_feature' feature (755 to 1152) on strand 0,
     KanMX CDS 'misc_feature' feature (1152 to 1962) on strand 0,
     KanMX terminator 'misc_feature' feature (1962 to 2200) on strand 0,
     M13 Forward (-47) primer 'primer_bind' feature (2200 to 2224) on strand 0,
     pACT1 'misc_feature' feature (2224 to 2885) on strand 0,
     Extra sequence not found in Gottschling map 'misc_feature' feature (2921 to 2932) on strand 0,
     GAL4(1-93) DBD 'misc_feature' feature (2940 to 3218) on strand 0,
     Differs from Gottschling map (backbone) 'misc_feature' feature (3218 to 3219) on strand 0,
     hER HBD 'misc_feature' feature (3255 to 4140) on strand 0,
     HSV1 VP16 'misc_feature' feature (4140 to 4344) on strand 0,
     Differs from Gottschling Map 'misc_feature' feature (4235 to 4236) on strand 0,
     stop codon 'misc_feature' feature (4344 to 4347) on strand 0,
     L2 'misc_feature' feature (4347 to 4377) on strand 0,
     T + pBluescript KS linker 'misc_feature' feature (4377 to 4399) on strand 0,
     CYC1 'terminator' feature (4403 to 4643) on strand 0,
     pYESTrp_rev primer 'primer_bind' feature (4412 to 4431) on strand 1,
     T7 EEV primer 'primer_bind' feature (4643 to 4665) on strand 0,
     upstream HO targeting 'misc_feature' feature (4665 to 5571) on strand 0,
     PmeI 'misc_feature' feature (5571 to 5579) on strand 0,
     PmeI site 'misc_feature' feature (5571 to 5579) on strand 0,
     M13R 'misc_feature' feature (5579 to 5619) on strand 0,
     origin-extended 'misc_feature' feature (5804 to 5889) on strand 0,
     ori 'misc_feature' feature (5889 to 6744) on strand 0,
     is a g in normal maps. 'misc_feature' feature (6426 to 6427) on strand 0,
     bla 'misc_feature' feature (6744 to 7605) on strand 0,
     AmpR promoter 'misc_feature' feature (7605 to 7684) on strand 0,
     New Feature 'misc_feature' feature (7684 to 7704) on strand 0]



With all of these features, manual slicing is inconvenient. The
``.extract()`` method makes it easy to isolate features from a complex
sequence:

.. code:: python

    # The beta-lactamase coding sequence, essential for propagation in *E. coli* on Amp/Carb media.
    # Note that it is transcribed in the direction of the bottom strand (right to left on this sequence)
    pKL278.extract('bla')



.. parsed-literal::

    linear dsDNA:
    ttaccaatgcttaatcagtgaggcacctatctcagcgatc ... aaaagggaataagggcgacacggaaatgttgaatactcat
    aatggttacgaattagtcactccgtggatagagtcgctag ... ttttcccttattcccgctgtgcctttacaacttatgagta



The ``.features`` attribute is just a list of ``sequence.Feature``
objects - you can add or remove them at will using standard python list
methods (like ``.pop`` and ``.append``). The use of ``sequence.Feature``
will be covered in a different tutorial.

In addition, you can efficiently match patterns in your sequence using
``.locate()``, which searches for a string on both the top and bottom
strands, returning a tuple containing the indexes of the matches (top
and bottom strands). In the following case, there are 8 matches for the
top strand and 5 for the bottom strand. In the case of a palindromic
query, only the top strand is reported.

.. code:: python

    pKL278.locate('atgcc')  # All occurrences of the pattern atgcc on the top and bottom strands (both 5'->3')



.. parsed-literal::

    [[78, 286, 1380, 2431, 4177, 4315, 7261, 7556], [737, 3718, 3828, 4131, 6939]]



Other methods
~~~~~~~~~~~~~

There are additional methods that can't be (easily) demonstrated in this
tutorial.

The ``.ape()`` method will launch ApE with your sequence if it is found
in your PATH environment variable. This enables some convenient analyses
that are faster with a GUI like simulating a digest or viewing the
general layout of annotations.
