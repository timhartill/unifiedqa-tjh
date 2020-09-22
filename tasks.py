import logging
import t5
import os
import json
import functools
import tensorflow as tf
import tensorflow_datasets as tfds

DATASETS = [
    "ai2_science_middle",
    "ai2_science_elementary",
    "arc_hard",
    "arc_easy",
    "mctest",
    "mctest_corrected_the_separator",
    "natural_questions",
    "quoref",
    "squad1_1",
    "squad2",
    "boolq",
    "multirc",
    "newsqa",
    "race_string",
    "ropes",
    "drop",
    "narrativeqa",
    "openbookqa",
    "qasc",
    "boolq_np",
    "contrast_sets_boolq",
    "contrast_sets_drop",
    "contrast_sets_quoref",
    "contrast_sets_ropes",
    "commonsenseqa",
    "qasc_with_ir",
    "openbookqa_with_ir",
    "arc_easy_with_ir",
    "arc_hard_with_ir",
    "ambigqa",
    "natural_questions_direct_ans",
    "natural_questions_with_dpr_para",
    "winogrande_xs",
    "winogrande_s",
    "winogrande_m",
    "winogrande_l",
    "winogrande_xl",
    "social_iqa",
    "physical_iqa",
]


for dataset in DATASETS:
    print(f" >>>> reading dataset: {dataset}")
    t5.data.set_tfds_data_dir_override(DATA_DIR + dataset)
    t5.data.TaskRegistry.add(
        f"{dataset}_task",
        # Supply a function which returns a tf.data.Dataset.
        dataset_fn=functools.partial(dataset_fn, dataset=dataset),
        splits=["train", "dev", "test"],
        # Supply a function which preprocesses text from the tf.data.Dataset.
        text_preprocessor=[dataset_preprocessor],
        # Use the same vocabulary that we used for pre-training.
        sentencepiece_model_path=t5.data.DEFAULT_SPM_PATH,
        # Lowercase targets before computing metrics.
        postprocess_fn=t5.data.postprocessors.lower_text,
        metric_fns=[t5.evaluation.metrics.accuracy],
    )
    print(f" >>>> adding one mixture per dataset: `{dataset}_mixture`")
    t5.data.MixtureRegistry.add(
        f"{dataset}_mixture", [f"{dataset}_task"], default_rate=1.0
    )

# dataset-pair mixtures
for dataset1 in DATASETS:
    for dataset2 in DATASETS:
        if dataset1 == dataset2:
            continue
        print(f" >>>> adding one mixture for dataset-pair: `{dataset1}_{dataset2}_mixture`")
        t5.data.MixtureRegistry.add(
            f"{dataset1}_{dataset2}_mixture",
            [f"{dataset1}_task", f"{dataset2}_task"],
            default_rate=1.0
        )

# union model: used for training UnifiedQA
union_datasets = [
    "narrativeqa",
    "ai2_science_middle", "ai2_science_elementary",
    "arc_hard", "arc_easy",
    "mctest_corrected_the_separator",
    "squad1_1", "squad2",
    "boolq",
    "race_string",
    "openbookqa",
]
print(f" >>>> adding one mixture for `union_mixture`")
t5.data.MixtureRegistry.add(
    f"union_mixture",
    [f"{d}_task" for d in union_datasets],
    default_rate=1.0
)

# leave-one-out
for dd in union_datasets:
    filtered_datasets = [f"{d}_task" for d in union_datasets if d != dd]
    assert len(filtered_datasets) < len(union_datasets)
    t5.data.MixtureRegistry.add(
        f"union_minus_{dd}_mixture",
        filtered_datasets,
        default_rate=1.0
    )