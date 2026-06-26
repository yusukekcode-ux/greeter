<script lang="ts">
	import { api } from '$lib/api/client';
	import type { VisitorResponse } from '$lib/api/generated';

	let name = $state('');
	let purpose = $state('');
	let staffName = $state('');
	let ticket = $state<VisitorResponse | null>(null);
	let loading = $state(false);
	let error = $state('');

	async function register() {
		if (!name || !purpose || !staffName) return;
		loading = true;
		error = '';
		try {
			const res = await api.visitors.create({ name, purpose, staff_name: staffName });
			ticket = res.data;
		} catch {
			error = '受付に失敗しました。もう一度お試しください。';
		} finally {
			loading = false;
		}
	}

	function reset() {
		ticket = null;
		name = '';
		purpose = '';
		staffName = '';
		error = '';
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
			<button
				onclick={reset}
				class="w-full py-3 bg-gray-100 hover:bg-gray-200 rounded-xl text-gray-700 transition"
			>
				最初に戻る
			</button>
		</div>
	{:else}
		<div class="bg-white rounded-2xl shadow-lg p-10 max-w-md w-full">
			<h1 class="text-2xl font-bold text-gray-800 mb-8 text-center">受付</h1>

			<form onsubmit={(e) => { e.preventDefault(); register(); }} class="space-y-5">
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1">お名前</label>
					<input
						bind:value={name}
						type="text"
						required
						placeholder="山田 太郎"
						class="w-full border border-gray-300 rounded-xl px-4 py-3 text-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
					/>
				</div>
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1">ご用件</label>
					<input
						bind:value={purpose}
						type="text"
						required
						placeholder="打ち合わせ"
						class="w-full border border-gray-300 rounded-xl px-4 py-3 text-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
					/>
				</div>
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1">担当スタッフ名</label>
					<input
						bind:value={staffName}
						type="text"
						required
						placeholder="田中"
						class="w-full border border-gray-300 rounded-xl px-4 py-3 text-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
					/>
				</div>

				{#if error}
					<p class="text-red-500 text-sm">{error}</p>
				{/if}

				<button
					type="submit"
					disabled={loading}
					class="w-full py-4 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-lg font-semibold rounded-xl transition"
				>
					{loading ? '受付中...' : '受付する'}
				</button>
			</form>

			<div class="mt-6 text-center">
				<a href="/kiosk/reservations" class="text-blue-500 hover:underline text-sm">
					事前予約の方はこちら
				</a>
			</div>
		</div>
	{/if}
</div>
