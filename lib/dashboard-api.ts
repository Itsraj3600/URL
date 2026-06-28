export interface BotStats {
  status: 'online' | 'offline' | 'busy';
  users: number;
  movies: number;
  tvShows: number;
  anime: number;
  channels: number;
  todaySearches: number;
  downloads: number;
  cacheHitRate: number;
}

export interface WorkerStatus {
  id: string;
  status: 'busy' | 'idle' | 'paused';
  cpu: number;
  ram: number;
  currentJob?: string;
  queue: number;
}

export interface SystemHealth {
  mongodb: 'healthy' | 'degraded' | 'offline';
  telegram: 'healthy' | 'degraded' | 'offline';
  workers: number;
  uptime: number;
  cpuUsage: number;
  ramUsage: number;
}

export interface IndexJob {
  id: string;
  type: 'movies' | 'tvshows' | 'anime';
  progress: number;
  eta: number;
  speed: number;
  duplicates: number;
  errors: number;
}

export interface User {
  id: string;
  username: string;
  searches: number;
  downloads: number;
  premium: boolean;
  lastSeen: Date;
  joinDate: Date;
}

export interface SearchAnalytic {
  timestamp: Date;
  searches: number;
}

export interface TopMovie {
  title: string;
  searches: number;
  downloads: number;
}

export interface SystemAlert {
  id: string;
  type: 'worker' | 'database' | 'floodwait' | 'queue' | 'index';
  message: string;
  severity: 'info' | 'warning' | 'critical';
  timestamp: Date;
}

// Generate mock bot stats
export function generateBotStats(): BotStats {
  return {
    status: Math.random() > 0.95 ? 'offline' : Math.random() > 0.8 ? 'busy' : 'online',
    users: Math.floor(Math.random() * 50000) + 10000,
    movies: Math.floor(Math.random() * 100000) + 50000,
    tvShows: Math.floor(Math.random() * 50000) + 20000,
    anime: Math.floor(Math.random() * 30000) + 10000,
    channels: Math.floor(Math.random() * 100) + 20,
    todaySearches: Math.floor(Math.random() * 5000) + 1000,
    downloads: Math.floor(Math.random() * 10000) + 2000,
    cacheHitRate: Math.random() * 100,
  };
}

// Generate mock worker data
export function generateWorkers(count: number = 3): WorkerStatus[] {
  return Array.from({ length: count }, (_, i) => ({
    id: `worker-${i + 1}`,
    status: Math.random() > 0.7 ? 'idle' : Math.random() > 0.5 ? 'busy' : 'paused',
    cpu: Math.random() * 100,
    ram: Math.floor(Math.random() * 512) + 100,
    currentJob: Math.random() > 0.5 ? 'Movies HD' : 'TV Shows 4K',
    queue: Math.floor(Math.random() * 200) + 50,
  }));
}

// Generate mock system health
export function generateSystemHealth(): SystemHealth {
  return {
    mongodb: Math.random() > 0.95 ? 'offline' : Math.random() > 0.98 ? 'degraded' : 'healthy',
    telegram: Math.random() > 0.95 ? 'offline' : Math.random() > 0.98 ? 'degraded' : 'healthy',
    workers: Math.floor(Math.random() * 5) + 2,
    uptime: Math.floor(Math.random() * 86400) + 3600,
    cpuUsage: Math.random() * 100,
    ramUsage: Math.random() * 100,
  };
}

// Generate mock index jobs
export function generateIndexJobs(): IndexJob[] {
  return [
    {
      id: 'job-1',
      type: 'movies',
      progress: Math.random() * 100,
      eta: Math.floor(Math.random() * 3600),
      speed: Math.random() * 1000,
      duplicates: Math.floor(Math.random() * 500),
      errors: Math.floor(Math.random() * 50),
    },
    {
      id: 'job-2',
      type: 'tvshows',
      progress: Math.random() * 100,
      eta: Math.floor(Math.random() * 3600),
      speed: Math.random() * 1000,
      duplicates: Math.floor(Math.random() * 300),
      errors: Math.floor(Math.random() * 30),
    },
    {
      id: 'job-3',
      type: 'anime',
      progress: Math.random() * 100,
      eta: Math.floor(Math.random() * 3600),
      speed: Math.random() * 1000,
      duplicates: Math.floor(Math.random() * 200),
      errors: Math.floor(Math.random() * 20),
    },
  ];
}

// Generate mock users
export function generateUsers(count: number = 10): User[] {
  return Array.from({ length: count }, (_, i) => ({
    id: `user-${i + 1}`,
    username: `user${Math.floor(Math.random() * 10000)}`,
    searches: Math.floor(Math.random() * 1000),
    downloads: Math.floor(Math.random() * 500),
    premium: Math.random() > 0.7,
    lastSeen: new Date(Date.now() - Math.random() * 86400000),
    joinDate: new Date(Date.now() - Math.random() * 86400000 * 30),
  }));
}

// Generate mock search analytics
export function generateSearchAnalytics(hours: number = 24): SearchAnalytic[] {
  const data = [];
  for (let i = 0; i < hours; i++) {
    const time = new Date();
    time.setHours(time.getHours() - i);
    data.push({
      timestamp: time,
      searches: Math.floor(Math.random() * 500) + 100,
    });
  }
  return data.reverse();
}

// Generate mock top movies
export function generateTopMovies(count: number = 10): TopMovie[] {
  const titles = [
    'Inception', 'The Dark Knight', 'Interstellar', 'Pulp Fiction', 'Fight Club',
    'The Matrix', 'Forrest Gump', 'Titanic', 'Avatar', 'The Avengers',
  ];
  return titles.slice(0, count).map(title => ({
    title,
    searches: Math.floor(Math.random() * 10000) + 1000,
    downloads: Math.floor(Math.random() * 5000) + 500,
  }));
}

// Generate mock system alerts
export function generateAlerts(count: number = 5): SystemAlert[] {
  const types: SystemAlert['type'][] = ['worker', 'database', 'floodwait', 'queue', 'index'];
  const messages = {
    worker: 'Worker 1 Restarted',
    database: 'MongoDB Connection Restored',
    floodwait: 'Telegram FloodWait Detected',
    queue: 'Processing Queue Full',
    index: 'Indexing Job Completed',
  };

  return Array.from({ length: count }, (_, i) => {
    const type = types[Math.floor(Math.random() * types.length)];
    return {
      id: `alert-${i + 1}`,
      type,
      message: messages[type],
      severity: Math.random() > 0.7 ? 'critical' : Math.random() > 0.5 ? 'warning' : 'info',
      timestamp: new Date(Date.now() - Math.random() * 3600000),
    };
  });
}

// API call functions that use mock data
export async function fetchBotStats(): Promise<BotStats> {
  await new Promise(r => setTimeout(r, 100));
  return generateBotStats();
}

export async function fetchWorkers(): Promise<WorkerStatus[]> {
  await new Promise(r => setTimeout(r, 100));
  return generateWorkers();
}

export async function fetchSystemHealth(): Promise<SystemHealth> {
  await new Promise(r => setTimeout(r, 100));
  return generateSystemHealth();
}

export async function fetchIndexJobs(): Promise<IndexJob[]> {
  await new Promise(r => setTimeout(r, 100));
  return generateIndexJobs();
}

export async function fetchUsers(): Promise<User[]> {
  await new Promise(r => setTimeout(r, 100));
  return generateUsers();
}

export async function fetchSearchAnalytics(): Promise<SearchAnalytic[]> {
  await new Promise(r => setTimeout(r, 100));
  return generateSearchAnalytics();
}

export async function fetchTopMovies(): Promise<TopMovie[]> {
  await new Promise(r => setTimeout(r, 100));
  return generateTopMovies();
}

export async function fetchAlerts(): Promise<SystemAlert[]> {
  await new Promise(r => setTimeout(r, 100));
  return generateAlerts();
}
