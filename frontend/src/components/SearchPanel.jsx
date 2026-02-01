import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import api from '../services/api';

const SearchPanel = () => {
  const [query, setQuery] = useState('');
  const [companyFilter, setCompanyFilter] = useState('');
  const [filingTypeFilter, setFilingTypeFilter] = useState('');
  const [limit, setLimit] = useState(5);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await api.post('/search', {
        query: query.trim(),
        company_filter: companyFilter || null,
        filing_type_filter: filingTypeFilter || null,
        limit: limit
      });
      
      setResult(response.data);
    } catch (err) {
      console.error('Search error:', err);
      setError(err.response?.data?.detail || 'An error occurred while searching. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
    } catch {
      return dateString;
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          AI-Powered SEC Document Search
        </h1>
        <p className="text-gray-600">
          Ask questions about SEC filings and get intelligent answers with source citations
        </p>
      </div>

      {/* Search Form */}
      <form onSubmit={handleSearch} className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="space-y-4">
          {/* Query Input */}
          <div>
            <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
              Your Question
            </label>
            <input
              type="text"
              id="query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., What was Apple's revenue in the latest quarter?"
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={loading}
            />
          </div>

          {/* Filters Row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Company Filter */}
            <div>
              <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-2">
                Company (optional)
              </label>
              <input
                type="text"
                id="company"
                value={companyFilter}
                onChange={(e) => setCompanyFilter(e.target.value)}
                placeholder="e.g., Apple Inc."
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={loading}
              />
            </div>

            {/* Filing Type Filter */}
            <div>
              <label htmlFor="filingType" className="block text-sm font-medium text-gray-700 mb-2">
                Filing Type (optional)
              </label>
              <select
                id="filingType"
                value={filingTypeFilter}
                onChange={(e) => setFilingTypeFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={loading}
              >
                <option value="">All Types</option>
                <option value="10-K">10-K (Annual Report)</option>
                <option value="10-Q">10-Q (Quarterly Report)</option>
                <option value="8-K">8-K (Current Report)</option>
                <option value="DEF 14A">DEF 14A (Proxy Statement)</option>
              </select>
            </div>

            {/* Result Limit */}
            <div>
              <label htmlFor="limit" className="block text-sm font-medium text-gray-700 mb-2">
                Max Results
              </label>
              <select
                id="limit"
                value={limit}
                onChange={(e) => setLimit(Number(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={loading}
              >
                <option value="3">3</option>
                <option value="5">5</option>
                <option value="10">10</option>
                <option value="15">15</option>
                <option value="20">20</option>
              </select>
            </div>
          </div>

          {/* Search Button */}
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-md font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Searching...
              </span>
            ) : (
              'Search'
            )}
          </button>
        </div>
      </form>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex">
            <svg className="h-5 w-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <p className="text-sm text-red-800">{error}</p>
          </div>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* AI Answer */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg shadow-md p-6">
            <div className="flex items-start mb-3">
              <svg className="h-6 w-6 text-blue-600 mr-2 flex-shrink-0 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              <div className="flex-1">
                <h2 className="text-xl font-semibold text-gray-900 mb-3">
                  AI Answer
                </h2>
                <div className="text-gray-700 leading-relaxed prose prose-blue max-w-none markdown-content">
                  <ReactMarkdown>{result.answer}</ReactMarkdown>
                </div>
                {result.total_chunks > 0 && (
                  <p className="text-sm text-gray-500 mt-3">
                    Based on {result.total_chunks} relevant source{result.total_chunks !== 1 ? 's' : ''}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Source Chunks */}
          {result.chunks && result.chunks.length > 0 && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Source Documents
              </h2>
              <div className="space-y-4">
                {result.chunks.map((chunk, index) => (
                  <div key={index} className="bg-white rounded-lg shadow-md p-5 border border-gray-200">
                    {/* Source Header */}
                    <div className="flex items-start justify-between mb-3 pb-3 border-b border-gray-200">
                      <div className="flex-1">
                        <div className="flex items-center mb-1">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mr-2">
                            Source {index + 1}
                          </span>
                          <span className="text-sm font-semibold text-gray-900">
                            {chunk.metadata.company_name}
                          </span>
                        </div>
                        <div className="flex items-center text-sm text-gray-600 space-x-3">
                          <span className="font-medium">{chunk.metadata.filing_type}</span>
                          <span>•</span>
                          <span>{formatDate(chunk.metadata.filing_date)}</span>
                          <span>•</span>
                          <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">
                            Relevance: {(chunk.score * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                      {chunk.metadata.document_url && (
                        <a
                          href={chunk.metadata.document_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="ml-3 inline-flex items-center px-3 py-1.5 border border-gray-300 rounded-md text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                        >
                          <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                          View Original
                        </a>
                      )}
                    </div>

                    {/* Chunk Content */}
                    <div className="text-sm text-gray-700 leading-relaxed">
                      <p className="whitespace-pre-wrap">
                        {chunk.content.length > 500 
                          ? `${chunk.content.substring(0, 500)}...` 
                          : chunk.content
                        }
                      </p>
                    </div>

                    {/* Chunk Metadata */}
                    <div className="mt-3 pt-3 border-t border-gray-100 text-xs text-gray-500">
                      Chunk {chunk.metadata.chunk_index + 1} of {chunk.metadata.total_chunks} • 
                      {' '}{chunk.metadata.chunk_char_count} characters
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* No Results */}
          {result.total_chunks === 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
              <svg className="mx-auto h-12 w-12 text-yellow-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-gray-700 font-medium mb-1">No relevant documents found</p>
              <p className="text-sm text-gray-600">
                Try adjusting your search query or filters
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SearchPanel;

