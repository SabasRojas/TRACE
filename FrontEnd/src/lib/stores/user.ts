// src/lib/stores/user.ts
import { writable } from 'svelte/store';

export const currentUser = writable<{ id: number; name: string; role: string } | null>(null);

if (typeof localStorage !== "undefined") {
  const stored = localStorage.getItem("currentUser");
  if (stored) currentUser.set(JSON.parse(stored));

  currentUser.subscribe(value => {
    if (value) localStorage.setItem("currentUser", JSON.stringify(value));
    else localStorage.removeItem("currentUser");
  });
}
