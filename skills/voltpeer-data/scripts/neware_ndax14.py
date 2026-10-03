"""Preserve the three source layers of the checked NDAX NDC-14 layout.

Field layouts/units follow NewareNDA 2026.6.11, _read_ndc_14_filetype_1,
_read_ndc_14_filetype_18 and _read_ndc_14_filetype_7. The pinned reader is
required and cross-checks the decoded quantities. No binary format is inferred.
Repeated run information and zero voltage observations stay in their layers;
no one-to-many join, time interpolation or cycle regeneration is performed.

The layout attribution and BSD terms are retained below from NewareNDA.
Copyright (c) 2022-2024 SES AI Corporation, All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""
from __future__ import annotations

import importlib.metadata
import logging
import math
import shutil
import struct
import tempfile
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

READER_VERSION = '2026.6.11'
MAX_UNCOMPRESSED_BYTES = 256 * 1024 * 1024
LAYOUT = {'data.ndc': (1, 14), 'data_runInfo.ndc': (18, 14), 'data_step.ndc': (7, 14)}
LAYOUT_SOURCE = 'https://github.com/d-cogswell/NewareNDA/blob/master/NewareNDA/NewareNDAx.py'


class NativeExportNeeded(ValueError):
    def __init__(self, code, message, details=None):
        super().__init__(message)
        self.code = code
        self.details = details or {}


def _blocks(data, name, item_format, trailer):
    if len(data) < 8192 or len(data) % 4096:
        raise NativeExportNeeded('malformed_native_blocks', 'NDAX 数据块长度不符合已验证版本；请用 BTSDA 导出完整表格。')
    for offset in range(4096, len(data), 4096):
        block = data[offset + 132:offset + 4096 - trailer]
        item_size = struct.calcsize(item_format)
        if len(block) % item_size:
            raise NativeExportNeeded('malformed_native_blocks', 'NDAX 数据块不能按已验证记录布局读取。')
        for item_offset, row in enumerate(struct.iter_unpack(item_format, block)):
            yield offset + 132 + item_offset * item_size, row


class _LogCapture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.messages = []

    def emit(self, record):
        self.messages.append({'level': record.levelname, 'message': record.getMessage()})


def _library_read(path, reader):
    logger = logging.getLogger('newarenda')
    capture = _LogCapture()
    old_level, old_propagate, old_handlers = logger.level, logger.propagate, list(logger.handlers)
    # Version/remark logs can contain unpublished context. Keep CLI stdout as
    # JSON and save these messages only in the caller's private import record.
    logger.handlers = [capture]
    logger.propagate = False
    try:
        frame = reader.read(str(path), software_cycle_number=False, cycle_mode='chg', log_level='INFO')
    finally:
        logger.handlers = old_handlers
        logger.setLevel(old_level)
        logger.propagate = old_propagate
    if any('interpolated data' in item['message'] for item in capture.messages):
        raise NativeExportNeeded('native_interpolation_required', '读取器需要补算记录；请从 BTSDA 导出，原生路线不插值。')
    return frame, capture.messages


def read_source_layers(path):
    """Return matrices plus a private import record; caller writes new outputs."""
    try:
        version = importlib.metadata.version('NewareNDA')
    except importlib.metadata.PackageNotFoundError as error:
        raise NativeExportNeeded('native_dependency_missing', '可选原生读取器未安装；在项目环境安装 requirements-native.txt，或用 BTSDA 导出。') from error
    if version != READER_VERSION:
        raise NativeExportNeeded('native_dependency_version', '原生读取仅验证 NewareNDA 2026.6.11；请使用固定依赖或 BTSDA 导出。', {'installed_version': version})
    try:
        import NewareNDA
        from NewareNDA.dicts import state_dict
    except ImportError as error:
        raise NativeExportNeeded('native_dependency_missing', '原生读取器依赖不完整；安装 requirements-native.txt 或用 BTSDA 导出。') from error

    try:
        with zipfile.ZipFile(path) as archive:
            members = archive.infolist()
            names = [member.filename for member in members]
            if len(names) != len(set(names)):
                raise NativeExportNeeded('duplicate_native_members', 'NDAX 中有重复文件成员；请从 BTSDA 重新导出。')
            if sum(member.file_size for member in members) > MAX_UNCOMPRESSED_BYTES:
                raise NativeExportNeeded('native_size_limit', 'NDAX 解压体积超过本地读取上限；请分通道/记录区间导出。')
            if any(member.flag_bits & 1 for member in members):
                raise NativeExportNeeded('encrypted_native_file', '加密 NDAX 需要厂商软件导出。')
            if not set(LAYOUT) <= set(names):
                raise NativeExportNeeded('unvalidated_native_layout', 'NDAX 不是已验证的 NDC-14 分层布局；请用 BTSDA 导出。')
            # Auxiliary channel alignment is not covered by the checked samples.
            allowed_ndc = set(LAYOUT) | {'data_log.ndc', 'data_es.ndc'}
            if any(name.casefold().endswith('.ndc') and name not in allowed_ndc for name in names):
                raise NativeExportNeeded('unvalidated_native_auxiliary', '该 NDAX 含未验证的辅助通道；请用 BTSDA 导出，避免丢失或误配通道。')
            payload = {}
            for name, expected in LAYOUT.items():
                data = archive.read(name)
                if len(data) < 3 or (data[0], data[2]) != expected:
                    raise NativeExportNeeded('unvalidated_native_version', 'NDAX 的 NDC 版本/类型未在本项目验证；请用 BTSDA 导出。')
                payload[name] = data
    except NativeExportNeeded:
        raise
    except (OSError, zipfile.BadZipFile, RuntimeError, NotImplementedError) as error:
        raise NativeExportNeeded('malformed_native_archive', 'NDAX 归档无法完整读取；保留原文件并用 BTSDA 检查/导出。') from error

    # Preserve all runInfo entries, including repeated Index values. Reading
    # a separate layer avoids selecting one timestamp/capacity by a join rule.
    run_rows, first_run = [], {}
    for offset, values in _blocks(payload['data_runInfo.ndc'], 'runInfo', '<ixffff8xiiiih8s', 4):
        if values[8] == 0:  # Padding marker in the pinned layout.
            continue
        if values[8] < 0 or not 0 <= values[9] < 1000:
            raise NativeExportNeeded('invalid_native_identifier', '运行信息有无效记录号或毫秒字段；请用 BTSDA 核对。')
        run_rows.append((offset, values))
        first_run.setdefault(values[8], values)
    if not run_rows:
        raise NativeExportNeeded('empty_native_records', 'NDAX 没有可读取运行信息；请检查导出范围。')

    slots = list(_blocks(payload['data.ndc'], 'measurement', '<ff', 4))
    if any(index > len(slots) for index in first_run):
        raise NativeExportNeeded('native_alignment_missing', '运行信息记录号超出测量层范围；请用 BTSDA 导出。')
    nonzero = {i for i, (_, values) in enumerate(slots, 1) if values[0] != 0}
    if nonzero - set(first_run):
        raise NativeExportNeeded('native_interpolation_required', '测量记录缺少运行信息；原生路线不补算时间/容量/能量，请用 BTSDA 导出。',
                                 {'records_without_run_information': len(nonzero - set(first_run))})
    retained_indices = sorted(nonzero | set(first_run))
    if len(retained_indices) != retained_indices[-1]:
        raise NativeExportNeeded('native_unreferenced_zero_slot', '有效记录区间内有未配运行信息的零值位置；不能当作尾部填充删除，请用 BTSDA 导出。')
    zero_voltage = sum(slots[index - 1][1][0] == 0 for index in retained_indices)
    measurement_rows = [[str(index), str(slots[index - 1][0]), repr(slots[index - 1][1][0]), repr(slots[index - 1][1][1])]
                        for index in retained_indices]

    native_steps = []
    for offset, values in _blocks(payload['data_step.ndc'], 'step', '<ii16sb12s', 5):
        if values[1] != 0:
            if values[3] not in state_dict:
                raise NativeExportNeeded('unvalidated_native_status', 'NDAX 有读取器未支持的工步状态；请用 BTSDA 导出。')
            native_steps.append([str(len(native_steps) + 1), str(offset), str(values[0]), str(values[1]),
                                 str(values[3]), state_dict[values[3]], values[2].hex(), values[4].hex()])
    if not native_steps:
        raise NativeExportNeeded('empty_native_steps', 'NDAX 无工步层，不能确认记录身份；请用 BTSDA 导出。')

    # Reader units: Voltage V, Time s, Current mA, capacity mAh and energy mWh.
    # The source v14 slots store A/Ah/Wh and milliseconds, as explicitly stated
    # by the pinned source transformations. Compare, never infer from magnitudes.
    with tempfile.TemporaryDirectory(prefix='vp-ndax-') as temp:
        checked_path = Path(temp) / 'source.ndax'
        shutil.copyfile(path, checked_path)
        try:
            frame, logs = _library_read(checked_path, NewareNDA)
        except NativeExportNeeded:
            raise
        except Exception as error:
            raise NativeExportNeeded('native_decoder_error', '固定版本原生读取器报错；请用 BTSDA 检查/导出。', {'exception_type': type(error).__name__}) from error
    required = ['Index', 'Time', 'Voltage', 'Current(mA)', 'Charge_Capacity(mAh)',
                'Discharge_Capacity(mAh)', 'Charge_Energy(mWh)', 'Discharge_Energy(mWh)', 'Timestamp']
    if any(column not in frame.columns for column in required) or len(frame) != len(nonzero):
        raise NativeExportNeeded('native_decoder_count_mismatch', '原生读取器输出列或记录数与源层不一致；请用 BTSDA 导出。')
    column_index = {name: frame.columns.get_loc(name) for name in required}
    compared = 0
    for row in frame.itertuples(index=False, name=None):
        index = int(row[column_index['Index']])
        if index not in nonzero:
            raise NativeExportNeeded('native_decoder_index_mismatch', '原生读取器记录号与源层不一致。')
        voltage, current_a = slots[index - 1][1]
        metadata = first_run[index]
        expected = {'Voltage': voltage, 'Current(mA)': current_a * 1000, 'Time': metadata[0] / 1000,
                    'Charge_Capacity(mAh)': metadata[1] * 1000, 'Discharge_Capacity(mAh)': metadata[2] * 1000,
                    'Charge_Energy(mWh)': metadata[3] * 1000, 'Discharge_Energy(mWh)': metadata[4] * 1000}
        for name, number in expected.items():
            if not math.isclose(float(row[column_index[name]]), number, rel_tol=5e-7, abs_tol=1e-7):
                raise NativeExportNeeded('native_decoder_quantity_mismatch', '原生读取器的时间/电压/电流/容量/能量与源层单位核对不一致。', {'field': name})
        timestamp = row[column_index['Timestamp']]
        if not hasattr(timestamp, 'timestamp') or abs(timestamp.timestamp() - (metadata[6] + metadata[9] / 1000)) > 0.000001:
            raise NativeExportNeeded('native_decoder_timestamp_mismatch', '原生读取器时间戳与源层不一致。')
        compared += 1

    decoded_run = []
    for offset, values in run_rows:
        timestamp = datetime.fromtimestamp(values[6] + values[9] / 1000, timezone.utc).isoformat()
        decoded_run.append([str(values[8]), str(offset), str(values[7]), str(values[0]), str(values[5]),
                            repr(values[1]), repr(values[2]), repr(values[3]), repr(values[4]), str(values[6]),
                            str(values[9]), timestamp, values[10].hex()])
    counts = Counter(values[8] for _, values in run_rows)
    duplicate_rows = sum(count - 1 for count in counts.values())
    conflicting_ids = sum(any(values != first_run[index] for _, values in run_rows if values[8] == index)
                          for index, count in counts.items() if count > 1)
    pending = ['原生源层尚未与同一次测试的 BTSDA 导出报表做定量一致性核对。',
               '测量、运行信息、工步层保持独立；确认目标图所需的记录对应方式和原生零基循环定义。']
    if duplicate_rows:
        pending.append('运行信息有重复记录号；不同时间/容量条目均保留，绘图前确认对应规则。')
    if zero_voltage:
        pending.append('源文件有零电压测量，已保留；第三方读取器会略过这些记录，须核对仪器标记/测试状态。')
    info = {'reader': 'NewareNDA', 'reader_version': version, 'license': 'BSD-3-Clause',
            'layout': 'NDC-14 split source layers', 'layout_source': LAYOUT_SOURCE,
            'reader_arguments': {'software_cycle_number': False, 'cycle_mode': 'chg', 'log_level': 'INFO'},
            'native_cycle_basis': 'Cycle_ZeroBased copied from step layer; no +1 or regenerated cycles in exported source layers',
            'source_layer_counts': {'measurements': len(measurement_rows), 'run_information': len(run_rows), 'native_steps': len(native_steps)},
            'reader_interpreted_records': len(frame), 'quantity_records_compared': compared,
            'zero_voltage_records_retained': zero_voltage, 'duplicate_run_information_rows_retained': duplicate_rows,
            'conflicting_run_information_ids': conflicting_ids, 'padding_slots_excluded': len(slots) - len(retained_indices),
            'unit_and_timestamp_comparison': 'pass', 'vendor_equivalence': 'not_verified',
            'merged_records': False, 'interpolation': False, 'scientific_validation': False,
            'pending_context': pending, 'decoder_log': logs}
    common = {'format': 'NDAX NDC-14', 'formula_evaluation': False,
              'source_row_meaning': 'decoded source-layer row; Native_Byte_Offset gives original member byte location',
              'cross_layer_alignment_confirmed': False}
    matrices = [
        ('native-measurements', [['Index', 'Native_Byte_Offset', 'Voltage(V)', 'Current(A)'], *measurement_rows],
         {**common, 'table_role': 'record', 'member': 'data.ndc', 'index_origin': 'one-based physical slot ordinal'}),
        ('native-run-information', [['Index', 'Native_Byte_Offset', 'Step_Encoded', 'Time(ms)', 'Interval(ms)',
          'Charge_Capacity(Ah)', 'Discharge_Capacity(Ah)', 'Charge_Energy(Wh)', 'Discharge_Energy(Wh)',
          'Timestamp_Epoch(s)', 'Timestamp_Millisecond(ms)', 'Timestamp_UTC', 'Reserved_Hex'], *decoded_run],
         {**common, 'table_role': 'record_metadata', 'member': 'data_runInfo.ndc', 'timestamp_utc_is_derived': True}),
        ('native-step-information', [['Native_Step_Ordinal', 'Native_Byte_Offset', 'Cycle_ZeroBased', 'Step_Index',
          'Status_Code', 'Status', 'Reserved_1_Hex', 'Reserved_2_Hex'], *native_steps],
         {**common, 'table_role': 'step_metadata', 'member': 'data_step.ndc', 'status_label_source': 'pinned reader state_dict'}),
    ]
    return matrices, info
