// Mock comparison data and summary generators for Phase 5.
export const mockComparisons = {
  'zustand-vs-redux-toolkit': {
    winner: 'Zustand (based on Developer Experience & footprint)',
    strengthsA: [
      'Almost zero boilerplate code required to set up store closures.',
      'Subscription-based rendering triggers avoid render overhead.',
      'Can be initialized anywhere without wrapping the App in a Provider context.'
    ],
    strengthsB: [
      'Highly opinionated framework structure ideal for large collaborative teams.',
      'Integrated Redux DevTools support out-of-the-box.',
      'Powerful RTK Query addon for API request caching and lifecycle tracking.'
    ],
    useCases: 'Zustand is highly recommended for lightweight React widgets, rapid MVPs, and modular state models. Redux Toolkit is recommended for complex corporate enterprises requiring unified global state tracing and standardized middleware structures.',
    difficulty: 'Low. Zustand uses straightforward JavaScript closures, making refactoring from simple React hooks trivial.',
    activity: 'Zustand shows higher commit frequency and issue close rates, whereas Redux Toolkit has a larger absolute community volume but slower release cycles.'
  }
};

export function getComparisonSummary(repoA, repoB) {
  if (!repoA || !repoB) return null;

  const key1 = `${repoA.name.toLowerCase()}-vs-${repoB.name.toLowerCase()}`;
  const key2 = `${repoB.name.toLowerCase()}-vs-${repoA.name.toLowerCase()}`;

  if (mockComparisons[key1]) {
    return { ...mockComparisons[key1], isReversed: false };
  }
  if (mockComparisons[key2]) {
    const original = mockComparisons[key2];
    return {
      winner: original.winner.includes(repoB.name) ? `${repoB.name} (Reversed)` : `${repoA.name} (Reversed)`,
      strengthsA: original.strengthsB,
      strengthsB: original.strengthsA,
      useCases: original.useCases,
      difficulty: original.difficulty,
      activity: original.activity
    };
  }

  // Dynamic seed generator for unmocked pairs
  const scoreA = repoA.matchScore || (repoA.stars > repoB.stars ? 90 : 80);
  const scoreB = repoB.matchScore || (repoB.stars > repoA.stars ? 90 : 80);
  const winnerName = scoreA > scoreB ? repoA.name : repoB.name;

  return {
    winner: `${winnerName} (based on comparative AI metrics)`,
    strengthsA: [
      `Higher score in specific metric subsets.`,
      `Optimal developer ecosystem indicators.`
    ],
    strengthsB: [
      `Robust feature documentation compliance.`,
      `Strong developer usage footprints.`
    ],
    useCases: `Use ${repoA.name} if you prioritize lightweight configurations. Use ${repoB.name} if you require extensive plugins coverage.`,
    difficulty: 'Medium. Integration path depends on framework compatibility and dependencies.',
    activity: 'Both repositories are actively maintained with weekly commit updates.'
  };
}
