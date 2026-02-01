/**
 * Document card component.
 * Displays a single document with key metadata.
 */
const DocumentCard = ({ document, onClick }) => {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getFilingTypeBadgeColor = (type) => {
    const colors = {
      '10-K': 'bg-blue-100 text-blue-800',
      '10-Q': 'bg-green-100 text-green-800',
      '8-K': 'bg-yellow-100 text-yellow-800',
      '20-F': 'bg-purple-100 text-purple-800',
      'S-1': 'bg-red-100 text-red-800',
      'DEF 14A': 'bg-indigo-100 text-indigo-800',
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div
      onClick={onClick}
      className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow cursor-pointer"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-lg font-semibold text-gray-900 flex-1">
          {document.company_name}
        </h3>
        <span
          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getFilingTypeBadgeColor(
            document.filing_type
          )}`}
        >
          {document.filing_type}
        </span>
      </div>

      {/* Filing Date */}
      <div className="flex items-center text-sm text-gray-500 mb-3">
        <svg
          className="h-4 w-4 mr-1"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
        {formatDate(document.filing_date)}
      </div>

      {/* Description */}
      <p className="text-sm text-gray-600 line-clamp-3 mb-4">
        {document.description || 'No description available'}
      </p>

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>CIK: {document.company_cik}</span>
      </div>
    </div>
  );
};

export default DocumentCard;

