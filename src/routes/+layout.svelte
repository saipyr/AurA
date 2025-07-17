<script>
	import { io } from 'socket.io-client';
	import { spring } from 'svelte/motion';
	import PyodideWorker from '$lib/workers/pyodide.worker?worker';

	let loadingProgress = spring(0, {
		stiffness: 0.05
	});

	import { onMount, tick, setContext, onDestroy } from 'svelte';
	import {
		config,
		user,
		settings,
		theme,
		AURA_NAME,
		mobile,
		socket,
		chatId,
		chats,
		currentChatPage,
		tags,
		temporaryChatEnabled,
		isLastActiveTab,
		isApp,
		appInfo,
		toolServers,
		playingNotificationSound
	} from '$lib/stores';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { Toaster, toast } from 'svelte-sonner';

	import { executeToolServer, getBackendConfig } from '$lib/apis';
	import { getSessionUser, userSignOut } from '$lib/apis/auths';

	import '../tailwind.css';
	import '../app.css';

	import 'tippy.js/dist/tippy.css';

	import { AURA_BASE_URL, AURA_HOSTNAME } from '$lib/constants';
	import i18n, { initI18n, getLanguages, changeLanguage } from '$lib/i18n';
	import { bestMatchingLanguage } from '$lib/utils';
	import { getAllTags, getChatList } from '$lib/apis/chats';
	import NotificationToast from '$lib/components/NotificationToast.svelte';
	import AppSidebar from '$lib/components/app/AppSidebar.svelte';
	import { chatCompletion } from '$lib/apis/openai';

	import { beforeNavigate } from '$app/navigation';
	import { updated } from '$app/state';

	import FuzzyFinderModal from '../../AurA/frontend/src/lib/components/FuzzyFinderModal.svelte';
	let showFuzzyFinder = false;
	function handleKeydown(e) {
		if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'p') {
			e.preventDefault();
			showFuzzyFinder = true;
		}
	}

	// handle frontend updates (https://svelte.dev/docs/kit/configuration#version)
	beforeNavigate(({ willUnload, to }) => {
		if (updated.current && !willUnload && to?.url) {
			location.href = to.url.href;
		}
	});

	setContext('i18n', i18n);

	const bc = new BroadcastChannel('active-tab-channel');

	let loaded = false;
	let tokenTimer = null;

	const BREAKPOINT = 768;

	const setupSocket = async (enableWebsocket) => {
		const _socket = io(`${AURA_BASE_URL}` || undefined, {
			reconnection: true,
			reconnectionDelay: 1000,
			reconnectionDelayMax: 5000,
			randomizationFactor: 0.5,
			path: '/ws/socket.io',
			transports: enableWebsocket ? ['websocket'] : ['polling', 'websocket'],
			auth: { token: localStorage.token }
		});

		await socket.set(_socket);

		_socket.on('connect_error', (err) => {
			console.log('connect_error', err);
		});

		_socket.on('connect', () => {
			console.log('connected', _socket.id);
		});

		_socket.on('reconnect_attempt', (attempt) => {
			console.log('reconnect_attempt', attempt);
		});

		_socket.on('reconnect_failed', () => {
			console.log('reconnect_failed');
		});

		_socket.on('disconnect', (reason, details) => {
			console.log(`Socket ${_socket.id} disconnected due to ${reason}`);
			if (details) {
				console.log('Additional details:', details);
			}
		});
	};

	const executePythonAsWorker = async (id, code, cb) => {
		let result = null;
		let stdout = null;
		let stderr = null;

		let executing = true;
		let packages = [
			code.includes('requests') ? 'requests' : null,
			code.includes('bs4') ? 'beautifulsoup4' : null,
			code.includes('numpy') ? 'numpy' : null,
			code.includes('pandas') ? 'pandas' : null,
			code.includes('matplotlib') ? 'matplotlib' : null,
			code.includes('sklearn') ? 'scikit-learn' : null,
			code.includes('scipy') ? 'scipy' : null,
			code.includes('re') ? 'regex' : null,
			code.includes('seaborn') ? 'seaborn' : null,
			code.includes('sympy') ? 'sympy' : null,
			code.includes('tiktoken') ? 'tiktoken' : null,
			code.includes('pytz') ? 'pytz' : null
		].filter(Boolean);

		const pyodideWorker = new PyodideWorker();

		pyodideWorker.postMessage({
			id: id,
			code: code,
			packages: packages
		});

		setTimeout(() => {
			if (executing) {
				executing = false;
				stderr = 'Execution Time Limit Exceeded';
				pyodideWorker.terminate();

				if (cb) {
					cb(
						JSON.parse(
							JSON.stringify(
								{
									stdout: stdout,
									stderr: stderr,
									result: result
								},
								(_key, value) => (typeof value === 'bigint' ? value.toString() : value)
							)
						)
					);
				}
			}
		}, 60000);

		pyodideWorker.onmessage = (event) => {
			console.log('pyodideWorker.onmessage', event);
			const { id, ...data } = event.data;

			console.log(id, data);

			data['stdout'] && (stdout = data['stdout']);
			data['stderr'] && (stderr = data['stderr']);
			data['result'] && (result = data['result']);

			if (cb) {
				cb(
					JSON.parse(
						JSON.stringify(
							{
								stdout: stdout,
								stderr: stderr,
								result: result
							},
							(_key, value) => (typeof value === 'bigint' ? value.toString() : value)
						)
					)
				);
			}

			executing = false;
		};

		pyodideWorker.onerror = (event) => {
			console.log('pyodideWorker.onerror', event);

			if (cb) {
				cb(
					JSON.parse(
						JSON.stringify(
							{
								stdout: stdout,
								stderr: stderr,
								result: result
							},
							(_key, value) => (typeof value === 'bigint' ? value.toString() : value)
						)
					)
				);
			}
			executing = false;
		};
	};

	const executeTool = async (data, cb) => {
		const toolServer = $settings?.toolServers?.find((server) => server.url === data.server?.url);
		const toolServerData = $toolServers?.find((server) => server.url === data.server?.url);

		console.log('executeTool', data, toolServer);

		if (toolServer) {
			console.log(toolServer);
			const res = await executeToolServer(
				(toolServer?.auth_type ?? 'bearer') === 'bearer' ? toolServer?.key : localStorage.token,
				toolServer.url,
				data?.name,
				data?.params,
				toolServerData
			);

			console.log('executeToolServer', res);
			if (cb) {
				cb(JSON.parse(JSON.stringify(res)));
			}
		} else {
			if (cb) {
				cb(
					JSON.parse(
						JSON.stringify({
							error: 'Tool Server Not Found'
						})
					)
				);
			}
		}
	};

	const chatEventHandler = async (event, cb) => {
		const chat = $page.url.pathname.includes(`/c/${event.chat_id}`);

		let isFocused = document.visibilityState !== 'visible';
		if (window.electronAPI) {
			const res = await window.electronAPI.send({
				type: 'window:isFocused'
			});
			if (res) {
				isFocused = res.isFocused;
			}
		}

		await tick();
		const type = event?.data?.type ?? null;
		const data = event?.data?.data ?? null;

		if ((event.chat_id !== $chatId && !$temporaryChatEnabled) || isFocused) {
			if (type === 'chat:completion') {
				const { done, content, title } = data;

				if (done) {
					if ($settings?.notificationSoundAlways ?? false) {
						playingNotificationSound.set(true);

						const audio = new Audio(`/audio/notification.mp3`);
						audio.play().finally(() => {
							// Ensure the global state is reset after the sound finishes
							playingNotificationSound.set(false);
						});
					}

					if ($isLastActiveTab) {
						if ($settings?.notificationEnabled ?? false) {
							new Notification(`${title} • AurA IDE`, {
								body: content,
								icon: `${AURA_BASE_URL}/static/favicon.png`
							});
						}
					}

					toast.custom(NotificationToast, {
						componentProps: {
							onClick: () => {
								goto(`/c/${event.chat_id}`);
							},
							content: content,
							title: title
						},
						duration: 15000,
						unstyled: true
					});
				}
			} else if (type === 'chat:title') {
				currentChatPage.set(1);
				await chats.set(await getChatList(localStorage.token, $currentChatPage));
			} else if (type === 'chat:tags') {
				tags.set(await getAllTags(localStorage.token));
			}
		} else if (data?.session_id === $socket.id) {
			if (type === 'execute:python') {
				console.log('execute:python', data);
				executePythonAsWorker(data.id, data.code, cb);
			} else if (type === 'execute:tool') {
				console.log('execute:tool', data);
				executeTool(data, cb);
			} else if (type === 'request:chat:completion') {
				console.log(data, $socket.id);
				const { session_id, channel, form_data, model } = data;

				try {
					const directConnections = $settings?.directConnections ?? {};

					if (directConnections) {
						const urlIdx = model?.urlIdx;

						const OPENAI_API_URL = directConnections.OPENAI_API_BASE_URLS[urlIdx];
						const OPENAI_API_KEY = directConnections.OPENAI_API_KEYS[urlIdx];
						const API_CONFIG = directConnections.OPENAI_API_CONFIGS[urlIdx];

						try {
							if (API_CONFIG?.prefix_id) {
								const prefixId = API_CONFIG.prefix_id;
								form_data['model'] = form_data['model'].replace(`${prefixId}.`, ``);
							}

							const [res, controller] = await chatCompletion(
								OPENAI_API_KEY,
								form_data,
								OPENAI_API_URL
							);

							if (res) {
								// raise if the response is not ok
								if (!res.ok) {
									throw await res.json();
								}

								if (form_data?.stream ?? false) {
									cb({
										status: true
									});
									console.log({ status: true });

									// res will either be SSE or JSON
									const reader = res.body.getReader();
									const decoder = new TextDecoder();

									const processStream = async () => {
										while (true) {
											// Read data chunks from the response stream
											const { done, value } = await reader.read();
											if (done) {
												break;
											}

											// Decode the received chunk
											const chunk = decoder.decode(value, { stream: true });

											// Process lines within the chunk
											const lines = chunk.split('\n').filter((line) => line.trim() !== '');

											for (const line of lines) {
												console.log(line);
												$socket?.emit(channel, line);
											}
										}
									};

									// Process the stream in the background
									await processStream();
								} else {
									const data = await res.json();
									cb(data);
								}
							} else {
								throw new Error('An error occurred while fetching the completion');
							}
						} catch (error) {
							console.error('chatCompletion', error);
							cb(error);
						}
					}
				} catch (error) {
					console.error('chatCompletion', error);
					cb(error);
				} finally {
					$socket.emit(channel, {
						done: true
					});
				}
			} else {
				console.log('chatEventHandler', event);
			}
		}
	};

	const channelEventHandler = async (event) => {
		if (event.data?.type === 'typing') {
			return;
		}

		// check url path
		const channel = $page.url.pathname.includes(`/channels/${event.channel_id}`);

		let isFocused = document.visibilityState !== 'visible';
		if (window.electronAPI) {
			const res = await window.electronAPI.send({
				type: 'window:isFocused'
			});
			if (res) {
				isFocused = res.isFocused;
			}
		}

		if ((!channel || isFocused) && event?.user?.id !== $user?.id) {
			await tick();
			const type = event?.data?.type ?? null;
			const data = event?.data?.data ?? null;

			if (type === 'message') {
				if ($isLastActiveTab) {
					if ($settings?.notificationEnabled ?? false) {
						new Notification(`${data?.user?.name} (#${event?.channel?.name}) • AurA IDE`, {
							body: data?.content,
							icon: data?.user?.profile_image_url ?? `${AURA_BASE_URL}/static/favicon.png`
						});
					}
				}

				toast.custom(NotificationToast, {
					componentProps: {
						onClick: () => {
							goto(`/channels/${event.channel_id}`);
						},
						content: data?.content,
						title: event?.channel?.name
					},
					duration: 15000,
					unstyled: true
				});
			}
		}
	};

	const TOKEN_EXPIRY_BUFFER = 60; // seconds
	const checkTokenExpiry = async () => {
		const exp = $user?.expires_at; // token expiry time in unix timestamp
		const now = Math.floor(Date.now() / 1000); // current time in unix timestamp

		if (!exp) {
			// If no expiry time is set, do nothing
			return;
		}

		if (now >= exp - TOKEN_EXPIRY_BUFFER) {
			const res = await userSignOut();
			user.set(null);
			localStorage.removeItem('token');

			location.href = res?.redirect_url ?? '/auth';
		}
	};

	const availableThemes = [
		{ label: 'Light', value: 'light', emoji: '🌞' },
		{ label: 'Dark', value: 'dark', emoji: '🌚' },
		{ label: 'Rose Pine', value: 'rosepine', emoji: '🌸' },
		{ label: 'Solarized Light', value: 'solarized-light', emoji: '🟨' },
		{ label: 'Solarized Dark', value: 'solarized-dark', emoji: '🟦' },
		{ label: 'Dracula', value: 'dracula', emoji: '🟪' },
		{ label: 'Nord', value: 'nord', emoji: '❄️' },
		{ label: 'Monokai', value: 'monokai', emoji: '🟩' },
		{ label: 'GitHub Light', value: 'github-light', emoji: '⬜️' },
		{ label: 'GitHub Dark', value: 'github-dark', emoji: '⬛️' },
		{ label: 'One Dark', value: 'one-dark', emoji: '🟦' },
		{ label: 'One Light', value: 'one-light', emoji: '🟨' },
		{ label: 'Custom', value: 'custom', emoji: '🎨' }
	];

	let monacoLoaded = false;
	let monaco;

	async function loadMonacoThemes() {
		if (monacoLoaded) return;
		monaco = await import('monaco-editor');
		// Solarized Light
		monaco.editor.defineTheme('solarized-light', {
			base: 'vs',
			inherit: true,
			rules: [],
			colors: {
				'editor.background': '#fdf6e3',
				'editor.foreground': '#657b83',
				'editor.lineHighlightBackground': '#eee8d5',
				'editorCursor.foreground': '#657b83',
				'editor.selectionBackground': '#eee8d5',
				'editor.inactiveSelectionBackground': '#eee8d5',
				'diffEditor.insertedTextBackground': '#eaffea',
				'diffEditor.removedTextBackground': '#ffeaea',
			}
		});
		// Solarized Dark
		monaco.editor.defineTheme('solarized-dark', {
			base: 'vs-dark',
			inherit: true,
			rules: [],
			colors: {
				'editor.background': '#002b36',
				'editor.foreground': '#839496',
				'editor.lineHighlightBackground': '#073642',
				'editorCursor.foreground': '#93a1a1',
				'editor.selectionBackground': '#073642',
				'editor.inactiveSelectionBackground': '#073642',
				'diffEditor.insertedTextBackground': '#14421255',
				'diffEditor.removedTextBackground': '#60000055',
			}
		});
		// Dracula
		monaco.editor.defineTheme('dracula', {
			base: 'vs-dark',
			inherit: true,
			rules: [],
			colors: {
				'editor.background': '#282a36',
				'editor.foreground': '#f8f8f2',
				'editor.lineHighlightBackground': '#44475a',
				'editorCursor.foreground': '#f8f8f0',
				'editor.selectionBackground': '#44475a',
				'editor.inactiveSelectionBackground': '#44475a',
				'diffEditor.insertedTextBackground': '#50fa7b33',
				'diffEditor.removedTextBackground': '#ff555533',
			}
		});
		// Nord
		monaco.editor.defineTheme('nord', {
			base: 'vs-dark',
			inherit: true,
			rules: [],
			colors: {
				'editor.background': '#2e3440',
				'editor.foreground': '#d8dee9',
				'editor.lineHighlightBackground': '#3b4252',
				'editorCursor.foreground': '#d8dee9',
				'editor.selectionBackground': '#434c5e',
				'editor.inactiveSelectionBackground': '#434c5e',
				'diffEditor.insertedTextBackground': '#a3be8c33',
				'diffEditor.removedTextBackground': '#bf616a33',
			}
		});
		// Monokai
		monaco.editor.defineTheme('monokai', {
			base: 'vs-dark',
			inherit: true,
			rules: [],
			colors: {
				'editor.background': '#272822',
				'editor.foreground': '#f8f8f2',
				'editor.lineHighlightBackground': '#3e3d32',
				'editorCursor.foreground': '#f8f8f0',
				'editor.selectionBackground': '#49483e',
				'editor.inactiveSelectionBackground': '#49483e',
				'diffEditor.insertedTextBackground': '#a6e22e33',
				'diffEditor.removedTextBackground': '#f9267233',
			}
		});
		// GitHub Light
		monaco.editor.defineTheme('github-light', {
			base: 'vs',
			inherit: true,
			rules: [],
			colors: {
				'editor.background': '#ffffff',
				'editor.foreground': '#24292e',
				'editor.lineHighlightBackground': '#f6f8fa',
				'editorCursor.foreground': '#24292e',
				'editor.selectionBackground': '#c8e1ff',
				'editor.inactiveSelectionBackground': '#c8e1ff',
				'diffEditor.insertedTextBackground': '#acf2bd',
				'diffEditor.removedTextBackground': '#fdb8c0',
			}
		});
		// GitHub Dark
		monaco.editor.defineTheme('github-dark', {
			base: 'vs-dark',
			inherit: true,
			rules: [],
			colors: {
				'editor.background': '#0d1117',
				'editor.foreground': '#c9d1d9',
				'editor.lineHighlightBackground': '#161b22',
				'editorCursor.foreground': '#c9d1d9',
				'editor.selectionBackground': '#388bfd55',
				'editor.inactiveSelectionBackground': '#388bfd55',
				'diffEditor.insertedTextBackground': '#23863633',
				'diffEditor.removedTextBackground': '#da363333',
			}
		});
		// One Dark
		monaco.editor.defineTheme('one-dark', {
			base: 'vs-dark',
			inherit: true,
			rules: [],
			colors: {
				'editor.background': '#282c34',
				'editor.foreground': '#abb2bf',
				'editor.lineHighlightBackground': '#2c313c',
				'editorCursor.foreground': '#528bff',
				'editor.selectionBackground': '#3e4451',
				'editor.inactiveSelectionBackground': '#3e4451',
				'diffEditor.insertedTextBackground': '#98c37933',
				'diffEditor.removedTextBackground': '#e06c7533',
			}
		});
		// One Light
		monaco.editor.defineTheme('one-light', {
			base: 'vs',
			inherit: true,
			rules: [],
			colors: {
				'editor.background': '#fafafa',
				'editor.foreground': '#383a42',
				'editor.lineHighlightBackground': '#e5e5e6',
				'editorCursor.foreground': '#526fff',
				'editor.selectionBackground': '#d0d0d0',
				'editor.inactiveSelectionBackground': '#d0d0d0',
				'diffEditor.insertedTextBackground': '#c2e0c6',
				'diffEditor.removedTextBackground': '#ffdce0',
			}
		});
		// Rose Pine (if not already defined)
		monaco.editor.defineTheme('rosepine', {
			base: 'vs-dark',
			inherit: true,
			rules: [],
			colors: {
				'editor.background': '#232136',
				'editor.foreground': '#e0def4',
				'editor.lineHighlightBackground': '#393552',
				'editorCursor.foreground': '#e0def4',
				'editor.selectionBackground': '#393552',
				'editor.inactiveSelectionBackground': '#393552',
				'diffEditor.insertedTextBackground': '#31748f33',
				'diffEditor.removedTextBackground': '#eb6f9233',
			}
		});
		monacoLoaded = true;
	}

	async function setTheme(newTheme) {
		theme.set(newTheme);
		localStorage.setItem('theme', newTheme);
		await tick();
		await loadMonacoThemes();
		if (monaco) {
			monaco.editor.setTheme(newTheme);
		}
		// Dynamically load Svelte UI CSS if available
		const themeCss = `/static/themes/${newTheme}.css`;
		let link = document.getElementById('theme-css');
		if (link) link.remove();
		fetch(themeCss, { method: 'HEAD' }).then(res => {
			if (res.ok) {
				link = document.createElement('link');
				link.rel = 'stylesheet';
				link.id = 'theme-css';
				link.href = themeCss;
				document.head.appendChild(link);
			}
		});
	}

	import SettingsModal from '../../AurA/frontend/src/lib/components/SettingsModal.svelte';
	import SettingsEditorTab from '../../AurA/frontend/src/lib/components/SettingsEditorTab.svelte';
	import SettingsKeybindingsTab from '../../AurA/frontend/src/lib/components/SettingsKeybindingsTab.svelte';
	let showSettings = false;
	function handleSettingsKey(e) {
		if ((e.ctrlKey || e.metaKey) && e.key === ',') {
			e.preventDefault();
			showSettings = true;
		}
	}

	onMount(() => {
		window.addEventListener('keydown', handleSettingsKey);
	});
	onDestroy(() => {
		window.removeEventListener('keydown', handleSettingsKey);
	});
	function openSettings() { showSettings = true; }
	function closeSettings() { showSettings = false; }
	function applyEditorSettings(e) {
		const s = e.detail.settings;
		if (window.monaco) {
			window.monaco.editor.getModels().forEach(model => {
				model.updateOptions({
					tabSize: s.tabSize,
					insertSpaces: true
				});
			});
			window.monaco.editor.getEditors?.().forEach(editor => {
				editor.updateOptions({
					fontSize: s.fontSize,
					fontFamily: s.fontFamily,
					lineNumbers: s.lineNumbers ? 'on' : 'off',
					minimap: { enabled: s.minimap },
					wordWrap: s.wordWrap ? 'on' : 'off'
				});
			});
		}
	}

	onMount(() => {
		const savedTheme = localStorage.getItem('theme');
		setTheme(savedTheme || 'light');
		window.addEventListener('keydown', handleKeydown);
	});

	onDestroy(() => {
		window.removeEventListener('keydown', handleKeydown);
	});

	function openFuzzyFinder() {
		showFuzzyFinder = true;
	}
	function closeFuzzyFinder() {
		showFuzzyFinder = false;
	}

	onMount(async () => {
		if (typeof window !== 'undefined' && window.applyTheme) {
			window.applyTheme();
		}

		if (window?.electronAPI) {
			const info = await window.electronAPI.send({
				type: 'app:info'
			});

			if (info) {
				isApp.set(true);
				appInfo.set(info);

				const data = await window.electronAPI.send({
					type: 'app:data'
				});

				if (data) {
					appData.set(data);
				}
			}
		}

		// Listen for messages on the BroadcastChannel
		bc.onmessage = (event) => {
			if (event.data === 'active') {
				isLastActiveTab.set(false); // Another tab became active
			}
		};

		// Set yourself as the last active tab when this tab is focused
		const handleVisibilityChange = () => {
			if (document.visibilityState === 'visible') {
				isLastActiveTab.set(true); // This tab is now the active tab
				bc.postMessage('active'); // Notify other tabs that this tab is active

				// Check token expiry when the tab becomes active
				checkTokenExpiry();
			}
		};

		// Add event listener for visibility state changes
		document.addEventListener('visibilitychange', handleVisibilityChange);

		// Call visibility change handler initially to set state on load
		handleVisibilityChange();

		theme.set(localStorage.theme);

		mobile.set(window.innerWidth < BREAKPOINT);

		const onResize = () => {
			if (window.innerWidth < BREAKPOINT) {
				mobile.set(true);
			} else {
				mobile.set(false);
			}
		};
		window.addEventListener('resize', onResize);

		user.subscribe((value) => {
			if (value) {
				$socket?.off('chat-events', chatEventHandler);
				$socket?.off('channel-events', channelEventHandler);

				$socket?.on('chat-events', chatEventHandler);
				$socket?.on('channel-events', channelEventHandler);

				// Set up the token expiry check
				if (tokenTimer) {
					clearInterval(tokenTimer);
				}
				tokenTimer = setInterval(checkTokenExpiry, 15000);
			} else {
				$socket?.off('chat-events', chatEventHandler);
				$socket?.off('channel-events', channelEventHandler);
			}
		});

		let backendConfig = null;
		try {
			backendConfig = await getBackendConfig();
			console.log('Backend config:', backendConfig);
		} catch (error) {
			console.error('Error loading backend config:', error);
		}
		// Initialize i18n even if we didn't get a backend config,
		// so `/error` can show something that's not `undefined`.

		initI18n(localStorage?.locale);
		if (!localStorage.locale) {
			const languages = await getLanguages();
			const browserLanguages = navigator.languages
				? navigator.languages
				: [navigator.language || navigator.userLanguage];
			const lang = backendConfig.default_locale
				? backendConfig.default_locale
				: bestMatchingLanguage(languages, browserLanguages, 'en-US');
			changeLanguage(lang);
		}

		if (backendConfig) {
			// Save Backend Status to Store
			await config.set(backendConfig);
			await AURA_NAME.set(backendConfig.name);

			if ($config) {
				await setupSocket($config.features?.enable_websocket ?? true);

				const currentUrl = `${window.location.pathname}${window.location.search}`;
				const encodedUrl = encodeURIComponent(currentUrl);

				if (localStorage.token) {
					// Get Session User Info
					const sessionUser = await getSessionUser(localStorage.token).catch((error) => {
						toast.error(`${error}`);
						return null;
					});

					if (sessionUser) {
						// Save Session User to Store
						$socket.emit('user-join', { auth: { token: sessionUser.token } });

						await user.set(sessionUser);
						await config.set(await getBackendConfig());
					} else {
						// Redirect Invalid Session User to /auth Page
						localStorage.removeItem('token');
						await goto(`/auth?redirect=${encodedUrl}`);
					}
				} else {
					// Don't redirect if we're already on the auth page
					// Needed because we pass in tokens from OAuth logins via URL fragments
					if ($page.url.pathname !== '/auth') {
						await goto(`/auth?redirect=${encodedUrl}`);
					}
				}
			}
		} else {
			// Redirect to /error when Backend Not Detected
			await goto(`/error`);
		}

		await tick();

		if (
			document.documentElement.classList.contains('her') &&
			document.getElementById('progress-bar')
		) {
			loadingProgress.subscribe((value) => {
				const progressBar = document.getElementById('progress-bar');

				if (progressBar) {
					progressBar.style.width = `${value}%`;
				}
			});

			await loadingProgress.set(100);

			document.getElementById('splash-screen')?.remove();

			const audio = new Audio(`/audio/greeting.mp3`);
			const playAudio = () => {
				audio.play();
				document.removeEventListener('click', playAudio);
			};

			document.addEventListener('click', playAudio);

			loaded = true;
		} else {
			document.getElementById('splash-screen')?.remove();
			loaded = true;
		}

		return () => {
			window.removeEventListener('resize', onResize);
		};
	});
</script>

<svelte:head>
	<title>{$AURA_NAME}</title>
	<link crossorigin="anonymous" rel="icon" href="{AURA_BASE_URL}/static/favicon.png" />

	<!-- rosepine themes have been disabled as it's not up to date with our latest version. -->
	<!-- feel free to make a PR to fix if anyone wants to see it return -->
	<!-- <link rel="stylesheet" type="text/css" href="/themes/rosepine.css" />
	<link rel="stylesheet" type="text/css" href="/themes/rosepine-dawn.css" /> -->
</svelte:head>

<div style="position:fixed;top:8px;left:16px;z-index:1001;">
	<button on:click={openFuzzyFinder} title="Fuzzy Finder (Ctrl+P)">🔍 Fuzzy Finder</button>
</div>
<FuzzyFinderModal bind:open={showFuzzyFinder} on:close={closeFuzzyFinder} />

<div style="position:fixed;top:8px;right:56px;z-index:1001;">
	<button on:click={openSettings} title="Settings (Ctrl+,)">⚙️ Settings</button>
</div>
<SettingsModal bind:open={showSettings} on:close={closeSettings}>
	<svelte:fragment slot="editor">
		<SettingsEditorTab on:change={applyEditorSettings} />
	</svelte:fragment>
	<svelte:fragment slot="keybindings">
		<SettingsKeybindingsTab />
	</svelte:fragment>
</SettingsModal>

<div style="position:fixed;top:8px;right:16px;z-index:1001;">
	<label for="theme-select" style="margin-right:8px;">Theme:</label>
	<select id="theme-select" on:change={e => setTheme(e.target.value)} bind:value={$theme}>
		{#each availableThemes as t}
			<option value={t.value}>{t.emoji} {t.label}</option>
		{/each}
	</select>
</div>

{#if loaded}
	{#if $isApp}
		<div class="flex flex-row h-screen">
			<AppSidebar />

			<div class="w-full flex-1 max-w-[calc(100%-4.5rem)]">
				<slot />
			</div>
		</div>
	{:else}
		<slot />
	{/if}
{/if}

<Toaster
	theme={$theme.includes('dark')
		? 'dark'
		: $theme === 'system'
			? window.matchMedia('(prefers-color-scheme: dark)').matches
				? 'dark'
				: 'light'
			: 'light'}
	richColors
	position="top-right"
	closeButton
/>
