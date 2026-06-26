<script lang="ts">
	import { page } from '$app/stores';
	import { fly } from 'svelte/transition';
	import Nav from '$lib/components/Nav.svelte';
	import favicon from '$lib/assets/favicon.svg';
	import '../app.css';

	let { children } = $props();

	let showHoverNav = $state(false);
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

{#if $page.url.pathname === '/display'}
	<!-- 表示板: 上部ホバーで表示 -->
	<div
		class="fixed top-0 inset-x-0 z-20"
		onmouseenter={() => (showHoverNav = true)}
		onmouseleave={() => (showHoverNav = false)}
	>
		<div class="h-4"></div>
		{#if showHoverNav}
			<div transition:fly={{ y: -48, duration: 150 }} class="shadow-xl">
				<Nav />
			</div>
		{/if}
	</div>
{:else}
	<Nav />
{/if}

{@render children()}
