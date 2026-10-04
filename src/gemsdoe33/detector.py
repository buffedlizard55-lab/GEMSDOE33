"""Catalogue-supervised research detector; no private-fault performance is claimed.

The optional out-of-fold research field uses four broad raster quadrants: each model is fit on the
other three and predicts the fourth. This prevents direct pixel reuse across that broad split, but
there is no fault-system grouping or boundary buffer, and spatially adjacent structures may cross
partitions. The labels are the incomplete public catalogue. This is useful for descriptive feature
work only; it is **not** an independent holdout for faults absent from USGS/INGENIOUS, a DTI
validation, or evidence to approve a competition submission slot.

Negatives are a sampled set of owner-mirror footprint cells at least one pixel from known catalogue
labels. The detector and any generated OOF cache remain owner-mirror research artifacts. A future
candidate needs separate, valid field/fault-system-level holdout design before promotion.
"""
