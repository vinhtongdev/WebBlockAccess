document.addEventListener(
    "DOMContentLoaded",
    init
);


// ============================================================
// INIT
// ============================================================

async function init() {

    await loadConfig();


    document
        .getElementById(
            "saveBtn"
        )
        .addEventListener(
            "click",
            saveConfig
        );


    document
        .getElementById(
            "resetBtn"
        )
        .addEventListener(
            "click",
            resetConfig
        );

    document
        .getElementById(
        "viewLogsBtn"
        )
        .addEventListener(
        "click",
        openLogs
    );

}

function openLogs() {

    chrome.tabs.create({

        url:
            chrome.runtime.getURL(
                "logs.html"
            )

    });

}


// ============================================================
// LOAD CONFIG
// ============================================================

async function loadConfig() {

    const response =
        await chrome.runtime.sendMessage({

            type:
                "GET_CONFIG"

        });


    if (
        !response ||
        !response.success
    ) {

        showStatus(
            "Cannot load config"
        );

        return;
    }


    renderConfig(
        response.config
    );
}


// ============================================================
// RENDER
// ============================================================

function renderConfig(config) {

    document
        .getElementById(
            "enabled"
        )
        .checked =
            config.enabled;


    document
        .getElementById(
            "startTime"
        )
        .value =
            config.workingHours.start;


    document
        .getElementById(
            "endTime"
        )
        .value =
            config.workingHours.end;


    // --------------------------------------------------------
    // Working days
    // --------------------------------------------------------

    const dayCheckboxes =
        document.querySelectorAll(
            "#workingDays input"
        );


    dayCheckboxes.forEach(
        (checkbox) => {

            const day =
                Number(
                    checkbox.value
                );


            checkbox.checked =
                config
                    .workingDays
                    .includes(day);

        }
    );


    // --------------------------------------------------------
    // Whitelist
    // --------------------------------------------------------

    document
        .getElementById(
            "whitelist"
        )
        .value =
            rulesToText(
                config.whitelist
            );


    // --------------------------------------------------------
    // Blacklist
    // --------------------------------------------------------

    document
        .getElementById(
            "blacklist"
        )
        .value =
            rulesToText(
                config.blacklist
            );

}


// ============================================================
// SAVE
// ============================================================

async function saveConfig() {

    try {

        const config =
            buildConfigFromForm();


        const response =
            await chrome.runtime.sendMessage({

                type:
                    "SAVE_CONFIG",

                payload:
                    config

            });


        if (
            !response ||
            !response.success
        ) {

            throw new Error(
                response?.error ||
                "Save failed"
            );

        }


        showStatus(
            "Saved successfully"
        );


    } catch (error) {

        showStatus(
            error.message
        );

    }

}


// ============================================================
// BUILD CONFIG
// ============================================================

function buildConfigFromForm() {

    const enabled =
        document
            .getElementById(
                "enabled"
            )
            .checked;


    const start =
        document
            .getElementById(
                "startTime"
            )
            .value;


    const end =
        document
            .getElementById(
                "endTime"
            )
            .value;


    if (
        !start ||
        !end
    ) {

        throw new Error(
            "Working time is required"
        );

    }


    // --------------------------------------------------------
    // Days
    // --------------------------------------------------------

    const workingDays =
        Array
            .from(
                document.querySelectorAll(
                    "#workingDays input:checked"
                )
            )
            .map(
                checkbox =>
                    Number(
                        checkbox.value
                    )
            );


    // --------------------------------------------------------
    // Rules
    // --------------------------------------------------------

    const whitelist =
        textToRules(
            document
                .getElementById(
                    "whitelist"
                )
                .value
        );


    const blacklist =
        textToRules(
            document
                .getElementById(
                    "blacklist"
                )
                .value
        );


    return {

        enabled: enabled,

        workingHours: {
            start: start,
            end: end
        },

        workingDays:
            workingDays,

        whitelist:
            whitelist,

        blacklist:
            blacklist

    };
}


// ============================================================
// TEXT → RULES
// ============================================================

function textToRules(text) {

    const lines =
        text
            .split("\n")
            .map(
                line =>
                    line.trim()
            )
            .filter(Boolean);


    const ruleMap =
        new Map();


    for (const line of lines) {

        const parts =
            line.split("|");


        const host =
            normalizeHost(
                parts[0]
            );


        const path =
            parts[1]
                ?.trim() ||
            "*";


        if (!host) {
            continue;
        }


        if (
            !ruleMap.has(host)
        ) {

            ruleMap.set(
                host,
                []
            );

        }


        ruleMap
            .get(host)
            .push(path);

    }


    return Array
        .from(
            ruleMap.entries()
        )
        .map(
            ([host, paths]) => ({

                host: host,

                paths:
                    [...new Set(paths)]

            })
        );

}


// ============================================================
// RULES → TEXT
// ============================================================

function rulesToText(rules) {

    const lines = [];


    for (
        const rule of
        rules || []
    ) {

        const paths =
            rule.paths?.length
                ? rule.paths
                : ["*"];


        for (
            const path of paths
        ) {

            lines.push(
                `${rule.host}|${path}`
            );

        }

    }


    return lines.join(
        "\n"
    );
}


// ============================================================
// NORMALIZE DOMAIN
// ============================================================

function normalizeHost(host) {

    let value =
        host
            .trim()
            .toLowerCase();


    // User paste URL đầy đủ
    if (
        value.startsWith(
            "http://"
        ) ||
        value.startsWith(
            "https://"
        )
    ) {

        try {

            value =
                new URL(
                    value
                ).hostname;

        } catch {

            return "";

        }

    }


    if (
        value.startsWith(
            "www."
        )
    ) {

        value =
            value.substring(4);

    }


    return value;
}


// ============================================================
// RESET
// ============================================================

async function resetConfig() {

    const response =
        await chrome.runtime.sendMessage({

            type:
                "RESET_CONFIG"

        });


    if (
        !response ||
        !response.success
    ) {

        showStatus(
            "Reset failed"
        );

        return;
    }


    renderConfig(
        response.config
    );


    showStatus(
        "Reset completed"
    );
}


// ============================================================
// STATUS
// ============================================================

function showStatus(message) {

    const element =
        document.getElementById(
            "status"
        );


    element.textContent =
        message;


    setTimeout(
        () => {

            element.textContent =
                "";

        },
        2000
    );
}