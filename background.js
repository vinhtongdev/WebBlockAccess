console.log(
    "[Company Web Control] Background started"
);


// ============================================================
// STORAGE KEYS
// ============================================================

const STORAGE_KEY_CONFIG = "companyWebConfig";
const STORAGE_KEY_LOGS = "accessLogs";

const MAX_LOGS = 1000;
const LOG_DEDUP_WINDOW_MS = 5000;


// ============================================================
// DEFAULT CONFIG
// ============================================================

const DEFAULT_CONFIG = {

    enabled: true,

    workingHours: {
        start: "08:00",
        end: "17:30"
    },

    workingDays: [
        1, 2, 3, 4, 5, 6
    ],

    blacklist: [

        {
            host: "facebook.com",
            paths: ["*"]
        },

        {
            host: "tiktok.com",
            paths: ["*"]
        },

        {
            host: "youtube.com",
            paths: [
                "/shorts/*"
            ]
        },
        
        {
            host: "shopee.vn",
            paths: [
                "*"
            ]
        },
        
        {
            host: "lazada.vn",
            paths: [
                "*"
            ]
        },

    ],

    whitelist: [

        {
            host: "google.com",
            paths: ["*"]
        },

        {
            host: "youtube.com",
            paths: [
                "/watch*",
                "/@company/*"
            ]
        },

        {
            host: "moh.gov.vn",
            paths: ["*"]
        },

        {
            host: "itcom21.com.vn",
            paths: ["*"]
        }

    ]

};


// ============================================================
// EXTENSION INSTALL
// ============================================================

chrome.runtime.onInstalled.addListener(
    async () => {

        const result =
            await chrome.storage.local.get(
                STORAGE_KEY_CONFIG
            );


        // Chỉ tạo config mặc định nếu chưa tồn tại
        if (!result[STORAGE_KEY_CONFIG]) {

            await chrome.storage.local.set({

                [STORAGE_KEY_CONFIG]:
                    DEFAULT_CONFIG

            });


            console.log(
                "[Company Web Control] Default config created"
            );

        }

    }
);


// ============================================================
// MESSAGE LISTENER
// ============================================================

chrome.runtime.onMessage.addListener(
    (
        message,
        sender,
        sendResponse
    ) => {

        if (!message) {
            return;
        }


        // ====================================================
        // GET CONFIG
        // ====================================================

        if (
            message.type ===
            "GET_CONFIG"
        ) {

            getConfig()
                .then((config) => {

                    sendResponse({

                        success: true,
                        config: config

                    });

                })
                .catch((error) => {

                    sendResponse({

                        success: false,
                        error: error.message

                    });

                });


            return true;
        }


        // ====================================================
        // SAVE CONFIG
        // ====================================================

        if (
            message.type ===
            "SAVE_CONFIG"
        ) {

            saveConfig(
                message.payload
            )
                .then(() => {

                    sendResponse({
                        success: true
                    });

                })
                .catch((error) => {

                    sendResponse({

                        success: false,
                        error: error.message

                    });

                });


            return true;
        }


        // ====================================================
        // RESET CONFIG
        // ====================================================

        if (
            message.type ===
            "RESET_CONFIG"
        ) {

            resetConfig()
                .then(() => {

                    sendResponse({

                        success: true,
                        config:
                            DEFAULT_CONFIG

                    });

                })
                .catch((error) => {

                    sendResponse({

                        success: false,
                        error: error.message

                    });

                });


            return true;
        }


        // ====================================================
        // ACCESS LOG
        // ====================================================

        if (
            message.type ===
            "ACCESS_LOG"
        ) {

            saveAccessLog(
                message.payload,
                sender
            );

            return;
        }


        // ====================================================
        // GET LOGS
        // ====================================================

        if (
            message.type ===
            "GET_ACCESS_LOGS"
        ) {

            getAccessLogs()
                .then((logs) => {

                    sendResponse({

                        success: true,
                        logs: logs

                    });

                });


            return true;
        }


        // ====================================================
        // CLEAR LOGS
        // ====================================================

        if (
            message.type ===
            "CLEAR_ACCESS_LOGS"
        ) {

            clearAccessLogs()
                .then(() => {

                    sendResponse({
                        success: true
                    });

                });


            return true;
        }

    }
);


// ============================================================
// CONFIG
// ============================================================

async function getConfig() {

    const result =
        await chrome.storage.local.get(
            STORAGE_KEY_CONFIG
        );


    return (
        result[STORAGE_KEY_CONFIG] ||
        DEFAULT_CONFIG
    );
}


async function saveConfig(config) {

    validateConfig(config);


    await chrome.storage.local.set({

        [STORAGE_KEY_CONFIG]:
            config

    });


    console.log(
        "[Company Web Control] Config saved",
        config
    );
}


async function resetConfig() {

    await chrome.storage.local.set({

        [STORAGE_KEY_CONFIG]:
            structuredClone(
                DEFAULT_CONFIG
            )

    });

}


// ============================================================
// VALIDATE CONFIG
// ============================================================

function validateConfig(config) {

    if (
        !config ||
        typeof config !== "object"
    ) {

        throw new Error(
            "Invalid config"
        );
    }


    if (
        typeof config.enabled !==
        "boolean"
    ) {

        throw new Error(
            "Invalid enabled value"
        );
    }


    if (
        !config.workingHours ||
        !config.workingHours.start ||
        !config.workingHours.end
    ) {

        throw new Error(
            "Invalid working hours"
        );
    }


    if (
        !Array.isArray(
            config.workingDays
        )
    ) {

        throw new Error(
            "Invalid working days"
        );
    }


    if (
        !Array.isArray(
            config.whitelist
        )
    ) {

        throw new Error(
            "Invalid whitelist"
        );
    }


    if (
        !Array.isArray(
            config.blacklist
        )
    ) {

        throw new Error(
            "Invalid blacklist"
        );
    }

}


// ============================================================
// LOG
// ============================================================

async function saveAccessLog(
    data,
    sender
) {

    try {

        if (!data) {
            return;
        }


        const result =
            await chrome.storage.local.get(
                STORAGE_KEY_LOGS
            );


        let logs =
            result[STORAGE_KEY_LOGS] ||
            [];


        // ====================================================
        // DEDUPLICATION
        // chống log trùng
        // ====================================================

        const lastLog =
            logs.length > 0
                ? logs[logs.length - 1]
                : null;


        if (lastLog) {

            const previousTime =
                new Date(
                    lastLog.timestamp
                ).getTime();


            const currentTime =
                new Date(
                    data.timestamp
                ).getTime();


            const timeDiff =
                currentTime -
                previousTime;


            const isSameLog =
                lastLog.url === data.url &&
                lastLog.decision ===
                    data.decision &&
                lastLog.reason ===
                    data.reason &&
                lastLog.tabId ===
                    (
                        sender.tab?.id ??
                        null
                    );


            if (
                isSameLog &&
                timeDiff <
                    LOG_DEDUP_WINDOW_MS
            ) {

                console.log(
                    "[Company Web Control] Duplicate log skipped"
                );

                return;
            }

        }


        // ====================================================
        // CREATE LOG
        // ====================================================

        const logItem = {

            id:
                generateLogId(),

            decision:
                data.decision,

            reason:
                data.reason,

            url:
                data.url,

            title:
                data.title || "",

            hostname:
                data.hostname || "",

            timestamp:
                data.timestamp,

            tabId:
                sender.tab?.id ?? null

        };


        logs.push(
            logItem
        );


        if (
            logs.length >
            MAX_LOGS
        ) {

            logs =
                logs.slice(
                    -MAX_LOGS
                );

        }


        await chrome.storage.local.set({

            [STORAGE_KEY_LOGS]:
                logs

        });


        console.log(
            "[Company Web Control] Log saved",
            logItem
        );


    } catch (error) {

        console.error(
            "[Company Web Control] Save log error",
            error
        );

    }

}

// ============================================================
// GET LOG
// ============================================================

async function getAccessLogs() {

    const result =
        await chrome.storage.local.get(
            STORAGE_KEY_LOGS
        );


    return (
        result[STORAGE_KEY_LOGS] ||
        []
    );
}


// ============================================================
// CLEAR LOG
// ============================================================

async function clearAccessLogs() {

    await chrome.storage.local.remove(
        STORAGE_KEY_LOGS
    );

}


// ============================================================
// ID
// ============================================================

function generateLogId() {

    return (
        Date.now().toString(36) +
        "-" +
        Math.random()
            .toString(36)
            .substring(2, 10)
    );

}