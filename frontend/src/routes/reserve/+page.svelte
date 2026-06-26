<script lang="ts">
	import { api } from '$lib/api/client';
	import type { ReservationResponse } from '$lib/api/generated';

	let name = $state('');
	let purpose = $state('');
	let staffName = $state('');
	let reservedDate = $state('');
	let reservedTime = $state('');
	let reservation = $state<ReservationResponse | null>(null);
	let loading = $state(false);
	let error = $state('');

	async function submit() {
		loading = true;
		error = '';
		try {
			const res = await api.reservations.create({
				name,
				purpose,
				staff_name: staffName,
				reserved_date: reservedDate,
				reserved_time: reservedTime ? reservedTime + ':00' : undefined,
			});
			reservation = res.data;
		} catch {
			error = '予約の登録に失敗しました。もう一度お試しください。';
		} finally {
			loading = false;
		}
	}

	function reset() {
		reservation = null;
		name = '';
		purpose = '';
		staffName = '';
		reservedDate = '';
		reservedTime = '';
		error = '';
	}

	function formatDate(d: string) {
		const [y, m, day] = d.split('-');
		return `${y}年${m}月${day}日`;
	}
</script>

<div class="min-h-screen bg-gray-50 flex items-center justify-center p-6">
	{#if reservation}
		<div class="bg-white rounded-2xl shadow-lg p-12 max-w-md w-full text-center">
			<div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
				<svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
				</svg>
			</div>
			<h2 class="text-2xl font-bold text-gray-800 mb-2">予約完了</h2>
			<p class="text-gray-500 mb-8">ご予約を承りました。</p>

			<div class="bg-gray-50 rounded-xl p-5 text-left space-y-2 mb-8">
				<div class="flex justify-between text-sm">
					<span class="text-gray-500">お名前</span>
					<span class="font-medium">{reservation.name} 様</span>
				</div>
				<div class="flex justify-between text-sm">
					<span class="text-gray-500">ご用件</span>
					<span class="font-medium">{reservation.purpose}</span>
				</div>
				<div class="flex justify-between text-sm">
					<span class="text-gray-500">担当</span>
					<span class="font-medium">{reservation.staff_name}</span>
				</div>
				<div class="flex justify-between text-sm">
					<span class="text-gray-500">日時</span>
					<span class="font-medium">
						{formatDate(reservation.reserved_date)}
						{#if reservation.reserved_time}
							{reservation.reserved_time.slice(0, 5)}
						{/if}
					</span>
				</div>
			</div>

			<button
				onclick={reset}
				class="w-full py-3 bg-gray-100 hover:bg-gray-200 rounded-xl text-gray-700 transition"
			>
				新しく予約する
			</button>
		</div>
	{:else}
		<div class="bg-white rounded-2xl shadow-lg p-10 max-w-md w-full">
			<h1 class="text-2xl font-bold text-gray-800 mb-8 text-center">事前予約</h1>

			<form onsubmit={(e) => { e.preventDefault(); submit(); }} class="space-y-5">
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1">お名前 <span class="text-red-400">*</span></label>
					<input
						bind:value={name}
						type="text"
						required
						placeholder="山田 太郎"
						class="w-full border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-400"
					/>
				</div>
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1">ご用件 <span class="text-red-400">*</span></label>
					<input
						bind:value={purpose}
						type="text"
						required
						placeholder="打ち合わせ"
						class="w-full border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-400"
					/>
				</div>
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1">担当スタッフ名 <span class="text-red-400">*</span></label>
					<input
						bind:value={staffName}
						type="text"
						required
						placeholder="田中"
						class="w-full border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-400"
					/>
				</div>
				<div class="grid grid-cols-2 gap-3">
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">希望日 <span class="text-red-400">*</span></label>
						<input
							bind:value={reservedDate}
							type="date"
							required
							class="w-full border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-400"
						/>
					</div>
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1">希望時刻</label>
						<input
							bind:value={reservedTime}
							type="time"
							class="w-full border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-400"
						/>
					</div>
				</div>

				{#if error}
					<p class="text-red-500 text-sm">{error}</p>
				{/if}

				<button
					type="submit"
					disabled={loading}
					class="w-full py-4 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-lg font-semibold rounded-xl transition"
				>
					{loading ? '登録中...' : '予約する'}
				</button>
			</form>
		</div>
	{/if}
</div>
