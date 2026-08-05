from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional

from .models import CandidateRepo, FactorScore
from .weight_manager import WeightManager

logger = logging.getLogger(__name__)


class BaseFactor:
    name: str = ""
    label: str = ""

    def __init__(self, weight_manager: WeightManager):
        self._wm = weight_manager

    def compute(
        self, repo: CandidateRepo, query: str = "", intent: Optional[str] = None
    ) -> Optional[FactorScore]:
        raise NotImplementedError

    def _make_score(
        self, raw_value: float, metadata: Optional[dict[str, Any]] = None
    ) -> FactorScore:
        normalized = self._wm.normalize(self.name, raw_value)
        weight = self._wm.get_weight(self.name)
        return FactorScore(
            name=self.name,
            label=self.label,
            raw_value=raw_value,
            normalized_score=normalized,
            weight=weight,
            contribution=weight * normalized,
            metadata=metadata,
        )


class SemanticSimilarity(BaseFactor):
    name = "semantic_similarity"
    label = "Semantic Similarity"

    def compute(
        self, repo: CandidateRepo, query: str = "", intent: Optional[str] = None
    ) -> FactorScore:
        return self._make_score(repo.semantic_score)


class UserIntentMatch(BaseFactor):
    name = "user_intent_match"
    label = "User Intent Match"

    def compute(
        self, repo: CandidateRepo, query: str = "", intent: Optional[str] = None
    ) -> FactorScore:
        score = repo.semantic_score
        if intent and repo.metadata:
            repo_intent = repo.metadata.get("intent", "")
            if repo_intent and intent.lower() == repo_intent.lower():
                score = min(1.0, score + 0.2)
        return self._make_score(score)


class GitHubStars(BaseFactor):
    name = "github_stars"
    label = "GitHub Stars"

    def compute(
        self, repo: CandidateRepo, query: str = "", intent: Optional[str] = None
    ) -> FactorScore:
        return self._make_score(float(repo.stars), {"stars": repo.stars})


class ForkCount(BaseFactor):
    name = "fork_count"
    label = "Fork Count"

    def compute(
        self, repo: CandidateRepo, query: str = "", intent: Optional[str] = None
    ) -> FactorScore:
        return self._make_score(float(repo.forks), {"forks": repo.forks})


class ContributorCount(BaseFactor):
    name = "contributor_count"
    label = "Contributor Count"

    def compute(
        self, repo: CandidateRepo, query: str = "", intent: Optional[str] = None
    ) -> FactorScore:
        return self._make_score(float(repo.contributors), {"contributors": repo.contributors})


class CommitFrequency(BaseFactor):
    name = "commit_frequency"
    label = "Commit Frequency"

    def compute(
        self, repo: CandidateRepo, query: str = "", intent: Optional[str] = None
    ) -> FactorScore:
        return self._make_score(
            float(repo.commits_last_3_months),
            {"commits_last_3_months": repo.commits_last_3_months},
        )


class RecentActivity(BaseFactor):
    name = "recent_activity"
    label = "Recent Activity"

    def compute(
        self, repo: CandidateRepo, query: str = "", intent: Optional[str] = None
    ) -> FactorScore:
        days = repo.days_since_last_commit
        if days is None:
            return self._make_score(365.0, {"days_since_last_commit": None})
        return self._make_score(float(days), {"days_since_last_commit": days})


class RepositoryAge(BaseFactor):
    name = "repository_age"
    label = "Repository Age"

    def compute(
        self, repo: CandidateRepo, query: str = "", intent: Optional[str] = None
    ) -> FactorScore:
        days = 0
        if repo.created_at:
            try:
                created = datetime.fromisoformat(repo.created_at.replace("Z", "+00:00"))
                days = (datetime.now().astimezone() - created).days
            except (ValueError, TypeError):
                days = 0
        return self._make_score(float(days), {"age_days": days})


class ReleaseFrequency(BaseFactor):
    name = "release_frequency"
    label = "Release Frequency"

    def compute(
        self, repo: CandidateRepo, query: str = "", intent: Optional[str] = None
    ) -> FactorScore:
        return self._make_score(
            float(repo.releases_last_year),
            {"releases_last_year": repo.releases_last_year},
        )


class IssueResolutionRate(BaseFactor):
    name = "issue_resolution_rate"
    label = "Issue Resolution Rate"

    def compute(
        self, repo: CandidateRepo, query: str = "", intent: Optional[str] = None
    ) -> FactorScore:
        rate = 0.0
        if repo.issues_total > 0:
            rate = repo.issues_closed / repo.issues_total
        return self._make_score(rate, {"closed": repo.issues_closed, "total": repo.issues_total})


class PRActivity(BaseFactor):
    name = "pr_activity"
    label = "Pull Request Activity"

    def compute(
        self, repo: CandidateRepo, query: str = "", intent: Optional[str] = None
    ) -> FactorScore:
        rate = 0.0
        if repo.prs_total > 0:
            rate = repo.prs_merged / repo.prs_total
        return self._make_score(rate, {"merged": repo.prs_merged, "total": repo.prs_total})


class DocumentationQuality(BaseFactor):
    name = "documentation_quality"
    label = "Documentation Quality"

    def compute(
        self, repo: CandidateRepo, query: str = "", intent: Optional[str] = None
    ) -> FactorScore:
        score = 0.0
        if repo.has_documentation:
            score = 0.7
            if repo.has_readme and repo.readme_length > 500:
                score = 1.0
        elif repo.has_readme:
            score = 0.4 if repo.readme_length > 200 else 0.2
        return self._make_score(score, {
            "has_documentation": repo.has_documentation,
            "has_readme": repo.has_readme,
            "readme_length": repo.readme_length,
        })


class READMECompleteness(BaseFactor):
    name = "readme_completeness"
    label = "README Completeness"

    def compute(
        self, repo: CandidateRepo, query: str = "", intent: Optional[str] = None
    ) -> FactorScore:
        score = 0.0
        if repo.has_readme:
            length_score = min(1.0, repo.readme_length / 2000.0)
            sections_score = min(1.0, repo.readme_sections / 6.0)
            badges_score = 0.3 if repo.readme_has_badges else 0.0
            score = 0.4 * length_score + 0.4 * sections_score + 0.2 * badges_score
        return self._make_score(score, {
            "readme_length": repo.readme_length,
            "readme_sections": repo.readme_sections,
            "has_badges": repo.readme_has_badges,
        })


class LicenseAvailability(BaseFactor):
    name = "license_availability"
    label = "License Availability"

    def compute(
        self, repo: CandidateRepo, query: str = "", intent: Optional[str] = None
    ) -> FactorScore:
        return self._make_score(1.0 if repo.has_license else 0.0, {"has_license": repo.has_license})


class RepositoryHealth(BaseFactor):
    name = "repository_health"
    label = "Repository Health"

    def compute(
        self, repo: CandidateRepo, query: str = "", intent: Optional[str] = None
    ) -> FactorScore:
        signals = []
        if repo.contributors >= 3:
            signals.append(1.0)
        elif repo.contributors > 0:
            signals.append(0.5)
        else:
            signals.append(0.0)

        if repo.days_since_last_commit is not None and repo.days_since_last_commit < 90:
            signals.append(1.0)
        elif repo.days_since_last_commit is not None and repo.days_since_last_commit < 365:
            signals.append(0.5)
        else:
            signals.append(0.0)

        if repo.issues_total > 0:
            signals.append(min(1.0, repo.issues_closed / max(1, repo.issues_total)))
        else:
            signals.append(0.5)

        if repo.prs_total > 0:
            signals.append(min(1.0, repo.prs_merged / max(1, repo.prs_total)))
        else:
            signals.append(0.5)

        if repo.releases_last_year > 0:
            signals.append(1.0)
        else:
            signals.append(0.0)

        score = sum(signals) / len(signals) if signals else 0.0
        return self._make_score(score, {
            "contributors": repo.contributors,
            "recent_commits": repo.days_since_last_commit,
            "issue_rate": repo.issues_closed / max(1, repo.issues_total),
            "pr_rate": repo.prs_merged / max(1, repo.prs_total),
        })


class CommunityAdoption(BaseFactor):
    name = "community_adoption"
    label = "Community Adoption"

    def compute(
        self, repo: CandidateRepo, query: str = "", intent: Optional[str] = None
    ) -> FactorScore:
        star_score = min(1.0, repo.stars / 10000.0) if repo.stars > 0 else 0.0
        fork_score = min(1.0, repo.forks / 3000.0) if repo.forks > 0 else 0.0
        contrib_score = min(1.0, repo.contributors / 500.0) if repo.contributors > 0 else 0.0
        score = 0.5 * star_score + 0.3 * fork_score + 0.2 * contrib_score
        return self._make_score(score, {
            "stars": repo.stars,
            "forks": repo.forks,
            "contributors": repo.contributors,
        })


class PopularityTrend(BaseFactor):
    name = "popularity_trend"
    label = "Popularity Trend"

    def compute(
        self, repo: CandidateRepo, query: str = "", intent: Optional[str] = None
    ) -> FactorScore:
        return self._make_score(
            float(repo.stars_last_90_days),
            {"stars_last_90_days": repo.stars_last_90_days},
        )


class TechnologyMatch(BaseFactor):
    name = "technology_match"
    label = "Technology Match"

    def compute(
        self, repo: CandidateRepo, query: str = "", intent: Optional[str] = None
    ) -> FactorScore:
        score = repo.semantic_score
        if repo.metadata and query:
            query_lower = query.lower()
            repo_topics = [t.lower() for t in repo.topics] if repo.topics else []
            for topic in repo_topics:
                if topic in query_lower or query_lower in topic:
                    score = min(1.0, score + 0.15)
            if repo.language and repo.language.lower() in query_lower:
                score = min(1.0, score + 0.1)
        return self._make_score(score, {
            "topics": repo.topics,
            "language": repo.language,
        })


class RepositoryTrust(BaseFactor):
    name = "repository_trust"
    label = "Repository Trust"

    def compute(
        self, repo: CandidateRepo, query: str = "", intent: Optional[str] = None
    ) -> FactorScore:
        star_score = min(1.0, repo.stars / 5000.0) if repo.stars > 0 else 0.0
        contrib_score = min(1.0, repo.contributors / 50.0) if repo.contributors > 0 else 0.0
        score = 0.5 * star_score + 0.5 * contrib_score
        return self._make_score(score, {"stars": repo.stars, "contributors": repo.contributors})


class ProjectMaturity(BaseFactor):
    name = "project_maturity"
    label = "Project Maturity"

    def compute(
        self, repo: CandidateRepo, query: str = "", intent: Optional[str] = None
    ) -> FactorScore:
        days = 0
        if repo.created_at:
            try:
                created = datetime.fromisoformat(repo.created_at.replace("Z", "+00:00"))
                days = (datetime.now().astimezone() - created).days
            except (ValueError, TypeError):
                days = 0
        age_score = min(1.0, days / 365.0)
        release_score = min(1.0, repo.releases_last_year / 5.0)
        score = 0.5 * age_score + 0.5 * release_score
        return self._make_score(score, {"age_days": days, "releases_last_year": repo.releases_last_year})


FACTOR_CLASSES: list[type[BaseFactor]] = [
    SemanticSimilarity,
    GitHubStars,
    ForkCount,
    ContributorCount,
    CommitFrequency,
    RecentActivity,
    RepositoryAge,
    ReleaseFrequency,
    IssueResolutionRate,
    PRActivity,
    DocumentationQuality,
    READMECompleteness,
    LicenseAvailability,
    RepositoryHealth,
    CommunityAdoption,
    PopularityTrend,
    TechnologyMatch,
    UserIntentMatch,
    RepositoryTrust,
    ProjectMaturity,
]

