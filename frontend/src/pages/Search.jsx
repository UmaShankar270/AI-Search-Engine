import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Filter, SlidersHorizontal, ArrowUpRight } from 'lucide-react';
import { mockRepositories } from '../data/mockRepositories';

// Components
import SearchHeader from '../components/SearchBar/SearchHeader';
import SearchFilters from '../components/Filters/SearchFilters';
import SearchResults from '../components/RepoCard/SearchResults';
import EmptyState from '../components/SearchBar/EmptyState';
import LoadingSkeleton from '../components/Loader/LoadingSkeleton';
import Pagination from '../components/Filters/Pagination';

export default function Search() {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryParam = searchParams.get('q') || '';

  // Local Search Input State
  const [query, setQuery] = useState(queryParam);
  const [hasSearched, setHasSearched] = useState(!!queryParam);

  // States
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [repositories, setRepositories] = useState([]);
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);

  // Filters State
  const [filters, setFilters] = useState({
    language: 'All',
    stars: 'All',
    forks: 'All',
    license: 'All',
    updated: 'All',
    sortBy: 'match',
  });

  // Pagination State
  const [currentPage, setCurrentPage] = useState(1);
  const resultsPerPage = 4; // Low limit to demonstrate pagination easily

  // Trigger search execution when search query param changes
  useEffect(() => {
    if (!queryParam) {
      setRepositories([]);
      setHasSearched(false);
      return;
    }

    setQuery(queryParam);
    setHasSearched(true);
    setLoading(true);
    setError(null);
    setCurrentPage(1);

    // Simulate network delay for realistic experience
    const timer = setTimeout(() => {
      try {
        // Query simulation check for error state
        if (queryParam.toLowerCase() === 'error') {
          throw new Error('Simulation API error');
        }

        // Filter mock DB based on query terms
        const searchTerms = queryParam.toLowerCase().split(' ');
        const matched = mockRepositories.map((repo) => {
          let matches = 0;
          const searchSource = `${repo.name} ${repo.owner} ${repo.description} ${repo.language} ${repo.topics.join(' ')}`.toLowerCase();
          
          searchTerms.forEach((term) => {
            if (searchSource.includes(term)) {
              matches += 1;
            }
          });

          // Calculate a simulated match percentage based on matched keywords
          let baseScore = repo.matchScore;
          if (matches === 0) {
            baseScore = Math.max(30, repo.matchScore - 45);
          } else {
            baseScore = Math.min(100, repo.matchScore + matches * 3);
          }

          return { ...repo, matchScore: baseScore };
        });

        // Filter out very poor matches if they have no keywords
        const filtered = matched.filter((repo) => {
          const searchSource = `${repo.name} ${repo.owner} ${repo.description} ${repo.language}`.toLowerCase();
          const hasKeyword = searchTerms.some((t) => searchSource.includes(t));
          return hasKeyword || repo.matchScore > 60;
        });

        setRepositories(filtered);
      } catch (err) {
        setError('Failed to fetch repositories due to an unexpected API error.');
      } finally {
        setLoading(false);
      }
    }, 700);

    return () => clearTimeout(timer);
  }, [queryParam]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setSearchParams({ q: query });
  };

  const handleRetry = () => {
    setSearchParams({ q: queryParam });
  };

  // Perform client-side Filtering & Sorting logic
  const getProcessedRepositories = () => {
    let result = [...repositories];

    // 1. Language Filter
    if (filters.language !== 'All') {
      result = result.filter(
        (repo) => repo.language?.toLowerCase() === filters.language.toLowerCase()
      );
    }

    // 2. Stars Filter
    if (filters.stars !== 'All') {
      const minStars = parseInt(filters.stars, 10);
      result = result.filter((repo) => repo.stars >= minStars);
    }

    // 3. Forks Filter
    if (filters.forks !== 'All') {
      const minForks = parseInt(filters.forks, 10);
      result = result.filter((repo) => repo.forks >= minForks);
    }

    // 4. License Filter
    if (filters.license !== 'All') {
      result = result.filter(
        (repo) => repo.license?.toLowerCase() === filters.license.toLowerCase()
      );
    }

    // 5. Recently Updated Filter (relative to current mock date July 30, 2026)
    if (filters.updated !== 'All') {
      const daysLimit = parseInt(filters.updated, 10);
      const limitDate = new Date('2026-07-30');
      limitDate.setDate(limitDate.getDate() - daysLimit);

      result = result.filter((repo) => {
        if (!repo.lastUpdated) return false;
        const updatedDate = new Date(repo.lastUpdated);
        return updatedDate >= limitDate;
      });
    }

    // 6. Sorting
    if (filters.sortBy === 'match') {
      result.sort((a, b) => b.matchScore - a.matchScore);
    } else if (filters.sortBy === 'stars') {
      result.sort((a, b) => b.stars - a.stars);
    } else if (filters.sortBy === 'forks') {
      result.sort((a, b) => b.forks - a.forks);
    } else if (filters.updated === 'updated' || filters.sortBy === 'updated') {
      result.sort((a, b) => new Date(b.lastUpdated) - new Date(a.lastUpdated));
    } else if (filters.sortBy === 'name') {
      result.sort((a, b) => a.name.localeCompare(b.name));
    }

    return result;
  };

  const processedRepos = getProcessedRepositories();

  // Pagination bounds calculation
  const totalPages = Math.ceil(processedRepos.length / resultsPerPage);
  const paginatedRepos = processedRepos.slice(
    (currentPage - 1) * resultsPerPage,
    currentPage * resultsPerPage
  );

  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
    // Scroll smoothly to top of results grid on page switch
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 flex flex-col space-y-6">
      {/* Top Header Section */}
      <SearchHeader
        query={query}
        setQuery={setQuery}
        onSearch={handleSearch}
        totalResults={processedRepos.length}
        executionTime={0.12}
        hasSearched={hasSearched}
      />

      {/* Main Grid: Left Filters, Right Results */}
      {!hasSearched ? (
        <EmptyState type="empty" />
      ) : error ? (
        <EmptyState type="error" onRetry={handleRetry} />
      ) : loading ? (
        <div className="flex flex-col lg:flex-row gap-8 items-start">
          {/* Static Filters on Desktop */}
          <SearchFilters filters={filters} setFilters={setFilters} isOpen={false} />
          <div className="flex-1 w-full">
            <LoadingSkeleton />
          </div>
        </div>
      ) : (
        <div className="flex flex-col lg:flex-row gap-8 items-start">
          {/* Desktop Search Filters Sidebar */}
          <SearchFilters
            filters={filters}
            setFilters={setFilters}
            isOpen={mobileFiltersOpen}
            onClose={() => setMobileFiltersOpen(false)}
          />

          {/* Right Area: Results list */}
          <div className="flex-1 w-full space-y-6">
            {/* Mobile Filter Button toggle */}
            <div className="flex lg:hidden justify-between items-center bg-white dark:bg-brand-gray-900 border border-brand-gray-200 dark:border-brand-gray-800 rounded-xl p-3 shadow-sm">
              <span className="text-xs font-semibold text-brand-gray-500">
                Found {processedRepos.length} matches
              </span>
              <button
                onClick={() => setMobileFiltersOpen(true)}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 border border-brand-gray-200 dark:border-brand-gray-850 rounded-lg text-xs font-semibold text-brand-gray-700 dark:text-brand-gray-300 bg-brand-gray-50 dark:bg-brand-gray-950 hover:bg-brand-gray-100 cursor-pointer"
              >
                <SlidersHorizontal className="w-3.5 h-3.5" />
                <span>Filters</span>
              </button>
            </div>

            {/* Results Grid / List */}
            {processedRepos.length === 0 ? (
              <EmptyState
                type="no-results"
                message="Try adjusting your stars count, language selection, or searching with another keyword expression."
              />
            ) : (
              <div className="space-y-6">
                <SearchResults repositories={paginatedRepos} />
                
                {/* Pagination Controls */}
                <Pagination
                  currentPage={currentPage}
                  totalPages={totalPages}
                  onPageChange={handlePageChange}
                />
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
