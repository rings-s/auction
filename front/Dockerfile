# Stage 1: Build the SvelteKit application
FROM node:20-alpine
WORKDIR /app

# Set environment variables for file watching
ENV CHOKIDAR_USEPOLLING=true

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Install all dependencies (including devDependencies for development)
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the port Vite/SvelteKit dev server will run on
EXPOSE 5173

# Command to run the SvelteKit dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]