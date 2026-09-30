"""Create a public bundle from explicitly permitted final files, excluding recovery data."""
from __future__ import annotations
import argparse
import base64
import io
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from output_safety import new_directory
from delivery_contract import check_working_bundle, digest

SECRET = re.compile(r'(?i)(?:sk-[a-z0-9_-]{12,}|(?:api[_ -]?key|access[_ -]?token|password|secret)\s*[:=]\s*["\']?[^\s"\']{6,}|(?<![a-z0-9])[a-z]:[\\/]|/(?:Users|home)/[^\s]+|file://)')
STANDARD_SVG_DOCTYPE = re.compile(r'<!DOCTYPE\s+svg\s+PUBLIC\s+"-//W3C//DTD SVG 1\.1//EN"\s+"http://www\.w3\.org/Graphics/SVG/1\.1/DTD/svg11\.dtd"\s*>', re.I)


def public_svg(path):
    text = path.read_text(encoding='utf-8-sig')
    if SECRET.search(text):
        raise ValueError(f'{path.name} 含有敏感文本，请人工修改后重新交付。')
    # Matplotlib writes this standard header; strip it without fetching its DTD.
    text = STANDARD_SVG_DOCTYPE.sub('', text)
    if re.search(r'<!DOCTYPE|<!ENTITY|@import', text, re.I):
        raise ValueError(f'{path.name} 含外部样式或实体引用。')
    for match in re.finditer(r'url\(([^)]+)\)', text, re.I):
        value = match.group(1).strip().strip('"\'')
        if not value.startswith(('#', 'data:image/')):
            raise ValueError(f'{path.name} 含外部样式引用。')
    root = ET.fromstring(text)
    for node in root.iter():
        if node.tag.rsplit('}', 1)[-1] in {'script', 'foreignObject'}:
            raise ValueError(f'{path.name} 含脚本或嵌入网页。')
        for key, value in node.attrib.items():
            if key.rsplit('}', 1)[-1].lower().startswith('on'):
                raise ValueError(f'{path.name} 含交互脚本属性。')
            if key.endswith('href') and not value.startswith(('#', 'data:image/')):
                raise ValueError(f'{path.name} 含外部文件引用。')
            if key.endswith('href') and value.startswith('data:image/'):
                if not value.startswith(('data:image/png;base64,', 'data:image/jpeg;base64,')):
                    raise ValueError(f'{path.name} 含未支持的内嵌图像，请用PNG或JPEG嵌入。')
                from PIL import Image
                header, encoded = value.split(',', 1)
                try:
                    with Image.open(io.BytesIO(base64.b64decode(encoded, validate=True))) as embedded:
                        clean = embedded.copy()
                        clean.info.clear()
                        buffer = io.BytesIO()
                        clean.save(buffer, format='PNG')
                    node.set(key, 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode('ascii'))
                except (OSError, ValueError) as exc:
                    raise ValueError(f'{path.name} 的内嵌图像无法核对。') from exc
    return root


def create_share_bundle(working: Path, requested: Path, *, rights_confirmed: bool,
                        license_name: str, sources: list[str] = ()) -> Path:
    if not rights_confirmed or not license_name.strip():
        raise ValueError('请确认最终图件允许公开，并填写适用许可；原始数据和内部恢复记录不会进入分享包。')
    issues = check_working_bundle(working)
    if issues:
        raise ValueError('交付文件已变化，请先更新工作记录：' + '; '.join(issues))
    if SECRET.search(license_name) or any(SECRET.search(item) or not item.startswith(('https://', 'http://', 'doi:')) for item in sources):
        raise ValueError('许可或公开来源含有本地路径、密钥或无效来源，请修正后分享。')
    manifest = json.loads((working / '.voltpeer/manifest.json').read_text(encoding='utf-8-sig'))
    allowed = [working / item['path'] for item in manifest['files'] if item['role'] == 'result']
    if not allowed:
        raise ValueError('没有可分享的最终图件。')
    for path in allowed:
        if path.suffix.lower() == '.pdf':
            from pypdf import PdfReader
            reader = PdfReader(path)
            if reader.is_encrypted:
                raise ValueError('请先提供可读的最终 PDF，分享包不处理加密文件。')
            for page in reader.pages:
                if SECRET.search(page.extract_text() or ''):
                    raise ValueError(f'{path.name} 含本地路径或疑似密钥，请人工核对后重新交付。')
        if path.suffix.lower() == '.svg':
            public_svg(path)
    output, _ = new_directory(requested)
    files = []
    for i, path in enumerate(allowed, 1):
        # Generated names exclude private project names and user directory names.
        target = output / f'figure_{i:02d}{path.suffix.lower()}'
        if path.suffix.lower() in {'.png', '.tif', '.tiff'}:
            from PIL import Image
            with Image.open(path) as image:
                options = {'dpi': image.info['dpi']} if 'dpi' in image.info else {}
                if path.suffix.lower() in {'.tif', '.tiff'}:
                    options['compression'] = 'tiff_lzw'
                clean = image.copy()
                clean.info.clear()
                clean.save(target, **options)
        elif path.suffix.lower() == '.pdf':
            from pypdf import PdfReader, PdfWriter
            writer = PdfWriter()
            for page in PdfReader(path).pages:
                # Form data, hyperlinks/actions and page metadata are not scientific artwork.
                for key in ('/Annots', '/AA', '/Metadata'):
                    if key in page:
                        del page[key]
                writer.add_page(page)
            writer.add_metadata({})
            with target.open('wb') as stream:
                writer.write(stream)
        elif path.suffix.lower() == '.svg':
            root = public_svg(path)
            # Exporter metadata can contain local creator fields; visible labels and credits remain.
            for parent in root.iter():
                for child in list(parent):
                    if child.tag.rsplit('}', 1)[-1] == 'metadata':
                        parent.remove(child)
            ET.register_namespace('', 'http://www.w3.org/2000/svg')
            ET.ElementTree(root).write(target, encoding='utf-8', xml_declaration=True)
        else:
            raise ValueError('Unsupported public file: ' + path.suffix)
        files.append({'path': target.name, 'sha256': digest(target)})
    public = {'schema_version': 1, 'bundle_type': 'share', 'license': license_name,
              'sources': list(sources), 'files': files,
              'review': {'rights': 'author_confirmed', 'visible_labels_and_science': 'author_review_required'},
              'note': 'Raw inputs, TASK_STATE and local provenance excluded. Inspect visible labels before publishing.'}
    (output / 'share.json').write_text(json.dumps(public, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (output / 'README.md').write_text('公开分享前，请再检查图里的姓名、课题名和未公开内容。\n许可：' + license_name + '\n' + '\n'.join(sources) + '\n', encoding='utf-8')
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--working', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--rights-confirmed', action='store_true')
    parser.add_argument('--license', required=True)
    parser.add_argument('--source', action='append', default=[])
    args = parser.parse_args()
    try:
        path = create_share_bundle(args.working.resolve(), args.out.resolve(), rights_confirmed=args.rights_confirmed,
                                   license_name=args.license, sources=args.source)
    except (OSError, ValueError, KeyError, ET.ParseError) as exc:
        parser.exit(2, str(exc) + '\n')
    print(json.dumps({'share_folder': str(path), 'next': '检查可见标签后再公开；本命令没有上传。'}, ensure_ascii=False))


if __name__ == '__main__':
    from cli_runtime import configure_utf8
    configure_utf8()
    main()
