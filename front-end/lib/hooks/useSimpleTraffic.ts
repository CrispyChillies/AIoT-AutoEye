import { useState, useEffect } from 'react';
import { getTrafficData, checkHealth } from '../api/simple';
import { TrafficData, HealthResponse } from '../api/types';

export function useTrafficData(){
  // Basically the useState is for the dynamic variable
  const [data, setData] = useState<TrafficData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  const loadData = async () => {
    try { 
      setLoading(true);
      setError('');
      const result = await getTrafficData();
      setData(result);
    }catch(err){
      setError('Failed to load traffic data');
      console.error(err);
    }finally{
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return {
    data,        // The traffic data
    loading,     // True when loading
    error,       // Error message if something went wrong
    refresh: loadData  // Function to reload data
  };
}

// Custom hook to check if backend is healthy
export function useHealth() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isOnline, setIsOnline] = useState(false);

  const checkBackend = async () => {
    try {
      const result = await checkHealth();
      setHealth(result);
      setIsOnline(true);
    } catch (err) {
      setHealth(null);
      setIsOnline(false);
    }
  };

  useEffect(() => {
    checkBackend();
    // Check every 30 seconds
    const interval = setInterval(checkBackend, 30000);
    return () => clearInterval(interval);
  }, []);

  return {
    health,
    isOnline,
    refresh: checkBackend
  };
}