import React from 'react';
import TrendingCard from './TrendingCard';

export default function TrendingGrid({ repositories = [] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full pt-2">
      {repositories.map((repo) => (
        <TrendingCard key={repo.id} repo={repo} />
      ))}
    </div>
  );
}
