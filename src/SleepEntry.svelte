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
    const updateData = {};

    updateData.start = Timestamp.fromDate(entry.start);

    if (entry.end) {
      updateData.end = Timestamp.fromDate(entry.end);
    }

    await updateDoc(doc(db, db_table, entry.id), updateData);
    editState.update((state) => ({ ...state, [entry.id]: false }));
  }
</script>

<div class="card mb-3 {latest ? 'text-bg-success' : 'border-success'}">
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
      {#if entry.deona}
        <div class="position-absolute bottom-0 end-0 m-2">
          <button
            class="btn {latest ? 'btn-dark' : 'btn-light'}"
            style="background: transparent; border: none;"
          >
            <i class="bi bi-cloud" style="font-size: 1.5em;"></i>
          </button>
        </div>
      {/if}
      <div class="position-absolute top-0 end-0 m-2">
        <!-- Edit button with icon -->
        <button
          on:click={() => enableEdit(entry.id)}
          class="btn {latest ? 'btn-dark' : 'btn-light'}"
          style="background: transparent; border: none;"
        >
          <i class="bi bi-pencil-square" style="font-size: 1.5em;"></i>
        </button>
        <button
          on:click={() => onDelete(entry.id)}
          class="btn {latest ? 'btn-dark' : 'btn-light'}"
          style="background: transparent; border: none;"
        >
          <i class="bi bi-trash-fill" style="font-size: 1.5em;"></i>
        </button>
      </div>
      <div class="row">
        <div class="col-auto text-center">
          <i class="bi bi-moon-stars" style="font-size: 4em;"></i>
        </div>
        <div class="col">
          <!-- <h5 class="card-title">Sleep</h5> -->
          <h2 class="display-5 fw-bold">
            {entry.end ? formatTime(entry.end - entry.start) : "In progress"}
          </h2>
          <p class="card-text {latest ? 'text-light' : 'text-muted'}">
            {formatCardTime(entry.start, entry.end)}
          </p>
        </div>
      </div>
    </div>
  {/if}
</div>
