import instance from './axios';

export async function getComments(listingId) {
  const res = await instance.get(`/api/listings/${listingId}/comments/`);
  return res.data; // Array<Comment>
}

export async function addComment(listingId, text) {
  const res = await instance.post(`/api/listings/${listingId}/comments/`, { text });
  return res.data; // Comment
}

export async function deleteComment(commentId) {
  const res = await instance.delete(`/api/comments/${commentId}/`);
  return res.data; // empty (204)
}

export const CommentKeys = {
  list: (listingId) => ['comments', { listingId }],
};
