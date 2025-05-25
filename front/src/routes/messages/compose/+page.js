import { browser } from '$app/environment';

/** @type {import('./$types').PageLoad} */
export async function load({ url, fetch }) {
  const replyId = url.searchParams.get('reply');
  
  return {
    replyId
  };
}
