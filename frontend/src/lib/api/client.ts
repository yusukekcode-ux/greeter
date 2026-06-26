import axios from 'axios';
import type { VisitorCreate, VisitorResponse, ReservationResponse, ReservationCreate } from './generated';

const baseURL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

const http = axios.create({ baseURL });

export const api = {
	visitors: {
		list: () => http.get<VisitorResponse[]>('/api/visitors'),
		create: (body: VisitorCreate) => http.post<VisitorResponse>('/api/visitors', body),
		call: (id: number) => http.post<VisitorResponse>(`/api/visitors/${id}/call`),
		done: (id: number) => http.post<VisitorResponse>(`/api/visitors/${id}/done`),
		cancel: (id: number) => http.post<VisitorResponse>(`/api/visitors/${id}/cancel`),
	},
	reservations: {
		list: (status?: string) =>
			http.get<ReservationResponse[]>('/api/reservations', { params: status ? { status } : {} }),
		create: (body: ReservationCreate) => http.post<ReservationResponse>('/api/reservations', body),
		checkin: (id: number) => http.post<VisitorResponse>(`/api/reservations/${id}/checkin`),
		cancel: (id: number) => http.post<ReservationResponse>(`/api/reservations/${id}/cancel`),
	},
};
