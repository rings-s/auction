/** @type {import('@sveltejs/kit').Handle} */
export async function handle({ event, resolve }) {
    return resolve(event, {
      preload: ({ type }) => {
        // Preload fonts, CSS, and JS files for better performance
        return type === 'font' || type === 'js' || type === 'css';
      }
    });
  }