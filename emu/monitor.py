import datetime
import flask
import humanize
import os

from itertools import chain
from flask import Flask
from typing import Dict, List

import emu

app = Flask(__name__)


def unexpand_user(path: str) -> str:
    return path.replace(os.path.expanduser("~"), "~", 1)


def get_sink_data(sink: emu.Sink) -> Dict[str, str]:
    d =  {
        "name": sink.name,
        "path": unexpand_user(sink.path),
        "space": {
            "used": humanize.naturalsize(sink.used_space_on_device),
            "free": humanize.naturalsize(sink.free_space_on_device),
            "total": humanize.naturalsize(sink.device_capacity),
            "ratio_used": int((1 - sink.free_space_ratio) * 100),
            "ratio_free": int(sink.free_space_ratio * 100),
        }
    }

    if sink.is_inprogress:
        d["in_progress"] = True
        d["in_progress_since"] = (datetime.datetime.now() - sink.lock.date).total_seconds()
    else:
        d["in_progress"] = False
        d["in_progress_since"] = None

    return d


def get_snapshot_data(snapshot: emu.Snapshot) -> Dict[str, str]:
    return {
        "sink": snapshot.sink.name,
        "name": snapshot.name,
        "how_long_ago": humanize.naturaltime(datetime.datetime.now() - snapshot.date),
        "seconds_ago": (datetime.datetime.now() - snapshot.date).total_seconds(),
    }


def get_snapshots_data(source: emu.Source) -> List[Dict[str, str]]:
    snapshots = sum(chain(list(sink.snapshots()) for sink in source.sinks()), [])
    snapshots = list(reversed(sorted(snapshots, key=lambda x: x.id.snapshot_name)))
    data = list(get_snapshot_data(snapshot) for snapshot in snapshots)

    # determine timeline positions
    gaps = [data[0]["seconds_ago"]]
    for i in range(1, len(data)):
        gaps.append(data[i]["seconds_ago"] - data[i-1]["seconds_ago"])
    mingap = min(gaps)
    gaps = [g / mingap for g in gaps]  # normalize
    acc = 0
    for d, gap in zip(data, gaps):
        acc += gap
        d["position"] = acc
        d["padding_top"] = gap

    return data


@app.route('/')
def index():
    source_dir = emu.find_source_dir('.')
    source = emu.Source(source_dir)

    data = {
        "refresh_every": 60,  # seconds
        "assets": {
            "cache_tag": 1,
            "styles_css": flask.url_for('static', filename='styles.css'),
            "site_js": flask.url_for('static', filename='site.js'),
        },
        "source": {
            "path": unexpand_user(source.path),
        },
        "sinks": [get_sink_data(sink) for sink in source.sinks()],
        "snapshots": get_snapshots_data(source),
        "emu": {
            "version": emu.Meta.version,
        },
    }

    data["num_snapshots"] = len(data["snapshots"])
    data["num_sinks"] = len(data["sinks"])

    data["in_progress"] = sum(1 if sink["in_progress"] else 0 for sink in data["sinks"])
    data["in_progress_since"] = max(sink["in_progress_since"] for sink in data["sinks"])
    if data["in_progress_since"]:
        data["in_progress_since_hr"] = humanize.naturaltime(
            datetime.datetime.now() - datetime.timedelta(seconds=data["in_progress_since"]))

    return flask.render_template("timeline.html", **data)


def main(source_dir="/", **flask_opts):
    """
    Main monitor loop. This method never returns.

    Arguments:
        **flask_opts:
    """
    os.chdir(source_dir)
    app.run(**flask_opts)


if __name__ == "__main__":
    main()
