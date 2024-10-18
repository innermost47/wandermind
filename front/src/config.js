export const config = {
  development: {
    apiUrl: "http://localhost:8000",
  },
  production: {
    apiUrl: "https://your-production-url.com",
  },
};

export const environment =
  window.location.hostname === "127.0.0.1" ? "development" : "production";

export const apiUrl = config[environment].apiUrl;

export const categories = {
  wikipedia: "wikipedia",
  events: "events",
  accomodations: "19014,19012,19013,19006",
  culturals: "10027,10023,10034,10032",
  restaurants: "restaurants",
};
