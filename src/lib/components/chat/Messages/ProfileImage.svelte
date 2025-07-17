<script lang="ts">
	import { AURA_BASE_URL } from '$lib/constants';

	export let className = 'size-8';
	export let src = `${AURA_BASE_URL}/static/favicon.png`;
</script>

<img
	crossorigin="anonymous"
	src={src === ''
		? `${AURA_BASE_URL}/static/favicon.png`
		: src.startsWith(AURA_BASE_URL) ||
			  src.startsWith('https://www.gravatar.com/avatar/') ||
			  src.startsWith('data:') ||
			  src.startsWith('/')
			? src
			: `${AURA_BASE_URL}/user.png`}
	class=" {className} object-cover rounded-full"
	alt="profile"
	draggable="false"
/>
