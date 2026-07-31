from ai.models.comparison import ComparisonDimension, ComparisonResult
from ai.models.exceptions import AIModuleError, SummaryError


def test_models_exceptions() -> None:
    # Verify inheritance structure
    exc = SummaryError("Failed to generate summary")
    assert isinstance(exc, AIModuleError)
    assert isinstance(exc, Exception)
    assert str(exc) == "Failed to generate summary"


def test_comparison_models() -> None:
    # Verify ComparisonDimension model validation
    dim = ComparisonDimension(name="Features", scores={"repo-a": 8.0, "repo-b": 7.5})
    assert dim.name == "Features"
    assert dim.scores["repo-a"] == 8.0

    # Verify ComparisonResult model validation
    res = ComparisonResult(
        repositories=["repo-a", "repo-b"],
        dimensions=[dim],
        recommendation="Recommend repo-a",
    )
    assert res.repositories == ["repo-a", "repo-b"]
    assert len(res.dimensions) == 1
    assert res.recommendation == "Recommend repo-a"
