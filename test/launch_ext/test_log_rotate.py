
from pathlib import Path
import datetime
from tempfile import TemporaryDirectory
import os

from launch import LaunchContext
from launch_ext.actions import LogRotate

def create_dir_from_date(date: datetime.datetime, root: Path) -> Path:
    d = root / date.strftime("%Y-%m-%d-%H-%M-%S-%f-test-1704875")
    d.mkdir()
    os.utime(d, (date.timestamp(), date.timestamp()))
    return d


def test_file_contents():
    lc = LaunchContext()

    with TemporaryDirectory() as td:
        old = [create_dir_from_date(datetime.datetime.now() - datetime.timedelta(days=i), Path(td)) for i in range(3, 10)]
        fresh = [create_dir_from_date(datetime.datetime.now(), Path(td))]

        action = LogRotate(datetime.timedelta(days=1), td)
        action.visit(lc)

        for d in old:
            assert not d.exists()

        for d in fresh:
            assert d.exists()

# def test_rm_user_logs():
#     lc = LaunchContext()

#     action = LogRotate(datetime.timedelta(days=1), dry_run=True)
#     action.visit(lc)
