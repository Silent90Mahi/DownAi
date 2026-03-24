const DB_NAME = 'OfflineAppDB';
const DB_VERSION = 1;

const STORES = {
  products: { keyPath: 'id', autoIncrement: false },
  orders: { keyPath: 'id', autoIncrement: false },
  users: { keyPath: 'id', autoIncrement: false },
  cache: { keyPath: 'key', autoIncrement: false },
};

class IndexedDBWrapper {
  constructor() {
    this.db = null;
    this.isInitializing = false;
    this.initPromise = null;
  }

  async init() {
    if (this.db) {
      return this.db;
    }

    if (this.isInitializing && this.initPromise) {
      return this.initPromise;
    }

    this.isInitializing = true;
    this.initPromise = this._initDB();
    
    try {
      this.db = await this.initPromise;
      return this.db;
    } finally {
      this.isInitializing = false;
    }
  }

  _initDB() {
    return new Promise((resolve, reject) => {
      if (!window.indexedDB) {
        reject(new Error('IndexedDB is not supported in this browser'));
        return;
      }

      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onerror = (event) => {
        reject(new Error(`Failed to open database: ${event.target.error}`));
      };

      request.onsuccess = (event) => {
        resolve(event.target.result);
      };

      request.onupgradeneeded = (event) => {
        const database = event.target.result;

        for (const [storeName, config] of Object.entries(STORES)) {
          if (!database.objectStoreNames.contains(storeName)) {
            database.createObjectStore(storeName, {
              keyPath: config.keyPath,
              autoIncrement: config.autoIncrement,
            });
          }
        }
      };
    });
  }

  async _getStore(storeName, mode = 'readonly') {
    const db = await this.init();
    
    if (!STORES[storeName]) {
      throw new Error(`Unknown store: ${storeName}`);
    }

    const transaction = db.transaction(storeName, mode);
    return transaction.objectStore(storeName);
  }

  async get(storeName, key) {
    const store = await this._getStore(storeName, 'readonly');
    
    return new Promise((resolve, reject) => {
      const request = store.get(key);

      request.onsuccess = () => {
        resolve(request.result || null);
      };

      request.onerror = () => {
        reject(new Error(`Failed to get item: ${request.error}`));
      };
    });
  }

  async set(storeName, key, value) {
    const store = await this._getStore(storeName, 'readwrite');
    
    const data = storeName === 'cache' 
      ? { key, value, timestamp: Date.now() }
      : { ...value, id: key };

    return new Promise((resolve, reject) => {
      const request = store.put(data);

      request.onsuccess = () => {
        resolve(request.result);
      };

      request.onerror = () => {
        reject(new Error(`Failed to set item: ${request.error}`));
      };
    });
  }

  async delete(storeName, key) {
    const store = await this._getStore(storeName, 'readwrite');
    
    return new Promise((resolve, reject) => {
      const request = store.delete(key);

      request.onsuccess = () => {
        resolve(true);
      };

      request.onerror = () => {
        reject(new Error(`Failed to delete item: ${request.error}`));
      };
    });
  }

  async getAll(storeName) {
    const store = await this._getStore(storeName, 'readonly');
    
    return new Promise((resolve, reject) => {
      const request = store.getAll();

      request.onsuccess = () => {
        resolve(request.result || []);
      };

      request.onerror = () => {
        reject(new Error(`Failed to get all items: ${request.error}`));
      };
    });
  }

  async clear(storeName) {
    const store = await this._getStore(storeName, 'readwrite');
    
    return new Promise((resolve, reject) => {
      const request = store.clear();

      request.onsuccess = () => {
        resolve(true);
      };

      request.onerror = () => {
        reject(new Error(`Failed to clear store: ${request.error}`));
      };
    });
  }

  async getMany(storeName, keys) {
    const store = await this._getStore(storeName, 'readonly');
    
    return new Promise((resolve, reject) => {
      const results = [];
      let completed = 0;

      keys.forEach((key, index) => {
        const request = store.get(key);

        request.onsuccess = () => {
          results[index] = request.result || null;
          completed++;

          if (completed === keys.length) {
            resolve(results);
          }
        };

        request.onerror = () => {
          results[index] = null;
          completed++;

          if (completed === keys.length) {
            resolve(results);
          }
        };
      });
    });
  }

  async count(storeName) {
    const store = await this._getStore(storeName, 'readonly');
    
    return new Promise((resolve, reject) => {
      const request = store.count();

      request.onsuccess = () => {
        resolve(request.result);
      };

      request.onerror = () => {
        reject(new Error(`Failed to count items: ${request.error}`));
      };
    });
  }

  async getCached(key, maxAge = 5 * 60 * 1000) {
    const cached = await this.get('cache', key);

    if (!cached) {
      return null;
    }

    const age = Date.now() - cached.timestamp;

    if (age > maxAge) {
      await this.delete('cache', key);
      return null;
    }

    return cached.value;
  }

  async setCache(key, value) {
    return this.set('cache', key, value);
  }

  async close() {
    if (this.db) {
      this.db.close();
      this.db = null;
    }
  }
}

const db = new IndexedDBWrapper();

export { IndexedDBWrapper };

export default db;
