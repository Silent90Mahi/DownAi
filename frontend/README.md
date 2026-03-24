# SHG Frontend

React frontend for the Ooumph SHG Smart Market Linkage Platform - designed for rural Self-Help Groups with voice-first interactions and offline support.

## Features

- **Voice-First Interface**: Voice input/output for accessibility
- **Offline Support**: Works without internet (PWA)
- **Multi-Language**: Hindi, Telugu, Tamil, English
- **Low-Bandwidth Mode**: Optimized for slow connections
- **Real-Time Updates**: WebSocket integration
- **Mobile-Responsive**: Works on all devices

## Tech Stack

- **React 19** - UI framework
- **Vite 8** - Build tool
- **Tailwind CSS 4** - Styling
- **React Router 7** - Navigation
- **Axios** - HTTP client
- **Recharts** - Data visualization
- **Lucide React** - Icons
- **React Media Recorder** - Voice recording

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running (see backend README)

### Installation

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   ```
   
   Set the backend API URL:
   ```bash
   VITE_API_URL=http://localhost:8000
   ```

3. **Start Development Server**
   ```bash
   npm run dev
   ```

4. **Open Browser**
   ```
   http://localhost:5173
   ```

## Components

### Pages

| Component | Route | Description |
|-----------|-------|-------------|
| `Login` | `/login` | Phone-based authentication |
| `Dashboard` | `/` | Main dashboard with quick actions |
| `Marketplace` | `/marketplace` | Browse and buy products |
| `SellProduct` | `/sell` | List products for sale |
| `MyProducts` | `/my-products` | Manage your listings |
| `OrdersList` | `/orders` | View all orders |
| `OrderDetail` | `/orders/:id` | Order details and tracking |
| `MarketAnalyzer` | `/market` | Price trends and analytics |
| `SupplierMarket` | `/suppliers` | Raw materials sourcing |
| `BuyerMatches` | `/matches` | AI buyer recommendations |
| `Profile` | `/profile` | User profile settings |
| `TrustWallet` | `/trust` | Trust coins and verification |
| `BulkRequests` | `/bulk` | Bulk order management |
| `CommunityHub` | `/community` | Community posts and events |
| `Reports` | `/reports` | Sales and analytics reports |
| `AdminDashboard` | `/admin` | Admin controls (restricted) |

### Core Components

| Component | Description |
|-----------|-------------|
| `ChatAssistant` | Vaani AI chat interface |
| `VoiceButton` | Voice input trigger |
| `VoiceInputOverlay` | Voice recording modal |
| `VoiceSummary` | Voice transcription display |
| `AudioFeedback` | Audio playback component |
| `NotificationsPanel` | Real-time notifications |
| `OfflineIndicator` | Connection status |
| `TrustWallet` | Trust coins display |
| `LanguageToggle` | Language switcher |
| `IconNav` | Navigation icons |

### Context Providers

| Provider | Description |
|----------|-------------|
| `AuthContext` | Authentication state |
| `RealTimeProvider` | WebSocket connection |

### Hooks

| Hook | Description |
|------|-------------|
| `useWebSocket` | WebSocket connection management |
| `useAuth` | Authentication hooks |

### Services

| Service | Description |
|---------|-------------|
| `api.js` | Axios HTTP client |
| `recommendationAPI.js` | Recommendation endpoints |
| `offlineManager.js` | Offline data sync |
| `db.js` | IndexedDB operations |

## Development

### Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── Dashboard.jsx
│   │   ├── Login.jsx
│   │   ├── ChatAssistant.jsx
│   │   └── ...
│   ├── contexts/         # React contexts
│   │   └── AuthContext.jsx
│   ├── hooks/            # Custom hooks
│   │   └── useWebSocket.js
│   ├── services/         # API services
│   │   ├── api.js
│   │   └── recommendationAPI.js
│   ├── utils/            # Utilities
│   │   ├── db.js
│   │   └── offlineManager.js
│   ├── assets/           # Static assets
│   ├── App.jsx           # Main app component
│   ├── App.css           # App styles
│   ├── main.jsx          # Entry point
│   └── index.css         # Global styles
├── public/               # Public assets
├── index.html            # HTML template
├── package.json          # Dependencies
├── vite.config.js        # Vite configuration
├── nginx.conf            # Nginx config (production)
└── Dockerfile            # Docker configuration
```

### Available Scripts

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_URL` | Yes | `http://localhost:8000` | Backend API URL |

### Styling

The app uses Tailwind CSS 4 with a custom color scheme:

- **Primary (Saffron)**: `#FF9933`
- **Secondary (Green)**: `#138808`
- **Accent**: `#000080` (Navy)

Example:
```jsx
<div className="bg-gradient-to-br from-[#FF9933]/10 to-[#138808]/10">
  <button className="bg-[#FF9933] hover:bg-[#FF9933]/90 text-white">
    Click me
  </button>
</div>
```

## Building

### Development Build

```bash
npm run build
```

Output in `dist/` directory.

### Docker Build

```bash
docker build -t ooumph-frontend .
docker run -p 3000:80 ooumph-frontend
```

### Production Optimization

The production build includes:
- Code splitting
- Tree shaking
- CSS minification
- Asset hashing
- Gzip compression (via Nginx)

## Offline Support

The app supports offline functionality using IndexedDB:

```javascript
import { offlineManager } from './utils/offlineManager';

// Queue action for later sync
offlineManager.queueAction({
  type: 'CREATE_ORDER',
  data: orderData
});

// Sync when online
window.addEventListener('online', () => {
  offlineManager.syncPendingActions();
});
```

## WebSocket Integration

Real-time updates via WebSocket:

```javascript
import { useWebSocket } from './hooks/useWebSocket';

function MyComponent() {
  const { subscribe, isConnected } = useWebSocket();
  
  useEffect(() => {
    subscribe('notifications', (data) => {
      console.log('New notification:', data);
    });
  }, []);
}
```

## Accessibility

- Voice-first design for low-literacy users
- High contrast colors
- Large touch targets
- Screen reader support
- Keyboard navigation

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari, Chrome Android)

## Troubleshooting

### API Connection Issues

```bash
# Check backend is running
curl http://localhost:8000/health

# Verify CORS settings
# In backend .env:
FRONTEND_URL=http://localhost:5173
```

### Build Errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Voice Not Working

- Ensure HTTPS in production (required for microphone)
- Check browser permissions
- Verify OpenAI API key is set in backend

## Deployment

### Static Hosting

```bash
npm run build
# Upload dist/ folder to hosting service
```

### Docker

```bash
docker-compose up -d frontend
```

### Nginx Configuration

See [nginx.conf](./nginx.conf) for production configuration.
