<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api/client';
	import type { VisitorResponse } from '$lib/api/generated';

	let visitors = $state<VisitorResponse[]>([]);
	let loading = $state(true);
	let acting = $state<number | null>(null);
	let error = $state('');

	async function fetchVisitors() {
		try {
			const res = await api.visitors.list();
			visitors = res.data;
		} catch {
			error = '来訪者の取得に失敗しました。';
		} finally {
			loading = false;
		}
	}

	async function call(id: number) {
		acting = id;
		try {
			await api.visitors.call(id);
			await fetchVisitors();
		} catch {
			error = '操作に失敗しました。';
		} finally {
			acting = null;
		}
	}

	async function done(id: number) {
		acting = id;
		try {
			await api.visitors.done(id);
			await fetchVisitors();
		} catch {
			error = '操作に失敗しました。';
		} finally {
			acting = null;
		}
	}

	async function cancel(id: number) {
		acting = id;
		try {
			await api.visitors.cancel(id);
			await fetchVisitors();
		} catch {
			error = '操作に失敗しました。';
		} finally {
			acting = null;
		}
	}

	onMount(fetchVisitors);
</script>

<div class="min-h-screen bg-gray-50">
	<header class="bg-white border-b border-gray-200 px-8 py-4 flex items-center justify-between">
		<h1 class="text-xl font-bold text-gray-800">管理画面</h1>
		<div class="flex items-center gap-4">
			<a href="/admin/reservations" class="text-sm text-blue-500 hover:underline">予約管理</a>
			<button
				onclick={fetchVisitors}
				class="text-sm px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition"
			>
				更新
			</button>
		</div>
	</header>

	<main class="max-w-3xl mx-auto p-8">
		{#if error}
			<p class="text-red-500 text-sm mb-4">{error}</p>
		{/if}

		{#if loading}
			<p class="text-gray-400 text-center py-16">読み込み中...</p>
		{:else if visitors.length === 0}
			<div class="text-center py-16 text-gray-400">
				<p class="text-5xl mb-4">—</p>
				<p>現在、待機中の来訪者はいません。</p>
			</div>
		{:else}
			<ul class="space-y-3">
				{#each visitors as v (v.id)}
					<li class="bg-white rounded-xl border {v.status === 'called' ? 'border-blue-300 shadow-md' : 'border-gray-200'} p-5 flex items-center gap-4">
						<!-- 番号 -->
						<span class="text-4xl font-black w-16 text-center shrink-0 {v.status === 'called' ? 'text-blue-600' : 'text-gray-300'}">
							{v.ticket_number}
						</span>

						<!-- 情報 -->
						<div class="flex-1 min-w-0">
							<div class="flex items-center gap-2 mb-1">
								<span class="font-semibold text-gray-800">{v.name} 様</span>
								{#if v.status === 'called'}
									<span class="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full">呼出中</span>
								{:else}
									<span class="text-xs px-2 py-0.5 bg-gray-100 text-gray-500 rounded-full">待機中</span>
								{/if}
							</div>
							<p class="text-sm text-gray-500 truncate">{v.purpose}　／　担当：{v.staff_name}</p>
						</div>

						<!-- アクション -->
						<div class="flex gap-2 shrink-0">
							{#if v.status === 'waiting'}
								<button
									onclick={() => call(v.id)}
									disabled={acting !== null}
									class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white text-sm font-medium rounded-lg transition"
								>
									呼出
								</button>
							{:else}
								<button
									onclick={() => done(v.id)}
									disabled={acting !== null}
									class="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-40 text-white text-sm font-medium rounded-lg transition"
								>
									完了
								</button>
							{/if}
							<button
								onclick={() => cancel(v.id)}
								disabled={acting !== null}
								class="px-4 py-2 bg-gray-100 hover:bg-gray-200 disabled:opacity-40 text-gray-600 text-sm font-medium rounded-lg transition"
							>
								取消
							</button>
						</div>
					</li>
				{/each}
			</ul>
		{/if}
	</main>
</div>
