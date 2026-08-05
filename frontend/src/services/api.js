import axios from 'axios';
import { mockRepositories } from '../data/mockRepositories';
import { getGeneratedMockDetails } from '../data/mockRepositoryDetails';
import { getComparisonSummary } from '../data/mockComparison';
import { mockTrendingRepositories } from '../data/mockTrendingRepositories';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  },
});

const toNumber = (value, fallback = 0) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
};

const normalizeRepository = (repo, fallbackOwner = 'unknown', fallbackRepo = 'repository') => {
  const owner = repo.owner || repo.full_name?.split('/')[0] || fallbackOwner;
  const name = repo.name || repo.full_name?.split('/')[1] || fallbackRepo;
  const description = repo.description || 'No description available.';
  const stars = toNumber(repo.stars ?? repo.stargazers_count, 0);
  const forks = toNumber(repo.forks ?? repo.forks_count, 0);
  const openIssues = toNumber(repo.openIssues ?? repo.open_issues ?? repo.open_issues_count, 0);
  const language = repo.language || 'Unknown';
  const avatar = repo.avatar || `https://github.com/${owner}.png`;
  const lastUpdated = repo.lastUpdated || repo.updated_at || repo.pushed_at || null;
  const topics = Array.isArray(repo.topics) ? repo.topics : [];
  const id = repo.id || `${owner}/${name}`;

  return {
    id,
    owner,
    name,
    fullName: repo.full_name || `${owner}/${name}`,
    description,
    stars,
    forks,
    openIssues,
    license: repo.license || null,
    language,
    avatar,
    lastUpdated,
    topics,
    url: repo.url || repo.html_url || `https://github.com/${owner}/${name}`,
    matchScore: repo.matchScore ?? 0,
    aiScore: repo.aiScore ?? repo.matchScore ?? 0,
    rank: repo.rank || null,
    matchReasonBullets: repo.matchReasonBullets || [],
    size: repo.size || null,
    defaultBranch: repo.defaultBranch || 'main',
    latestRelease: repo.latestRelease || null,
    visibility: repo.visibility || 'Public',
    createdDate: repo.createdDate || repo.created_at || null,
    about: repo.about || description,
    homepageUrl: repo.homepageUrl || repo.homepage || null,
    readmeHtml: repo.readmeHtml || '',
    aiAnalysis: repo.aiAnalysis || null,
    contributors: repo.contributors || [],
    activity: repo.activity || null,
    watchers: repo.watchers ?? repo.watchers_count ?? Math.round(stars * 0.08),
    open_issues: repo.open_issues ?? openIssues,
    languages: repo.languages || [],
  };
};

const normalizeSearchResponse = (payload) => {
  const results = Array.isArray(payload?.results) ? payload.results : Array.isArray(payload) ? payload : [];
  return results.map((repo) => normalizeRepository(repo));
};

const normalizeTrendingResponse = (payload) => {
  const results = Array.isArray(payload) ? payload : Array.isArray(payload?.results) ? payload.results : [];
  return results.map((repo) => {
    const normalized = normalizeRepository(repo);
    return {
      ...normalized,
      aiPopularityScore: repo.aiPopularityScore ?? repo.ai_score ?? Math.max(70, normalized.stars > 1000 ? 90 : 80),
      totalStars: normalized.stars,
      forks: normalized.forks,
      starsToday: repo.starsToday ?? Math.max(1, Math.round(normalized.stars * 0.01)),
      updatedDate: normalized.lastUpdated,
      owner: normalized.owner,
      name: normalized.name,
    };
  });
};

/**
 * Helper to log errors for debugging without crashing the UI.
 */
const logApiError = (methodName, error) => {
  console.warn(
    `[API Service] Error in ${methodName}. Backend might be offline. Falling back to local mock data. Details:`,
    error.message || error
  );
};

/**
 * GET /search?q=
 */
export async function searchRepositories(query, filters = {}) {
  try {
    const response = await apiClient.get('/search', {
      params: { q: query, ...filters },
    });
    const payload = response.data;
    const normalized = normalizeSearchResponse(payload);
    return {
      results: normalized,
      totalCount: payload?.total_count ?? normalized.length
    };
  } catch (error) {
    logApiError('searchRepositories', error);

    const searchTerms = query.toLowerCase().split(' ');
    const matched = mockRepositories.map((repo) => {
      let matches = 0;
      const searchSource = `${repo.name} ${repo.owner} ${repo.description} ${repo.language} ${repo.topics.join(' ')}`.toLowerCase();

      searchTerms.forEach((term) => {
        if (searchSource.includes(term)) {
          matches += 1;
        }
      });

      let baseScore = repo.matchScore;
      if (matches === 0) {
        baseScore = Math.max(30, repo.matchScore - 45);
      } else {
        baseScore = Math.min(100, repo.matchScore + matches * 3);
      }

      return { ...repo, matchScore: baseScore };
    });

    const filtered = matched.filter((repo) => {
      const searchSource = `${repo.name} ${repo.owner} ${repo.description} ${repo.language}`.toLowerCase();
      const hasKeyword = searchTerms.some((t) => searchSource.includes(t));
      return hasKeyword || repo.matchScore > 60;
    });

    const sortedFiltered = filtered.sort((a, b) => b.matchScore - a.matchScore).map((repo, idx) => ({
      ...repo,
      rank: idx + 1
    }));

    return {
      results: sortedFiltered,
      totalCount: sortedFiltered.length
    };
  }
}

/**
 * GET /repo/{owner}/{repo}
 */
export async function getRepositoryDetails(owner, repo, platform = 'github') {
  try {
    const response = await apiClient.get(`/repo/${owner}/${repo}`, {
      params: { platform }
    });
    const payload = response.data;
    return normalizeRepository(payload, owner, repo);
  } catch (error) {
    logApiError('getRepositoryDetails', error);
    const generated = getGeneratedMockDetails(owner, repo);
    return normalizeRepository(generated, owner, repo);
  }
}

/**
 * POST /compare
 */
export async function compareRepositories(repoA, repoB) {
  try {
    const response = await apiClient.post('/compare', {
      repo_a: repoA.name,
      repo_b: repoB.name,
      owner_a: repoA.owner,
      owner_b: repoB.owner,
    });
    return response.data;
  } catch (error) {
    logApiError('compareRepositories', error);
    return getComparisonSummary(repoA, repoB);
  }
}

/**
 * GET /trending
 */
export async function getTrendingRepositories(filters = {}) {
  try {
    const response = await apiClient.get('/trending', { params: filters });
    return normalizeTrendingResponse(response.data);
  } catch (error) {
    logApiError('getTrendingRepositories', error);

    let result = [...mockTrendingRepositories];
    if (filters.language && filters.language !== 'All') {
      result = result.filter(
        (repo) => repo.language?.toLowerCase() === filters.language.toLowerCase()
      );
    }
    return result.map((repo) => normalizeRepository(repo));
  }
}
