import flask
import humanize
import os

from datetime import datetime
from itertools import chain
from flask import Flask
from typing import Dict, List

import emu

app = Flask(__name__)


def unexpand_user(path: str) -> str:
    return path.replace(os.path.expanduser("~"), "~", 1)


def get_sink_data(sink: emu.Sink) -> Dict[str, str]:
    return {
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


def get_snapshot_data(snapshot: emu.Snapshot) -> Dict[str, str]:
    return {
        "sink": snapshot.sink.name,
        "name": snapshot.name,
        "how_long_ago": humanize.naturaltime(datetime.now() - snapshot.date),
        "seconds_ago": (datetime.now() - snapshot.date).seconds,
    }


def get_snapshots_data(source: emu.Source) -> List[Dict[str, str]]:
    snapshots = sum(chain(list(sink.snapshots()) for sink in source.sinks()), [])
    snapshots = list(reversed(sorted(snapshots, key=lambda x: x.id.snapshot_name)))
    data = list(get_snapshot_data(snapshot) for snapshot in snapshots)

    # determine timeline positions
    gaps = [data[0]["seconds_ago"]]
    for i in range(1, len(data)):
        gaps.append(data[i]["seconds_ago"] - data[i-1]["seconds_ago"])
    gaps = [g / max(gaps) for g in gaps]  # normalize
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
        "refresh_every": 10,  # seconds
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

    return flask.render_template("timeline.html", **data)


def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()
