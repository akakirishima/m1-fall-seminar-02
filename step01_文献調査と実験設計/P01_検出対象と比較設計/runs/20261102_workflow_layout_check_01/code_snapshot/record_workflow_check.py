from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib
import json
import platform
import shutil
import subprocess
import sys

root = Path.cwd().resolve()
sys.path.insert(0, str(root / 'research_tools'))
import ai_records

state = ai_records.read_json(root / 'research_state.json')
package = next(p for p in state['work_packages'] if p['id'] == 'P01')
run_id = '20261102_workflow_layout_check_01'
run_relative = Path(package['runs_dir']) / run_id
run = root / run_relative
run.mkdir(parents=True, exist_ok=False)
(run / 'code_snapshot').mkdir()
(run / 'input_snapshot').mkdir()

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

codes = []
for source, name in [
    (root / 'research_tools/verify_workflow_layout.py', 'verify_workflow_layout.py'),
    (root / 'research_tools/ai_records.py', 'ai_records.py'),
    (Path(__file__), 'record_workflow_check.py'),
]:
    target = run / 'code_snapshot' / name
    shutil.copyfile(source, target)
    codes.append({'id': name, 'snapshot_ref': 'code_snapshot/' + name, 'sha256': digest(target)})

inputs = []
for name in ['research_state.json', '研究計画_詳細.md', '共通/作業フォルダと発表根拠の運用.md']:
    target = run / 'input_snapshot' / Path(name).name
    shutil.copyfile(root / name, target)
    inputs.append({'id': Path(name).stem, 'role': 'workflow_reference_snapshot', 'version': '1.7',
                   'sha256': digest(target), 'storage': 'repository', 'ref': target.relative_to(root).as_posix()})

report_relative = (run_relative / 'verification.json').as_posix()
command = ['python', (run_relative / 'code_snapshot/verify_workflow_layout.py').as_posix(),
           '--root', '.', '--output', report_relative]
manifest = ai_records.read_json(root / 'templates/experiment_manifest.json')
manifest.update({
    'is_template': False, 'run_id': run_id, 'step_id': 'step01', 'method_id': None,
    'operation': 'workflow_record_structure_check',
    'purpose': '工程フォルダと参照文書の整合性確認。実データと研究モデルの評価ではない。',
    'status': 'running', 'plan_version': state['plan_version'],
    'protocol_versions': state['protocol_versions'], 'parent_run_ids': [],
    'started_at': datetime.now(timezone(timedelta(hours=9))).isoformat(),
    'command_argv': command, 'working_directory': '.', 'code': codes, 'inputs': inputs,
    'config': {'work_package_id': 'P01', 'expected_package_count': 14,
               'scope': 'registered folders, dependencies and document links'},
    'environment': {'python': sys.version, 'platform': platform.platform()},
    'notes_ref': (run_relative / '実行結果.md').as_posix(),
    'reproduction': {'status': 'not_checked',
                     'command_argv': command[:-1] + ['NEW_OUTPUT_PATH'],
                     'missing': ['別環境での再実行は未確認', '参照文書全体と存在するリンク先の版は完全には複製していない']},
})
ai_records.write_json(run / 'manifest.json', manifest)
result = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding='utf-8')
(run / 'process_output.txt').write_text(result.stdout + result.stderr, encoding='utf-8')
manifest['finished_at'] = datetime.now(timezone(timedelta(hours=9))).isoformat()
manifest['exit_code'] = result.returncode
manifest['status'] = 'completed' if result.returncode == 0 else 'failed'
manifest['validation'] = {'status': 'passed' if result.returncode == 0 else 'failed',
                          'checks': ['工程の登録、専用フォルダ、依存関係、文書とリンクの存在を検査']}
if result.returncode:
    manifest['failure'] = {'type': 'workflow_check_failed', 'message': 'process_output.txtとverification.jsonを参照'}
for name in ['verification.json', 'process_output.txt']:
    target = run / name
    if target.exists():
        manifest['outputs'].append({'id': name, 'role': 'workflow_check_output', 'version': '1',
                                    'sha256': digest(target), 'storage': 'repository',
                                    'ref': target.relative_to(root).as_posix()})
ai_records.write_json(run / 'manifest.json', manifest)
notes = '''# 工程フォルダと記録の構成確認

## 目的と実施範囲

P01からP14の登録先、専用のコードと設定と実行保存先、依存関係、文書とリンクを保存コードから検査した。
実行条件、環境、入出力の識別値はmanifest.jsonを、個別の結果はverification.jsonとprocess_output.txtを参照する。
新しい工程内のrunsへ記録を置く運用の確認を兼ねる。

## 制約と次の作業

この実行は管理構成の確認で、モデルの推論や学習、実注釈、性能評価、PowerPointの検証ではない。
入力として状態JSONと計画と作業規則の実行時コピーを保存したが、参照先全体の完全複製や別環境での再現確認は行っていない。
次は索引生成と記録検査を行い、P02の動画所在と試行患者の割当確認へ進む。
'''
(run / '実行結果.md').write_text(notes, encoding='utf-8')
print(json.dumps({'run_id': run_id, 'status': manifest['status'], 'output': report_relative}, ensure_ascii=True))
print(result.stdout)
raise SystemExit(result.returncode)
