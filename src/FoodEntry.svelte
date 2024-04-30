<script>
  import { formatCardTime } from "./utils";
  import { editState } from "./stores";
  import { enableEdit, cancelEdit } from "./editUtils";
  import { updateDoc } from "firebase/firestore";

  export let entry;
  export let latest;
  export let onDelete;

  async function saveEditFood(entry) {
    await updateDoc(doc(db, db_table, entry.id), {
      start: Timestamp.fromDate(entry.start),
      end: Timestamp.fromDate(entry.end),
      subtype: entry.subtype,
      amount: entry.amount,
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
      <div class="btn-group w-100 mb-2">
        <button
          on:click={() => (entry.subtype = "formula")}
          class="{entry.subtype === 'formula'
            ? 'btn btn'
            : 'btn btn-outline'}{latest ? '-light' : '-primary'}"
        >
          <i class="bi bi-cup-straw"></i> Infant Formula
        </button>
        <button
          on:click={() => (entry.subtype = "solid")}
          class="{entry.subtype === 'solid'
            ? 'btn btn'
            : 'btn btn-outline'}{latest ? '-light' : '-success'}"
        >
          <i class="bi bi-apple"></i> Solid Food
        </button>
      </div>
      <input
        type="number"
        bind:value={entry.amount}
        class="form-control mb-2"
        placeholder="Hoeveel?"
      />
      <button
        class="btn {latest ? 'btn-light' : 'btn-primary'} on:click={() =>
          saveEditFood(entry)}">Save</button
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
        <i
          class={entry.subtype === "formula"
            ? "bi bi-cup-straw"
            : "bi bi-apple"}
        ></i>
        {entry.end
          ? entry.subtype === "formula"
            ? "Infant Formula"
            : "Solid Food"
          : "Nog bezig"}
      </h5>
      <p class="card-text">
        {formatCardTime(entry.start, entry.end)}
      </p>
      <p class="card-text">
        Amount: {entry.amount
          ? entry.amount + (entry.subtype === "formula" ? " ml" : " gr")
          : "Niet ingevuld"}
      </p>
    </div>
  {/if}
</div>
