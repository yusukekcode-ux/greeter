<script lang="ts">
	import { page } from '$app/stores';

	const links = [
		{ href: '/', label: 'ホーム', exact: true },
		{ href: '/kiosk', label: 'キオスク', exact: false },
		{ href: '/reserve', label: '事前予約', exact: true },
		{ href: '/admin', label: '管理画面', exact: true },
		{ href: '/admin/reservations', label: '予約管理', exact: true },
		{ href: '/display', label: '表示板', exact: true },
	];

	function isActive(link: { href: string; exact: boolean }) {
		if (link.exact) return $page.url.pathname === link.href;
		return $page.url.pathname.startsWith(link.href);
	}
</script>

<nav class="bg-white border-b border-gray-200 sticky top-0 z-10">
	<div class="max-w-5xl mx-auto px-4 flex items-center h-12 gap-1">
		<a href="/" class="font-black text-gray-900 text-base mr-4 shrink-0 hover:text-blue-600 transition">
			greeter
		</a>
		<div class="flex items-center gap-0.5 overflow-x-auto">
			{#each links as link}
				<a
					href={link.href}
					class="px-3 py-1.5 text-sm rounded-md whitespace-nowrap transition {isActive(link)
						? 'bg-gray-100 text-gray-900 font-medium'
						: 'text-gray-500 hover:text-gray-800 hover:bg-gray-50'}"
				>
					{link.label}
				</a>
			{/each}
		</div>
	</div>
</nav>
