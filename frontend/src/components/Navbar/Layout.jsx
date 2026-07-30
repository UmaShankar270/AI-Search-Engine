import React from 'react';
import Navbar from './Navbar';
import Footer from '../Footer/Footer';

export default function Layout({ children }) {
  return (
    <div className="min-h-screen flex flex-col bg-brand-gray-50 dark:bg-brand-gray-950 text-brand-gray-900 dark:text-brand-gray-100 transition-colors">
      <Navbar />
      <main className="flex-1 flex flex-col w-full">
        {children}
      </main>
      <Footer />
    </div>
  );
}
