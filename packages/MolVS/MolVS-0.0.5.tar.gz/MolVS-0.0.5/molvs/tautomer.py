# -*- coding: utf-8 -*-
"""
molvs.tautomer
~~~~~~~~~~~~~~

This module contains tools for enumerating tautomers and determining a canonical tautomer.

:copyright: Copyright 2016 by Matt Swain.
:license: MIT, see LICENSE file for more details.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
import copy
import logging

from rdkit import Chem
from rdkit.Chem.rdchem import BondDir, BondStereo, BondType

from .utils import memoized_property, pairwise

log = logging.getLogger(__name__)


class TautomerTransform(object):
    """Rules to transform one tautomer to another.

    Each TautomerTransform is defined by a SMARTS pattern where the transform involves moving a hydrogen from the first
    atom in the pattern to the last atom in the pattern. By default, alternating single and double bonds along the
    pattern are swapped accordingly to account for the hydrogen movement. If necessary, the transform can instead define
    custom resulting bond orders and also resulting atom charges.
    """

    BONDMAP = {'-': BondType.SINGLE, '=': BondType.DOUBLE, '#': BondType.TRIPLE, ':': BondType.AROMATIC}
    CHARGEMAP = {'+': 1, '0': 0, '-': -1}

    def __init__(self, name, smarts, bonds=(), charges=(), radicals=()):
        """Initialize a TautomerTransform with a name, SMARTS pattern and optional bonds and charges.

        The SMARTS pattern match is applied to a Kekule form of the molecule, so use explicit single and double bonds
        rather than aromatic.

        Specify custom bonds as a string of ``-``, ``=``, ``#``, ``:`` for single, double, triple and aromatic bonds
        respectively. Specify custom charges as ``+``, ``0``, ``-`` for +1, 0 and -1 charges respectively.

        :param string name: A name for this TautomerTransform.
        :param string smarts: SMARTS pattern to match for the transform.
        :param string bonds: Optional specification for the resulting bonds.
        :param string charges: Optional specification for the resulting charges on the atoms.
        """
        self.name = name
        self.tautomer_str = smarts
        self.bonds = [self.BONDMAP[b] for b in bonds]
        self.charges = [self.CHARGEMAP[b] for b in charges]
        # TODO: Raise error (ValueError?) if bonds and charges lists are not the correct length

    @memoized_property
    def tautomer(self):
        return Chem.MolFromSmarts(self.tautomer_str)

    def __repr__(self):
        return 'TautomerTransform({!r}, {!r}, {!r}, {!r}, {!r})'.format(self.name, self.tautomer_str, self.bonds, self.charges)

    def __str__(self):
        return self.name


class TautomerScore(object):
    """A substructure defined by SMARTS and its score contribution to determine the canonical tautomer."""

    def __init__(self, name, smarts, score):
        """Initialize a TautomerScore with a name, SMARTS pattern and score.

        :param name: A name for this TautomerScore.
        :param smarts: SMARTS pattern to match a substructure.
        :param score: The score to assign for this substructure.
        """
        self.name = name
        self.smarts_str = smarts
        self.score = score

    @memoized_property
    def smarts(self):
        return Chem.MolFromSmarts(self.smarts_str)

    def __repr__(self):
        return 'TautomerScore({!r}, {!r}, {!r})'.format(self.name, self.smarts_str, self.score)

    def __str__(self):
        return self.name


#: The default list of TautomerTransforms.
TAUTOMER_TRANSFORMS = (
    TautomerTransform('1,3 (thio)keto/enol f', '[CX4!H0]-[C]=[O,S,Se,Te;X1]'),
    TautomerTransform('1,3 (thio)keto/enol r', '[O,S,Se,Te;X2!H0]-[C]=[C]'),
    TautomerTransform('1,5 (thio)keto/enol f', '[CX4,NX3;!H0]-[C]=[C][CH0]=[O,S,Se,Te;X1]'),
    TautomerTransform('1,5 (thio)keto/enol r', '[O,S,Se,Te;X2!H0]-[CH0]=[C]-[C]=[C,N]'),
    TautomerTransform('aliphatic imine f', '[CX4!H0]-[C]=[NX2]'),
    TautomerTransform('aliphatic imine r', '[NX3!H0]-[C]=[CX3]'),
    TautomerTransform('special imine f', '[N!H0]-[C]=[CX3R0]'),
    TautomerTransform('special imine r', '[CX4!H0]-[c]=[n]'),
    TautomerTransform('1,3 aromatic heteroatom H shift f', '[#7!H0]-[#6R1]=[O,#7X2]'),
    TautomerTransform('1,3 aromatic heteroatom H shift r', '[O,#7;!H0]-[#6R1]=[#7X2]'),
    TautomerTransform('1,3 heteroatom H shift', '[#7,S,O,Se,Te;!H0]-[#7X2,#6,#15]=[#7,#16,#8,Se,Te]'),
    TautomerTransform('1,5 aromatic heteroatom H shift', '[#7,#16,#8;!H0]-[#6,#7]=[#6]-[#6,#7]=[#7,#16,#8;H0]'),
    TautomerTransform('1,5 aromatic heteroatom H shift f', '[#7,#16,#8,Se,Te;!H0]-[#6,nX2]=[#6,nX2]-[#6,#7X2]=[#7X2,S,O,Se,Te]'),
    TautomerTransform('1,5 aromatic heteroatom H shift r', '[#7,S,O,Se,Te;!H0]-[#6,#7X2]=[#6,nX2]-[#6,nX2]=[#7,#16,#8,Se,Te]'),
    TautomerTransform('1,7 aromatic heteroatom H shift f', '[#7,#8,#16,Se,Te;!H0]-[#6,#7X2]=[#6,#7X2]-[#6,#7X2]=[#6]-[#6,#7X2]=[#7X2,S,O,Se,Te,CX3]'),
    TautomerTransform('1,7 aromatic heteroatom H shift r', '[#7,S,O,Se,Te,CX4;!H0]-[#6,#7X2]=[#6]-[#6,#7X2]=[#6,#7X2]-[#6,#7X2]=[NX2,S,O,Se,Te]'),
    TautomerTransform('1,9 aromatic heteroatom H shift f', '[#7,O;!H0]-[#6,#7X2]=[#6,#7X2]-[#6,#7X2]=[#6,#7X2]-[#6,#7X2]=[#6,#7X2]-[#6,#7X2]=[#7,O]'),
    TautomerTransform('1,11 aromatic heteroatom H shift f', '[#7,O;!H0]-[#6,nX2]=[#6,nX2]-[#6,nX2]=[#6,nX2]-[#6,nX2]=[#6,nX2]-[#6,nX2]=[#6,nX2]-[#6,nX2]=[#7X2,O]'),
    TautomerTransform('furanone f', '[O,S,N;!H0]-[#6r5]=[#6X3r5;$([#6]([#6r5])=[#6r5])]'),
    TautomerTransform('furanone r', '[#6r5!H0;$([#6]([#6r5])[#6r5])]-[#6r5]=[O,S,N]'),
    TautomerTransform('keten/ynol f', '[C!H0]=[C]=[O,S,Se,Te;X1]', bonds='#-'),
    TautomerTransform('keten/ynol r', '[O,S,Se,Te;!H0X2]-[C]#[C]', bonds='=='),
    TautomerTransform('ionic nitro/aci-nitro f', '[C!H0]-[N+;$([N][O-])]=[O]'),
    TautomerTransform('ionic nitro/aci-nitro r', '[O!H0]-[N+;$([N][O-])]=[C]'),
    TautomerTransform('oxim/nitroso f', '[O!H0]-[N]=[C]'),
    TautomerTransform('oxim/nitroso r', '[C!H0]-[N]=[O]'),
    TautomerTransform('oxim/nitroso via phenol f', '[O!H0]-[N]=[C]-[C]=[C]-[C]=[OH0]'),
    TautomerTransform('oxim/nitroso via phenol r', '[O!H0]-[c]=[c]-[c]=[c]-[N]=[OH0]'),
    TautomerTransform('cyano/iso-cyanic acid f', '[O!H0]-[C]#[N]', bonds='=='),
    TautomerTransform('cyano/iso-cyanic acid r', '[N!H0]=[C]=[O]', bonds='#-'),
    # TautomerTransform('formamidinesulfinic acid f', '[O,N;!H0]-[C]=[S,Se,Te]=[O]', bonds='=--'),  # TODO: WAT!?
    # TautomerTransform('formamidinesulfinic acid r', '[O!H0]-[S,Se,Te]-[C]=[O,N]', bonds='=--'),
    TautomerTransform('isocyanide f', '[C-0!H0]#[N+0]', bonds='#', charges='-+'),
    TautomerTransform('isocyanide r', '[N+!H0]#[C-]', bonds='#', charges='-+'),
    TautomerTransform('phosphonic acid f', '[OH]-[PH0]', bonds='='),
    TautomerTransform('phosphonic acid r', '[PH]=[O]', bonds='-'),
)

#: The default list of TautomerScores.
TAUTOMER_SCORES = (
    TautomerScore('benzoquinone', '[#6]1([#6]=[#6][#6]([#6]=[#6]1)=,:[N,S,O])=,:[N,S,O]', 25),
    TautomerScore('oxim', '[#6]=[N][OH]', 4),
    TautomerScore('C=O', '[#6]=,:[#8]', 2),
    TautomerScore('N=O', '[#7]=,:[#8]', 2),
    TautomerScore('P=O', '[#15]=,:[#8]', 2),
    TautomerScore('C=hetero', '[#6]=[!#1;!#6]', 1),
    TautomerScore('methyl', '[CX4H3]', 1),
    TautomerScore('guanidine terminal=N', '[#7][#6](=[NR0])[#7H0]', 1),
    TautomerScore('guanidine endocyclic=N', '[#7;R][#6;R]([N])=[#7;R]', 2),
    TautomerScore('aci-nitro', '[#6]=[N+]([O-])[OH]', -4),
)

#: The default value for the maximum number of tautomers to enumerate, a limit to prevent combinatorial explosion.
MAX_TAUTOMERS = 1000


class TautomerCanonicalizer(object):
    """

    """

    def __init__(self, transforms=TAUTOMER_TRANSFORMS, scores=TAUTOMER_SCORES, max_tautomers=MAX_TAUTOMERS):
        """

        :param transforms: A list of TautomerTransforms to use to enumerate tautomers.
        :param scores: A list of TautomerScores to use to choose the canonical tautomer.
        :param max_tautomers: The maximum number of tautomers to enumerate, a limit to prevent combinatorial explosion.
        """
        self.transforms = transforms
        self.scores = scores
        self.max_tautomers = max_tautomers

    def __call__(self, mol):
        """Calling a TautomerCanonicalizer instance like a function is the same as calling its canonicalize(mol) method."""
        return self.canonicalize(mol)

    def canonicalize(self, mol):
        """Return a canonical tautomer by enumerating and scoring all possible tautomers.

        :param mol: The input molecule.
        :type mol: :rdkit:`Mol <Chem.rdchem.Mol-class.html>`
        :return: The canonical tautomer.
        :rtype: :rdkit:`Mol <Chem.rdchem.Mol-class.html>`
        """
        # TODO: Overload the mol parameter to pass a list of pre-enumerated tautomers
        tautomers = self._enumerate_tautomers(mol)
        if len(tautomers) == 1:
            return tautomers[0]
        # Calculate score for each tautomer
        highest = None
        for t in tautomers:
            smiles = Chem.MolToSmiles(t, isomericSmiles=True)
            log.debug('Tautomer: %s', smiles)
            score = 0
            # Add aromatic ring scores
            ssr = Chem.GetSymmSSSR(t)
            for ring in ssr:
                btypes = {t.GetBondBetweenAtoms(*pair).GetBondType() for pair in pairwise(ring)}
                elements = {t.GetAtomWithIdx(idx).GetAtomicNum() for idx in ring}
                if btypes == {BondType.AROMATIC}:
                    log.debug('Score +100 (aromatic ring)')
                    score += 100
                    if elements == {6}:
                        log.debug('Score +150 (carbocyclic aromatic ring)')
                        score += 150
            # Add SMARTS scores
            for tscore in self.scores:
                for match in t.GetSubstructMatches(tscore.smarts):
                    log.debug('Score %+d (%s)', tscore.score, tscore.name)
                    score += tscore.score
            # Add (P,S,Se,Te)-H scores
            for atom in t.GetAtoms():
                if atom.GetAtomicNum() in {15, 16, 34, 52}:
                    hs = atom.GetTotalNumHs()
                    if hs:
                        log.debug('Score %+d (%s-H bonds)', -hs, atom.GetSymbol())
                        score -= hs
            # Set as highest if score higher or if score equal and smiles comes first alphabetically
            if not highest or highest['score'] < score or (highest['score'] == score and smiles < highest['smiles']):
                log.debug('New highest tautomer: %s (%s)', smiles, score)
                highest = {'smiles': smiles, 'tautomer': t, 'score': score}
        return highest['tautomer']

    @memoized_property
    def _enumerate_tautomers(self):
        return TautomerEnumerator(self.transforms, self.max_tautomers)


class TautomerEnumerator(object):
    """

    """

    def __init__(self, transforms=TAUTOMER_TRANSFORMS, max_tautomers=MAX_TAUTOMERS):
        """

        :param transforms: A list of TautomerTransforms to use to enumerate tautomers.
        :param max_tautomers: The maximum number of tautomers to enumerate (limit to prevent combinatorial explosion).
        """
        self.transforms = transforms
        self.max_tautomers = max_tautomers

    def __call__(self, mol):
        """Calling a TautomerEnumerator instance like a function is the same as calling its enumerate(mol) method."""
        return self.enumerate(mol)

    def enumerate(self, mol):
        """Enumerate all possible tautomers and return them as a list.

        :param mol: The input molecule.
        :type mol: :rdkit:`Mol <Chem.rdchem.Mol-class.html>`
        :return: A list of all possible tautomers of the molecule.
        :rtype: list of :rdkit:`Mol <Chem.rdchem.Mol-class.html>`
        """
        smiles = Chem.MolToSmiles(mol, isomericSmiles=True)
        tautomers = {smiles: copy.deepcopy(mol)}
        # Create a kekulized form of the molecule to match the SMARTS against
        kekulized = copy.deepcopy(mol)
        Chem.Kekulize(kekulized)
        kekulized = {smiles: kekulized}
        done = set()
        while len(tautomers) < self.max_tautomers:
            for tsmiles in sorted(tautomers):
                if tsmiles in done:
                    continue
                for transform in self.transforms:
                    for match in kekulized[tsmiles].GetSubstructMatches(transform.tautomer):
                        # log.debug('Matched rule: %s to %s for %s', transform.name, tsmiles, match)
                        # Create a copy of in the input molecule so we can modify it
                        # Use kekule form so bonds are explicitly single/double instead of aromatic
                        product = copy.deepcopy(kekulized[tsmiles])
                        # Remove a hydrogen from the first matched atom and add one to the last
                        first = product.GetAtomWithIdx(match[0])
                        last = product.GetAtomWithIdx(match[-1])
                        # log.debug('%s: H%s -> H%s' % (first.GetSymbol(), first.GetTotalNumHs(), first.GetTotalNumHs() - 1))
                        # log.debug('%s: H%s -> H%s' % (last.GetSymbol(), last.GetTotalNumHs(), last.GetTotalNumHs() + 1))
                        first.SetNumExplicitHs(max(0, first.GetTotalNumHs() - 1))
                        last.SetNumExplicitHs(last.GetTotalNumHs() + 1)
                        # Remove any implicit hydrogens from the first and last atoms now we have set the count explicitly
                        first.SetNoImplicit(True)
                        last.SetNoImplicit(True)
                        # Adjust bond orders
                        for bi, pair in enumerate(pairwise(match)):
                            if transform.bonds:
                                # Set the resulting bond types as manually specified in the transform
                                # log.debug('%s-%s: %s -> %s' % (product.GetAtomWithIdx(pair[0]).GetSymbol(), product.GetAtomWithIdx(pair[1]).GetSymbol(), product.GetBondBetweenAtoms(*pair).GetBondType(), transform.bonds[bi]))
                                product.GetBondBetweenAtoms(*pair).SetBondType(transform.bonds[bi])
                            else:
                                # If no manually specified bond types, just swap single and double bonds
                                current_bond_type = product.GetBondBetweenAtoms(*pair).GetBondType()
                                product.GetBondBetweenAtoms(*pair).SetBondType(BondType.DOUBLE if current_bond_type == BondType.SINGLE else BondType.SINGLE)
                                # log.debug('%s-%s: %s -> %s' % (product.GetAtomWithIdx(pair[0]).GetSymbol(), product.GetAtomWithIdx(pair[1]).GetSymbol(), current_bond_type, product.GetBondBetweenAtoms(*pair).GetBondType()))
                        # Adjust charges
                        if transform.charges:
                            for ci, idx in enumerate(match):
                                atom = product.GetAtomWithIdx(idx)
                                # log.debug('%s: C%s -> C%s' % (atom.GetSymbol(), atom.GetFormalCharge(), atom.GetFormalCharge() + transform.charges[ci]))
                                atom.SetFormalCharge(atom.GetFormalCharge() + transform.charges[ci])
                        try:
                            Chem.SanitizeMol(product)
                            smiles = Chem.MolToSmiles(product, isomericSmiles=True)
                            log.debug('Applied rule: %s to %s', transform.name, tsmiles)
                            if smiles not in tautomers:
                                log.debug('New tautomer produced: %s' % smiles)
                                kekulized_product = copy.deepcopy(product)
                                Chem.Kekulize(kekulized_product)
                                tautomers[smiles] = product
                                kekulized[smiles] = kekulized_product
                            else:
                                log.debug('Previous tautomer produced again: %s' % smiles)
                        except ValueError:
                            log.debug('ValueError Applying rule: %s', transform.name)
                done.add(tsmiles)
            if len(tautomers) == len(done):
                break
        else:
            log.warn('Tautomer enumeration stopped at maximum %s', self.max_tautomers)
        # Clean up stereochemistry
        for tautomer in tautomers.values():
            Chem.AssignStereochemistry(tautomer, force=True, cleanIt=True)
            for bond in tautomer.GetBonds():
                if bond.GetBondType() == BondType.DOUBLE and bond.GetStereo() > BondStereo.STEREOANY:
                    begin = bond.GetBeginAtomIdx()
                    end = bond.GetEndAtomIdx()
                    for othertautomer in tautomers.values():
                        if not othertautomer.GetBondBetweenAtoms(begin, end).GetBondType() == BondType.DOUBLE:
                            neighbours = tautomer.GetAtomWithIdx(begin).GetBonds() + tautomer.GetAtomWithIdx(end).GetBonds()
                            for otherbond in neighbours:
                                if otherbond.GetBondDir() in {BondDir.ENDUPRIGHT, BondDir.ENDDOWNRIGHT}:
                                    otherbond.SetBondDir(BondDir.NONE)
                            Chem.AssignStereochemistry(tautomer, force=True, cleanIt=True)
                            log.debug('Removed stereochemistry from unfixed double bond')
                            break
        return tautomers.values()


class SayleTautomerEnumerator(object):
    """An alternative tautomer enumeration method based on the algorithm described by Sayle and Delany:
    http://www.daylight.com/meetings/emug99/Delany/taut_html/index.htm

    The Keto/Enol enumeration isn't working properly yet.

    """

    def __init__(self, keto_enol=False, max_tautomers=MAX_TAUTOMERS):
        """

        :param bool keto_enol: Whether to enumerate keto-enol tautomers.
        :param int max_tautomers: The maximum number of tautomers to enumerate (limit to prevent combinatorial explosion).
        """
        self.keto_enol = keto_enol
        self.max_tautomers = max_tautomers

    def __call__(self, mol):
        """Calling a TautomerEnumerator instance like a function is the same as calling its enumerate(mol) method."""
        return self.enumerate(mol)

    def _backtrack(self, atom_classes, bond_classes, levels, num_hydrogens):
        """Backtrack in the search. Remove last assignment and all its propagated assignments."""
        last_atom = levels[-1]['assigned']
        log.debug('Backtrack %s' % last_atom.GetIdx())
        atom_classes[last_atom.GetIdx()] = 'unassigned'
        for pa in levels[-1]['propagated_atoms']:
            if atom_classes[pa.GetIdx()] == 'donor':
                num_hydrogens += 1
            atom_classes[pa.GetIdx()] = 'unassigned'
        for pb in levels[-1]['propagated_bonds']:
            bond_classes[pb.GetIdx()] = 'unassigned'
        levels.pop()

    def _propagate_assignment(self, mol, atom_classes, bond_classes, canon_atoms, num_hydrogens, levels):
        """Propagate the consequences of an assignment to neighbouring bonds and atoms."""
        changed = True
        while changed:
            changed = False
            # Assigning an atom Donor causes all of its bonds to be assigned single
            for atom in mol.GetAtoms():
                if atom_classes[atom.GetIdx()] == 'donor':
                    for bond in atom.GetBonds():
                        if bond_classes[bond.GetIdx()] == 'unassigned':
                            bond_classes[bond.GetIdx()] = 'single'
                            levels[-1]['propagated_bonds'].append(bond)
                            changed = True
                            log.debug('Rule 1: Assign %s - %s single' % (bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()))

            # Any unassigned atom that has all of its bonds assigned single, must be assigned a donor
            for atom in mol.GetAtoms():
                if not atom_classes[atom.GetIdx()] == 'unassigned':
                    continue
                all_bonds_single = True
                for bond in atom.GetBonds():
                    if not bond_classes[bond.GetIdx()] == 'single':
                        all_bonds_single = False
                        break
                if all_bonds_single:
                    atom_classes[atom.GetIdx()] = 'donor'
                    num_hydrogens -= 1
                    levels[-1]['propagated_atoms'].append(atom)
                    changed = True
                    log.debug('Rule 2: Assign %s donor' % atom.GetIdx())

            # Any unassigned atom with an assigned double bond must be assigned an acceptor
            for atom in mol.GetAtoms():
                if not atom_classes[atom.GetIdx()] == 'unassigned':
                    continue
                has_double_bond = False
                for bond in atom.GetBonds():
                    if bond_classes[bond.GetIdx()] == 'double':
                        has_double_bond = True
                        break
                if has_double_bond:
                    atom_classes[atom.GetIdx()] = 'acceptor'
                    levels[-1]['propagated_atoms'].append(atom)
                    changed = True
                    log.debug('Rule 3: Assign %s acceptor' % atom.GetIdx())

            # A hybridized or acceptor atom with assigned double bond assigns all the remaining unassigned bonds single
            for atom in mol.GetAtoms():
                if atom_classes[atom.GetIdx()] not in {'acceptor', 'hybridized'}:
                    continue
                has_double_bond = False
                for bond in atom.GetBonds():
                    if bond_classes[bond.GetIdx()] == 'double':
                        has_double_bond = True
                        break
                if has_double_bond:
                    for bond in atom.GetBonds():
                        if bond_classes[bond.GetIdx()] == 'unassigned':
                            bond_classes[bond.GetIdx()] = 'single'
                            levels[-1]['propagated_bonds'].append(bond)
                            changed = True
                            log.debug('Rule 4: Assign %s - %s single' % (bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()))

            # A hybridized or acceptor atom with a single unassigned bond assigns it double if it doesn't already have one
            for atom in mol.GetAtoms():
                if atom_classes[atom.GetIdx()] not in {'acceptor', 'hybridized'}:
                    continue
                has_double_bond = False
                num_unassigned = 0
                for bond in atom.GetBonds():
                    if bond_classes[bond.GetIdx()] == 'double':
                        has_double_bond = True
                    if bond_classes[bond.GetIdx()] == 'unassigned':
                        num_unassigned += 1
                if not has_double_bond and num_unassigned == 1:
                    for bond in atom.GetBonds():
                        if bond_classes[bond.GetIdx()] == 'unassigned':
                            bond_classes[bond.GetIdx()] = 'double'
                            levels[-1]['propagated_bonds'].append(bond)
                            changed = True
                            log.debug('Rule 5: Assign %s - %s double' % (bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()))

        # An invalid atom type causes the search to backtrack
        invalid = False
        for atom in mol.GetAtoms():
            num_single = 0
            num_double = 0
            num_unassigned = 0
            for bond in atom.GetBonds():
                if bond_classes[bond.GetIdx()] == 'single':
                    num_single += 1
                if bond_classes[bond.GetIdx()] == 'double':
                    num_double += 1
                if bond_classes[bond.GetIdx()] == 'unassigned':
                    num_unassigned += 1

            if atom_classes[atom.GetIdx()] == 'donor':
                if num_double:
                    invalid = True
                    log.debug('Invalid donor')

            if atom_classes[atom.GetIdx()] in {'acceptor', 'hybridized'}:
                if not num_unassigned and not num_double:
                    invalid = True
                    log.debug('Invalid acceptor/hybridized type 1 on %s' % atom.GetIdx())
                if num_double > 1:
                    invalid = True
                    log.debug('Invalid acceptor/hybridized type 2 on %s' % atom.GetIdx())

        # Check to see if we are at a leaf node (i.e. no unassigned atoms left)
        leafnode = True
        for ac in atom_classes:
            if ac == 'unassigned':
                leafnode = False
                break
        if leafnode:
            # Check to make sure there are no unassigned bonds remaining
            # This happens for phenyl rings...
            unassigned_bonds = False
            for i, bc in enumerate(bond_classes):
                if bc == 'unassigned':
                    unassigned_bonds = True
                    log.debug('Randomly assigning single bond')
                    # Randomly assign a single bond, the other bonds will be propagated
                    bond_classes[i] = 'single'
                    break
            if unassigned_bonds:
                for t in self._propagate_assignment(mol, atom_classes, bond_classes, canon_atoms, num_hydrogens, levels):
                    yield t
                return

        if not invalid:
            if leafnode:
                output_mol = copy.deepcopy(mol)
                # NOTE: At this stage, some bonds may still be unassigned. So we rely on RDKit kekulization to fix it?
                for bond in output_mol.GetBonds():
                    if bond_classes[bond.GetIdx()] == 'single':
                        bond.SetBondType(BondType.SINGLE)
                    if bond_classes[bond.GetIdx()] == 'double':
                        bond.SetBondType(BondType.DOUBLE)
                if not num_hydrogens:
                    log.debug('leafnode reached...')
                    try:
                        Chem.SanitizeMol(output_mol)
                        log.debug(Chem.MolToSmiles(output_mol, isomericSmiles=True))
                        yield output_mol
                    except ValueError as e:
                        log.debug(e)
            else:
                # Go to the next unassigned atom
                for t in self._enumerate_r(mol, atom_classes, bond_classes, canon_atoms, num_hydrogens, levels):
                    yield t

    def _enumerate_r(self, mol, atom_classes, bond_classes, canon_atoms, num_hydrogens, levels=None):
        log.debug('enumerate_r')
        if levels is None:
            levels = []
        # Select next lowest canonical unassigned atom
        for atom in canon_atoms:
            if atom_classes[atom.GetIdx()] == 'unassigned':
                if num_hydrogens > 0:
                    # Assign it a hydrogen if there are hydrogens left
                    atom_classes[atom.GetIdx()] = 'donor'
                    num_hydrogens -= 1
                    log.debug('Assigned %s donor' % atom.GetIdx())
                    #tmp_img(m, bond_classes, h_counts)
                else:
                    # Otherwise an acceptor
                    atom_classes[atom.GetIdx()] = 'acceptor'
                    log.debug('Assigned %s acceptor' % atom.GetIdx())
                # Store the atom for backtracking later
                levels.append({'assigned': atom, 'propagated_atoms': [], 'propagated_bonds': []})
                break
        # Check to ensure there are at least enough unassigned atoms left to assign hydrogens to
        num_unassigned = 0
        for atom in canon_atoms:
            if atom_classes[atom.GetIdx()] == 'unassigned':
                num_unassigned += 1
        if num_unassigned < num_hydrogens:
            log.debug('Backtrack!')
            self._backtrack(atom_classes, bond_classes, levels, num_hydrogens)
            return
        if levels:
            for t in self._propagate_assignment(mol, atom_classes, bond_classes, canon_atoms, num_hydrogens, levels):
                yield t
            log.debug('atom_classes: %s' % atom_classes)
            last_atom = levels[-1]['assigned']
            if atom_classes[last_atom.GetIdx()] == 'donor':
                # Change atom to acceptor and continue the search
                atom_classes[last_atom.GetIdx()] = 'acceptor'
                num_hydrogens += 1
                log.debug('Change %s to acceptor' % last_atom.GetIdx())
                for pa in levels[-1]['propagated_atoms']:
                    if atom_classes[pa.GetIdx()] == 'donor':
                        num_hydrogens += 1
                    atom_classes[pa.GetIdx()] = 'unassigned'
                for pb in levels[-1]['propagated_bonds']:
                    bond_classes[pb.GetIdx()] = 'unassigned'
                for t in self._propagate_assignment(mol, atom_classes, bond_classes, canon_atoms, num_hydrogens, levels):
                    yield t
            ('atom_classes: %s' % atom_classes)
            self._backtrack(atom_classes, bond_classes, levels, num_hydrogens)

    def enumerate(self, mol):
        """Enumerate all possible tautomers and return them as a list.

        :param mol: The input molecule.
        :type mol: :rdkit:`Mol <Chem.rdchem.Mol-class.html>`
        :return: A list of all possible tautomers of the molecule.
        :rtype: list of :rdkit:`Mol <Chem.rdchem.Mol-class.html>`
        """
        # Take a copy of the mol, so we can transform it without affecting the input mol (is this necessary?)
        mol = copy.deepcopy(mol)

        # Kekulize to get all bond types as single/double instead of aromatic
        Chem.Kekulize(mol)

        # Convert all hydrogens to implicit, so H removal/addition is auto calculated when bonds are changed
        # Calling SanitizeMol on a resulting tautomer will convert back to standard mix of implicit/explicit
        for atom in mol.GetAtoms():
            atom.SetNumExplicitHs(0)
            atom.SetNoImplicit(False)
            atom.UpdatePropertyCache()

        # Classify atoms as hybridized, donor, acceptor or other
        atom_classes = []
        for atom in mol.GetAtoms():
            an = atom.GetAtomicNum()
            if an == 6:
                if BondType.DOUBLE in {b.GetBondType() for b in atom.GetBonds()}:
                    atom_classes.append('hybridized')
                else:
                    atom_classes.append('other')
            elif an == 7:
                if BondType.DOUBLE in {b.GetBondType() for b in atom.GetBonds()}:
                    atom_classes.append('acceptor')
                elif atom.GetTotalNumHs() > 0:
                    atom_classes.append('donor')
                else:
                    atom_classes.append('other')
            elif an in {8, 16, 34, 52}:
                if BondType.DOUBLE in {b.GetBondType() for b in atom.GetBonds()}:
                    atom_classes.append('acceptor')
                elif atom.GetTotalNumHs() > 0:
                    atom_classes.append('donor')
                else:
                    atom_classes.append('other')
            else:
                atom_classes.append('other')

        # Keto-enol extension
        if self.keto_enol:
            old_atom_classes = copy.copy(atom_classes)
            for atom in mol.GetAtoms():
                if atom.GetAtomicNum() == 6:
                    bond_type_set = {b.GetBondType() for b in atom.GetBonds()}
                    if BondType.DOUBLE in bond_type_set:
                        atom_classes[atom.GetIdx()] = 'acceptor'
                    elif bond_type_set == {BondType.SINGLE} and atom.GetTotalNumHs() > 0:
                        for neighbor in atom.GetNeighbors():
                            nb_class = old_atom_classes[neighbor.GetIdx()]
                            if nb_class in {'donor', 'acceptor', 'hybridized'}:
                                atom_classes[atom.GetIdx()] = 'donor'
                                break

        # Classify bonds as unassigned if neighboured by a donor/acceptor/hybridized atom
        bond_classes = []
        for bond in mol.GetBonds():
            if not atom_classes[bond.GetBeginAtomIdx()] == 'other' and not atom_classes[bond.GetEndAtomIdx()] == 'other':
                bond_classes.append('unassigned')
            else:
                bond_classes.append('assigned')

        # Count hydrogens that are mobile between the donor/acceptor atoms, and set all donor/acceptors to unassigned
        num_hydrogens = 0
        for i, atom_class in enumerate(atom_classes):
            if atom_class == 'donor':
                num_hydrogens += 1
            if atom_class == 'donor' or atom_class == 'acceptor':
                atom_classes[i] = 'unassigned'
        # TODO: Couldn't we just count Hs on first build of atom_classes, and set all donors/acceptors to unassigned?

        # Set all unassigned bonds to single and get get canonical atom rank (This way it is the same for all tautomers)
        for i, bond in enumerate(mol.GetBonds()):
            if bond_classes[i] == 'unassigned':
                bond.SetBondType(BondType.SINGLE)
        rank = list(Chem.CanonicalRankAtoms(mol))

        # Adjust rank: C(other) < N < Te < Se < S < O < C(conjugated ring)
        new_rank = []
        ring_carbons = []
        other_carbons = []
        for i in range(0, mol.GetNumAtoms()):
            potential_atom = mol.GetAtomWithIdx(rank[i])
            if potential_atom.GetAtomicNum() == 6:
                if potential_atom.IsInRing():  # TODO: Further check for aromatic/conjugated?
                    ring_carbons.append(rank[i])
                else:
                    other_carbons.append(rank[i])
        for an in [7, 52, 34, 16, 8]:
            for i in range(0, mol.GetNumAtoms()):
                potential_atom = mol.GetAtomWithIdx(rank[i])
                if potential_atom.GetAtomicNum() == an:
                    new_rank.append(rank[i])
        for i in range(0, m.GetNumAtoms()):
            potential_atom = m.GetAtomWithIdx(rank[i])
            if potential_atom.GetAtomicNum() not in {6, 7, 52, 34, 16, 8}:
                new_rank.append(rank[i])
        rank = other_carbons + new_rank + ring_carbons

        # List of atoms in canonical order
        canon_atoms = []
        for i in range(0, mol.GetNumAtoms()):
            canon_atoms.append(mol.GetAtomWithIdx(rank[i]))
        # TODO: Just use Idx here rather than actual atom object?

        tautomers = list(self._enumerate_r(mol, atom_classes, bond_classes, canon_atoms, num_hydrogens))
        return tautomers
