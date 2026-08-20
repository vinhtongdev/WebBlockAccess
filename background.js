console.log("[Company Web Control] Background started");

// ============================================================
// API
// ============================================================

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

const POLICY_API_URL = `${API_BASE_URL}/policy`;

// ============================================================
// STORAGE
// ============================================================

const STORAGE_KEY_CONFIG = "companyWebConfig";

const STORAGE_KEY_POLICY_META = "policyCacheMeta";

const STORAGE_KEY_LOGS = "accessLogs";

const MAX_LOGS = 1000;

const LOG_DEDUP_WINDOW_MS = 5000;

// ============================================================
// POLICY CACHE
//
// 5 phút
// ============================================================

const POLICY_CACHE_TTL_MS = 5 * 60 * 1000;

// ============================================================
// HTTP TIMEOUT
// ============================================================

const API_TIMEOUT_MS = 3000;

// ============================================================
// EMERGENCY DEFAULT CONFIG
//
// Chỉ sử dụng khi:
// - Server không kết nối được
// - Chưa từng có policy cache
// ============================================================

const DEFAULT_CONFIG = {
	id: 0,

	name: "Emergency Default",

	enabled: true,

	workingHours: {
		start: "08:00",
		end: "17:30",
	},

	workingDays: [1, 2, 3, 4, 5, 6],

	whitelist: [
		{
			host: "google.com",
			paths: ["*"],
		},
	],

	blacklist: [
		{
			host: "facebook.com",
			paths: ["*"],
		},

		{
			host: "tiktok.com",
			paths: ["*"],
		},
	],
};

// ============================================================
// INSTALL
// ============================================================

chrome.runtime.onInstalled.addListener(async () => {
	console.log("[Company Web Control] Extension installed");

	await initializePolicy();
});

// ============================================================
// CHROME STARTUP
// ============================================================

chrome.runtime.onStartup.addListener(async () => {
	console.log("[Company Web Control] Chrome started");

	await syncPolicyFromServer();
});

// ============================================================
// INITIALIZE POLICY
// ============================================================

async function initializePolicy() {
	try {
		// ----------------------------------------------------
		// Ưu tiên lấy server
		// ----------------------------------------------------

		const policy = await fetchPolicyFromServer();

		await savePolicyCache(policy, "SERVER");

		console.log("[Company Web Control] Initial server policy loaded");
	} catch (error) {
		console.warn(
			"[Company Web Control] Server unavailable during initialization",
			error,
		);

		const cached = await getCachedPolicy();

		// Đã có cache
		if (cached) {
			console.log("[Company Web Control] Existing cache retained");

			return;
		}

		// Chưa có gì cả
		await savePolicyCache(DEFAULT_CONFIG, "DEFAULT");

		console.warn("[Company Web Control] Emergency default policy created");
	}
}

// ============================================================
// MESSAGE LISTENER
// ============================================================

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
	if (!message) {
		return;
	}

	// ====================================================
	// GET CONFIG
	// ====================================================

	if (message.type === "GET_CONFIG") {
		getConfigWithFallback()
			.then((result) => {
				sendResponse({
					success: true,

					config: result.config,

					source: result.source,
				});
			})
			.catch((error) => {
				sendResponse({
					success: false,

					error: error.message,
				});
			});

		return true;
	}

	// ====================================================
	// FORCE POLICY SYNC
	// ====================================================

	if (message.type === "SYNC_POLICY") {
		syncPolicyFromServer()
			.then((policy) => {
				sendResponse({
					success: true,

					config: policy,
				});
			})
			.catch((error) => {
				sendResponse({
					success: false,

					error: error.message,
				});
			});

		return true;
	}

	// ====================================================
	// GET POLICY STATUS
	// ====================================================

	if (message.type === "GET_POLICY_STATUS") {
		getPolicyStatus().then((status) => {
			sendResponse({
				success: true,

				status: status,
			});
		});

		return true;
	}

	// ====================================================
	// ACCESS LOG
	// ====================================================

	if (message.type === "ACCESS_LOG") {
		saveAccessLog(message.payload, sender);

		return;
	}

	// ====================================================
	// GET LOGS
	// ====================================================

	if (message.type === "GET_ACCESS_LOGS") {
		getAccessLogs().then((logs) => {
			sendResponse({
				success: true,

				logs: logs,
			});
		});

		return true;
	}

	// ====================================================
	// CLEAR LOGS
	// ====================================================

	if (message.type === "CLEAR_ACCESS_LOGS") {
		clearAccessLogs().then(() => {
			sendResponse({
				success: true,
			});
		});

		return true;
	}
});

// ============================================================
// GET CONFIG WITH FALLBACK
// ============================================================

async function getConfigWithFallback() {
	const cache = await getPolicyCacheData();

	// ========================================================
	// CACHE còn mới
	// ========================================================

	if (cache.config && cache.meta && !isPolicyCacheExpired(cache.meta)) {
		return {
			config: cache.config,

			source: cache.meta.source || "CACHE",
		};
	}

	// ========================================================
	// CACHE hết hạn
	//
	// thử gọi server
	// ========================================================

	try {
		const policy = await fetchPolicyFromServer();

		await savePolicyCache(policy, "SERVER");

		return {
			config: policy,

			source: "SERVER",
		};
	} catch (error) {
		console.warn("[Company Web Control] Policy server unavailable", error);
	}

	// ========================================================
	// SERVER lỗi → cache cũ
	// ========================================================

	if (cache.config) {
		console.warn("[Company Web Control] Using stale policy cache");

		return {
			config: cache.config,

			source: "STALE_CACHE",
		};
	}

	// ========================================================
	// Không có server
	// Không có cache
	//
	// emergency config
	// ========================================================

	await savePolicyCache(DEFAULT_CONFIG, "DEFAULT");

	return {
		config: DEFAULT_CONFIG,

		source: "DEFAULT",
	};
}

// ============================================================
// FETCH POLICY
// ============================================================

async function fetchPolicyFromServer() {
	console.log("[Company Web Control] Fetching policy...");

	const controller = new AbortController();

	const timeoutId = setTimeout(() => {
		controller.abort();
	}, API_TIMEOUT_MS);

	try {
		const response = await fetch(POLICY_API_URL, {
			method: "GET",

			headers: {
				Accept: "application/json",
			},

			cache: "no-store",

			signal: controller.signal,
		});

		if (!response.ok) {
			throw new Error(`Policy API HTTP ${response.status}`);
		}

		const policy = await response.json();

		validateServerPolicy(policy);

		console.log("[Company Web Control] Server policy received", policy);

		return policy;
	} finally {
		clearTimeout(timeoutId);
	}
}

// ============================================================
// VALIDATE POLICY
// ============================================================

function validateServerPolicy(policy) {
	if (!policy || typeof policy !== "object") {
		throw new Error("Invalid policy response");
	}

	if (typeof policy.enabled !== "boolean") {
		throw new Error("Invalid policy.enabled");
	}

	if (
		!policy.workingHours ||
		!policy.workingHours.start ||
		!policy.workingHours.end
	) {
		throw new Error("Invalid policy.workingHours");
	}

	if (!Array.isArray(policy.workingDays)) {
		throw new Error("Invalid policy.workingDays");
	}

	if (!Array.isArray(policy.whitelist)) {
		throw new Error("Invalid policy.whitelist");
	}

	if (!Array.isArray(policy.blacklist)) {
		throw new Error("Invalid policy.blacklist");
	}
}

// ============================================================
// SAVE POLICY CACHE
// ============================================================

async function savePolicyCache(policy, source) {
	const meta = {
		policyId: policy.id ?? null,

		policyName: policy.name ?? "",

		fetchedAt: new Date().toISOString(),

		source: source,
	};

	await chrome.storage.local.set({
		[STORAGE_KEY_CONFIG]: policy,

		[STORAGE_KEY_POLICY_META]: meta,
	});

	console.log("[Company Web Control] Policy cached", meta);
}

// ============================================================
// GET CACHE
// ============================================================

async function getCachedPolicy() {
	const result = await chrome.storage.local.get(STORAGE_KEY_CONFIG);

	return result[STORAGE_KEY_CONFIG] || null;
}

// ============================================================
// GET CACHE + META
// ============================================================

async function getPolicyCacheData() {
	const result = await chrome.storage.local.get([
		STORAGE_KEY_CONFIG,

		STORAGE_KEY_POLICY_META,
	]);

	return {
		config: result[STORAGE_KEY_CONFIG] || null,

		meta: result[STORAGE_KEY_POLICY_META] || null,
	};
}

// ============================================================
// CACHE EXPIRED?
// ============================================================

function isPolicyCacheExpired(meta) {
	if (!meta || !meta.fetchedAt) {
		return true;
	}

	const fetchedTime = new Date(meta.fetchedAt).getTime();

	if (Number.isNaN(fetchedTime)) {
		return true;
	}

	return Date.now() - fetchedTime > POLICY_CACHE_TTL_MS;
}

// ============================================================
// MANUAL SYNC
// ============================================================

async function syncPolicyFromServer() {
	const policy = await fetchPolicyFromServer();

	await savePolicyCache(policy, "SERVER");

	return policy;
}

// ============================================================
// POLICY STATUS
// ============================================================

async function getPolicyStatus() {
	const cache = await getPolicyCacheData();

	return {
		serverUrl: POLICY_API_URL,

		hasCache: Boolean(cache.config),

		policyId: cache.meta?.policyId ?? null,

		policyName: cache.meta?.policyName ?? "",

		fetchedAt: cache.meta?.fetchedAt ?? null,

		source: cache.meta?.source ?? null,

		expired: cache.meta ? isPolicyCacheExpired(cache.meta) : true,
	};
}

// ============================================================
// ACCESS LOG
// ============================================================

async function saveAccessLog(data, sender) {
	try {
		if (!data) {
			return;
		}

		const result = await chrome.storage.local.get(STORAGE_KEY_LOGS);

		let logs = result[STORAGE_KEY_LOGS] || [];

		// ====================================================
		// DEDUP
		// ====================================================

		const lastLog = logs.length > 0 ? logs[logs.length - 1] : null;

		if (lastLog) {
			const previousTime = new Date(lastLog.timestamp).getTime();

			const currentTime = new Date(data.timestamp).getTime();

			const timeDiff = currentTime - previousTime;

			const currentTabId = sender.tab?.id ?? null;

			const isSameLog =
				lastLog.url === data.url &&
				lastLog.decision === data.decision &&
				lastLog.reason === data.reason &&
				lastLog.tabId === currentTabId;

			if (isSameLog && timeDiff < LOG_DEDUP_WINDOW_MS) {
				return;
			}
		}

		// ====================================================
		// CREATE
		// ====================================================

		const logItem = {
			id: generateLogId(),

			decision: data.decision,

			reason: data.reason,

			url: data.url,

			title: data.title || "",

			hostname: data.hostname || "",

			timestamp: data.timestamp,

			tabId: sender.tab?.id ?? null,
		};

		logs.push(logItem);

		if (logs.length > MAX_LOGS) {
			logs = logs.slice(-MAX_LOGS);
		}

		await chrome.storage.local.set({
			[STORAGE_KEY_LOGS]: logs,
		});
	} catch (error) {
		console.error("[Company Web Control] Save log error", error);
	}
}

// ============================================================
// GET LOGS
// ============================================================

async function getAccessLogs() {
	const result = await chrome.storage.local.get(STORAGE_KEY_LOGS);

	return result[STORAGE_KEY_LOGS] || [];
}

// ============================================================
// CLEAR LOG
// ============================================================

async function clearAccessLogs() {
	await chrome.storage.local.remove(STORAGE_KEY_LOGS);
}

// ============================================================
// LOG ID
// ============================================================

function generateLogId() {
	return (
		Date.now().toString(36) +
		"-" +
		Math.random().toString(36).substring(2, 10)
	);
}
