FROM node:20-alpine
WORKDIR /app

# Set environment variables for file watching
ENV CHOKIDAR_USEPOLLING=true

# Copy package files
COPY package*.json ./

# Install dependencies with retry logic and increased timeout
RUN npm install --prefer-offline --no-audit --timeout=600000 --registry=https://registry.npmjs.org/ || \
    npm install --prefer-offline --no-audit --timeout=600000 --registry=https://registry.npmjs.org/ || \
    npm install --timeout=600000 --registry=https://registry.npmjs.org/

# Copy the rest of the application code
COPY . .

# Expose the port Vite/SvelteKit dev server will run on
EXPOSE 5173

# Command to run the SvelteKit dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]