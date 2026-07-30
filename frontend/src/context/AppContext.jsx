import React, { createContext, useContext, useState } from 'react';

const AppContext = createContext();

export function AppProvider({ children }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [compareRepos, setCompareRepos] = useState([]); // Array of max 2 repo objects

  const addRepoToCompare = (repo) => {
    setCompareRepos((prev) => {
      // If already added, do nothing
      if (prev.some((r) => r.id === repo.id)) return prev;
      // If 2 already added, replace the last one or do nothing
      if (prev.length >= 2) {
        return [prev[0], repo];
      }
      return [...prev, repo];
    });
  };

  const removeRepoFromCompare = (repoId) => {
    setCompareRepos((prev) => prev.filter((r) => r.id !== repoId));
  };

  const clearCompare = () => {
    setCompareRepos([]);
  };

  return (
    <AppContext.Provider
      value={{
        searchQuery,
        setSearchQuery,
        searchResults,
        setSearchResults,
        compareRepos,
        addRepoToCompare,
        removeRepoFromCompare,
        clearCompare,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}
