export const load = async ({ params, fetch, url }) => {
    const projectId = params.id;

    // Retrieve optional query params
    const requesterIdRaw = url.searchParams.get("requester_id");
    const initials = url.searchParams.get("initials") || "";

    // Validate requesterId (must be digits only)
    const requesterId = requesterIdRaw && /^\d+$/.test(requesterIdRaw) ? requesterIdRaw : null;

    let backendUrl = "http://localhost";
    if (typeof window !== "undefined") {
        backendUrl = sessionStorage.getItem("backendUrl") || "http://localhost";
    }

    // Build the fetch URL
    const query = requesterId ? `?requester_id=${requesterId}` : "";
    const fetchUrl = `${backendUrl}:8000/project/${projectId}${query}`;

    try {
        const res = await fetch(fetchUrl);

        if (!res.ok) {
            let errorMsg = `API error: ${res.status}`;
            try {
                const errorData = await res.json();
                errorMsg = errorData.detail || `API error: ${res.status}`;
            } catch (e) { /* Ignore JSON parsing errors */ }
            console.error("❌ Layout Load API returned error:", errorMsg);
            return {
                project: null,
                projectId,
                requesterId,
                initials,
                error: errorMsg
            };
        }

        const data = await res.json();

        // Ensure IPList is always parsed as a list of tuples
        let rawList = data.project.IPList;
        try {
            if (typeof rawList === "string") {
                rawList = JSON.parse(rawList);
            }
        } catch (e) {
            console.warn("⚠️ Layout Load Failed to parse IPList:", rawList);
            rawList = [];
        }
        data.project.IPList = Array.isArray(rawList) ? rawList : [];

        return {
            project: data.project,
            projectId,
            requesterId,
            initials,
            error: null
        };

    } catch (err) {
        console.error("❌ Layout Load Failed to fetch project:", err);
        return {
            project: null,
            projectId,
            requesterId,
            initials,
            error: err instanceof Error ? err.message : "Failed to connect to the API."
        };
    }
};
