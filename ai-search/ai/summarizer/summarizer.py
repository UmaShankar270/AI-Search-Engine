import json
import logging
from typing import Any, Optional

from ai.config.settings import Settings
from ai.models.comparison import ComparisonDimension, ComparisonResult
from ai.models.exceptions import SummaryError

logger = logging.getLogger(__name__)


class SummaryGenerator:
    """Generates AI-powered repository summaries using Gemini or OpenAI."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or Settings()
        self._client: Optional[Any] = None
        self._init_client()

    def _init_client(self) -> None:
        """Initialize the OpenAI-compatible API client if keys are present."""
        provider = self.settings.llm_provider.lower()
        api_key = ""
        base_url = None

        if provider == "openai":
            api_key = self.settings.openai_api_key
            model = self.settings.openai_model
        elif provider == "gemini":
            api_key = self.settings.gemini_api_key
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
            model = self.settings.gemini_model
        else:
            logger.warning(
                "Unsupported LLM provider '%s'. Falling back to mock summaries.",
                provider,
            )
            return


        if api_key:
            try:
                import openai
                self._client = openai.OpenAI(api_key=api_key, base_url=base_url)
                self._model = model
                logger.info(
                    "Initialized LLM client for provider '%s' using model '%s'",
                    provider,
                    model,
                )
            except Exception as e:
                logger.error("Failed to initialize OpenAI client: %s", str(e))
                self._client = None
        else:
            logger.info("No API key configured for '%s'. Running in fallback mock mode.", provider)

    def _get_repo_name(self, repository: Any) -> str:
        if isinstance(repository, dict):
            return str(repository.get("name") or repository.get("full_name") or "unknown-repo")
        if hasattr(repository, "name"):
            return str(repository.name)
        if hasattr(repository, "full_name"):
            return str(repository.full_name)
        return "unknown-repo"

    def _get_repo_description(self, repository: Any) -> str:
        if isinstance(repository, dict):
            return str(repository.get("description") or "")
        if hasattr(repository, "description"):
            return str(repository.description) or ""
        return ""

    def _get_repo_language(self, repository: Any) -> str:
        if isinstance(repository, dict):
            return str(repository.get("language") or "")
        if hasattr(repository, "language"):
            return str(repository.language) or ""
        return ""

    def _get_repo_stars(self, repository: Any) -> int:
        if isinstance(repository, dict):
            return int(repository.get("stars") or repository.get("stargazers_count") or 0)
        if hasattr(repository, "stars"):
            return int(repository.stars or 0)
        return 0

    def generate(self, repository: Any) -> str:
        """Generate a 2-3 sentence AI summary for a single repository."""
        name = self._get_repo_name(repository)
        description = self._get_repo_description(repository)
        language = self._get_repo_language(repository)
        stars = self._get_repo_stars(repository)

        if not self._client:
            # Fallback to local rule-based mock summary
            desc_part = f": {description}" if description else " (no description available)"
            lang_part = f" written in {language}" if language else ""
            return (
                f"{name} is an open-source repository{lang_part} "
                f"with {stars} stars{desc_part}. "
                "It is optimized for modularity and scalability."
            )

        system_prompt = (
            "You are a helpful Senior AI Engineer that summarizes open-source "
            "repositories in 2-3 concise sentences. "
            "Focus on the core value proposition, primary use case, and target audience. "
            "Do not output markdown, HTML, or formatting. Write only plain text."
        )
        user_prompt = (
            f"Repository Name: {name}\n"
            f"Description: {description}\n"
            f"Language: {language}\n"
            f"Stars: {stars}"
        )

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=self.settings.summary_max_tokens,
                temperature=self.settings.summary_temperature,
            )
            content = response.choices[0].message.content
            summary = content.strip() if content else ""
            return str(summary)
        except Exception as e:
            logger.error("LLM summary generation failed for %s: %s", name, str(e))
            raise SummaryError(f"LLM summary generation failed: {str(e)}") from e

    def generate_batch(self, repositories: list[Any]) -> list[str]:
        """Batch generate summaries with concurrency."""
        if not repositories:
            return []

        # Use ThreadPoolExecutor to run generate() concurrently across threads
        # without scheduling on the asyncio event loop. This prevents deadlock.
        from concurrent.futures import ThreadPoolExecutor

        max_workers = min(len(repositories), 10)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.generate, repo) for repo in repositories]
            results = []
            for fut in futures:
                try:
                    results.append(fut.result())
                except Exception as exc:
                    logger.warning("Batch summary item failed: %s", str(exc))
                    results.append("Summary generation failed due to a transient API error.")
        return results


    def compare(self, repositories: list[Any]) -> ComparisonResult:
        """Generate comparative analysis of multiple repositories."""
        if not repositories:
            return ComparisonResult(repositories=[], dimensions=[])

        repo_names = [self._get_repo_name(r) for r in repositories]

        if not self._client:
            # Fallback mock comparison based on metadata heuristics
            dimensions = []
            for dim_name in ["Features", "Activity", "Documentation", "Community"]:
                scores = {}
                for r in repositories:
                    r_name = self._get_repo_name(r)
                    stars = self._get_repo_stars(r)
                    desc = self._get_repo_description(r)
                    # Simple heuristics
                    if dim_name == "Community":
                        score = min(10.0, stars / 1000.0)
                    elif dim_name == "Documentation":
                        score = 8.5 if len(desc) > 30 else 5.0
                    else:
                        score = 7.5
                    scores[r_name] = round(score, 1)
                dimensions.append(ComparisonDimension(name=dim_name, scores=scores))

            rec = (
                f"We recommend {repo_names[0]} based on its popularity "
                "and active community ecosystem."
                if repo_names
                else None
            )
            return ComparisonResult(
                repositories=repo_names, dimensions=dimensions, recommendation=rec
            )

        system_prompt = (
            "You are an expert software architect comparing open-source repositories. "
            "Compare the given repositories across 4 dimensions: Features, Activity, "
            "Documentation, and Community. "
            "Rate each repository in each dimension with a score from 1.0 to 10.0. "
            "Provide a final comparison recommendation text. "
            "You MUST return ONLY a raw JSON object matching the following schema. "
            "Do not wrap the JSON in ```json blocks or markdown formatting. "
            "Just output the raw JSON text:\n"
            "{\n"
            '  "repositories": ["repo1", "repo2"],\n'
            '  "dimensions": [\n'
            '    {"name": "Features", "scores": {"repo1": 8.5, "repo2": 7.0}},\n'
            '    {"name": "Activity", "scores": {"repo1": 9.0, "repo2": 6.5}}\n'
            "  ],\n"
            '  "recommendation": "recommendation text..."\n'
            "}"
        )
        user_prompt = "\n".join(
            f"Repo: {self._get_repo_name(r)}\n"
            f"Description: {self._get_repo_description(r)}\n"
            f"Stars: {self._get_repo_stars(r)}"
            for r in repositories
        )

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=500,
                temperature=self.settings.summary_temperature,
            )
            raw_content = response.choices[0].message.content.strip()
            # Clean possible markdown wrapping
            if raw_content.startswith("```"):
                lines = raw_content.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                raw_content = "\n".join(lines).strip()

            data = json.loads(raw_content)

            dimensions = []
            for dim_data in data.get("dimensions", []):
                dimensions.append(
                    ComparisonDimension(
                        name=dim_data.get("name", ""),
                        scores=dim_data.get("scores", {}),
                    )
                )

            return ComparisonResult(
                repositories=data.get("repositories", repo_names),
                dimensions=dimensions,
                recommendation=data.get("recommendation"),
            )
        except Exception as e:
            logger.error("Comparative analysis generation failed: %s", str(e))
            raise SummaryError(f"Comparative analysis generation failed: {str(e)}") from e

    def _generate_mock_insight(self, name: str, description: str, language: str, stars: int, forks: int, open_issues: int) -> dict:
        maintenance = min(98, max(50, 75 + (stars // 1000) - (open_issues // 10)))
        documentation = min(98, max(45, 60 + (len(description) // 5)))
        community = min(98, max(40, 50 + (stars // 500)))
        code_quality = min(98, max(55, 70 + (forks // 200)))
        security = min(98, max(60, 80 - (open_issues // 20)))

        return {
            "summary": f"{name} is a robust {language} repository focusing on {description or 'open source development'}. It provides developers with highly optimized structures, modular interfaces, and active community backing.",
            "scores": {
                "maintenance": int(maintenance),
                "documentation": int(documentation),
                "community": int(community),
                "codeQuality": int(code_quality),
                "security": int(security)
            },
            "strengths": [
                f"Highly active community support with {stars} stars.",
                f"Solid codebase architecture utilizing {language}.",
                "Optimized rendering performance and minimal external dependencies."
            ],
            "weaknesses": [
                "Documentation could be expanded with more advanced integration guides." if documentation < 80 else "Rigid structure may require initial setup learning curve.",
                f"Has {open_issues} open issues that need community screening." if open_issues > 30 else "Minor vulnerability patches pending dependency updates."
            ],
            "bestUseCases": [
                f"Production-grade applications built with {language}.",
                "Scalable enterprise micro-service integrations.",
                "Rapid prototyping and developer utility scripts."
            ]
        }

    def generate_insight_report(self, repository: Any, readme_text: str = "") -> dict[str, Any]:
        name = self._get_repo_name(repository)
        description = self._get_repo_description(repository)
        language = self._get_repo_language(repository)
        stars = self._get_repo_stars(repository)
        
        open_issues = 0
        forks = 0
        if isinstance(repository, dict):
            open_issues = int(repository.get("open_issues") or repository.get("open_issues_count") or 0)
            forks = int(repository.get("forks") or repository.get("forks_count") or 0)

        if not self._client:
            return self._generate_mock_insight(name, description, language, stars, forks, open_issues)

        system_prompt = (
            "You are a helpful software architect. Analyze the repository metadata and README text, "
            "then generate a structured JSON analysis report of the repository. "
            "You MUST respond ONLY with a raw JSON object matching the following format (no markdown, no formatting, no wrapping):\n"
            "{\n"
            '  "summary": "2-3 sentences executive summary...",\n'
            '  "scores": {\n'
            '    "maintenance": 85,\n'
            '    "documentation": 90,\n'
            '    "community": 75,\n'
            '    "codeQuality": 88,\n'
            '    "security": 92\n'
            '  },\n'
            '  "strengths": ["strength 1", "strength 2", "strength 3"],\n'
            '  "weaknesses": ["weakness 1", "weakness 2"],\n'
            '  "bestUseCases": ["use case 1", "use case 2", "use case 3"]\n'
            "}"
        )

        readme_snippet = readme_text[:6000] if readme_text else "No README available."
        user_prompt = (
            f"Name: {name}\n"
            f"Description: {description}\n"
            f"Language: {language}\n"
            f"Stars: {stars}\n"
            f"Forks: {forks}\n"
            f"Open Issues: {open_issues}\n"
            f"README snippet:\n{readme_snippet}"
        )

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=600,
                temperature=0.3,
            )
            raw_content = response.choices[0].message.content.strip()
            
            if raw_content.startswith("```"):
                lines = raw_content.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                raw_content = "\n".join(lines).strip()

            data = json.loads(raw_content)
            required_keys = ["summary", "scores", "strengths", "weaknesses", "bestUseCases"]
            if all(k in data for k in required_keys):
                return data
            else:
                logger.warning("LLM response did not contain all required keys. Falling back to mock.")
                return self._generate_mock_insight(name, description, language, stars, forks, open_issues)
        except Exception as e:
            logger.error(f"Failed to generate LLM insight report: {e}")
            return self._generate_mock_insight(name, description, language, stars, forks, open_issues)

