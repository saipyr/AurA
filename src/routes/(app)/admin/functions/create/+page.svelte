<script>
	import { toast } from 'svelte-sonner';
	import { onMount, getContext } from 'svelte';
	import { goto } from '$app/navigation';

	import { config, functions, models, settings } from '$lib/stores';
	import { createNewFunction, getFunctions } from '$lib/apis/functions';
	import FunctionEditor from '$lib/components/admin/Functions/FunctionEditor.svelte';
	import { getModels } from '$lib/apis';
	import { compareVersion, extractFrontmatter } from '$lib/utils';
	import { AURA_VERSION } from '$lib/constants';

	const i18n = getContext('i18n');

	let mounted = false;
	let clone = false;
	let func = null;

	const saveHandler = async (data) => {
		console.log(data);

		const manifest = extractFrontmatter(data.content);
		if (compareVersion(manifest?.required_open_aura_version ?? '0.0.0', AURA_VERSION)) {
			console.log('Version is lower than required');
			toast.error(
				$i18n.t(
					'AurA IDE version (v{{OPEN_AURA_VERSION}}) is lower than required version (v{{REQUIRED_VERSION}})',
					{
						OPEN_AURA_VERSION: AURA_VERSION,
						REQUIRED_VERSION: manifest?.required_open_aura_version ?? '0.0.0'
					}
				)
			);
			return;
		}

		const res = await createNewFunction(localStorage.token, {
			id: data.id,
			name: data.name,
			meta: data.meta,
			content: data.content
		}).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (res) {
			toast.success($i18n.t('Function created successfully'));
			functions.set(await getFunctions(localStorage.token));
			models.set(
				await getModels(
					localStorage.token,
					$config?.features?.enable_direct_connections && ($settings?.directConnections ?? null),
					false,
					true
				)
			);

			await goto('/admin/functions');
		}
	};

	onMount(() => {
		window.addEventListener('message', async (event) => {
			if (
				!['https://aura.com', 'https://www.aura.com', 'http://localhost:9999'].includes(
					event.origin
				)
			)
				return;

			func = JSON.parse(event.data);
			console.log(func);
		});

		if (window.opener ?? false) {
			window.opener.postMessage('loaded', '*');
		}

		if (sessionStorage.function) {
			func = JSON.parse(sessionStorage.function);
			sessionStorage.removeItem('function');

			console.log(func);
			clone = true;
		}

		mounted = true;
	});
</script>

{#if mounted}
	{#key func?.content}
		<FunctionEditor
			id={func?.id ?? ''}
			name={func?.name ?? ''}
			meta={func?.meta ?? { description: '' }}
			content={func?.content ?? ''}
			{clone}
			onSave={(value) => {
				saveHandler(value);
			}}
		/>
	{/key}
{/if}
