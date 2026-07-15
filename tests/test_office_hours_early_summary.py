from datetime import datetime
from pathlib import Path

import yaml

from trendradar.core.scheduler import Scheduler


class Storage:
    pass


def load():
    config=yaml.safe_load(Path('config/config.yaml').read_text(encoding='utf-8'))
    timeline=yaml.safe_load(Path('config/timeline.yaml').read_text(encoding='utf-8'))
    return config,timeline


def resolve(at):
    config,timeline=load()
    return Scheduler(config['schedule'],timeline,Storage(),lambda:at).resolve()


def test_office_hours_keeps_original_windows():
    for at,key,mode in [
        (datetime(2026,7,14,9,30),'morning_briefing','current'),
        (datetime(2026,7,14,13,30),'noon_update','current'),
        (datetime(2026,7,14,17,30),'closing_summary','daily'),
    ]:
        r=resolve(at); assert r.period_key==key and r.push and r.report_mode==mode


def test_workday_0730_daily_summary():
    r=resolve(datetime(2026,7,14,7,30))
    assert r.period_key=='early_daily_summary' and r.push and r.analyze
    assert r.report_mode=='daily' and r.ai_mode=='daily' and r.once_push


def test_weekend_has_no_0730_summary():
    r=resolve(datetime(2026,7,18,7,30))
    assert r.period_key is None and not r.push


def test_cron_has_dedicated_workday_0730_without_hourly_collision():
    wf=yaml.safe_load(Path('.github/workflows/crawler.yml').read_text(encoding='utf-8'))
    schedules=wf.get('on',wf.get(True))['schedule']
    crons=[x['cron'] for x in schedules]
    assert '30 23 * * 0-4' in crons
    assert '33 0-22 * * *' in crons
    assert '33 * * * *' not in crons
