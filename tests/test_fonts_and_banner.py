"""Actual glyphs and rendered condition-note bounds; synthetic layout fixtures."""
from __future__ import annotations
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.font_manager import FontProperties
from PIL import Image
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/battery-review-figure/scripts'))
from batteryplot.style import make_figure, condition_banner, _font_characters
from batteryplot.data import DataContractError
from batteryplot import cycle_retention, save_bundle


def visible_text(value):
    return ''.join(value.split())


class FontAndBannerTests(unittest.TestCase):
    def tearDown(self):
        plt.close('all')

    def test_available_caller_family_is_preserved_and_global_rc_is_restored(self):
        before = list(mpl.rcParams['font.family'])
        with mpl.rc_context({'font.family': ['DejaVu Serif']}):
            fig, ax = make_figure()
            ax.set_xlabel('Capacity / mAh')
            ax.plot([0, 1], [3, 4])
        fig.canvas.draw()
        self.assertEqual(ax.xaxis.label.get_fontproperties().get_name(), 'DejaVu Serif')
        self.assertEqual(mpl.rcParams['font.family'], before)
        self.assertTrue(all(ax.spines[side].get_visible() for side in ('top', 'right', 'bottom', 'left')))

    def test_explicit_caller_font_file_survives_render(self):
        fig, ax = make_figure()
        path = font_manager.findfont(FontProperties(family=['DejaVu Serif']))
        ax.set_xlabel('Author selected font', fontproperties=FontProperties(fname=path, size=8))
        fig.canvas.draw()
        self.assertEqual(ax.xaxis.label.get_fontproperties().get_file(), path)

    def test_chinese_labels_use_actual_complete_glyph_coverage(self):
        fig, ax = make_figure()
        ax.set_xlabel('循环次数')
        ax.set_ylabel('放电容量 / mAh g-1')
        ax.plot([1, 2, 3], [150, 143, 135], label='样品甲')
        legend = ax.legend()
        fig.canvas.draw()
        for text in (ax.xaxis.label, ax.yaxis.label, *legend.get_texts()):
            props = text.get_fontproperties()
            self.assertTrue({ord(c) for c in text.get_text() if not c.isspace()} <= _font_characters(props.get_file()))
        self.assertTrue(any('循环' in item['text'] and item['status'] == 'PASS_GLYPH_COVERAGE_ONLY' for item in fig.batteryplot_font_report))

    def test_absent_glyphs_fail_visibly_without_ascii_replacement(self):
        fig, ax = make_figure()
        original = '中文缺字边界'
        ax.set_xlabel(original)
        with patch('batteryplot.style._font_characters', return_value=frozenset(range(32, 128))):
            with self.assertRaisesRegex(DataContractError, 'No usable installed font'):
                fig.canvas.draw()
        self.assertEqual(ax.get_xlabel(), original)

    def test_long_mixed_note_retains_every_word_and_reserves_space(self):
        note = ('Current density, electrolyte volume and temperature differ across samples. '
                '测试条件不同，不能据此直接排名性能；所有条件与未知值必须保留。 ')*10
        for width in (89, 180):
            with self.subTest(width=width):
                fig, ax = make_figure(width_mm=width)
                ax.plot([0, 100, 300], [150, 145, 130])
                ax.set_xlabel('Cycle'); ax.set_ylabel('Capacity / mAh g-1')
                old = fig.get_figheight()
                condition_banner(fig, note)
                fig.canvas.draw()
                banner = fig.batteryplot_condition_text
                renderer = fig.canvas.get_renderer()
                box = banner.get_window_extent(renderer)
                self.assertEqual(visible_text(banner.get_text()), visible_text('Comparison limits · '+note))
                self.assertGreater(len(banner.get_text().splitlines()), 3)
                self.assertGreater(fig.get_figheight(), old)
                self.assertGreaterEqual(box.x0, fig.bbox.x0)
                self.assertLessEqual(box.x1, fig.bbox.x1)
                self.assertLessEqual(box.y1, fig.bbox.y1)
                self.assertFalse(box.overlaps(ax.get_window_extent(renderer)))
                self.assertEqual(fig.canvas.get_width_height()[1], int(fig.bbox.height))
                self.assertEqual(list(ax.lines[0].get_ydata()), [150, 145, 130])
                first = fig.get_size_inches().copy()
                fig.canvas.draw()
                self.assertEqual(list(first), list(fig.get_size_inches()))

    def test_updated_note_does_not_accumulate_previous_reserved_height(self):
        fig, ax = make_figure()
        original = fig.get_figheight()
        condition_banner(fig, 'Conditions differ.')
        fig.canvas.draw(); short = fig.get_figheight()
        condition_banner(fig, 'Conditions differ in ' + 'current temperature pressure '*15)
        fig.canvas.draw()
        self.assertGreater(fig.get_figheight(), short)
        condition_banner(fig, 'Conditions differ.')
        fig.canvas.draw()
        self.assertEqual(fig.batteryplot_condition_base_height, original)
        self.assertAlmostEqual(fig.get_figheight(), short)

    def test_real_pdf_svg_png_contain_chinese_and_full_long_note(self):
        note = ('电流密度与电解液量不同。 Do not infer a direct ranking from this contextual comparison. ')*5
        rows = [{'source_id': 'test:synthetic', 'evidence_state': 'verified', 'chemistry': 'synthetic Li-ion',
                 'cell_configuration': 'synthetic half cell', 'temperature_c': '25',
                 'loading_mg_cm2': '2', 'electrolyte_ul_mg': '10', 'rate': '1 C',
                 'series': '样品甲', 'cycle': str(cycle), 'reference_cycle': '0',
                 'retention_pct': str(value), 'retention_basis': 'synthetic reference'}
                for cycle, value in ((0, 100), (1, 98), (3, 93))]
        fig, ax = cycle_retention(rows)
        ax.set_xlabel('循环次数'); ax.set_ylabel('放电容量')
        condition_banner(fig, note)
        with tempfile.TemporaryDirectory(prefix='字形与 横幅 ') as temp:
            root = Path(temp)
            save_bundle(fig, root / 'figure', claim='Synthetic font/layout regression fixture',
                        source_data='test:synthetic', caption_notes='Not a scientific result', dpi=300)
            with Image.open(root / 'figure.png') as image:
                self.assertAlmostEqual(image.height / 300, fig.get_figheight(), delta=.01)
            with pymupdf.open(root / 'figure.pdf') as pdf:
                text = ''.join(page.get_text() for page in pdf)
                self.assertIn('循环次数', text)
                self.assertIn('放电容量', text)
                self.assertIn(visible_text(note), visible_text(text))
                self.assertTrue(any(pdf.extract_font(font[0])[3] for font in pdf[0].get_fonts(full=True)))
            svg = (root / 'figure.svg').read_text(encoding='utf-8')
            self.assertIn('循环次数', svg)
            self.assertIn('放电容量', svg)
            self.assertEqual(fig.batteryplot_condition_layout['boundary_and_data_overlap_check'], 'PASS')


if __name__ == '__main__':
    unittest.main()
