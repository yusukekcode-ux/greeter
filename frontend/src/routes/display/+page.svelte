<script lang="ts">
	import { onMount, onDestroy } from 'svelte';

	const apiUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

	type CalledData = { ticket_number: number; name: string; staff_name: string };

	let current = $state<CalledData | null>(null);
	let flash = $state(false);
	let connected = $state(false);
	let es: EventSource | null = null;

	function connect() {
		es = new EventSource(`${apiUrl}/api/sse`);

		es.onopen = () => { connected = true; };

		es.onmessage = (e) => {
			const msg = JSON.parse(e.data) as { event: string; data: CalledData };
			if (msg.event === 'called') {
				current = msg.data;
				flash = false;
				setTimeout(() => { flash = true; }, 10);
			} else if (msg.event === 'done' || msg.event === 'cancelled') {
				current = null;
			}
		};

		es.onerror = () => {
			connected = false;
			es?.close();
			setTimeout(connect, 3000);
		};
	}

	onMount(connect);
	onDestroy(() => es?.close());
</script>

<div class="min-h-screen bg-gray-900 text-white flex flex-col">
	<!-- ステータスバー -->
	<div class="flex justify-between items-center px-8 py-4 bg-gray-800 text-sm">
		<span class="text-gray-300 text-lg font-semibold tracking-wide">受付番号 呼び出し</span>
		<span class="flex items-center gap-2 text-xs">
			<span class="w-2 h-2 rounded-full {connected ? 'bg-green-400' : 'bg-red-400'}"></span>
			{connected ? '接続中' : '再接続中...'}
		</span>
	</div>

	<!-- メインエリア -->
	<div class="flex-1 flex items-center justify-center">
		{#if current}
			<div class="text-center {flash ? 'animate-pulse-once' : ''}">
				<p class="text-2xl text-gray-400 mb-4 tracking-widest">番号をお呼びしています</p>
				<p class="text-[12rem] font-black leading-none text-white tabular-nums">
					{current.ticket_number}
				</p>
				<p class="text-5xl font-bold mt-6 text-blue-300">{current.name} 様</p>
				<p class="text-3xl text-gray-400 mt-4">
					<span class="text-gray-500">担当：</span>{current.staff_name} までお越しください
				</p>
			</div>
		{:else}
			<div class="text-center text-gray-500">
				<p class="text-6xl font-light mb-4">—</p>
				<p class="text-2xl tracking-wide">しばらくお待ちください</p>
			</div>
		{/if}
	</div>
</div>

<style>
	@keyframes pulse-once {
		0%   { opacity: 0.4; transform: scale(0.97); }
		40%  { opacity: 1;   transform: scale(1.01); }
		100% { opacity: 1;   transform: scale(1); }
	}
	.animate-pulse-once {
		animation: pulse-once 0.5s ease-out forwards;
	}
</style>
