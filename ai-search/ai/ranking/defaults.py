# Weight and normalization defaults for the Ranking Engine.
# Weights sum to 1.00. Loaded by WeightManager; can be overridden
# via JSON config file or programmatic API.

DEFAULT_WEIGHTS = {
    "semantic_similarity": 0.25,
    "user_intent_match": 0.10,
    "recent_activity": 0.08,
    "commit_frequency": 0.07,
    "issue_resolution_rate": 0.06,
    "technology_match": 0.05,
    "repository_health": 0.05,
    "community_adoption": 0.05,
    "contributor_count": 0.05,
    "documentation_quality": 0.05,
    "release_frequency": 0.03,
    "pr_activity": 0.03,
    "readme_completeness": 0.03,
    "github_stars": 0.02,
    "fork_count": 0.02,
    "license_availability": 0.02,
    "popularity_trend": 0.02,
    "repository_age": 0.02,
}

# Sum check
_WEIGHT_SUM = sum(DEFAULT_WEIGHTS.values())
assert abs(_WEIGHT_SUM - 1.0) < 0.001, f"Weights sum to {_WEIGHT_SUM}, expected 1.0"

DEFAULT_NORMALIZATION = {
    "semantic_similarity": {"method": "identity", "max_value": 1.0},
    "user_intent_match": {"method": "identity", "max_value": 1.0},
    "github_stars": {"method": "log_scale", "max_value": 100000, "cap": 50000},
    "fork_count": {"method": "log_scale", "max_value": 50000, "cap": 25000},
    "contributor_count": {"method": "log_scale", "max_value": 5000, "cap": 2000},
    "commit_frequency": {"method": "sigmoid", "midpoint": 30, "k": 0.1},
    "recent_activity": {"method": "exp_decay", "lambda": 0.02, "max_days": 365},
    "repository_age": {"method": "sigmoid", "midpoint": 730, "k": 0.005},
    "release_frequency": {"method": "sigmoid", "midpoint": 2, "k": 1.0},
    "issue_resolution_rate": {"method": "identity", "max_value": 1.0},
    "pr_activity": {"method": "identity", "max_value": 1.0},
    "documentation_quality": {"method": "identity", "max_value": 1.0},
    "readme_completeness": {"method": "identity", "max_value": 1.0},
    "license_availability": {"method": "boolean"},
    "repository_health": {"method": "identity", "max_value": 1.0},
    "community_adoption": {"method": "identity", "max_value": 1.0},
    "popularity_trend": {"method": "sigmoid", "midpoint": 50, "k": 0.02},
    "technology_match": {"method": "identity", "max_value": 1.0},
}

DEFAULT_RANKING_CONFIG = {
    "version": "1.0",
    "weights": DEFAULT_WEIGHTS,
    "normalization": DEFAULT_NORMALIZATION,
}
