import axios from 'axios';
import { mockRepositories } from '../data/mockRepositories';
import { getGeneratedMockDetails } from '../data/mockRepositoryDetails';
import { getComparisonSummary } from '../data/mockComparison';
import { mockTrendingRepositories } from '../data/mockTrendingRepositories';

// Create a reusable Axios instance
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  },
});

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
    return response.data;
  } catch (error) {
    logApiError('searchRepositories', error);

    // Fallback logic representing backend matching
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

    return filtered;
  }
}

/**
 * GET /repo/{owner}/{repo}
 */
export async function getRepositoryDetails(owner, repo) {
  try {
    const response = await apiClient.get(`/repo/${owner}/${repo}`);
    return response.data;
  } catch (error) {
    logApiError('getRepositoryDetails', error);
    return getGeneratedMockDetails(owner, repo);
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
    return response.data;
  } catch (error) {
    logApiError('getTrendingRepositories', error);
    
    // Fallback filters logic
    let result = [...mockTrendingRepositories];
    if (filters.language && filters.language !== 'All') {
      result = result.filter(
        (repo) => repo.language?.toLowerCase() === filters.language.toLowerCase()
      );
    }
    return result;
  }
}
