"""Validate the versioned demo metadata schema and distributed input closure.

This is a dependency-free validator for the keywords used in our schema, not a
general JSON Schema engine. Unknown validation keywords stop rather than pass.
"""
from __future__ import annotations
import json
import math
from pathlib import Path, PurePosixPath
import re
from zipfile import ZipFile


class MetadataError(ValueError):
    pass


SCHEMA_PATH = Path(__file__).resolve().parents[1] / 'docs/DEMO_METADATA_SCHEMA.json'
ANNOTATIONS = {'$schema', '$id', 'title', 'description'}
KEYWORDS = {'type', 'const', 'enum', 'required', 'properties', 'additionalProperties',
            'items', 'minItems', 'uniqueItems', 'minLength', 'minimum', 'pattern', 'anyOf'}


def validate_schema(value, schema, location='$'):
    if isinstance(value, float) and not math.isfinite(value):
        raise MetadataError(f'{location}: JSON numbers must be finite')
    unknown = set(schema) - KEYWORDS - ANNOTATIONS
    if unknown:
        raise MetadataError(f'Unsupported schema keywords: {sorted(unknown)}')
    if 'anyOf' in schema:
        for branch in schema['anyOf']:
            try:
                validate_schema(value, branch, location)
                break
            except MetadataError:
                pass
        else:
            raise MetadataError(f'{location}: does not match a metadata variant')
    checks = {'object': lambda v: isinstance(v, dict), 'array': lambda v: isinstance(v, list),
              'string': lambda v: isinstance(v, str), 'integer': lambda v: type(v) is int,
              'number': lambda v: type(v) in (int, float), 'boolean': lambda v: type(v) is bool,
              'null': lambda v: v is None}
    expected = schema.get('type')
    if expected and not any(checks[t](value) for t in ([expected] if isinstance(expected, str) else expected)):
        raise MetadataError(f'{location}: expected {expected}')
    if 'const' in schema and (type(value) != type(schema['const']) or value != schema['const']):
        raise MetadataError(f'{location}: expected constant {schema["const"]!r}')
    if 'enum' in schema and value not in schema['enum']:
        raise MetadataError(f'{location}: invalid value {value!r}')
    if isinstance(value, str):
        if len(value.strip()) < schema.get('minLength', 0):
            raise MetadataError(f'{location}: empty or short text')
        if 'pattern' in schema and not re.search(schema['pattern'], value):
            raise MetadataError(f'{location}: invalid text format')
    if type(value) in (int, float) and value < schema.get('minimum', float('-inf')):
        raise MetadataError(f'{location}: number below minimum')
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0):
            raise MetadataError(f'{location}: too few entries')
        if schema.get('uniqueItems') and len({json.dumps(v, sort_keys=True) for v in value}) != len(value):
            raise MetadataError(f'{location}: duplicate entries')
        for index, entry in enumerate(value):
            validate_schema(entry, schema.get('items', {}), f'{location}[{index}]')
    if isinstance(value, dict):
        missing = set(schema.get('required', [])) - set(value)
        if missing:
            raise MetadataError(f'{location}: missing {sorted(missing)}')
        properties = schema.get('properties', {})
        for key, entry in value.items():
            if key in properties:
                validate_schema(entry, properties[key], f'{location}.{key}')
            elif schema.get('additionalProperties') is False:
                raise MetadataError(f'{location}: undeclared field {key}')
            elif isinstance(schema.get('additionalProperties'), dict):
                validate_schema(entry, schema['additionalProperties'], f'{location}.{key}')
            else:
                validate_schema(entry, {}, f'{location}.{key}')


def validate_metadata(meta, schema_path=SCHEMA_PATH):
    validate_schema(meta, json.loads(Path(schema_path).read_text(encoding='utf-8')))
    # Every current demo must carry measured artist checks, not just a PASS word.
    if not (meta.get('data_frame_checks') or meta.get('actual_artist_checks')):
        raise MetadataError('Missing actual data-frame artist records')
    return meta


def check_demo(folder, website_folder, archive_path, *, source_root=None, schema_path=SCHEMA_PATH):
    folder, website_folder = Path(folder).resolve(), Path(website_folder).resolve()
    root = Path(source_root or folder.parent).resolve()
    metadata = validate_metadata(json.loads((folder/'metadata.json').read_text(encoding='utf-8-sig')), schema_path)
    site_meta = json.loads((website_folder/'metadata.json').read_text(encoding='utf-8-sig'))
    if site_meta != metadata:
        raise MetadataError(f'{folder.name}: site metadata differs from source')
    with ZipFile(archive_path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise MetadataError('ZIP contains duplicate members')
        for name in names:
            part = PurePosixPath(name)
            if part.is_absolute() or '..' in part.parts or '\\' in name:
                raise MetadataError('Unsafe ZIP member')
        packed_meta = json.loads(archive.read(folder.name+'/metadata.json'))
        if packed_meta != metadata:
            raise MetadataError(f'{folder.name}: ZIP metadata differs from source')
        for entry in metadata['source_files']:
            source = (folder/entry).resolve()
            if not source.is_relative_to(root) or not source.is_file():
                raise MetadataError(f'{folder.name}: invalid input {entry}')
            relative = source.relative_to(root).as_posix()
            if archive.read(relative) != source.read_bytes():
                raise MetadataError(f'{folder.name}: ZIP input differs: {entry}')
            served = (website_folder/entry).resolve()
            if not served.is_relative_to(website_folder.parent) or not served.is_file() or served.read_bytes() != source.read_bytes():
                raise MetadataError(f'{folder.name}: site input differs: {entry}')
        for suffix in ('png', 'svg', 'pdf'):
            if (website_folder/f'figure.{suffix}').read_bytes() != (folder/f'figure.{suffix}').read_bytes():
                raise MetadataError(f'{folder.name}: site figure differs: {suffix}')
    return {'id': folder.name, 'schema': 'PASS', 'source_site_zip_metadata': 'PASS',
            'source_site_zip_inputs': 'PASS', 'source_site_figures': 'PASS'}
