// What a user looks like
export type User = {
  _id: string;
  personal: {
    name: string;
    email: string;
  };
}

// What traffic data looks like
export type TrafficData = {
  _id: string;
  location: string;
  vehicle_count: number;
  status: string;
  timestamp: string;
};

// What the health check returns
export type HealthResponse = {
  status: string;
  database: string;
};