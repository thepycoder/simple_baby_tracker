<!-- src/App.svelte -->
<script>
  import { db, db_table } from "./firebase";
  import {
    collection,
    query,
    orderBy,
    onSnapshot,
    doc,
    limit,
    deleteDoc,
    where,
  } from "firebase/firestore";
  import { formatTime, convertToDatetimeLocal } from "./utils";
  import { onMount, onDestroy } from "svelte";
  import ConfirmModal from "./ConfirmModal.svelte";
  import SleepEntry from "./SleepEntry.svelte";
  import FoodEntry from "./FoodEntry.svelte";
  import FoodInput from "./FoodInput.svelte";
  import SleepInput from "./SleepInput.svelte";
  import StatsBar from "./StatsBar.svelte";
  import { foodEntries, sleepEntries } from "./stores";

  onMount(() => {
    const fq = query(
      collection(db, db_table),
      where("type", "==", "food"),
      orderBy("start", "desc"),
      limit(10)
    );
    const f_unsubscribe = onSnapshot(fq, (snapshot) => {
      const newFoodEntries = snapshot.docs.map((doc) => {
        const data = doc.data();
        return {
          id: doc.id,
          ...data,
          start: data.start.toDate(),
          edit_start: convertToDatetimeLocal(data.start.toDate()),
          end: data.end ? data.end.toDate() : null,
          edit_end: data.end ? convertToDatetimeLocal(data.end.toDate()) : null,
        };
      });

      const sq = query(
        collection(db, db_table),
        where("type", "==", "sleep"),
        orderBy("start", "desc"),
        limit(10)
      );
      const s_unsubscribe = onSnapshot(sq, (snapshot) => {
        const newSleepEntries = snapshot.docs.map((doc) => {
          const data = doc.data();
          return {
            id: doc.id,
            ...data,
            start: data.start.toDate(),
            edit_start: convertToDatetimeLocal(data.start.toDate()),
            end: data.end ? data.end.toDate() : null,
            edit_end: data.end
              ? convertToDatetimeLocal(data.end.toDate())
              : null,
          };
        });

        sleepEntries.set(newSleepEntries);
        foodEntries.set(newFoodEntries);
      });

      return () => {
        s_unsubscribe();
        f_unsubscribe(); // Unsubscribe when the component is destroyed
      };
    });
  });

  let showModal = false;
  let entryIdToDelete = null;

  async function removeEntry(entryId) {
    try {
      await deleteDoc(doc(db, db_table, entryId));
      // Optionally add some UI feedback here, e.g., a toast notification
    } catch (error) {
      console.error("Error removing document: ", error);
      // Handle errors, e.g., show an error message to the user
    }
  }

  function requestDelete(entryId) {
    entryIdToDelete = entryId;
    showModal = true;
  }

  function handleConfirm() {
    removeEntry(entryIdToDelete);
    showModal = false;
    entryIdToDelete = null;
  }

  function handleCancel() {
    showModal = false;
    entryIdToDelete = null;
  }
</script>

<main class="container mt-5 pb-5">
  <ConfirmModal
    show={showModal}
    message="Are you sure you want to delete this entry?"
    on:confirm={handleConfirm}
    on:cancel={handleCancel}
  />

  <div class="row justify-content-center">
    <!-- Sleep input -->
    <section class="col-md-6 mb-3">
      <SleepInput />
    </section>
    <!-- Food input -->
    <section class="col-md-6 mb-3">
      <FoodInput />
    </section>
  </div>
  <div class="row justify-content-center">
    <!-- Latest Sleep entry -->
    <div class="col-md-6">
      {#each $sleepEntries.slice(0, 1) as entry}
        <SleepEntry {entry} latest={true} onDelete={requestDelete} />
      {/each}
    </div>
    <!-- Latest Food entry -->
    <div class="col-md-6">
      {#each $foodEntries.slice(0, 1) as entry}
        <FoodEntry {entry} latest={true} onDelete={requestDelete} />
      {/each}
    </div>
  </div>
  <div class="row justify-content-center">
    <!-- All Sleep entries excluding the latest -->
    <div class="col-md-6">
      <h2 class="mobile-header">Slaapjes</h2>
      {#each $sleepEntries.slice(1) as entry}
        <SleepEntry {entry} latest={false} onDelete={requestDelete} />
      {/each}
    </div>
    <!-- All Food entries excluding the latest -->
    <div class="col-md-6">
      <h2 class="mobile-header">Voedingen</h2>
      {#each $foodEntries.slice(1) as entry}
        <FoodEntry {entry} latest={false} onDelete={requestDelete} />
      {/each}
    </div>
  </div>
  <div class="row justify-content-center">
    <h2 class="mobile-header">Statistiekskes</h2>
    <StatsBar />
  </div>
</main>

<style>
  .mobile-header {
    display: none;
  }

  @media (max-width: 768px) {
    .mobile-header {
      display: block;
      font-size: 1.5rem;
      margin-top: 20px;
      text-align: center;
    }
  }
</style>
