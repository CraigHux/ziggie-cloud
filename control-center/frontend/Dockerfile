# Ziggie Control Center - Frontend Dockerfile
# Development setup using Node.js 20

FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port 3001 for Ziggie Control Center Frontend
EXPOSE 3001

# Set environment variable for Vite
ENV VITE_API_BASE_URL=http://localhost:54112

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3001"]
