import instance from './axios';

export async function getTopListings(limit = 20) {
  const res = await instance.get('/api/listings/', { params: { limit } });
  return res.data; // Array<Listing>
}

export async function getListing(id) {
  const res = await instance.get(`/api/listings/${id}/`);
  return res.data; // Listing
}

export async function ingestByUrl(url) {
  const res = await instance.post('/api/listings/ingest-url/', { url });
  return res.data; // Listing (created or refreshed)
}

export const ListingKeys = {
  list: (limit) => ['listings', { limit }],
  detail: (id) => ['listing', { id }],
};
