import React from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';

import Layout from './components/Navbar/Layout';

// Pages
import Home from './pages/Home';
import Search from './pages/Search';
import RepoDetails from './pages/RepoDetails';
import Compare from './pages/Compare';
import Trending from './pages/Trending';
import NotFound from './pages/NotFound';

const PageWrapper = ({ children }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
      className="flex-1 flex flex-col w-full"
    >
      {children}
    </motion.div>
  );
};

export default function App() {
  const location = useLocation();

  return (
    <Layout>
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route
            path="/"
            element={
              <PageWrapper>
                <Home />
              </PageWrapper>
            }
          />
          <Route
            path="/search"
            element={
              <PageWrapper>
                <Search />
              </PageWrapper>
            }
          />
          <Route
            path="/repo/:owner/:repo"
            element={
              <PageWrapper>
                <RepoDetails />
              </PageWrapper>
            }
          />
          <Route
            path="/compare"
            element={
              <PageWrapper>
                <Compare />
              </PageWrapper>
            }
          />
          <Route
            path="/trending"
            element={
              <PageWrapper>
                <Trending />
              </PageWrapper>
            }
          />
          <Route
            path="*"
            element={
              <PageWrapper>
                <NotFound />
              </PageWrapper>
            }
          />
        </Routes>
      </AnimatePresence>
    </Layout>
  );
}
