"""Ship the referenced science guides inside every independently installable skill.

Copies only linked reference/assets closure, preserving authoring sources. Optional
links to another skill's entry point stay pinned online and do not imply it is installed.
"""
from __future__ import annotations
from pathlib import Path
import re
import shutil
from check_skill_distribution import markdown_paths, PLACEHOLDER

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / 'skills'
PIN = '79b4238a5a7dfc963bafc0aefacd2337f9795ba8'
REMOTE = f'https://github.com/arrizabalagags-png/BatteryReviewForge/blob/{PIN}/'
LINK = re.compile(r'(?P<prefix>\]\()(?P<path>[^\s)#]+)(?P<anchor>#[^\s)]*)?(?P<suffix>\))')


def is_local(value):
    return not re.match(r'^(?:https?:|mailto:|data:|#)', value)


def sync_skill(folder):
    pending, copied = [], {}
    def canonical(target):
        while target.is_relative_to(SKILLS):
            parts = target.relative_to(SKILLS).parts
            if 'shared' not in parts:
                break
            idx = parts.index('shared')
            if idx < 1 or parts[idx - 1] != 'references':
                break
            target = SKILLS.joinpath(*parts[idx + 1:])
        return target

    def locate(origin, path):
        target = (origin.parent / path).resolve()
        if not target.is_file():
            raise ValueError(f'Missing referenced source: {origin.relative_to(ROOT)} -> {path}')
        return canonical(target)

    def shared(target):
        if target.name == 'SKILL.md' or not target.is_relative_to(SKILLS):
            return None
        destination = folder / 'references/shared' / target.relative_to(SKILLS)
        if target not in copied:
            copied[target] = destination
            pending.append(target)
        return destination

    def rewrite(origin, destination, content):
        def replace(match):
            value = match['path']
            if not is_local(value):
                return match[0]
            target = locate(origin, value)
            if target.is_relative_to(folder):
                relative = __import__('os').path.relpath(target, destination.parent).replace('\\', '/')
                return '](' + relative + (match['anchor'] or '') + ')'
            # Authoring docs/gallery are optional online, never runtime requirements.
            local = shared(target)
            if local is None:
                return '](' + REMOTE + target.relative_to(ROOT).as_posix() + (match['anchor'] or '') + ')'
            relative = __import__('os').path.relpath(local, destination.parent).replace('\\', '/')
            return '](' + relative + (match['anchor'] or '') + ')'
        content = LINK.sub(replace, content)
        owner = SKILLS / origin.relative_to(SKILLS).parts[0]
        installed_owner_required = False
        # Bare paths in copied guides have the source Skill's root semantics,
        # not the recipient Skill's root. Copy scientific reference/assets only;
        # executable instructions explicitly require the independently installed owner.
        for value, linked, _ in list(markdown_paths(content)):
            if linked or PLACEHOLDER.search(value):
                continue
            base = origin.parent if value.startswith(('./', '../')) else owner
            target = (base / value).resolve()
            if target.is_relative_to(folder):
                continue
            if not target.exists():
                raise ValueError(f'Missing bare source path: {origin.relative_to(ROOT)} -> {value}')
            if target.is_relative_to(owner / 'scripts') or target.is_relative_to(owner / 'examples'):
                replacement = f'<installed-{owner.name}>/' + target.relative_to(owner).as_posix()
                installed_owner_required = True
            else:
                local = shared(target) if target.is_file() else None
                if local:
                    relative = __import__('os').path.relpath(local, destination.parent).replace('\\', '/')
                    replacement = f'[{value}]({relative})'
                else:
                    replacement = f'[{value}]({REMOTE}{target.relative_to(ROOT).as_posix()})'
            content = content.replace(value, replacement)
        if installed_owner_required:
            notice = (f'> This is a copied science guide. Its executable commands require a separately installed '
                      f'`{owner.name}`; `<installed-{owner.name}>` means that Skill\'s actual root. '
                      'Those scripts and Python dependencies are not supplied by this guide.\n\n')
            content = notice + content
        return content

    entry = folder / 'SKILL.md'
    # Refresh previously copied guides after their owning source changes.
    shared_root = folder / 'references/shared'
    if shared_root.exists():
        for old in sorted(shared_root.rglob('*')):
            if old.is_file():
                origin = canonical(SKILLS / old.relative_to(shared_root))
                if origin.is_file():
                    shared(origin)
    entry.write_text(rewrite(entry, entry, entry.read_text(encoding='utf-8-sig')), encoding='utf-8', newline='\n')
    # Existing local guide links also need standalone closure (atlas + demos).
    for guide in sorted((folder / 'references').glob('*.md')):
        guide.write_text(rewrite(guide, guide, guide.read_text(encoding='utf-8-sig')), encoding='utf-8', newline='\n')
    while pending:
        origin = pending.pop(0)
        destination = copied[origin]
        destination.parent.mkdir(parents=True, exist_ok=True)
        if origin.suffix == '.md':
            destination.write_text(rewrite(origin, destination, origin.read_text(encoding='utf-8-sig')), encoding='utf-8', newline='\n')
        else:
            shutil.copyfile(origin, destination)
    return len(copied)


if __name__ == '__main__':
    for folder in sorted(SKILLS.iterdir()):
        if (folder / 'SKILL.md').is_file():
            print(folder.name, sync_skill(folder))
