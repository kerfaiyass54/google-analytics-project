import { AppType } from './app-type';

export interface GooglePlayAppResponse {
  id: number;
  app: string;
  category: string;
  rating: number;
  reviews: number;
  sizeMb: number;
  installs: string;
  type: AppType;
  price: number;
  contentRating: string;
  genres: string;
  lastUpdated: string;
  currentVersion: string;
  androidVersion: string;
}
