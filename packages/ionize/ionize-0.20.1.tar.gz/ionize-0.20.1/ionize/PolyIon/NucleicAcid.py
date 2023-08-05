from math import exp, log, pi

from .PolyIon import PolyIon
from ..Ion import fixed_state


@fixed_state
class NucleicAcid(PolyIon):

    _state = {'name': 'Name of the ion.',
              'size': 'Number of bases or base pairs in the nucleic acid.',
              'species': 'Type of nucleic acid species.',
              'sequence': 'Sequence of the nucleic acid.',
              }

    _name = 'Nucleic Acid'
    _size = float('inf')
    _species = 'DNA'
    _sequence = None

    __species_options = {'DNA': {'duplex': True},
                         'RNA': {'duplex': False},
                         'dsDNA': {'duplex': True},
                         'ssDNA': {'duplex': False},
                         'ssRNA': {'duplex': False}}

    def __init__(self, name=None,
                 size=None, sequence=None,
                 species=None):

        self._name = name or self.name
        self._size = size or self.size
        self._sequence = sequence or self.sequence

        self._species = species or self.species
        assert self.species in self.__species_options.keys()

    def mobility(self, pH=None, ionic_strength=None, temperature=None):
        pH, ionic_strength, temperature = \
                self._resolve_context(pH, ionic_strength, temperature)
        # TODO: Introduce manning condensation model
        mu = (3.75 - 1.8 * (self.size**-.6)) * 1e-8
        k = 1./self._solvent.debye(ionic_strength, temperature)
        # mu = 6 * pi * self.solvent.viscosity() * lb / self.friction()
        # mu -= 2 * self.charge() * log(1 - exp(-k * lb / self.charge()))
        return mu

    def charge(self, pH=None, ionic_strength=None, temperature=None,
               moment=1):

        # TODO: introduce manning condensation model
        # return self.size * (1 + self.__species_options[self.species]['duplex'])
        raise NotImplementedError

    def friction(self, pH=None, ionic_strength=None, temperature=None):
        pass
