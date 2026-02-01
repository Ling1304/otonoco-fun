# SEC Edgar Document Explorer - Frontend

React frontend application for browsing and searching SEC regulatory filings. Built with Vite, Tailwind CSS, and modern React patterns.

## Features

- **Document Browsing**: View SEC filings in a responsive grid layout
- **Advanced Filtering**: Filter by filing type, company name, and date range
- **Search**: Real-time search across company names and descriptions
- **Document Details**: View full document information in a modal
- **Pagination**: Navigate through large document sets
- **Sync Documents**: Fetch latest filings from SEC Edgar API
- **Responsive Design**: Works seamlessly on mobile, tablet, and desktop

## Tech Stack

- **React 18**: Modern React with hooks
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API requests
- **Custom Hooks**: Reusable state management logic

## Prerequisites

- Node.js 18 or higher
- npm or yarn

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create a `.env` file (or use the existing `.env.example`):

```env
VITE_API_BASE_URL=http://localhost:8000
```

The frontend will connect to the backend API at this URL.

### 3. Run Development Server

```bash
npm run dev
```

The application will be available at **http://localhost:5173**

### 4. Build for Production

```bash
npm run build
```

Built files will be in the `dist/` directory.

### 5. Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # React components
│   │   ├── DocumentList.jsx      # Main list component
│   │   ├── DocumentCard.jsx      # Document card
│   │   ├── DocumentDetail.jsx    # Detail modal
│   │   ├── FilterBar.jsx         # Filter controls
│   │   ├── SearchBar.jsx         # Search input
│   │   ├── Pagination.jsx        # Pagination controls
│   │   └── LoadingSpinner.jsx    # Loading state
│   ├── hooks/
│   │   └── useDocuments.js       # Document fetching hook
│   ├── services/
│   │   └── api.js                # API client
│   ├── App.jsx          # Main app component
│   ├── index.css        # Tailwind directives
│   └── main.jsx         # Entry point
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── README.md
```

## Components

### DocumentList
Main component that orchestrates the entire application. Manages state for filtering, pagination, and document selection.

### DocumentCard
Displays a single document with:
- Company name
- Filing type badge (color-coded)
- Filing date
- Description preview
- Chunking status

### DocumentDetail
Modal component showing:
- Full document metadata
- Content preview
- Link to official SEC document
- Chunking information

### FilterBar
Provides filtering controls:
- Filing type dropdown
- Company name input
- Date range pickers
- Clear filters button
- Responsive: Collapsible on mobile

### SearchBar
Debounced search input (300ms delay) for real-time search across documents.

### Pagination
Navigation controls with:
- Previous/Next buttons
- Page number buttons
- Smart ellipsis for large page counts
- Mobile-friendly display

## Custom Hooks

### useDocuments
Encapsulates document fetching logic:
- Fetches documents from API
- Manages loading and error states
- Handles filtering and pagination
- Provides methods for navigation

**Usage:**
```jsx
const {
  documents,
  total,
  loading,
  error,
  updateFilters,
  nextPage,
  prevPage,
} = useDocuments();
```

## API Integration

The frontend communicates with the backend through the `api.js` service:

```javascript
import { documentAPI } from './services/api';

// List documents
const response = await documentAPI.listDocuments({
  skip: 0,
  limit: 20,
  filing_type: '10-K',
  search: 'Apple'
});

// Get document details
const doc = await documentAPI.getDocument(documentId);

// Sync new documents
await documentAPI.syncDocuments({
  max_filings_per_company: 5
});
```

## Styling with Tailwind

The application uses Tailwind CSS for styling:

### Responsive Breakpoints
- **Mobile**: default (< 640px)
- **Tablet**: `sm:` (640px+)
- **Desktop**: `lg:` (1024px+)

### Color Scheme
- **Primary**: Blue (600/700 shades)
- **Success**: Green
- **Warning**: Yellow
- **Error**: Red
- **Neutral**: Gray scale

### Filing Type Badge Colors
- **10-K**: Blue
- **10-Q**: Green
- **8-K**: Yellow
- **20-F**: Purple
- **S-1**: Red
- **DEF 14A**: Indigo

## User Workflows

### Browse Documents
1. Open application
2. View grid of documents
3. Use filters to narrow results
4. Click document card to view details

### Search Documents
1. Enter search term in search bar
2. Results update automatically (debounced)
3. Search across company names and descriptions

### Filter Documents
1. Open filter bar (auto-expanded on desktop)
2. Select filing type from dropdown
3. Enter company name
4. Set date range
5. Click "Clear All Filters" to reset

### Sync New Documents
1. Click "Sync Documents" button in header
2. Wait for sync to complete
3. View success message with statistics
4. Document list automatically refreshes

### View Document Details
1. Click on any document card
2. Modal opens with full details
3. View content preview
4. Click "View on SEC.gov" to see official filing
5. Close modal with X button or backdrop click

## Development

### Running Linter
```bash
npm run lint
```

### Format Code
```bash
npm run format
```

### Type Checking (if TypeScript is added)
```bash
npm run type-check
```

## Responsive Design Features

### Mobile (< 640px)
- Single column grid
- Collapsible filter bar
- Simplified pagination (current page only)
- Full-screen modals
- Touch-friendly buttons

### Tablet (640px - 1024px)
- 2-column grid
- Expanded filter bar
- Standard pagination

### Desktop (1024px+)
- 3-column grid
- Always-visible filters
- Full pagination with page numbers
- Hover effects

## Performance Optimizations

- **Debounced Search**: 300ms delay to reduce API calls
- **Lazy Loading**: Components loaded on demand
- **Optimized Re-renders**: useCallback and useMemo where needed
- **Responsive Images**: No images currently, but prepared for future use

## Troubleshooting

### "Cannot connect to backend"
- Ensure backend is running on http://localhost:8000
- Check `.env` file has correct `VITE_API_BASE_URL`
- Verify CORS is configured in backend

### "Documents not loading"
- Check browser console for errors
- Verify backend database has documents
- Run sync operation to fetch documents from SEC

### Styling issues
- Ensure Tailwind is properly configured
- Check `index.css` has Tailwind directives
- Run `npm run dev` to rebuild styles

## Future Enhancements

- [ ] AI-powered semantic search (RAG implementation)
- [ ] Bookmarking documents (local storage)
- [ ] Export documents list to CSV
- [ ] Advanced filtering (multi-select, saved filters)
- [ ] Document comparison view
- [ ] Dark mode toggle
- [ ] Accessibility improvements (ARIA labels)

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

MIT License
