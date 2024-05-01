<script>
  import { formatTime, formatCardTime } from "./utils";
  import { editState } from "./stores";
  import { enableEdit, cancelEdit } from "./editUtils";
  import { updateDoc, doc, Timestamp } from "firebase/firestore";
  import { db, db_table } from "./firebase";

  export let entry;
  export let latest;
  export let onDelete;

  async function saveEditSleep(entry) {
    await updateDoc(doc(db, db_table, entry.id), {
      start: Timestamp.fromDate(entry.start),
      end: Timestamp.fromDate(entry.end),
    });
    editState.update((state) => ({ ...state, [entry.id]: false }));
  }
</script>

<div class="card mb-3 {latest ? 'text-bg-success' : ''}">
  {#if $editState[entry.id]}
    <div class="card-body">
      <input
        type="datetime-local"
        class="form-control mb-2"
        bind:value={entry.edit_start}
        on:input={() => (entry.start = new Date(entry.edit_start))}
      />
      <input
        type="datetime-local"
        class="form-control mb-2"
        bind:value={entry.edit_end}
        on:input={() => (entry.end = new Date(entry.edit_end))}
      />
      <button
        class="btn {latest ? 'btn-light' : 'btn-primary'}"
        on:click={() => saveEditSleep(entry)}>Save</button
      >
      <button
        class="btn {latest ? 'btn-outline-light' : 'btn-outline-primary'}"
        on:click={() => cancelEdit(entry.id)}>Cancel</button
      >
    </div>
  {:else}
    <div class="card-body position-relative">
      <div class="position-absolute top-0 end-0 m-2">
        <!-- Edit button with icon -->
        <button on:click={() => enableEdit(entry.id)} class="btn btn-light">
          <i class="bi bi-pencil-square"></i>
        </button>
        <button
          on:click={() => onDelete(entry.id)}
          class="btn btn-light"
          style="right: 40px;"
        >
          <i class="bi bi-trash-fill"></i>
        </button>
      </div>
      <h5 class="card-title">
        <i class="bi bi-moon-stars"></i> Sleep
      </h5>
      <p class="card-text">
        {formatCardTime(entry.start, entry.end)}
      </p>
      <p class="card-text">
        Duration: {entry.end
          ? formatTime(entry.end - entry.start)
          : "In progress"}
      </p>
    </div>
  {/if}
</div>
