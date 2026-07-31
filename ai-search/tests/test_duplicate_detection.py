import pytest

from ai.duplicate_detection.detector import DuplicateDetector


@pytest.fixture
def detector() -> DuplicateDetector:
    return DuplicateDetector(name_threshold=0.9, desc_threshold=0.8)


def test_str_similarity(detector: DuplicateDetector) -> None:
    assert detector._str_similarity("tensorflow", "tensorflow") == 1.0
    assert detector._str_similarity("tensorflow", "pytorch") < 0.3
    assert detector._str_similarity("", "pytorch") == 0.0


def test_normalize_repo_name(detector: DuplicateDetector) -> None:
    assert detector._normalize_repo_name("owner/repo-name") == "reponame"
    assert detector._normalize_repo_name("owner/repo-name-mirror") == "reponame"
    assert detector._normalize_repo_name("owner/repo-name.git") == "reponame"
    assert detector._normalize_repo_name("replica-repo") == "repo"


def test_are_duplicates_url_match(detector: DuplicateDetector) -> None:
    repo1 = {"name": "repo1", "url": "https://github.com/org/repo"}
    repo2 = {"name": "repo2", "url": "https://github.com/org/repo"}
    assert detector.are_duplicates(repo1, repo2) is True


def test_are_duplicates_name_and_desc_match(detector: DuplicateDetector) -> None:
    repo1 = {
        "name": "react-native",
        "description": "A framework for building native applications using React",
        "language": "JavaScript",
    }
    repo2 = {
        "name": "reactnative-mirror",
        "description": "A framework for building native applications using React",
        "language": "JavaScript",
    }
    assert detector.are_duplicates(repo1, repo2) is True


def test_are_duplicates_different_languages(detector: DuplicateDetector) -> None:
    repo1 = {
        "name": "react-native",
        "description": "A framework for building native applications using React",
        "language": "JavaScript",
    }
    repo2 = {
        "name": "reactnative-mirror",
        "description": "A framework for building native applications using React",
        "language": "Python",
    }
    assert detector.are_duplicates(repo1, repo2) is False


def test_are_duplicates_different_descriptions(detector: DuplicateDetector) -> None:
    repo1 = {
        "name": "react-native",
        "description": "A framework for building native applications using React",
        "language": "JavaScript",
    }
    repo2 = {
        "name": "reactnative-mirror",
        "description": "Some totally different tool for react native development",
        "language": "JavaScript",
    }
    assert detector.are_duplicates(repo1, repo2) is False


def test_deduplicate_keeps_canonical(detector: DuplicateDetector) -> None:
    repositories = [
        {
            "repo_id": "gitlab/repo-mirror",
            "name": "repo-mirror",
            "description": "Awesome python library",
            "stars": 10,
            "forks": 2,
            "language": "Python",
            "url": "https://gitlab.com/org/repo",
        },
        {
            "repo_id": "github/repo",
            "name": "repo",
            "description": "Awesome python library",
            "stars": 100,
            "forks": 20,
            "language": "Python",
            "url": "https://github.com/org/repo",
        },
    ]

    dedupped = detector.deduplicate(repositories)
    assert len(dedupped) == 1
    assert dedupped[0]["repo_id"] == "github/repo"
    assert dedupped[0]["stars"] == 100
    assert len(dedupped[0]["metadata"]["mirrors"]) == 1
    assert dedupped[0]["metadata"]["mirrors"][0]["repo_id"] == "gitlab/repo-mirror"


def test_deduplicate_empty_list(detector: DuplicateDetector) -> None:
    assert detector.deduplicate([]) == []
