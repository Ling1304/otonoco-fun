/**
 * Pagination component for navigating through document pages.
 */
const Pagination = ({ currentPage, totalPages, onPageChange, onNext, onPrev }) => {
  const getPageNumbers = () => {
    const pages = [];
    const showPages = 5; // Number of page buttons to show
    let startPage = Math.max(0, currentPage - Math.floor(showPages / 2));
    let endPage = Math.min(totalPages - 1, startPage + showPages - 1);

    // Adjust start if we're near the end
    if (endPage - startPage < showPages - 1) {
      startPage = Math.max(0, endPage - showPages + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }

    return pages;
  };

  if (totalPages <= 1) return null;

  const pageNumbers = getPageNumbers();

  return (
    <div className="flex items-center justify-center gap-2 mt-8">
      {/* Previous Button */}
      <button
        onClick={onPrev}
        disabled={currentPage === 0}
        className="px-4 py-2 rounded-md border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Previous
      </button>

      {/* Page Numbers */}
      <div className="hidden sm:flex gap-2">
        {currentPage > 2 && (
          <>
            <button
              onClick={() => onPageChange(0)}
              className="px-4 py-2 rounded-md border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              1
            </button>
            {currentPage > 3 && <span className="px-2 py-2">...</span>}
          </>
        )}

        {pageNumbers.map((page) => (
          <button
            key={page}
            onClick={() => onPageChange(page)}
            className={`px-4 py-2 rounded-md border text-sm font-medium ${
              page === currentPage
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
            }`}
          >
            {page + 1}
          </button>
        ))}

        {currentPage < totalPages - 3 && (
          <>
            {currentPage < totalPages - 4 && <span className="px-2 py-2">...</span>}
            <button
              onClick={() => onPageChange(totalPages - 1)}
              className="px-4 py-2 rounded-md border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              {totalPages}
            </button>
          </>
        )}
      </div>

      {/* Mobile: Show current page */}
      <div className="sm:hidden px-4 py-2 text-sm text-gray-700">
        Page {currentPage + 1} of {totalPages}
      </div>

      {/* Next Button */}
      <button
        onClick={onNext}
        disabled={currentPage >= totalPages - 1}
        className="px-4 py-2 rounded-md border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Next
      </button>
    </div>
  );
};

export default Pagination;

