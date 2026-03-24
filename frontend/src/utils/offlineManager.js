const QUEUE_KEY = 'offline_action_queue';

class OfflineManager {
  constructor() {
    this._online = navigator.onLine;
    this._setupListeners();
  }

  _setupListeners() {
    window.addEventListener('online', () => {
      this._online = true;
      window.dispatchEvent(new CustomEvent('app:online'));
    });

    window.addEventListener('offline', () => {
      this._online = false;
      window.dispatchEvent(new CustomEvent('app:offline'));
    });
  }

  isOnline() {
    return this._online;
  }

  getQueue() {
    try {
      const queue = localStorage.getItem(QUEUE_KEY);
      return queue ? JSON.parse(queue) : [];
    } catch (e) {
      return [];
    }
  }

  _saveQueue(queue) {
    try {
      localStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
    } catch (e) {
      console.error('Failed to save offline queue:', e);
    }
  }

  addToQueue(action) {
    const queue = this.getQueue();
    const queueItem = {
      id: Date.now() + Math.random().toString(36).substr(2, 9),
      action,
      timestamp: new Date().toISOString(),
      attempts: 0,
    };
    queue.push(queueItem);
    this._saveQueue(queue);
    window.dispatchEvent(new CustomEvent('queue:updated', { detail: { queue } }));
    return queueItem.id;
  }

  removeFromQueue(itemId) {
    const queue = this.getQueue();
    const filtered = queue.filter(item => item.id !== itemId);
    this._saveQueue(filtered);
    window.dispatchEvent(new CustomEvent('queue:updated', { detail: { queue: filtered } }));
  }

  async processQueue() {
    if (!this.isOnline()) {
      return { success: false, reason: 'offline' };
    }

    const queue = this.getQueue();
    if (queue.length === 0) {
      return { success: true, processed: 0 };
    }

    window.dispatchEvent(new CustomEvent('sync:start'));

    const results = {
      processed: 0,
      failed: 0,
      errors: [],
    };

    for (const item of queue) {
      try {
        item.attempts += 1;
        await this._executeAction(item.action);
        this.removeFromQueue(item.id);
        results.processed += 1;
      } catch (error) {
        results.failed += 1;
        results.errors.push({
          id: item.id,
          error: error.message,
        });

        if (item.attempts >= 3) {
          this.removeFromQueue(item.id);
        }
      }
    }

    this._saveQueue(queue.filter(item => item.attempts < 3));
    window.dispatchEvent(new CustomEvent('sync:complete', { detail: results }));

    return results;
  }

  async _executeAction(action) {
    const { method, url, body, headers = {} } = action;

    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...headers,
      },
    };

    if (body && method !== 'GET') {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response;
  }

  clearQueue() {
    localStorage.removeItem(QUEUE_KEY);
    window.dispatchEvent(new CustomEvent('queue:updated', { detail: { queue: [] } }));
  }

  getQueueCount() {
    return this.getQueue().length;
  }

  updateQueueItem(itemId, updates) {
    const queue = this.getQueue();
    const index = queue.findIndex(item => item.id === itemId);
    if (index !== -1) {
      queue[index] = { ...queue[index], ...updates };
      this._saveQueue(queue);
    }
  }
}

const offlineManager = new OfflineManager();

export { OfflineManager };

export default offlineManager;
