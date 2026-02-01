/**
 * Filter bar component for document filtering.
 * Provides controls for filing type, company name, and date range.
 */
import { useState, useEffect } from 'react';
import { documentAPI } from '../services/api';

const FilterBar = ({ onFilterChange, currentFilters }) => {
  const [filingTypes, setFilingTypes] = useState([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const [localFilters, setLocalFilters] = useState({
    filing_type: currentFilters.filing_type || '',
    company_name: currentFilters.company_name || '',
    start_date: currentFilters.start_date || '',
    end_date: currentFilters.end_date || '',
  });

  // Fetch filing types on mount
  useEffect(() => {
    const fetchFilingTypes = async () => {
      try {
        const response = await documentAPI.getFilingTypes();
        setFilingTypes(response.data);
      } catch (error) {
        console.error('Error fetching filing types:', error);
      }
    };

    fetchFilingTypes();
  }, []);

  const handleFilterChange = (key, value) => {
    const newFilters = { ...localFilters, [key]: value };
    setLocalFilters(newFilters);
    
    // Remove empty values
    const cleanFilters = Object.entries(newFilters).reduce((acc, [k, v]) => {
      if (v) acc[k] = v;
      return acc;
    }, {});
    
    onFilterChange(cleanFilters);
  };

  const handleClearFilters = () => {
    const emptyFilters = {
      filing_type: '',
      company_name: '',
      start_date: '',
      end_date: '',
    };
    setLocalFilters(emptyFilters);
    onFilterChange({});
  };

  const hasActiveFilters = Object.values(localFilters).some((v) => v !== '');

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
      {/* Mobile toggle button */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex w-full items-center justify-between lg:hidden"
      >
        <span className="font-medium text-gray-700">Filters</span>
        <svg
          className={`h-5 w-5 transform transition-transform ${isExpanded ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Filters */}
      <div className={`${isExpanded ? 'block' : 'hidden'} lg:block mt-4 lg:mt-0`}>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Filing Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Filing Type
            </label>
            <select
              value={localFilters.filing_type}
              onChange={(e) => handleFilterChange('filing_type', e.target.value)}
              className="w-full rounded-md border border-gray-300 py-2 px-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
            >
              <option value="">All Types</option>
              {filingTypes.map((type) => (
                <option key={type.id} value={type.code}>
                  {type.code} - {type.description}
                </option>
              ))}
            </select>
          </div>

          {/* Company Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Company Name
            </label>
            <input
              type="text"
              value={localFilters.company_name}
              onChange={(e) => handleFilterChange('company_name', e.target.value)}
              placeholder="Enter company name"
              className="w-full rounded-md border border-gray-300 py-2 px-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
            />
          </div>

          {/* Start Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Start Date
            </label>
            <input
              type="date"
              value={localFilters.start_date}
              onChange={(e) => handleFilterChange('start_date', e.target.value)}
              className="w-full rounded-md border border-gray-300 py-2 px-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
            />
          </div>

          {/* End Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              End Date
            </label>
            <input
              type="date"
              value={localFilters.end_date}
              onChange={(e) => handleFilterChange('end_date', e.target.value)}
              className="w-full rounded-md border border-gray-300 py-2 px-3 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
            />
          </div>
        </div>

        {/* Clear Filters Button */}
        {hasActiveFilters && (
          <div className="mt-4">
            <button
              onClick={handleClearFilters}
              className="text-sm text-blue-600 hover:text-blue-800 font-medium"
            >
              Clear All Filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default FilterBar;

