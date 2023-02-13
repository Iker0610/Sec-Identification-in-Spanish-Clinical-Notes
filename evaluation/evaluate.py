import argparse
import json
from collections import defaultdict
from pathlib import Path

from numpy import average
from tqdm import tqdm

from dataset_model import *
from segeval.format import BoundaryFormat
from segeval.similarity import B2_parameters as b2_default_parameters, weight_a
from segeval.similarity.boundary import boundary_similarity_2
from segeval.similarity.weight import weight_s, weight_t


def evaluate_boundaries(reference_boundaries: list[frozenset], prediction_boundaries: list[frozenset]) -> dict:
    error_type_mapper = {'a': 'additions', 'b': 'deletions'}

    base_parameters = {'boundary_types': set(ClinicalSections.list()), 'boundary_format': BoundaryFormat.sets}
    parameters_B = base_parameters | {'weight': (weight_a, weight_s, weight_t)}
    parameters_B2 = parameters_B | b2_default_parameters

    b2, file_stats = boundary_similarity_2(reference=reference_boundaries, hypothesis=prediction_boundaries, return_statistics=True, **parameters_B2)

    del file_stats['boundaries_all']
    del file_stats['boundary_types']
    del file_stats['full_misses']

    additions = file_stats['additions']
    file_stats['additions'] = []
    file_stats['deletions'] = []
    for section, error_type in additions:
        file_stats[error_type_mapper[error_type]].append(section)

    file_stats["transpositions"] = [{
        'start_offset': transposition[0],
        'end_offset': transposition[1],
        'boundary': transposition[2],
    } for transposition in file_stats['transpositions']]

    file_stats = {
        "matches": file_stats["matches"],
        "additions": file_stats["additions"],
        "deletions": file_stats["deletions"],
        "substitutions": file_stats["substitutions"],
        "transpositions": file_stats["transpositions"],
        "count_edits": file_stats["count_edits"],
        "weighted_transpositions": file_stats["weighted_transpositions"],
    }

    return {
        'stats': file_stats,
        'metrics': {'B2': b2}
    }


def evaluate_note(reference_boundaries: list[BoundaryAnnotation], prediction_boundaries: list[BoundaryAnnotation]) -> tuple[int, dict]:
    assert len(reference_boundaries) == len(prediction_boundaries), "The number of boundaries in the reference and the prediction do not match."

    processed_reference_boundaries: list[frozenset] = []
    processed_prediction_boundaries: list[frozenset] = []
    number_gold_sections = 0

    for reference_boundary, prediction_boundary in zip(reference_boundaries, prediction_boundaries):
        assert reference_boundary.start_offset == prediction_boundary.start_offset, "The offsets of the prediction do not match with the ground truth. This implies differences in the defined spans."
        assert reference_boundary.end_offset == prediction_boundary.end_offset, "The offsets of the prediction do not match with the ground truth. This implies differences in the defined spans."

        reference_boundary = reference_boundary.boundary
        prediction_boundary = prediction_boundary.boundary

        if reference_boundary is not None:
            processed_reference_boundaries.append(frozenset([reference_boundary]))
            number_gold_sections += 1
        else:
            processed_reference_boundaries.append(frozenset())

        processed_prediction_boundaries.append(frozenset([prediction_boundary]) if prediction_boundary is not None else frozenset())

    return number_gold_sections, evaluate_boundaries(processed_reference_boundaries, processed_prediction_boundaries)


def score_predictions(prediction_file: Path, reference_file: Path = None, output_result_file: Path = None, add_scores_in_prediction_file: bool = False):
    print(f"Loading predictions from {prediction_file}.")
    with open(prediction_file, encoding='utf-8') as f:
        predictions: ClinAISDataset = ClinAISDataset(**json.load(f))

    if reference_file is None:
        print(f"Loading references from the prediction file.")
        references = predictions
    else:
        print(f"Loading references from {reference_file}.")
        with open(reference_file, encoding='utf-8') as f:
            references: ClinAISDataset = ClinAISDataset(**json.load(f))

    # ---------------------------------------
    number_sections_per_file = []
    scores_per_file = []
    metrics_per_file = defaultdict(lambda: {
        'B2': None,
        'Statistics': None
    })

    print(f"Evaluating all predictions.")
    # Compute the scores
    for filename, reference in tqdm(references.annotated_entries.items()):
        prediction = predictions.annotated_entries[filename]
        number_sections, metrics = evaluate_note(
            reference_boundaries=reference.boundary_annotation.gold,
            prediction_boundaries=prediction.boundary_annotation.prediction
        )
        number_sections_per_file.append(number_sections)
        scores_per_file.append(metrics['metrics']['B2'])
        metrics_per_file[filename] = {
            'B2': metrics['metrics']['B2'],
            'Statistics': metrics['stats']
        }

    # Compute the final scores on the whole dataset
    scores = {
        'Weighted B2': average(scores_per_file, weights=number_sections_per_file),
        'Scores per file': metrics_per_file
    }

    if add_scores_in_prediction_file:
        prediction_dict = predictions.dict()
        prediction_dict['scores'] = scores

        with open(prediction_file.with_suffix('.evaluated.json'), 'w', encoding='utf8') as f:
            json.dump(prediction_dict, indent=2, ensure_ascii=False, fp=f)

    if output_result_file is not None:
        # If output file doesnt end in .json add it
        if not output_result_file.name.endswith('.json'):
            output_result_file = output_result_file.with_suffix('.json')

        with open(output_result_file, 'w', encoding='utf8') as f:
            json.dump(scores, indent=2, ensure_ascii=False, fp=f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Codalab scorer for the IberLEF 2023 ClinAIS task.')
    parser.add_argument('-p', '--prediction_file', type=Path, required=True, help='JSON file containing the predictions. If reference file is not provided, this file must include the reference annotations.')
    parser.add_argument('-r', '--reference_file', type=Path, required=False, default=None, help='JSON file containing the reference annotations. If not provided, the reference annotations must be included in the prediction file.')
    parser.add_argument('-o', '--output_result_file', type=Path, required=False, default=None, help='Output JSON file where evaluation results will be saved.')
    parser.add_argument('--add_scores_in_prediction_file', action='store_true', help='If set, the scores will be added to the prediction file.')
    args = parser.parse_args()

    score_predictions(**vars(args))
