<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import type { ReservationResponse } from '$lib/api/generated';

	let reservations = $state<ReservationResponse[]>([]);
	let loading = $state(true);
	let cancelling = $state<number | null>(null);
	let error = $state('');

	async function fetchReservations() {
		loading = true;
		try {
			const res = await api.reservations.list();
			reservations = res.data;
		} catch {
			error = '予約の取得に失敗しました。';
		} finally {
			loading = false;
		}
	}

	async function cancel(id: number) {
		cancelling = id;
		error = '';
		try {
			await api.reservations.cancel(id);
			await fetchReservations();
		} catch {
			error = 'キャンセルに失敗しました。';
		} finally {
			cancelling = null;
		}
	}

	function formatTime(t: string | null | undefined) {
		return t ? t.slice(0, 5) : '';
	}

	const statusLabel: Record<string, string> = {
		pending: '待機中',
		checked_in: 'チェックイン済',
		cancelled: 'キャンセル',
	};

	const statusClass: Record<string, string> = {
		pending: 'bg-blue-50 text-blue-700',
		checked_in: 'bg-green-50 text-green-700',
		cancelled: 'bg-gray-100 text-gray-400',
	};

	onMount(fetchReservations);
</script>

<div class="min-h-screen bg-gray-50">
	<header class="bg-white border-b border-gray-200 px-8 py-4 flex items-center justify-between">
		<div class="flex items-center gap-4">
			<a href="/admin" class="text-gray-400 hover:text-gray-600 transition text-sm">← 管理画面</a>
			<h1 class="text-xl font-bold text-gray-800">予約管理</h1>
		</div>
		<button
			onclick={fetchReservations}
			class="text-sm px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition"
		>
			更新
		</button>
	</header>

	<main class="max-w-3xl mx-auto p-8">
		{#if error}
			<p class="text-red-500 text-sm mb-4">{error}</p>
		{/if}

		{#if loading}
			<p class="text-gray-400 text-center py-16">読み込み中...</p>
		{:else if reservations.length === 0}
			<div class="text-center py-16 text-gray-400">
				<p class="text-5xl mb-4">—</p>
				<p>予約はありません。</p>
			</div>
		{:else}
			<ul class="space-y-3">
				{#each reservations as r (r.id)}
					<li class="bg-white rounded-xl border border-gray-200 p-5 flex items-center gap-4 {r.status === 'cancelled' ? 'opacity-50' : ''}">
						<!-- 日時 -->
						<div class="w-20 text-center shrink-0">
							<p class="text-sm font-semibold text-gray-700">{r.reserved_date.slice(5).replace('-', '/')}</p>
							<p class="text-xs text-gray-400">{formatTime(r.reserved_time) || '時刻未定'}</p>
						</div>

						<!-- 情報 -->
						<div class="flex-1 min-w-0">
							<div class="flex items-center gap-2 mb-1">
								<span class="font-semibold text-gray-800">{r.name} 様</span>
								<span class="text-xs px-2 py-0.5 rounded-full {statusClass[r.status]}">
									{statusLabel[r.status] ?? r.status}
								</span>
							</div>
							<p class="text-sm text-gray-500 truncate">{r.purpose}　／　担当：{r.staff_name}</p>
						</div>

						<!-- アクション -->
						{#if r.status === 'pending'}
							<button
								onclick={() => cancel(r.id)}
								disabled={cancelling !== null}
								class="shrink-0 px-4 py-2 bg-gray-100 hover:bg-red-50 hover:text-red-600 disabled:opacity-40 text-gray-600 text-sm font-medium rounded-lg transition"
							>
								{cancelling === r.id ? '処理中...' : 'キャンセル'}
							</button>
						{:else}
							<div class="shrink-0 w-20"></div>
						{/if}
					</li>
				{/each}
			</ul>
		{/if}
	</main>
</div>
