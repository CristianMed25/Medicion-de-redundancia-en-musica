from pathlib import Path

from music_entropy.analysis import AnalysisResult
from music_entropy import visualization


def _dummy_result(tmpdir: Path) -> AnalysisResult:
    local = [{"window": i, "h0": 1.0 + i * 0.1, "hk": 0.5 + i * 0.05} for i in range(4)]
    return AnalysisResult(
        path=tmpdir / "piece.mid",
        h0=2.0,
        hk=1.0,
        hmax=2.5,
        redundancy=1.5,
        lzc=3,
        lzc_normalized=0.6,
        ip=0.4,
        local=local,
    )


def test_plot_global_and_local(tmp_path):
    res = _dummy_result(tmp_path)
    global_path = tmp_path / "global.png"
    local_path = tmp_path / "local.png"
    visualization.plot_global_metrics(res, global_path)
    visualization.plot_local_entropies(res, local_path)
    assert global_path.exists()
    assert local_path.exists()
