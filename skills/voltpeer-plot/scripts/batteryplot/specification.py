"""Keep historical publisher profiles distinct from an explicit export choice."""
from __future__ import annotations
from typing import Mapping
from .data import DataContractError

CONTENT_CLASSES = {'line_art', 'image', 'mixed'}


def resolve_specification(profile: Mapping, *, content_class: str = 'line_art',
                          requested_dpi: int | None = None,
                          dpi_by_format: Mapping[str, int] | None = None) -> dict:
    if content_class not in CONTENT_CLASSES:
        raise DataContractError('Content class must be line_art, image or mixed')
    keys = {'line_art': 'line_art_raster_dpi', 'image': 'image_raster_dpi', 'mixed': 'mixed_raster_dpi'}
    declared = profile.get(keys[content_class])
    # A range cannot be reduced to its first value without an explicit choice.
    neutral = profile.get('profile_id') == 'journal_neutral'
    if neutral:
        declared = profile.get('review_raster_dpi', 300)
    elif declared is None:
        declared = profile.get('preferred_raster_dpi_min')
    explicit = requested_dpi is not None
    if explicit:
        effective = requested_dpi
    elif type(declared) is int:
        effective = declared
    else:
        raise DataContractError(f'该规格没有明确的 {content_class} 位图分辨率（记录为 {declared!r}）。请核对目标期刊并指定 --dpi；试运行可明确选择 --journal journal_neutral。')
    if type(effective) is not int or effective < 300:
        raise DataContractError('Raster DPI must be an integer >=300')
    per_format = dict(dpi_by_format or {})
    if set(per_format) - {'png', 'tiff'} or any(type(v) is not int or v < 300 for v in per_format.values()):
        raise DataContractError('Per-format DPI supports PNG/TIFF with integer values >=300')
    return {'profile_id': profile.get('profile_id'), 'content_class': content_class,
            'dpi': effective, 'dpi_by_format': per_format, 'declared_content_dpi': declared,
            'status': 'journal_neutral_preview' if neutral else 'author_requested' if explicit else 'stored_profile',
            'journal_requirements': 'needs_confirmation', 'source': profile.get('source'),
            'checked_date': profile.get('checked_date'),
            'note': 'Working preview; no publisher compliance claim.' if neutral else 'Recheck the current official guide for the exact journal, article type and content class before submission.'}
