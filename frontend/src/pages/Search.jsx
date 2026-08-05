import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { SlidersHorizontal } from 'lucide-react';
import { searchRepositories } from '../services/api';

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

  const [query, setQuery] = useState(queryParam);
  const [hasSearched, setHasSearched] = useState(!!queryParam);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [repositories, setRepositories] = useState([]);
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);

  const [filters, setFilters] = useState({
    language: 'All',
    stars: 'All',
    forks: 'All',
    license: 'All',
    updated: 'All',
    sortBy: 'match',
  });

  const [currentPage, setCurrentPage] = useState(1);
  const [totalResults, setTotalResults] = useState(0);
  const resultsPerPage = 4;

  useEffect(() => {
    setCurrentPage(1);
  }, [queryParam]);

  useEffect(() => {
    if (!queryParam) {
      setRepositories([]);
      setHasSearched(false);
      setTotalResults(0);
      return;
    }

    setQuery(queryParam);
    setHasSearched(true);
    setLoading(true);
    setError(null);

    let active = true;

    async function fetchSearch() {
      try {
        if (queryParam.toLowerCase() === 'error') {
          throw new Error('Simulation API error');
        }
        const data = await searchRepositories(queryParam, {
          ...filters,
          page: currentPage,
          per_page: resultsPerPage
        });
        if (active) {
          setRepositories(data.results);
          setTotalResults(data.totalCount);
        }
      } catch (err) {
        if (active) {
          setError('Failed to fetch repositories due to an unexpected API error.');
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    fetchSearch();

    return () => {
      active = false;
    };
  }, [queryParam, currentPage, filters]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setCurrentPage(1);
    setSearchParams({ q: query });
  };

  const handleRetry = () => {
    setCurrentPage(1);
    setSearchParams({ q: queryParam });
  };

  const processedRepos = repositories;
  const paginatedRepos = repositories;
  const totalPages = Math.ceil(totalResults / resultsPerPage);

  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 flex flex-col space-y-6">
      <SearchHeader
        query={query}
        setQuery={setQuery}
        onSearch={handleSearch}
        totalResults={totalResults}
        executionTime={0.12}
        hasSearched={hasSearched}
      />

      {!hasSearched ? (
        <EmptyState type="empty" />
      ) : error ? (
        <EmptyState type="error" onRetry={handleRetry} />
      ) : loading ? (
        <div className="flex flex-col lg:flex-row gap-8 items-start">
          <SearchFilters filters={filters} setFilters={setFilters} isOpen={false} />
          <div className="flex-1 w-full">
            <LoadingSkeleton />
          </div>
        </div>
      ) : (
        <div className="flex flex-col lg:flex-row gap-8 items-start">
          <SearchFilters
            filters={filters}
            setFilters={setFilters}
            isOpen={mobileFiltersOpen}
            onClose={() => setMobileFiltersOpen(false)}
          />

          <div className="flex-1 w-full space-y-6">
            <div className="flex lg:hidden justify-between items-center bg-white dark:bg-brand-gray-900 border border-brand-gray-200 dark:border-brand-gray-800 rounded-xl p-3 shadow-sm">
              <span className="text-xs font-semibold text-brand-gray-500">
                Found {totalResults} matches
              </span>
              <button
                onClick={() => setMobileFiltersOpen(true)}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 border border-brand-gray-200 dark:border-brand-gray-850 rounded-lg text-xs font-semibold text-brand-gray-700 dark:text-brand-gray-300 bg-brand-gray-50 dark:bg-brand-gray-950 hover:bg-brand-gray-100 cursor-pointer"
              >
                <SlidersHorizontal className="w-3.5 h-3.5" />
                <span>Filters</span>
              </button>
            </div>

            {totalResults === 0 ? (
              <EmptyState
                type="no-results"
                message="Try adjusting your stars count, language selection, or searching with another keyword expression."
              />
            ) : (
              <div className="space-y-6">
                <SearchResults repositories={paginatedRepos} />
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
