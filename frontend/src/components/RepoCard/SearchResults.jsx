import React from 'react';
import RepoCard from './RepoCard';

export default function SearchResults({ repositories = [] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full pt-2">
      {repositories.map((repo) => (
        <RepoCard key={repo.id} repo={repo} />
      ))}
    </div>
  );
}
