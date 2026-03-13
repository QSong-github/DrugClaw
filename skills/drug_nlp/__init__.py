"""Drug NLP/Text Mining dataset skills."""

from .ade_corpus import ADECorpusSkill
from .cadec import CADECSkill
from .ddi_corpus import DDICorpusSkill
from .drugehrqa import DrugEHRQASkill
from .drugprot import DrugProtSkill
from .n2c2_2018 import N2C22018Skill
from .phee import PHEESkill
from .psytar import PsyTARSkill
from .tac2017 import TAC2017ADRSkill

__all__ = [
    "ADECorpusSkill",
    "CADECSkill",
    "DDICorpusSkill",
    "DrugEHRQASkill",
    "DrugProtSkill",
    "N2C22018Skill",
    "PHEESkill",
    "PsyTARSkill",
    "TAC2017ADRSkill",
]
