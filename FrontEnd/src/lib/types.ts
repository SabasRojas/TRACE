export interface Project {
    id: number;
    name: string;
    owner_id: number;
    locked: boolean;
}

export interface User {
    id: number;
    name: string;
    permissions: string[];
}
