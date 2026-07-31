import logging
from typing import Any

from ai.utils.text_utils import TextUtils

logger = logging.getLogger(__name__)


class DuplicateDetector:
    """Detects and merges duplicate or mirror repositories across hosting platforms."""

    def __init__(self, name_threshold: float = 0.9, desc_threshold: float = 0.8) -> None:
        self.name_threshold = name_threshold
        self.desc_threshold = desc_threshold

    def _str_similarity(self, s1: str, s2: str) -> float:
        """Compute the normalized similarity score between two strings [0.0 - 1.0]."""
        if not s1 or not s2:
            return 0.0
        s1_clean = s1.strip().lower()
        s2_clean = s2.strip().lower()
        if s1_clean == s2_clean:
            return 1.0
        dist = TextUtils.levenshtein_distance(s1_clean, s2_clean)

        max_len = max(len(s1_clean), len(s2_clean))
        return 1.0 - (dist / max_len)

    def _normalize_repo_name(self, full_name: str) -> str:
        """Normalize repository name for comparison (e.g. 'owner/repo-name' -> 'reponame')."""
        name = full_name.split("/")[-1] if "/" in full_name else full_name
        name = name.lower().strip()
        if name.endswith(".git"):
            name = name[:-4]
        # Remove common mirror suffixes
        for suffix in ("-mirror", "mirror-", "-replica", "replica-", "-clone", "clone-"):
            if name.endswith(suffix):
                name = name[:-len(suffix)]
            if name.startswith(suffix):
                name = name[len(suffix):]
        # Strip non-alphanumeric characters
        return "".join(c for c in name if c.isalnum())

    def are_duplicates(self, repo1: dict[str, Any], repo2: dict[str, Any]) -> bool:
        """Determine if two repositories are duplicates or mirrors."""
        # 1. Exact match on URL
        url1 = repo1.get("url") or repo1.get("html_url")
        url2 = repo2.get("url") or repo2.get("html_url")
        if url1 and url2 and url1.strip().lower() == url2.strip().lower():
            return True

        # 2. Check normalized names
        name1 = repo1.get("name") or repo1.get("repo_id") or ""
        name2 = repo2.get("name") or repo2.get("repo_id") or ""
        norm1 = self._normalize_repo_name(name1)
        norm2 = self._normalize_repo_name(name2)

        if not norm1 or not norm2:
            return False

        # If name similarity is below the threshold, they are not duplicates
        name_sim = self._str_similarity(norm1, norm2)
        if name_sim < self.name_threshold:
            return False

        # 3. Check language compatibility (must not conflict)
        lang1 = (repo1.get("language") or "").strip().lower()
        lang2 = (repo2.get("language") or "").strip().lower()
        if lang1 and lang2 and lang1 != lang2:
            return False

        # 4. Check description similarity
        desc1 = repo1.get("description") or ""
        desc2 = repo2.get("description") or ""

        # If descriptions are empty, rely solely on language and name match
        if not desc1.strip() and not desc2.strip():
            return True

        desc_sim = self._str_similarity(desc1, desc2)
        return desc_sim >= self.desc_threshold

    def group_duplicates(self, repositories: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
        """Groups repositories that are duplicates of each other."""
        groups: list[list[dict[str, Any]]] = []
        for repo in repositories:
            matched = False
            for group in groups:
                if self.are_duplicates(repo, group[0]):
                    group.append(repo)
                    matched = True
                    break
            if not matched:
                groups.append([repo])
        return groups

    def deduplicate(self, repositories: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Deduplicates a list of repositories, keeping the canonical one for each group.

        Canonical repository selection criteria:
        1. Highest star count
        2. Highest fork count
        3. Platform priority (GitHub > others)
        """
        if not repositories:
            return []

        groups = self.group_duplicates(repositories)
        deduplicated = []

        for group in groups:
            # Sort to find canonical: stars desc, forks desc, owner name length asc
            def get_sort_key(r: dict[str, Any]) -> tuple[int, int, int]:
                stars = int(r.get("stars") or r.get("stargazers_count") or 0)
                forks = int(r.get("forks") or r.get("forks_count") or 0)
                # GitHub priority (simple check)
                url = (r.get("url") or r.get("html_url") or "").lower()
                platform_score = 1 if "github.com" in url else 0
                return (stars, forks, platform_score)

            group.sort(key=get_sort_key, reverse=True)
            canonical = group[0].copy()

            if len(group) > 1:
                # Add duplicate/mirror references to metadata
                if "metadata" not in canonical:
                    canonical["metadata"] = {}
                elif canonical["metadata"] is None:
                    canonical["metadata"] = {}

                mirrors = []
                for mirror in group[1:]:
                    mirrors.append({
                        "repo_id": mirror.get("repo_id") or mirror.get("name"),
                        "url": mirror.get("url") or mirror.get("html_url"),
                        "stars": mirror.get("stars") or mirror.get("stargazers_count") or 0,
                        "forks": mirror.get("forks") or mirror.get("forks_count") or 0,
                        "language": mirror.get("language"),
                    })
                canonical["metadata"]["mirrors"] = mirrors

            deduplicated.append(canonical)

        return deduplicated
