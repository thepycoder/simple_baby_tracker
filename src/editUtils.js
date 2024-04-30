import { editState } from "./stores";

export function enableEdit(entryId) {
    editState.update((state) => ({ ...state, [entryId]: true }));
  }

export function cancelEdit(entryId) {
    editState.update((state) => ({ ...state, [entryId]: false }));
  }