(() => {

    let CONFIG = null;

    let currentCheckedUrl = null;
    let blockerObserver = null;


    // ============================================================
    // LOAD CONFIG
    // ============================================================

    async function loadConfig() {
        try {
            const response = await chrome.runtime.sendMessage({
                type: "GET_CONFIG",
            });

            if (!response || !response.success) {
                console.error("[Company Web Control] Cannot load config");

                return false;
            }

            CONFIG = response.config;

            console.log("[Company Web Control] Config loaded", {
                source: response.source,

                policyId: CONFIG.id,

                policyName: CONFIG.name,

                config: CONFIG,
            });

            return true;
        } catch (error) {
            console.error("[Company Web Control] Load config error", error);

            return false;
        }
    }
    // ============================================================
    // MAIN CHECK
    // ============================================================

    function checkCurrentPage() {

        if (!CONFIG) {
            return;
        }

        if (!CONFIG.enabled) {
            removeBlocker();
            return;
        }

        const currentUrl = window.location.href;

        if (currentUrl === currentCheckedUrl) {
            return;
        }

        currentCheckedUrl = currentUrl;


        // --------------------------------------------------------
        // CHECK WORKING TIME
        // --------------------------------------------------------

        if (!isWorkingTime()) {

            logDecision(
                "ALLOW",
                currentUrl,
                "OUTSIDE_WORKING_TIME"
            );

            removeBlocker();

            return;
        }


        // --------------------------------------------------------
        // CHECK URL
        // --------------------------------------------------------

        const result = checkUrl(currentUrl);


        if (result.allowed) {

            logDecision(
                "ALLOW",
                currentUrl,
                result.reason
            );

            removeBlocker();

            return;
        }


        logDecision(
            "BLOCK",
            currentUrl,
            result.reason
        );


        blockPage(
            currentUrl,
            result.reason
        );
    }


    // ============================================================
    // WORKING TIME
    // ============================================================

    function isWorkingTime() {

        const now = new Date();

        const day = now.getDay();

        if (!CONFIG.workingDays.includes(day)) {
            return false;
        }


        const currentMinutes =
            now.getHours() * 60 +
            now.getMinutes();


        const startMinutes =
            timeToMinutes(
                CONFIG.workingHours.start
            );


        const endMinutes =
            timeToMinutes(
                CONFIG.workingHours.end
            );


        return (
            currentMinutes >= startMinutes &&
            currentMinutes <= endMinutes
        );
    }


    // ============================================================
    // TIME CONVERT
    // ============================================================

    function timeToMinutes(time) {

        const [hour, minute] =
            time.split(":").map(Number);

        return hour * 60 + minute;
    }


    // ============================================================
    // URL CHECK
    // ============================================================

    function checkUrl(urlString) {

        let url;


        try {

            url =
                new URL(
                    urlString
                );

        } catch (error) {

            return {
                allowed: false,
                reason: "INVALID_URL"
            };
        }


        const hostname =
            normalizeHostname(
                url.hostname
            );


        const pathname =
            url.pathname;


        // ========================================================
        // 1. BLACKLIST
        //
        // BLACKLIST luôn ưu tiên cao nhất
        // ========================================================

        const blacklistResult =
            matchRuleList(
                hostname,
                pathname,
                CONFIG.blacklist || []
            );


        if (
            blacklistResult.matched
        ) {

            return {
                allowed: false,
                reason:
                    "BLACKLIST_MATCH"
            };

        }


        // ========================================================
        // 2. WHITELIST
        // ========================================================

        const whitelistResult =
            matchRuleList(
                hostname,
                pathname,
                CONFIG.whitelist || []
            );


        if (
            whitelistResult.matched
        ) {

            return {
                allowed: true,
                reason:
                    whitelistResult.reason
            };

        }


        // ========================================================
        // 3. DEFAULT BLOCK
        // ========================================================

        return {
            allowed: false,
            reason:
                whitelistResult.hostMatched
                    ? "PATH_NOT_ALLOWED"
                    : "DOMAIN_NOT_ALLOWED"
        };
    }

    // ============================================================
// MATCH RULE LIST
// ============================================================

    function matchRuleList(
        hostname,
        pathname,
        rules
    ) {

        let hostMatched = false;


        for (const rule of rules) {

            if (!rule.host) {
                continue;
            }


            const ruleHost =
                normalizeHostname(
                    rule.host
                );


            // ----------------------------------------------------
            // HOST CHECK
            // ----------------------------------------------------

            if (
                !matchHost(
                    hostname,
                    ruleHost
                )
            ) {

                continue;

            }


            hostMatched = true;


            // ----------------------------------------------------
            // Không khai báo paths
            //
            // => toàn bộ domain match
            // ----------------------------------------------------

            if (
                !rule.paths ||
                rule.paths.length === 0
            ) {

                return {

                    matched: true,

                    hostMatched: true,

                    reason:
                        "DOMAIN_WHITELIST"
                };

            }


            // ----------------------------------------------------
            // PATH CHECK
            // ----------------------------------------------------

            for (
                const pathRule
                of rule.paths
            ) {

                if (
                    matchPath(
                        pathname,
                        pathRule
                    )
                ) {

                    return {

                        matched: true,

                        hostMatched: true,

                        reason:
                            "DOMAIN_AND_PATH_WHITELIST"
                    };

                }

            }

        }


        return {

            matched: false,

            hostMatched:
                hostMatched

        };
    }

    // ============================================================
    // NORMALIZE HOST
    // ============================================================

    function normalizeHostname(hostname) {

        let host =
            hostname
                .trim()
                .toLowerCase();


        // remove www.

        if (host.startsWith("www.")) {

            host =
                host.substring(4);

        }


        return host;
    }


    // ============================================================
    // HOST MATCH
    // ============================================================

    function matchHost(
        currentHost,
        allowedHost
    ) {

        if (
            currentHost === allowedHost
        ) {
            return true;
        }


        if (
            currentHost.endsWith(
                "." + allowedHost
            )
        ) {

            return true;
        }


        return false;
    }


    // ============================================================
    // PATH MATCH
    // ============================================================

    function matchPath(
        currentPath,
        rulePath
    ) {

        // "*" = toàn bộ path

        if (rulePath === "*") {
            return true;
        }


        // Exact match

        if (
            !rulePath.includes("*")
        ) {

            return (
                currentPath === rulePath
            );
        }


        // --------------------------------------------------------
        // Wildcard
        //
        // /watch*
        // /medical/*
        // /@company/*
        // --------------------------------------------------------

        const regexPattern =
            rulePath
                .replace(
                    /[.+?^${}()|[\]\\]/g,
                    "\\$&"
                )
                .replace(
                    /\*/g,
                    ".*"
                );


        const regex =
            new RegExp(
                "^" +
                regexPattern +
                "$"
            );


        return regex.test(
            currentPath
        );
    }


    // ============================================================
    // BLOCK PAGE
    // ============================================================

    function blockPage(
        url,
        reason
    ) {

        createOverlay(
            url,
            reason
        );


        startBlockerObserver();


        document.addEventListener(
            "keydown",
            blockKeyboard,
            true
        );


        document.addEventListener(
            "keyup",
            blockKeyboard,
            true
        );


        document.addEventListener(
            "click",
            blockInteraction,
            true
        );


        document.addEventListener(
            "mousedown",
            blockInteraction,
            true
        );


        document.addEventListener(
            "touchstart",
            blockInteraction,
            true
        );
    }


    // ============================================================
    // BLOCK INTERACTION
    // ============================================================

    function blockInteraction(event) {

        const blocker =
            document.getElementById(
                "company-web-blocker"
            );


        if (!blocker) {
            return;
        }


        // Click trong blocker vẫn được phép
        if (
            blocker.contains(
                event.target
            )
        ) {
            return;
        }


        event.preventDefault();

        event.stopPropagation();

        event.stopImmediatePropagation();
    }


    // ============================================================
    // KEYBOARD BLOCK
    // ============================================================

    function blockKeyboard(event) {

        const blocker =
            document.getElementById(
                "company-web-blocker"
            );


        if (!blocker) {
            return;
        }


        // Cho phép Ctrl + W / Cmd + W

        if (
            (event.ctrlKey || event.metaKey) &&
            event.key.toLowerCase() === "w"
        ) {

            return;
        }


        event.preventDefault();

        event.stopPropagation();

        event.stopImmediatePropagation();
    }


    // ============================================================
    // CREATE OVERLAY
    // ============================================================

    function createOverlay(
        url,
        reason
    ) {

        removeBlocker();


        const overlay =
            document.createElement(
                "div"
            );


        overlay.id =
            "company-web-blocker";


        const box =
            document.createElement(
                "div"
            );


        box.className =
            "company-web-blocker-box";


        const title =
            document.createElement(
                "h1"
            );


        title.textContent =
            "ACCESS RESTRICTED";


        const message =
            document.createElement(
                "p"
            );


        message.textContent =
            "Website này không được phép truy cập trong giờ làm việc.";


        const reasonText =
            document.createElement(
                "p"
            );


        reasonText.className =
            "company-web-blocker-reason";


        reasonText.textContent =
            "Reason: " +
            getReasonText(reason);


        const urlText =
            document.createElement(
                "p"
            );


        urlText.className =
            "company-web-blocker-url";


        urlText.textContent =
            url;


        box.appendChild(
            title
        );

        box.appendChild(
            message
        );

        box.appendChild(
            reasonText
        );

        box.appendChild(
            urlText
        );


        overlay.appendChild(
            box
        );


        if (
            document.documentElement
        ) {

            document.documentElement
                .appendChild(
                    overlay
                );

        }
    }


    // ============================================================
    // REMOVE BLOCKER
    // ============================================================

    function removeBlocker() {

        const blocker =
            document.getElementById(
                "company-web-blocker"
            );


        if (blocker) {

            blocker.remove();

        }
    }


    // ============================================================
    // OBSERVER
    // ============================================================

    function startBlockerObserver() {

        if (blockerObserver) {
            return;
        }


        blockerObserver =
            new MutationObserver(
                () => {

                    const blocker =
                        document.getElementById(
                            "company-web-blocker"
                        );


                    if (!blocker) {

                        const result =
                            checkUrl(
                                window.location.href
                            );


                        if (
                            isWorkingTime() &&
                            !result.allowed
                        ) {

                            createOverlay(
                                window.location.href,
                                result.reason
                            );

                        }

                    }

                }
            );


        blockerObserver.observe(
            document.documentElement,
            {
                childList: true,
                subtree: true
            }
        );
    }


    // ============================================================
    // REASON TEXT
    // ============================================================

    function getReasonText(reason) {

        const reasonMap = {
            
            BLACKLIST_MATCH:
                "Website nằm trong blacklist",

            DOMAIN_NOT_ALLOWED:
                "Domain không nằm trong whitelist",

            PATH_NOT_ALLOWED:
                "Đường dẫn không được phép",

            INVALID_URL:
                "URL không hợp lệ",

            DOMAIN_WHITELIST:
                "Domain được phép",

            DOMAIN_AND_PATH_WHITELIST:
                "Domain và path được phép",

            OUTSIDE_WORKING_TIME:
                "Ngoài giờ làm việc",

        };


        return (
            reasonMap[reason] ||
            reason
        );
    }


    // ============================================================
    // LOG
    // ============================================================

function logDecision(
    decision,
    url,
    reason
) {

    const logData = {

        decision:
            decision,

        reason:
            reason,

        url:
            url,

        title:
            document.title || "",

        hostname:
            window.location.hostname,

        timestamp:
            new Date()
                .toISOString()

    };


    // ========================================================
    // Console
    // ========================================================

    console.log(
        `[Company Web Control] ${decision}`,
        logData
    );


    // ========================================================
    // Send background service worker
    // ========================================================

    chrome.runtime
        .sendMessage({

            type:
                "ACCESS_LOG",

            payload:
                logData

        })
        .catch((error) => {

            console.warn(
                "[Company Web Control] Send log failed",
                error
            );

        });
}

    // ============================================================
    // SPA URL WATCHER
    // ============================================================

    function startUrlWatcher() {

        // ------------------------------------------
        // pushState
        // ------------------------------------------

        const originalPushState =
            history.pushState;


        history.pushState =
            function (...args) {

                originalPushState.apply(
                    this,
                    args
                );


                setTimeout(
                    checkCurrentPage,
                    0
                );
            };


        // ------------------------------------------
        // replaceState
        // ------------------------------------------

        const originalReplaceState =
            history.replaceState;


        history.replaceState =
            function (...args) {

                originalReplaceState.apply(
                    this,
                    args
                );


                setTimeout(
                    checkCurrentPage,
                    0
                );
            };


        // ------------------------------------------
        // Browser back / forward
        // ------------------------------------------

        window.addEventListener(
            "popstate",
            () => {

                setTimeout(
                    checkCurrentPage,
                    0
                );

            }
        );


        // ------------------------------------------
        // Fallback watcher
        // ------------------------------------------

        setInterval(
            () => {

                if (
                    window.location.href !==
                    currentCheckedUrl
                ) {

                    checkCurrentPage();

                }

            },
            1000
        );
    }


    // ============================================================
    // STORAGE CONFIG CHANGE
    // ============================================================

    chrome.storage.onChanged.addListener(
        (
            changes,
            areaName
        ) => {

            if (
                areaName !== "local"
            ) {
                return;
            }


            if (
                !changes.companyWebConfig
            ) {
                return;
            }


            CONFIG =
                changes
                    .companyWebConfig
                    .newValue;


            console.log(
                "[Company Web Control] Config updated",
                CONFIG
            );


            // Force check lại URL hiện tại
            currentCheckedUrl = null;


            checkCurrentPage();
        }
    );


    // ============================================================
    // START
    // ============================================================

    async function start() {

        const loaded =
            await loadConfig();


        if (!loaded) {

            console.error(
                "[Company Web Control] Extension initialization failed"
            );

            return;
        }


        checkCurrentPage();

        startUrlWatcher();
    }


    start();

})();

