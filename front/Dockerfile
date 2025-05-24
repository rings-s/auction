# Stage 1: Build the SvelteKit application
FROM node:20-alpine
WORKDIR /app

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Install all dependencies (including devDependencies for development)
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the port Vite/SvelteKit dev server will run on
# This should match the internal port in docker-compose.yml (e.g., 5173)
EXPOSE 5173

# Command to run the SvelteKit dev server
# --host 0.0.0.0 makes it accessible from outside the container
# --port 5173 ensures it runs on the port mapped in docker-compose.yml
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
