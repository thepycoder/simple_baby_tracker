<script>
  import { formatCardTime } from "./utils";
  import { editState } from "./stores";
  import { enableEdit, cancelEdit } from "./editUtils";
  import { updateDoc, Timestamp, doc } from "firebase/firestore";
  import { db, db_table } from "./firebase";

  export let entry;
  export let latest;
  export let onDelete;

  async function saveEditFood(entry) {
    console.log(entry);
    const updateData = {};

    updateData.start = Timestamp.fromDate(entry.start);
    updateData.subtype = entry.subtype;

    if (entry.end) {
      console.log(entry.end);
      updateData.end = Timestamp.fromDate(entry.end);
    }
    if (entry.amount) {
      console.log(entry.amount);
      updateData.amount = entry.amount;
    }

    await updateDoc(doc(db, db_table, entry.id), updateData);
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
          <i class="bi bi-cup-straw"></i> Flesje
        </button>
        <button
          on:click={() => (entry.subtype = "solid")}
          class="{entry.subtype === 'solid'
            ? 'btn btn'
            : 'btn btn-outline'}{latest ? '-light' : '-success'}"
        >
          <i class="bi bi-apple"></i> Vaste Voeding
        </button>
      </div>
      <input
        type="number"
        bind:value={entry.amount}
        class="form-control mb-2"
        placeholder="Hoeveel?"
      />
      <button
        class="btn {latest ? 'btn-light' : 'btn-primary'}"
        on:click={() => saveEditFood(entry)}>Opslaan</button
      >
      <button
        class="btn {latest ? 'btn-outline-light' : 'btn-outline-primary'}"
        on:click={() => cancelEdit(entry.id)}>Annuleer</button
      >
    </div>
  {:else}
    <div class="card-body position-relative">
      {#if entry.deona}
        <div class="position-absolute bottom-0 end-0 mx-3 my-2">
          <i class="bi bi-cloud"></i>
        </div>
      {/if}
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
            ? "Flesje"
            : "Vaste Voeding"
          : "Nog bezig"}
      </h5>
      <p class="card-text">
        {formatCardTime(entry.start, entry.end)}
      </p>
      <p class="card-text">
        Hoeveelheid: {entry.amount
          ? entry.amount + (entry.subtype === "formula" ? " ml" : " gr")
          : "Niet ingevuld"}
      </p>
    </div>
  {/if}
</div>
