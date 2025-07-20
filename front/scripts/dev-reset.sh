#!/bin/bash
# Frontend Development Reset Script
# Resolves common Vite/SvelteKit dependency and cache issues

echo "🔧 Resetting frontend development environment..."

# Kill any running dev servers
echo "Stopping any running dev servers..."
pkill -f "vite dev" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true

# Clean all caches
echo "Cleaning caches..."
rm -rf node_modules/.vite
rm -rf .svelte-kit/output 
rm -rf .svelte-kit/types
npm cache clean --force --silent

# Reinstall dependencies if package-lock.json is newer than node_modules
if [ package-lock.json -nt node_modules ]; then
    echo "Reinstalling dependencies..."
    rm -rf node_modules
    npm install
fi

# Regenerate SvelteKit configuration
echo "Regenerating SvelteKit configuration..."
npm run prepare

echo "✅ Frontend development environment reset complete!"
echo "You can now run 'npm run dev' to start the development server."