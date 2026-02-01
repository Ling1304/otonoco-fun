/**
 * Document list component.
 * Main component that displays a grid of document cards with filtering and pagination.
 */
import { useState } from 'react';
import DocumentCard from './DocumentCard';
import FilterBar from './FilterBar';
import SearchBar from './SearchBar';
import Pagination from './Pagination';
import LoadingSpinner from './LoadingSpinner';
import { useDocuments } from '../hooks/useDocuments';
import { documentAPI } from '../services/api';

const DocumentList = () => {
  const [syncing, setSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState('');

  const {
    documents,
    total,
    loading,
    error,
    filters,
    updateFilters,
    clearFilters,
    refetch,
    nextPage,
    prevPage,
    goToPage,
    currentPage,
    totalPages,
  } = useDocuments();

  const handleSearch = (searchTerm) => {
    updateFilters({ search: searchTerm || undefined });
  };

  const handleFilterChange = (newFilters) => {
    updateFilters(newFilters);
  };

  const handleDocumentClick = (document) => {
    // Open the SEC document URL in a new tab
    if (document.document_url) {
      window.open(document.document_url, '_blank');
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    setSyncMessage('');
    
    try {
      const response = await documentAPI.syncDocuments({
        max_filings_per_company: 5,
      });
      
      setSyncMessage(
        `Success! Created ${response.data.documents_created} documents, ` +
        `updated ${response.data.documents_updated}, ` +
        `and generated ${response.data.chunks_created} chunks.`
      );
      
      // Refresh the document list
      setTimeout(() => {
        refetch();
      }, 1000);
    } catch (error) {
      setSyncMessage(`Error: ${error.response?.data?.detail || 'Failed to sync documents'}`);
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                SEC Edgar Document Explorer
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                Browse and search SEC regulatory filings
              </p>
            </div>
            <button
              onClick={handleSync}
              disabled={syncing}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {syncing ? (
                <>
                  <svg
                    className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  Syncing...
                </>
              ) : (
                <>
                  <svg
                    className="-ml-1 mr-2 h-4 w-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                    />
                  </svg>
                  Sync Documents
                </>
              )}
            </button>
          </div>
          
          {/* Sync Message */}
          {syncMessage && (
            <div
              className={`mt-4 p-4 rounded-md ${
                syncMessage.startsWith('Error')
                  ? 'bg-red-50 text-red-800'
                  : 'bg-green-50 text-green-800'
              }`}
            >
              {syncMessage}
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Bar */}
        <div className="mb-6">
          <SearchBar onSearch={handleSearch} initialValue={filters.search || ''} />
        </div>

        {/* Filter Bar */}
        <FilterBar onFilterChange={handleFilterChange} currentFilters={filters} />

        {/* Results Summary */}
        <div className="mb-4 text-sm text-gray-600">
          {loading ? (
            'Loading...'
          ) : (
            <>
              Showing {documents.length} of {total} document{total !== 1 ? 's' : ''}
            </>
          )}
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Loading State */}
        {loading && <LoadingSpinner message="Loading documents..." />}

        {/* Empty State */}
        {!loading && documents.length === 0 && (
          <div className="text-center py-12">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No documents found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Try adjusting your filters or sync new documents
            </p>
            <div className="mt-6">
              <button
                onClick={clearFilters}
                className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Clear Filters
              </button>
            </div>
          </div>
        )}

        {/* Document Grid */}
        {!loading && documents.length > 0 && (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {documents.map((document) => (
                <DocumentCard
                  key={document.id}
                  document={document}
                  onClick={() => handleDocumentClick(document)}
                />
              ))}
            </div>

            {/* Pagination */}
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={goToPage}
              onNext={nextPage}
              onPrev={prevPage}
            />
          </>
        )}
      </main>
    </div>
  );
};

export default DocumentList;

