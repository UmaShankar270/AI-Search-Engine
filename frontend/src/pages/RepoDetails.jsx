import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate, useSearchParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { getRepositoryDetails } from '../services/api';

// Subcomponents
import RepositoryHeader from '../components/RepoCard/RepositoryHeader';
import RepositoryStats from '../components/RepoCard/RepositoryStats';
import LanguageBreakdown from '../components/RepoCard/LanguageBreakdown';
import RepositoryOverview from '../components/RepoCard/RepositoryOverview';
import AIAnalysisCard from '../components/RepoCard/AIAnalysisCard';
import ReadmePreview from '../components/RepoCard/ReadmePreview';
import ContributorsList from '../components/RepoCard/ContributorsList';
import RepositoryActivity from '../components/RepoCard/RepositoryActivity';
import ActionButtons from '../components/RepoCard/ActionButtons';
import ErrorState from '../components/Error/ErrorState';

export default function RepoDetails() {
  const { owner, repo } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const platform = searchParams.get('platform') || 'github';
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [details, setDetails] = useState(null);

  useEffect(() => {
    if (!owner || !repo) return;
    
    setLoading(true);
    setError(null);

    let active = true;

    async function fetchDetails() {
      try {
        const fetched = await getRepositoryDetails(owner, repo, platform);
        if (!fetched) {
          throw new Error('Repository details not found');
        }
        if (active) {
          setDetails(fetched);
        }
      } catch (err) {
        if (active) {
          setError('Failed to fetch details. The repository could not be located.');
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    fetchDetails();

    return () => {
      active = false;
    };
  }, [owner, repo, platform]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12 animate-pulse space-y-6 w-full text-left">
        <div className="h-6 bg-brand-gray-250 rounded w-24" />
        <div className="h-44 bg-brand-gray-200 rounded-2xl w-full" />
        <div className="grid grid-cols-4 gap-4">
          <div className="h-20 bg-brand-gray-200 rounded-xl" />
          <div className="h-20 bg-brand-gray-200 rounded-xl" />
          <div className="h-20 bg-brand-gray-200 rounded-xl" />
          <div className="h-20 bg-brand-gray-200 rounded-xl" />
        </div>
        <div className="grid grid-cols-3 gap-6">
          <div className="col-span-2 h-96 bg-brand-gray-200 rounded-2xl" />
          <div className="h-96 bg-brand-gray-200 rounded-2xl" />
        </div>
      </div>
    );
  }

  if (error || !details) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 flex-1 flex flex-col justify-center items-center">
        <ErrorState title="Discovery Error" message={error || "Repository details could not be found."} onRetry={() => navigate(0)} />
      </div>
    );
  }

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

      {/* Header component */}
      <RepositoryHeader details={details} />

      {/* Numerical Stats grid */}
      <RepositoryStats details={details} />

      {/* Main split details panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        {/* Left main: Overview info, Activity, Language composition, Readme */}
        <div className="lg:col-span-2 space-y-6">
          {/* Action buttons list */}
          <div className="border border-brand-gray-200 dark:border-brand-gray-800 bg-white dark:bg-brand-gray-900 rounded-2xl p-5 shadow-sm">
            <h3 className="text-xs font-bold text-brand-gray-400 dark:text-brand-gray-500 uppercase tracking-wider block mb-3 font-mono text-left">
              Quick Actions
            </h3>
            <ActionButtons details={details} />
          </div>

          <RepositoryOverview details={details} />
          <RepositoryActivity activity={details.activity} />
          <LanguageBreakdown languages={details.languages} />
          <ReadmePreview readmeHtml={details.readmeHtml} />
        </div>

        {/* Right side: AI Analysis & Contributors list */}
        <div className="lg:col-span-1 space-y-6 lg:sticky lg:top-20">
          <AIAnalysisCard analysis={details.aiAnalysis} />
          <ContributorsList contributors={details.contributors} />
        </div>
      </div>
    </div>
  );
}
