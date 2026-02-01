/**
 * Custom hook for fetching and managing documents.
 * Handles loading states, errors, and data fetching.
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import { documentAPI } from '../services/api';

export const useDocuments = (initialFilters = {}) => {
  const [documents, setDocuments] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    skip: 0,
    limit: 20,
    ...initialFilters,
  });

  // Use ref to track if we should fetch
  const prevFiltersRef = useRef();

  useEffect(() => {
    const fetchDocuments = async () => {
      // Skip if filters haven't changed
      const filtersStr = JSON.stringify(filters);
      if (prevFiltersRef.current === filtersStr) {
        return;
      }
      prevFiltersRef.current = filtersStr;

      setLoading(true);
      setError(null);

      try {
        const response = await documentAPI.listDocuments(filters);
        setDocuments(response.data.items);
        setTotal(response.data.total);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to fetch documents');
        console.error('Error fetching documents:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDocuments();
  }, [filters]);

  const updateFilters = useCallback((newFilters) => {
    setFilters((prev) => ({
      ...prev,
      ...newFilters,
      skip: 0, // Reset to first page when filters change
    }));
  }, []);

  const clearFilters = useCallback(() => {
    setFilters({
      skip: 0,
      limit: 20,
    });
  }, []);

  const refetch = useCallback(() => {
    // Force refetch by updating filters reference
    setFilters((prev) => ({ ...prev }));
  }, []);

  const nextPage = useCallback(() => {
    setFilters((prev) => ({
      ...prev,
      skip: prev.skip + prev.limit,
    }));
  }, []);

  const prevPage = useCallback(() => {
    setFilters((prev) => ({
      ...prev,
      skip: Math.max(0, prev.skip - prev.limit),
    }));
  }, []);

  const goToPage = useCallback((page) => {
    setFilters((prev) => ({
      ...prev,
      skip: page * prev.limit,
    }));
  }, []);

  const currentPage = Math.floor(filters.skip / filters.limit);
  const totalPages = Math.ceil(total / filters.limit);

  return {
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
  };
};

