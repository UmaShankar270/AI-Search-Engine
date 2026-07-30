import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { ArrowLeft, Sparkles, GitCompare } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { mockRepositories } from '../data/mockRepositories';
import { compareRepositories } from '../services/api';

// Components
import EmptyComparison from '../components/CompareCard/EmptyComparison';
import CompareCard from '../components/CompareCard/CompareCard';

export default function Compare() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { compareRepos, clearCompare } = useApp();

  const paramA = searchParams.get('a') || '';
  const paramB = searchParams.get('b') || '';

  const [repoA, setRepoA] = useState(null);
  const [repoB, setRepoB] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);

  // Sync state from URL params OR global comparison context
  useEffect(() => {
    let selectedA = null;
    let selectedB = null;

    if (paramA) {
      selectedA = mockRepositories.find((r) => r.name.toLowerCase() === paramA.toLowerCase()) || null;
    } else if (compareRepos[0]) {
      selectedA = compareRepos[0];
    }

    if (paramB) {
      selectedB = mockRepositories.find((r) => r.name.toLowerCase() === paramB.toLowerCase()) || null;
    } else if (compareRepos[1]) {
      selectedB = compareRepos[1];
    }

    setRepoA(selectedA);
    setRepoB(selectedB);
  }, [paramA, paramB, compareRepos]);

  // Generate summary when A & B are both set
  useEffect(() => {
    if (repoA && repoB) {
      setLoading(true);
      let active = true;

      async function fetchComparison() {
        try {
          const sum = await compareRepositories(repoA, repoB);
          if (active) {
            setSummary(sum);
          }
        } catch (err) {
          console.error(err);
        } finally {
          if (active) {
            setLoading(false);
          }
        }
      }

      fetchComparison();

      return () => {
        active = false;
      };
    } else {
      setSummary(null);
    }
  }, [repoA, repoB]);

  const handleSelectRepo = (slot, repo) => {
    if (slot === 'A') {
      setSearchParams((prev) => {
        prev.set('a', repo.name.toLowerCase());
        return prev;
      });
    } else {
      setSearchParams((prev) => {
        prev.set('b', repo.name.toLowerCase());
        return prev;
      });
    }
  };

  const handleRemoveRepo = (slot) => {
    if (slot === 'A') {
      setSearchParams((prev) => {
        prev.delete('a');
        return prev;
      });
      setRepoA(null);
    } else {
      setSearchParams((prev) => {
        prev.delete('b');
        return prev;
      });
      setRepoB(null);
    }
  };

  const handleSwap = () => {
    if (!repoA || !repoB) return;
    setSearchParams((prev) => {
      prev.set('a', repoB.name.toLowerCase());
      prev.set('b', repoA.name.toLowerCase());
      return prev;
    });
  };

  const handleClear = () => {
    setSearchParams({});
    setRepoA(null);
    setRepoB(null);
    clearCompare();
  };

  return (
    <div className="max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 flex flex-col space-y-6">
      {/* Back button */}
      <div>
        <Link
          to="/"
          className="inline-flex items-center space-x-1.5 text-xs font-semibold text-brand-gray-500 dark:text-brand-gray-400 hover:text-brand-gray-900 dark:hover:text-white transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Discover</span>
        </Link>
      </div>

      {/* Header Info */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-brand-gray-150 dark:border-brand-gray-800 pb-4 gap-4 text-left">
        <div className="space-y-1">
          <h2 className="text-2xl font-extrabold text-brand-gray-955 dark:text-white flex items-center space-x-2">
            <GitCompare className="w-5 h-5 text-accent-blue-500" />
            <span>Repository Comparison</span>
          </h2>
          <p className="text-xs text-brand-gray-400 dark:text-brand-gray-550 font-mono uppercase">
            Side-by-Side Code Health and Ecosystem Assessment
          </p>
        </div>
      </div>

      {loading ? (
        <div className="max-w-4xl mx-auto px-4 py-20 animate-pulse space-y-6 w-full text-left">
          <div className="grid grid-cols-2 gap-6">
            <div className="h-28 bg-brand-gray-200 rounded-2xl" />
            <div className="h-28 bg-brand-gray-200 rounded-2xl" />
          </div>
          <div className="h-64 bg-brand-gray-200 rounded-2xl" />
          <div className="h-44 bg-brand-gray-200 rounded-2xl" />
        </div>
      ) : repoA && repoB ? (
        <CompareCard
          repoA={repoA}
          repoB={repoB}
          summary={summary}
          onSwap={handleSwap}
          onClear={handleClear}
        />
      ) : (
        <EmptyComparison
          repoA={repoA}
          repoB={repoB}
          onSelectRepo={handleSelectRepo}
          onRemoveRepo={handleRemoveRepo}
        />
      )}
    </div>
  );
}
