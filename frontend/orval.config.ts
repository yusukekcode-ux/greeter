import { defineConfig } from 'orval';

export default defineConfig({
	greeter: {
		input: {
			target: '../backend/openapi.json'
		},
		output: {
			target: './src/lib/api/generated.ts',
			client: 'axios',
			baseUrl: process.env.VITE_API_URL ?? 'http://localhost:8000'
		}
	}
});
