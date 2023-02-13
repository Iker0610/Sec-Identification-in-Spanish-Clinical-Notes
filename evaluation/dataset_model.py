from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class ClinicalSections(str, Enum):
    PRESENT_ILLNESS = "PRESENT_ILLNESS"
    DERIVED_FROM_TO = "DERIVED_FROM/TO"
    PAST_MEDICAL_HISTORY = "PAST_MEDICAL_HISTORY"
    FAMILY_HISTORY = "FAMILY_HISTORY"
    EXPLORATION = "EXPLORATION"
    TREATMENT = "TREATMENT"
    EVOLUTION = "EVOLUTION"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class SectionAnnotation(BaseModel):
    segment: str
    label: ClinicalSections
    start_offset: int
    end_offset: int

    class Config:
        use_enum_values = True


class SectionAnnotations(BaseModel):
    gold: list[SectionAnnotation] = []
    prediction: list[SectionAnnotation] = []


class BoundaryAnnotation(BaseModel):
    span: str
    boundary: ClinicalSections | None
    start_offset: int
    end_offset: int

    class Config:
        use_enum_values = True


class BoundaryAnnotations(BaseModel):
    gold: list[BoundaryAnnotation] = []
    prediction: list[BoundaryAnnotation] = []


class Entry(BaseModel):
    note_id: str
    note_text: str
    section_annotation: SectionAnnotations = SectionAnnotations()
    boundary_annotation: BoundaryAnnotations = BoundaryAnnotations()


class ClinAISDataset(BaseModel):
    annotated_entries: dict[str, Entry]
