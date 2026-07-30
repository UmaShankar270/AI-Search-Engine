import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, SlidersHorizontal } from 'lucide-react';
import { trendingStatsSummary } from '../data/mockTrendingRepositories';
import { getTrendingRepositories } from '../services/api';

// Subcomponents
import TrendingHeader from '../components/Trending/TrendingHeader';
import TrendingFilters from '../components/Trending/TrendingFilters';
import TrendingGrid from '../components/Trending/TrendingGrid';
import TrendingStats from '../components/Trending/TrendingStats';
import TrendingPagination from '../components/Trending/TrendingPagination';
import TrendingSkeleton from '../components/Trending/TrendingSkeleton';
import EmptyTrending from '../components/Trending/EmptyTrending';

export default function Trending() {
  const [loading, setLoading] = useState(true);
  const [repositories, setRepositories] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);

  const [filters, setFilters] = useState({
    timeRange: 'today',
    language: 'All',
    sortBy: 'trendingScore',
  });

  const resultsPerPage = 4;

  useEffect(() => {
    setLoading(true);
    setCurrentPage(1);

    let active = true;

    async function fetchTrending() {
      try {
        const data = await getTrendingRepositories(filters);
        if (active) {
          setRepositories(data);
        }
      } catch (err) {
        console.error(err);
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    fetchTrending();

    return () => {
      active = false;
    };
  }, [filters]);

  const getFilteredRepositories = () => {
    let result = [...repositories];

    // Filter by search keyword
    if (searchQuery.trim()) {
      const term = searchQuery.toLowerCase();
      result = result.filter(
        (repo) =>
          repo.name.toLowerCase().includes(term) ||
          repo.owner.toLowerCase().includes(term) ||
          repo.description.toLowerCase().includes(term)
      );
    }

    // Sort repositories
    if (filters.sortBy === 'trendingScore') {
      result.sort((a, b) => b.aiPopularityScore - a.aiPopularityScore);
    } else if (filters.sortBy === 'stars') {
      result.sort((a, b) => b.totalStars - a.totalStars);
    } else if (filters.sortBy === 'forks') {
      result.sort((a, b) => b.forks - a.forks);
    } else if (filters.sortBy === 'updated') {
      result.sort((a, b) => new Date(b.updatedDate) - new Date(a.updatedDate));
    }

    return result;
  };

  const filteredRepos = getFilteredRepositories();

  // Paginated elements
  const totalPages = Math.ceil(filteredRepos.length / resultsPerPage);
  const paginatedRepos = filteredRepos.slice(
    (currentPage - 1) * resultsPerPage,
    currentPage * resultsPerPage
  );

  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 flex flex-col space-y-6">
      {/* Back button */}
      <div>
        <Link
          to="/"
          className="inline-flex items-center space-x-1.5 text-xs font-semibold text-brand-gray-500 dark:text-brand-gray-405 hover:text-brand-gray-900 dark:hover:text-white transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Discover</span>
        </Link>
      </div>

      {/* Header coordinates */}
      <TrendingHeader totalCount={filteredRepos.length} timeRange={filters.timeRange} />

      {/* Numerical Stats overview panels */}
      <TrendingStats stats={trendingStatsSummary} />

      {/* Splits sections */}
      <div className="flex flex-col lg:flex-row gap-8 items-start">
        {/* Filters Sidebar */}
        <TrendingFilters
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          filters={filters}
          setFilters={setFilters}
          isOpen={mobileFiltersOpen}
          onClose={() => setMobileFiltersOpen(false)}
        />

        {/* Repos list and paginations */}
        <div className="flex-1 w-full space-y-6">
          {/* Mobile Filter Toggle bar */}
          <div className="flex lg:hidden justify-between items-center bg-white dark:bg-brand-gray-900 border border-brand-gray-200 dark:border-brand-gray-800 rounded-xl p-3 shadow-sm">
            <span className="text-xs font-semibold text-brand-gray-500">
              Found {filteredRepos.length} trending items
            </span>
            <button
              onClick={() => setMobileFiltersOpen(true)}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 border border-brand-gray-200 dark:border-brand-gray-850 rounded-lg text-xs font-semibold text-brand-gray-750 dark:text-brand-gray-300 bg-brand-gray-50 dark:bg-brand-gray-950 hover:bg-brand-gray-100 cursor-pointer"
            >
              <SlidersHorizontal className="w-3.5 h-3.5" />
              <span>Filters</span>
            </button>
          </div>

          {loading ? (
            <TrendingSkeleton />
          ) : filteredRepos.length === 0 ? (
            <EmptyTrending />
          ) : (
            <div className="space-y-6">
              <TrendingGrid repositories={paginatedRepos} />
              <TrendingPagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={handlePageChange}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
