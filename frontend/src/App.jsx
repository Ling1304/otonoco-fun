/**
 * Main App component.
 * Entry point for the SEC Edgar Document Explorer application.
 */
import { useState } from 'react';
import DocumentList from './components/DocumentList';
import SearchPanel from './components/SearchPanel';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('search'); // Default to search tab

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with Navigation */}
      <header className="bg-white shadow-md border-b-2 border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <div className="flex items-center">
              <h1 className="text-3xl font-bold text-gray-900">
                SEC Edgar Explorer
              </h1>
            </div>
            
            {/* Tab Navigation */}
            <nav className="flex space-x-2">
              <button
                onClick={() => setActiveTab('search')}
                className={`relative px-6 py-3 text-base font-semibold rounded-lg transition-all duration-200 ${
                  activeTab === 'search'
                    ? 'bg-blue-600 text-white shadow-lg transform scale-105'
                    : 'text-gray-700 hover:text-blue-600 hover:bg-blue-50'
                }`}
              >
                <div className="flex items-center">
                  <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  AI Search
                </div>
                {activeTab === 'search' && (
                  <div className="absolute bottom-0 left-0 right-0 h-1 bg-blue-700 rounded-b-lg"></div>
                )}
              </button>
              
              <button
                onClick={() => setActiveTab('documents')}
                className={`relative px-6 py-3 text-base font-semibold rounded-lg transition-all duration-200 ${
                  activeTab === 'documents'
                    ? 'bg-blue-600 text-white shadow-lg transform scale-105'
                    : 'text-gray-700 hover:text-blue-600 hover:bg-blue-50'
                }`}
              >
                <div className="flex items-center">
                  <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Documents
                </div>
                {activeTab === 'documents' && (
                  <div className="absolute bottom-0 left-0 right-0 h-1 bg-blue-700 rounded-b-lg"></div>
                )}
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main>
        {activeTab === 'search' ? <SearchPanel /> : <DocumentList />}
      </main>
    </div>
  );
}

export default App;
