<div class="min-h-screen bg-gray-50 flex flex-col">
	<!-- ヘッダー -->
	<header class="bg-white border-b border-gray-200 px-8 py-6">
		<div class="max-w-3xl mx-auto">
			<h1 class="text-3xl font-black text-gray-900 tracking-tight">greeter</h1>
			<p class="text-sm text-gray-400 mt-1">受付・来訪者管理システム</p>
		</div>
	</header>

	<!-- メインコンテンツ -->
	<main class="flex-1 max-w-3xl w-full mx-auto px-8 py-10 space-y-8">
		<!-- 来訪者向け -->
		<section>
			<h2 class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">来訪者向け</h2>
			<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
				<a href="/kiosk" class="group bg-white border border-gray-200 rounded-xl p-5 hover:border-blue-400 hover:shadow-md transition">
					<div class="flex items-start gap-4">
						<span class="text-2xl">🪧</span>
						<div>
							<p class="font-semibold text-gray-800 group-hover:text-blue-600 transition">受付キオスク</p>
							<p class="text-sm text-gray-400 mt-0.5">来訪者のセルフ受付・チケット発行</p>
						</div>
					</div>
				</a>
				<a href="/reserve" class="group bg-white border border-gray-200 rounded-xl p-5 hover:border-blue-400 hover:shadow-md transition">
					<div class="flex items-start gap-4">
						<span class="text-2xl">📋</span>
						<div>
							<p class="font-semibold text-gray-800 group-hover:text-blue-600 transition">事前予約</p>
							<p class="text-sm text-gray-400 mt-0.5">来訪前のオンライン予約フォーム</p>
						</div>
					</div>
				</a>
			</div>
		</section>

		<!-- スタッフ向け -->
		<section>
			<h2 class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">スタッフ向け</h2>
			<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
				<a href="/admin" class="group bg-white border border-gray-200 rounded-xl p-5 hover:border-blue-400 hover:shadow-md transition">
					<div class="flex items-start gap-4">
						<span class="text-2xl">🖥️</span>
						<div>
							<p class="font-semibold text-gray-800 group-hover:text-blue-600 transition">管理画面</p>
							<p class="text-sm text-gray-400 mt-0.5">呼び出し・完了・取消の操作</p>
						</div>
					</div>
				</a>
				<a href="/admin/reservations" class="group bg-white border border-gray-200 rounded-xl p-5 hover:border-blue-400 hover:shadow-md transition">
					<div class="flex items-start gap-4">
						<span class="text-2xl">📅</span>
						<div>
							<p class="font-semibold text-gray-800 group-hover:text-blue-600 transition">予約管理</p>
							<p class="text-sm text-gray-400 mt-0.5">予約一覧の確認・キャンセル</p>
						</div>
					</div>
				</a>
			</div>
		</section>

		<!-- 表示板 -->
		<section>
			<h2 class="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">表示板</h2>
			<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
				<a href="/display" class="group bg-white border border-gray-200 rounded-xl p-5 hover:border-blue-400 hover:shadow-md transition">
					<div class="flex items-start gap-4">
						<span class="text-2xl">📺</span>
						<div>
							<p class="font-semibold text-gray-800 group-hover:text-blue-600 transition">ロビー表示板</p>
							<p class="text-sm text-gray-400 mt-0.5">呼び出し番号のリアルタイム表示</p>
						</div>
					</div>
				</a>
			</div>
		</section>
	</main>
</div>
