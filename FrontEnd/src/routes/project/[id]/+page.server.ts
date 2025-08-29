import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, url, fetch }) => {
    const requester_id = url.searchParams.get('requester_id');
    const initials = url.searchParams.get('initials');

    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';

    const queryString = requester_id
        ? `?requester_id=${requester_id}`
        : '';

    const res = await fetch(`${backendUrl}/project/${params.id}${queryString}`);

    if (!res.ok) {
        return { error: 'Failed to fetch project info.' };
    }

    const data = await res.json();

    return {
        project: data.project,
        projectId: params.id,
        requesterId: requester_id,
        initials: initials
    };
};
