let allLogs = [];


// ============================================================
// INIT
// ============================================================

document.addEventListener(
    "DOMContentLoaded",
    init
);


async function init() {

    document
        .getElementById(
            "refreshBtn"
        )
        .addEventListener(
            "click",
            loadLogs
        );


    document
        .getElementById(
            "clearBtn"
        )
        .addEventListener(
            "click",
            clearLogs
        );


    document
        .getElementById(
            "decisionFilter"
        )
        .addEventListener(
            "change",
            renderLogs
        );


    document
        .getElementById(
            "searchInput"
        )
        .addEventListener(
            "input",
            renderLogs
        );


    await loadLogs();
}


// ============================================================
// LOAD
// ============================================================

async function loadLogs() {

    const response =
        await chrome.runtime.sendMessage({

            type:
                "GET_ACCESS_LOGS"

        });


    if (
        !response ||
        !response.success
    ) {

        console.error(
            "Cannot load logs"
        );

        return;
    }


    allLogs =
        response.logs || [];


    renderLogs();
}


// ============================================================
// FILTER + RENDER
// ============================================================

function renderLogs() {

    const tbody =
        document.getElementById(
            "logTableBody"
        );


    tbody.textContent = "";


    const decisionFilter =
        document
            .getElementById(
                "decisionFilter"
            )
            .value;


    const search =
        document
            .getElementById(
                "searchInput"
            )
            .value
            .trim()
            .toLowerCase();


    let filtered =
        [...allLogs];


    // ========================================================
    // DECISION FILTER
    // ========================================================

    if (decisionFilter) {

        filtered =
            filtered.filter(
                item =>
                    item.decision ===
                    decisionFilter
            );

    }


    // ========================================================
    // SEARCH
    // ========================================================

    if (search) {

        filtered =
            filtered.filter(
                item => {

                    const host =
                        (
                            item.hostname ||
                            ""
                        )
                            .toLowerCase();


                    const url =
                        (
                            item.url ||
                            ""
                        )
                            .toLowerCase();


                    const title =
                        (
                            item.title ||
                            ""
                        )
                            .toLowerCase();


                    return (
                        host.includes(
                            search
                        ) ||
                        url.includes(
                            search
                        ) ||
                        title.includes(
                            search
                        )
                    );

                }
            );

    }


    // ========================================================
    // NEWEST FIRST
    // ========================================================

    filtered.sort(
        (a, b) => {

            return (
                new Date(
                    b.timestamp
                ) -
                new Date(
                    a.timestamp
                )
            );

        }
    );


    // ========================================================
    // ROWS
    // ========================================================

    for (
        const log
        of filtered
    ) {

        const tr =
            document.createElement(
                "tr"
            );


        appendCell(
            tr,
            formatTime(
                log.timestamp
            )
        );


        const decisionCell =
            appendCell(
                tr,
                log.decision
            );


        decisionCell.className =
            log.decision === "ALLOW"
                ? "decision-allow"
                : "decision-block";


        appendCell(
            tr,
            log.hostname
        );


        appendCell(
            tr,
            log.reason
        );


        const urlCell =
            appendCell(
                tr,
                log.url
            );


        urlCell.classList.add(
            "url-cell"
        );


        tbody.appendChild(
            tr
        );

    }


    renderSummary(
        filtered
    );
}


// ============================================================
// APPEND CELL
// ============================================================

function appendCell(
    row,
    value
) {

    const td =
        document.createElement(
            "td"
        );


    td.textContent =
        value || "";


    row.appendChild(
        td
    );


    return td;
}


// ============================================================
// SUMMARY
// ============================================================

function renderSummary(logs) {

    const allow =
        logs.filter(
            item =>
                item.decision ===
                "ALLOW"
        ).length;


    const block =
        logs.filter(
            item =>
                item.decision ===
                "BLOCK"
        ).length;


    document
        .getElementById(
            "summary"
        )
        .textContent =
            `Total: ${logs.length} | ALLOW: ${allow} | BLOCK: ${block}`;
}


// ============================================================
// TIME
// ============================================================

function formatTime(timestamp) {

    try {

        return new Date(
            timestamp
        ).toLocaleString();

    } catch {

        return timestamp;

    }
}


// ============================================================
// CLEAR
// ============================================================

async function clearLogs() {

    const confirmed =
        confirm(
            "Clear all access logs?"
        );


    if (!confirmed) {
        return;
    }


    const response =
        await chrome.runtime.sendMessage({

            type:
                "CLEAR_ACCESS_LOGS"

        });


    if (
        response &&
        response.success
    ) {

        allLogs = [];

        renderLogs();

    }
}