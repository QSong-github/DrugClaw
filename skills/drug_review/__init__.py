"""Drug Review/Patient Report skills."""

from .askapatient import AskAPatientSkill
from .drugs_com_reviews import DrugsComReviewsSkill
from .webmd import WebMDReviewsSkill

__all__ = [
    "AskAPatientSkill",
    "DrugsComReviewsSkill",
    "WebMDReviewsSkill",
]
