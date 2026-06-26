<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import type { ReservationResponse, VisitorResponse } from '$lib/api/generated';

	let reservations = $state<ReservationResponse[]>([]);
	let ticket = $state<VisitorResponse | null>(null);
	let loading = $state(true);
	let checkingIn = $state<number | null>(null);
	let error = $state('');

	onMount(async () => {
		try {
			const res = await api.reservations.list('pending');
			reservations = res.data;
		} catch {
			error = '予約の取得に失敗しました。';
		} finally {
			loading = false;
		}
	});

	async function checkin(id: number) {
		checkingIn = id;
		error = '';
		try {
			const res = await api.reservations.checkin(id);
			ticket = res.data;
		} catch {
			error = 'チェックインに失敗しました。もう一度お試しください。';
		} finally {
			checkingIn = null;
		}
	}

	function formatTime(time: string | null | undefined) {
		if (!time) return '';
		return time.slice(0, 5);
	}
</script>

<div class="min-h-screen bg-gray-50 flex items-center justify-center p-6">
	{#if ticket}
		<div class="bg-white rounded-2xl shadow-lg p-12 max-w-md w-full text-center">
			<p class="text-gray-500 text-lg mb-2">受付番号</p>
			<p class="text-8xl font-bold text-blue-600 mb-6">{ticket.ticket_number}</p>
			<p class="text-xl mb-1">{ticket.name} 様</p>
			<p class="text-gray-500 mb-8">担当：{ticket.staff_name}</p>
			<p class="text-gray-400 text-sm mb-8">番号をお呼びするまで、お待ちください。</p>
			<a
				href="/kiosk"
				class="block w-full py-3 bg-gray-100 hover:bg-gray-200 rounded-xl text-gray-700 text-center transition"
			>
				最初に戻る
			</a>
		</div>
	{:else}
		<div class="bg-white rounded-2xl shadow-lg p-10 max-w-lg w-full">
			<div class="flex items-center gap-3 mb-8">
				<a href="/kiosk" class="text-gray-400 hover:text-gray-600 transition">
					← 戻る
				</a>
				<h1 class="text-2xl font-bold text-gray-800">事前予約の方</h1>
			</div>

			{#if error}
				<p class="text-red-500 text-sm mb-4">{error}</p>
			{/if}

			{#if loading}
				<p class="text-gray-400 text-center py-10">読み込み中...</p>
			{:else if reservations.length === 0}
				<div class="text-center py-10">
					<p class="text-gray-400 mb-6">本日の予約はありません。</p>
					<a
						href="/kiosk"
						class="inline-block px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition"
					>
						通常受付へ
					</a>
				</div>
			{:else}
				<p class="text-sm text-gray-500 mb-4">お名前を選択してチェックインしてください。</p>
				<ul class="space-y-3">
					{#each reservations as r (r.id)}
						<li class="border border-gray-200 rounded-xl p-4 flex items-center justify-between">
							<div>
								<p class="font-semibold text-gray-800">{r.name} 様</p>
								<p class="text-sm text-gray-500">
									{r.reserved_date}
									{#if r.reserved_time}{formatTime(r.reserved_time)}{/if}
									　{r.purpose}
								</p>
							</div>
							<button
								onclick={() => checkin(r.id)}
								disabled={checkingIn !== null}
								class="ml-4 px-5 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-xl transition text-sm font-medium"
							>
								{checkingIn === r.id ? '処理中...' : 'チェックイン'}
							</button>
						</li>
					{/each}
				</ul>
			{/if}
		</div>
	{/if}
</div>
